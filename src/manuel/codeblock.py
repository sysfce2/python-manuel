import re
import manuel
import textwrap

CODEBLOCK_START = re.compile(r'^\.\.\s*(invisible-)?code-block::\s*python\b', re.MULTILINE)
CODEBLOCK_END = re.compile(r'(\n\Z|\n(?=\S))')


class CodeBlock(object):
    def __init__(self, code):
        self.code = code


def find_code_blocks(document):
    for region in document.find_regions(CODEBLOCK_START, CODEBLOCK_END):
        source = textwrap.dedent('\n'.join(region.source.splitlines()[1:]))
        source_location = '%s:%d' % (document.location, region.lineno)
        code = compile(source, source_location, 'exec', 0, True)
        document.replace_region(region, CodeBlock(code))


def execute_code_block(region, document, globs):
    if not isinstance(region.parsed, CodeBlock):
        return

    exec region.parsed.code in globs
    del globs['__builtins__'] # exec adds __builtins__, we don't want it


class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_code_blocks], [execute_code_block])

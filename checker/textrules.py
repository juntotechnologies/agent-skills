"""Rules that read changed text, for any file type."""
import fnmatch
import json
import re
from pathlib import Path, PurePosixPath

from model import Fault

UV_ONLY = json.loads((Path(__file__).resolve().parent / 'uv_only.json').read_text())
UV_SEGMENT = re.compile(r'\buv\s+[^;&|]*|\buvx\b[^;&|]*|\buv["\']?\s*,[^\]]*')
WORD_START = r'(^|[\s;&|(`"\'=/])'
# why: a quoted command in JSON, YAML or plist ends in a quote or tag, and a quoted key is followed by a colon
WORD_END = r'(\s|$|["\'<>,)\]](?!\s*:))'
BARE = re.compile(WORD_START + '(' + '|'.join(UV_ONLY['interpreters']) + ')' + WORD_END)
ALTERNATIVE = re.compile(WORD_START + '(' + '|'.join(map(re.escape, UV_ONLY['alternatives'])) + r')(\s|$)')
INSTALLS = [re.compile(pattern) for pattern in UV_ONLY['installs']]
CI_ACTION = re.compile('|'.join(map(re.escape, UV_ONLY['ci_actions'])))
INTERPRETER_PATH = re.compile('(?:.*/)?(?:' + '|'.join(UV_ONLY['interpreters']) + ')')
COMMAND_SPLIT =re.compile(r'[;&|]+')
COMMAND_PREFIX = re.compile(r'^(?:(?:sudo|env|time|nohup|exec|command)\s+|\w+=\S*\s+)+')
PYTHON_SHEBANG = re.compile(r'^#!.*\bpython[0-9.]*\b')
LIST_PUNCTUATION = re.compile(r'[\[\]"\',]')
LIST_ELEMENT = re.compile(r'^\s*["\']?(?:' + '|'.join(UV_ONLY['interpreters']) + r')["\']?,?\s*$')
UV_ELEMENT_ABOVE = re.compile(r'(?:^|\s)uv\s[^;&|]*$')


def holds_commands(path, limits):
    name = PurePosixPath(path).name
    return PurePosixPath(path).suffix in limits['js_suffixes'] or any(
        fnmatch.fnmatch(name, pattern) for pattern in limits['shell_paths'])


def command_installs_python(command):
    bare = COMMAND_PREFIX.sub('', command.strip())
    return any(pattern.search(bare) for pattern in INSTALLS)


def line_breaks_uv(text):
    stripped = UV_SEGMENT.sub(' ', text)
    if BARE.search(stripped) or ALTERNATIVE.search(stripped) or CI_ACTION.search(stripped):
        return True
    return any(command_installs_python(command) for command in COMMAND_SPLIT.split(stripped))


def under_uv_above(rows, index, span):
    """why: a JSON or YAML argument list may hold `uv`, `run`, `python` one element per line."""
    above = ' '.join(rows[max(0, index - span):index])
    return bool(UV_ELEMENT_ABOVE.search(LIST_PUNCTUATION.sub(' ', above)))


def adds_uv_fault(rows, line, span):
    row = rows[line - 1]
    covered = LIST_ELEMENT.match(row) and under_uv_above(rows, line - 1, span)
    return line_breaks_uv(row) and not covered and not row.lstrip().startswith('#')


def uv_faults(path, source, lines, limits):
    if not holds_commands(path, limits):
        return []
    rows, span = source.splitlines(), limits['list_context_lines']
    return [Fault(path, line, line, 'uv-only', 'call Python through uv') for line in sorted(lines)
            if line <= len(rows) and adds_uv_fault(rows, line, span)]


def shebang_faults(path, source, lines):
    first = source.splitlines()[0] if source else ''
    if 1 not in lines or not PYTHON_SHEBANG.match(UV_SEGMENT.sub(' ', first)):
        return []
    return [Fault(path, 1, 1, 'uv-only', f'shebang must be `{UV_ONLY["shebang"]}`')]


def claude_md_faults(path, lines):
    return [Fault(path, 1, 1, 'no-claude-md', 'use AGENTS.md')] if PurePosixPath(path).name == 'CLAUDE.md' and lines else []

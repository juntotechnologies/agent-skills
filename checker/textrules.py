"""Rules that read changed text, for any file type."""
import fnmatch
import re
from pathlib import PurePosixPath

from model import Fault

UV_PREFIX = re.compile(r'uv\s+(run|pip|tool)\b[^;&|]*|uvx\b[^;&|]*')
BARE = re.compile(r'(^|[\s;&|(`"\'])(python3?|pip3?)(\s|$)')
SETUP_PYTHON = re.compile(r'actions/setup-python')


def is_shell_like(path, limits):
    name = PurePosixPath(path).name
    return any(fnmatch.fnmatch(name, pattern) for pattern in limits['shell_paths'])


def line_breaks_uv(text):
    stripped = UV_PREFIX.sub(' ', text)
    return bool(BARE.search(stripped) or SETUP_PYTHON.search(stripped))


def uv_faults(path, source, lines, limits):
    if not is_shell_like(path, limits):
        return []
    rows = source.splitlines()
    return [Fault(path, line, line, 'uv-only', 'call Python through uv') for line in sorted(lines)
            if line <= len(rows) and line_breaks_uv(rows[line - 1]) and not rows[line - 1].lstrip().startswith('#')]


def claude_md_faults(path, lines):
    return [Fault(path, 1, 1, 'no-claude-md', 'use AGENTS.md')] if PurePosixPath(path).name == 'CLAUDE.md' and lines else []

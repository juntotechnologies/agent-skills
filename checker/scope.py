"""Which lines a change touched, from `git diff -U0`."""
import re

from model import Fault

HUNK = re.compile(r'^@@ -\S+ \+(\d+)(?:,(\d+))? @@')
TARGET = '+++ b/'


def hunk_lines(match):
    start, count = int(match.group(1)), int(match.group(2) or 1)
    return range(start, start + count)


def parse_diff(text):
    changed, path = {}, None
    for line in text.splitlines():
        path = line[len(TARGET):] if line.startswith(TARGET) else path
        match = HUNK.match(line)
        if match:
            changed.setdefault(path, set()).update(hunk_lines(match))
    return changed


def touched(fault: Fault, changed):
    lines = changed.get(fault.path, set())
    return any(line in lines for line in range(fault.line, fault.end + 1))

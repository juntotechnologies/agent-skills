"""Shared fault type and rule IDs. A fault's line span decides whether a change touched it."""
from dataclasses import dataclass

RULES = ('comment-why-only', 'docstring-why-only', 'no-nested-function', 'no-lambda', 'function-length', 'inline-sql',
         'uv-only', 'no-claude-md', 'syntax', 'ruff', 'eslint', 'repo-tests', 'tool-failed')


@dataclass(frozen=True)
class Fault:
    path: str
    line: int
    end: int
    rule: str
    message: str

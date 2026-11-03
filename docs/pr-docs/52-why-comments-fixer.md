# PR 52: Comment rule autofix

Status: in-scope work complete

Branch: `feat/why-comments-fixer`

## Goal
`local/why-comments` gets an ESLint fixer: deletes disallowed comment + own line, incl JSX `{/* */}`. Lets repos clear old comment faults by tool.

## Implementation Checklist
- [x] Fixer in `checker/js/why-comments.mjs`
- [x] Test in `tests/test_checker.py`

## Smoke Tests
- `uv run --no-project --with pytest python -m pytest tests/test_checker.py`

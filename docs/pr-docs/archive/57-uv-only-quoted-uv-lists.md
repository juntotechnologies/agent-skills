# PR 57: uv-only fixes after the first full scan

Status: done

Branch: `fix/uv-only-quoted-uv-lists`

## Goal

Three findings from scanning swarm-infra with the PR 56 gate.

1. PR 56 made a quoted interpreter a fault. That also flagged the correct form: `"command": ["~/.local/bin/uv", "run", "python", ...]` in `swarm-registry.json`.
2. `scripts/install-services.py:89` returns `["/usr/bin/python3", ...]` from a helper; the rule only read process calls, so a command built in one place and run in another slipped.
3. Converting `#!/usr/bin/env python3` to `#!/usr/bin/env -S uv run --script` needs PEP 723 inline dependencies for scripts that import PyYAML, and the comment rule called that block a fault.

## Implementation Checklist

### Tier 1 - Tests first

- [x] A JSON or YAML list that starts a command with `uv` passes; `["python3", "-m", "uv", "run"]` still faults.
- [x] A Python list of 2+ items that starts with an interpreter (`return ["/usr/bin/python3", str(script)]`) is a fault wherever it is used; a list that is the command of a process call is reported once; a 1-item list or `['uv', 'python']` passes.

### Tier 2 - Fix

- [x] `UV_SEGMENT` also strips from `uv` (quoted, then a comma) to the end of the list.
- [x] `pyrules.comment_faults` skips a closed PEP 723 `# /// script` block (`metadata_lines`, the PEP's own regex); an unclosed block or a stray `# dependencies` line still faults.
- [x] `pyrules.uv_call_faults` also reports a command list that starts with an interpreter (`starts_with_interpreter`); `textrules.INTERPRETER_PATH` comes from `uv_only.json`.

## Smoke Tests

Not applicable: no UI. Covered by `test_uv_only_catches_an_interpreter_quoted_in_data_files` and `test_a_bare_interpreter_before_uv_in_a_list_is_still_a_fault`. Real repo: `ops check --all --lint-only` in swarm-infra no longer lists `swarm-registry.json:398`.

## Product Decisions

- Slip found by the first full scan after PR 56: the new rule had a false positive. Fixed in its own PR the same day.

## Scope

- `checker/textrules.py`, `tests/test_checker.py`.

## Non-Goals

- Multi-line plist arrays (one `<string>` per line): a line cannot know its list.

## Rollback

- Revert the merge commit.

# PR planned: uv-only accepts quoted uv command lists

Status: planned

Branch: `fix/uv-only-quoted-uv-lists`

## Goal

PR 56 made a quoted interpreter a fault. That also flagged the correct form: `"command": ["~/.local/bin/uv", "run", "python", ...]` in `swarm-registry.json`.

## Implementation Checklist

### Tier 1 - Tests first

- [x] A JSON or YAML list that starts a command with `uv` passes; `["python3", "-m", "uv", "run"]` still faults.

### Tier 2 - Fix

- [x] `UV_SEGMENT` also strips from `uv` (quoted, then a comma) to the end of the list.

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

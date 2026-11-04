# PR 56: uv-only gate holes

Status: done

Branch: `fix/uv-only-gate-holes`

## Goal

Two documented `uv-only` checks never fired. Both now do.

## Context

PR 55 documents "any file, line 1: python shebang" and "bare or absolute `python*` in json, plist". A full scan of swarm-infra found neither:

| Hole | Cause | Live effect found |
|---|---|---|
| Shebang rule | `shebang_faults` existed and had a unit test, but `check.py` never called it | 33 files start with `#!/usr/bin/env python3` |
| Quoted interpreter | `python3` had to be followed by space or end of line; JSON `"/usr/bin/python3",` and plist `<string>/usr/bin/python3</string>` end in a quote or tag | a launchd job runs `/usr/bin/python3` (3.9.6) every 15 min |

## Implementation Checklist

### Tier 1 - Tests first

- [x] Quoted interpreter in JSON, YAML, plist is a fault; a quoted key such as `"python": "3.14.10"` is not.
- [x] `check.text_faults` reports a python shebang for any file type; a uv shebang passes.

### Tier 2 - Fix

- [x] `WORD_END` accepts a closing quote, tag or bracket after the interpreter; a quote followed by `:` (a key) stays allowed.
- [x] `file_text_faults` runs `shebang_faults` beside `uv_faults`.
- [x] `shebang_faults` ignores a `uv ...` segment, so `#!/usr/bin/env -S uv run --python 3.14 --script` passes.

## Smoke Tests

Not applicable: no UI. Covered by tests:

| Check | Covered by |
|---|---|
| Quoted command forms fault, keys pass | `test_uv_only_catches_an_interpreter_quoted_in_data_files` |
| Shebang reaches the text pass | `test_the_shebang_rule_runs_in_the_text_pass_for_any_file_type` |
| Real repo | `ops check --all --lint-only` in swarm-infra: 18 hits before, 40 after |

## Product Decisions

- Rule `slip-adds-gate` applies: the slip is the gate, so the gate is fixed first and the backlog cleanups follow per repo.
- A pinned uv interpreter path in data (`release.json`) is an exemption declared in that repo's `ops-check.json`, not a path allowance in the rule: textually it cannot be told from a command.

## Scope

- `checker/textrules.py`, `checker/check.py`, `tests/test_checker.py`.

## Non-Goals

- Fixing the hits in other repos (own PRs, tracked in the system roadmap, thread F).

## Rollback

- Revert the merge commit. Gates fall back to the PR 55 behavior.

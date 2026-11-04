# PR planned: uv-only reads JavaScript and TypeScript files

Status: planned

Branch: `fix/uv-only-js-files`

## Goal

A Node test that runs `execFileSync("python3", ...)` passed the gate, because `uv-only` read shell, json, yaml and plist files only. It now reads `.js .mjs .cjs .ts .tsx .jsx` too.

## Context

Found by the agent that cleaned `ClinPharmStats`: `tests/page-citations.test.mjs:10` runs bare `python3`. A full scan of the five cloned repos finds 2 hits with the new rule (that one, and a fixture string in the agent's own helper test).

## Implementation Checklist

### Tier 1 - Tests first

- [x] `a.mjs`, `a.js`, `a.cjs`, `a.ts`, `a.tsx`, `a.jsx`: `execFileSync('python3', ...)` faults, an `execFileSync('uv', ...)` line passes.

### Tier 2 - Fix

- [x] `textrules.holds_commands` (was `is_shell_like`) also accepts any suffix in `limits.json` `js_suffixes`: one list, no second copy.

## Smoke Tests

Not applicable: no UI. Covered by `test_uv_only_reads_javascript_and_typescript_files_too`. Real repos: `ops check --all --lint-only` in 5 clones finds 2 JS hits and no false positive in the other 4.

## Product Decisions

- Slip named under rule `slip-adds-gate`: the gate skipped a file type that can start Python.

## Scope

- `checker/textrules.py`, `tests/test_checker.py`.

## Non-Goals

- Markdown prose, docstrings, comments inside Python files.

## Rollback

- Revert the merge commit.

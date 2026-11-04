# PR 60: uv-only reads multi-line argument lists

Status: done

Branch: `fix/uv-only-multiline-lists`

## Goal

A `uv run --no-project python -m x` command written one element per line in JSON or YAML is not a fault. A bare interpreter in the same shape still is.

## Context

Found 2026-11-03 while fixing evals Spark launch hits: `"python",` on its own line, under `"entrypoint": "uv"` and `"run"`, was flagged. The line-based rule cannot see the lines above.

## Implementation Checklist

### Tier 1 - Quick wins

- [ ] Test: `uv`, `run`, `--no-project`, `python` one per line passes; `"entrypoint": "python3"` + `"python"` element still faults; `uv` more than 5 lines above does not cover
- [ ] `textrules.uv_faults`: a line that is only an interpreter list element is covered when a standalone `uv` element is within `list_context_lines` lines above
- [ ] `limits.json` `list_context_lines: 5` (one source for the window)

## Acceptance Coverage

| Requirement | Entry points | Roles and data | Persistence | Verification |
|---|---|---|---|---|
| No false positive on split uv lists | commit hook, CI, write hook | json, yaml | none | `tests/test_checker.py`; `ops check --all --lint-only` in evals shows 0 `uv-only` |

## Smoke Tests

Not applicable: no UI. Covered by tests.

## Product Decisions

Gate fixes follow rule `slip-adds-gate`.

## Scope

Text rule only.

## Non-Goals

- Reading YAML or JSON structure with a parser. Context window is enough for this shape.

## Rollback

Revert the commit.

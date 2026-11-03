# PR 44: UI rules on demand

Status: in-scope work complete

Branch: `feature/ui-rules-on-demand`

## Goal

Shaun, 2026-11-03: all UI rules kept + iterated forever w/o growing context. Agents know when to call them.

## Implementation Checklist

- [x] `taste.py rules [--area] [--id]`: 1 line per rule, loaded by query
- [x] 2 rules: `control-padding`, `one-card-padding`
- [x] SKILL workflow: query rules, `ops site-check`, new fault → new check
- [x] Global AGENTS: 2-line UI pointer

## Smoke Tests

Not applicable: no UI. Repo tests pass.

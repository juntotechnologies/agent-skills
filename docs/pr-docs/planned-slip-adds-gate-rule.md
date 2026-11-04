# PR planned: A slip adds its gate

Status: planned

Branch: `feature/slip-adds-gate-rule`

## Goal

Shaun, 2026-11-03: a fault slipped past the shared lint; "patch things that slip by ... so it never gets missed again". Global rule: fixing the instance is not done until the gate that should have caught it is added or widened in the same change.

Prose only: no tool can decide whether a gate was missing. The gates themselves are tools (write hook, commit + push hooks, CI): personal-config PR 36.

## Implementation Checklist

- [x] Rule `slip-adds-gate` in `rules/rules.json`, section Checks
- [x] `global/AGENTS.md` regenerated (`gen_rules.py check` passes)
- [x] Suite: `ops check` passes on the committed tree

## Smoke Tests

Not applicable: no UI. Generated file + registry drift check cover it.

## Related Docs

- personal-config PR 36 (write-time lint gate), merged

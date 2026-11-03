# PR 46: Rule registry + shared checker

Status: done

Branch: `feature/rule-registry`

## Goal

Shaun, 2026-11-03: rules central, deterministic, iterable. Every rule 1 place; same check in hook, CI, merge.

## Implementation Checklist

- [x] `rules/rules.json`: 50 global rules; `scripts/gen_rules.py` writes `global/AGENTS.md`; output byte-identical to old file
- [x] `checker/`: comment + docstring `why:` only, nested fn, lambda, fn length, inline SQL, uv only, no `CLAUDE.md`, ruff + ESLint presets
- [x] Changed lines only by default; `--all` for audit
- [x] `.github/workflows/check.yml`: reusable CI; `checker/templates/check-caller.yml`

## Known Limits

Enforcers not flipped yet: `ops check` + hub pilot next. ESLint complexity fault spans fn head only.

## Smoke Tests

Not applicable: no UI. `tests/test_checker.py` incl real git run: old line passes, new line fails.

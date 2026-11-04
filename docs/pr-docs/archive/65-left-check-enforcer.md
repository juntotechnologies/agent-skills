# PR 65: rule row-rec-yes-do-it names its enforcer

Status: done

Branch: `feature/left-check-enforcer`

## Goal

`ops left-check` (personal-config PR 46, Stop hook, registered) now enforces rule `row-rec-yes-do-it`. The rule gets `enforcer: hook ops left-check (Stop)`; enforced rules leave `~/AGENTS.md` (the hook fires by itself and its block message carries the wording).

## Implementation Checklist

### Tier 1 - Registry

- [x] `rules/rules.json` enforcer set; `global/AGENTS.md` regenerated; `ops rules --id row-rec-yes-do-it` shows `hook`

## Smoke Tests

Registry + generated file only; no manual walk.

## Product Decisions

- Prose leaves the prompt once a hook enforces it (rule `gates-not-memory`): a rule in both places drifts.

## Scope

- 1 rule.

## Non-Goals

- Changing the stop-list wording (`~/AGENTS.md` Autonomy).

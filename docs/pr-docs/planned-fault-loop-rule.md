# PR planned-fault-loop-rule: Tool errors get a gate or a waiver, enforced by `ops faults`

Status: underway

Branch: `feature/fault-loop-rule`

## Goal

Shaun, 2026-11-03: an agent hit several tool errors in 1 turn, retried each by hand, patched no gate. Rule text alone failed. The rule now has an enforcer: the `ops faults` hooks record each failed tool call and block the stop until each fault has `--gate` or a reasoned `--waive`.

## Context

- Enforcer + tool: [personal-config PR 40](https://github.com/shaunporwal/personal-config/pull/40) (`ops faults`, hook entries in `ops.json`). Merge that first; this PR is rule text only.
- Enforced rules are not rendered into `global/AGENTS.md`, so the prose half stays where it is: the "tool error" clause moves from `north-star-literals` to `north-star-done-check` (1 place for the sentence, no restatement).
- Codex has no hooks: the prose clause in `north-star-done-check` is all it gets. Claude Code gets the enforcer too.

## Implementation Checklist

### Tier 1 - Rule text

- [x] `north-star-fault-loop` (North star, `enforcer: {kind: hook, by: ops faults (...)}`): 1 gate or waiver per fault
- [x] `north-star-done-check` carries the "tool error -> patch its cause, name the gate" clause; `north-star-literals` drops it
- [x] `docs/rules-system.md`: where-things-live row for the loop

### Tier 2 - Generated + checks

- [x] `scripts/gen_rules.py build`; `gen_rules.py check` passes; `global/AGENTS.md` diff = the 2 moved lines
- [x] Agent-skills unit tests pass; `ops check` passes on the committed tree

## Acceptance Coverage

| Requirement | Entry points | Roles and data | Persistence | Verification |
|---|---|---|---|---|
| Rule has a named enforcer | `ops rules --id north-star-fault-loop` | agents | `rules/rules.json` | `ops rules` shows `[hook]`; registry tests |
| Prose pointer still reaches agents | `~/AGENTS.md`, `~/.codex/AGENTS.md` | all | `scripts/install.sh` (not run here) | `gen_rules.py check` |

## Smoke Tests

Not applicable: no UI. Rule text only.

## Product Decisions

- The enforced rule is not in generated prose; the block message from the hook carries the instruction at the moment it matters.
- `north-star-literals` keeps only literals + repeating patterns, so each sentence lives in 1 rule.
- `scripts/install.sh` is not run: the live `~/AGENTS.md` updates when Shaun installs.

## Scope

- `rules/rules.json`, generated `global/AGENTS.md`, `docs/rules-system.md`.

## Non-Goals

- Registering the hooks in live settings (`ops hooks --apply`, Shaun's step after PR 40 merges).

## Rollback

Revert the commit; regenerate; reinstall.

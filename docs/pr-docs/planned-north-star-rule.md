# PR planned: North star rule

Status: planned

Branch: `feature/north-star-rule`

## Goal

Global rules state Shaun's aim: hands-off. Agents turn every fact, procedure, host access and slip a tool can decide into a deterministic artifact, unasked.

## Context

Shaun (2026-11-03) had to remind an agent to add a CLI for Spark access. Existing rules (`automate-over-prose`, `slip-adds-gate`, CLI over prose) cover parts. None names the aim or the end-of-task question.

## Implementation Checklist

### Tier 1 - Quick wins

- [ ] 3 rules in new section `North star` (first section): `north-star-hands-off`, `north-star-done-check`, `north-star-literals`
- [ ] Regenerate `global/AGENTS.md` (`gen_rules.py build`); `gen_rules.py check` passes
- [ ] `ops check` passes on the committed tree

## Acceptance Coverage

| Requirement | Entry points | Roles and data | Persistence | Verification |
|---|---|---|---|---|
| New rules reach every agent | `~/AGENTS.md`, `~/.codex/AGENTS.md` | all | `scripts/install.sh` | `gen_rules.py check`; `ops rules --id north-star-hands-off` |

## Smoke Tests

Not applicable: no UI. Rule text only.

## Product Decisions

Decided by Shaun, 2026-11-03: hands-off is the true north; lint, registry, CI and hook rules are added without asking.

## Scope

Rule text. Enforcers (a literal-fact lint, an end-of-turn done-check hook) are separate PRs, tracked in the system roadmap.

## Non-Goals

- Building those enforcers here.

## Rollback

Revert the commit; regenerate; reinstall.

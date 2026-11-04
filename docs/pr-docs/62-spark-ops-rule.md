# PR 62: Spark access goes through `ops spark`

Status: underway

Branch: `feature/spark-ops-rule`

## Goal

Agents reach the DGX Spark through `ops spark`, never by recalling its address, ssh flags, docker cmds or ports. Global rules carry the 1-line pointer; `ops guard` is the enforcer.

## Context

- Tool + guard: [personal-config PR 39](https://github.com/shaunporwal/personal-config/pull/39) (`ops spark`, `guard.remote`). Merge that first; this PR is rule text only.
- Enforced rules are not rendered into `global/AGENTS.md` (generator keeps `enforcer: null` only), so the pointer is its own prose rule.

## Implementation Checklist

### Tier 1 - Rule text

- [x] `spark-through-ops-spark` (Acting, prose, `enforcer: null`): pointer to `ops spark --help`; no command text
- [x] `infra-access-through-ops-host` (Acting, `enforcer: {kind: hook, by: ops guard}`): registered host -> `ops <host>` verb; raw `ssh <host> docker|systemctl` mutation blocked
- [x] `docs/rules-system.md` guard row names the new block

### Tier 2 - Generated + checks

- [x] `scripts/gen_rules.py build`; `gen_rules.py check` passes; only the pointer line is added to `global/AGENTS.md`
- [x] Agent-skills unit tests pass; `ops check` passes on the committed tree

## Acceptance Coverage

| Requirement | Entry points | Roles and data | Persistence | Verification |
|---|---|---|---|---|
| Pointer reaches every agent | `~/AGENTS.md`, `~/.codex/AGENTS.md` | all | `scripts/install.sh` (not run here) | `gen_rules.py check`; `ops rules --id spark-through-ops-spark` |
| Raw ssh mutation has a named rule | `ops guard` | agents | `ops.json` `guard.remote` | personal-config `test_guard_ssh.py` |

## Smoke Tests

Not applicable: no UI. Rule text only.

Agent-run on commit `f34bb37`: `ops check` exit 0; 105 unit tests OK (1 skipped); `gen_rules.py check` exit 0.

## Product Decisions

- Pointer lives in `Acting`, next to the other hands-on rule.
- Generated file only; `scripts/install.sh` is not run, so the live `~/AGENTS.md` updates when Shaun installs.

## Scope

- `rules/rules.json`, generated `global/AGENTS.md`, `docs/rules-system.md`.

## Non-Goals

- The tool and the guard (personal-config PR 39).
- A rule for other hosts: each new `ops <host>` tool adds its own pointer line.

## Rollback

Revert the commit; regenerate.

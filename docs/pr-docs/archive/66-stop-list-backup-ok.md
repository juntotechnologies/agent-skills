# PR 66: a verified backup + rollback makes a prod data write a "do it"

Status: done

Branch: `feature/stop-list-backup-ok`

## Goal

Slip, 2026-11-03: swarm-infra PR 49 (Hermes upgrade, forward-only `state.db` migration) was asked as `[stop: prod-data]` although the backup was taken and checked (`ops hermes-backup`, integrity ok) and the PR doc names the rollback. Shaun: "obviously you should deploy Hermes." The stop-list line `prod data writes (migrations, backfills, deletes)` becomes `prod data writes w/o a verified backup + documented rollback (...)`.

## Implementation Checklist

### Tier 1 - Rule text

- [x] `rules/rules.json` Autonomy stop-list rule edited; `global/AGENTS.md` regenerated

## Smoke Tests

Rule text only; no manual walk.

## Product Decisions

- A write with a verified backup and a written rollback is reversible, so it falls under "reversible in-scope choice: decide". Without either it stays a stop-list item (tag `[stop: prod-data]`).

## Scope

- 1 rule line.

## Non-Goals

- Changing the other stop-list items.

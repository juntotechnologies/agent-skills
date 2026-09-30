# PR 19: Delegation Runs On The Mac Mini Only

Status: done

Branch: `chore/delegation-mac-only`

## Goal

Keep `local-model-delegation` truthful after the Spark was reserved for training
and benchmarks on 2026-09-30.

## Context

The skill told agents to fan out concurrently on the DGX Spark. After
swarm-infra PR 14 and hermes-config PR 26 the Spark serves nothing by default and
Hermes' delegation route points at the Mac mini. `delegate.py` reads its worker
endpoint from that route, so `fanout` keeps working with no code change, but on a
one-slot server its workers run in sequence.

## Implementation Checklist

- [x] Routing says everything runs on the Mac and never on the Spark; `fanout`
  isolates tasks rather than speeding them up.
- [x] Drop the Spark from the description, the fan-out label and the latency line.
- [x] Delegation (18) and install tests pass; wording only.

## Smoke Tests

- [ ] After hermes-config PR 26 deploys, `delegate.py fanout` with two tasks →
  both return, and the helper reports the Mac as the worker.

  Partly met 2026-09-30. Fan-out requires at least three tasks, so it was run with
  three; all returned in 3.0 s through the Mac. The helper still labels the route
  `spark-to-mac`, because its internal name for Hermes' delegation endpoint is
  "spark" — a stale label, not a routing fault.

## Non-Goals

- No helper change.

## Related Docs

- [PR 18 delegation for Claude Code](./18-delegation-for-claude-code.md)

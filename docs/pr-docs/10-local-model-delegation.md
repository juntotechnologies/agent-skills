# PR 10: Local Model Delegation

Status: in-scope work complete (manual smoke tests pending)

Branch: `feature/local-model-delegation`

## Goal

Give Codex a durable, reusable way to offload suitable analysis to Shaun's
local Mac mini and DGX Spark models while retaining final judgment, repository
mutation, and verification in Codex. Route serial work to the Mac mini and
parallel independent work to the Spark, with optional Mac-side synthesis before
returning a bounded result to Codex.

## Context

Hermes already routes its primary model to the Mac mini and delegated children
to the Spark, but `hermes -z` bypasses tool approvals and Hermes's built-in MCP
server exposes messaging conversations rather than a constrained inference
surface. The new skill therefore needs a read-only model-only seam that cannot
invoke Telegram, filesystem, shell, or other Hermes tools.

## Implementation Checklist

Ordered least -> most consequential/complex: quick, contained wins first;
integration and installation last.

### Tier 1 - Routing contract

- [x] Add failing tests for dynamic endpoint discovery from the existing Hermes
  and swarm configuration, with no hardcoded tailnet addresses.
- [x] Implement the smallest endpoint-discovery abstraction that makes those
  tests pass.
- [x] Add failing tests for the routing policy: Mac for single/serial work,
  Spark for parallel batches, and Spark fan-out followed by Mac synthesis for
  large divisible work.
- [x] Implement the routing policy and bounded response contract.

### Tier 2 - Read-only delegation helper

- [x] Add failing tests for OpenAI-compatible request construction, concurrency,
  timeouts, unavailable endpoints, malformed responses, and output limits.
- [x] Implement a read-only helper that talks directly to inference endpoints
  and exposes no agent tools or mutation path.
- [x] Test each modular helper independently and run the full repository test
  suite.

### Tier 3 - Skill and propagation

- [x] Add the `local-model-delegation` skill with discriminating activation
  guidance, workload-routing rules, safety boundaries, and stopping conditions.
- [x] Validate the skill with the skill-creator validator.
- [x] Install/link the canonical skill into supported agent environments with
  `scripts/install.sh` and verify the installed links resolve to this repo.
- [x] Exercise one serial Mac request and one parallel Spark-to-Mac request,
  then confirm Codex receives bounded results.

## Smoke Tests

- [ ] Ask Codex for one bounded analysis task -> the Mac mini handles it and
  Codex reports a concise verified result.
- [ ] Ask Codex to compare at least three independent items -> Spark handles the
  fan-out, the Mac mini condenses the findings, and Codex reports the final
  verified result.
- [ ] Make either endpoint unavailable -> Codex reports delegation unavailable
  and continues safely without attempting a mutation or silently fabricating a
  local-model result.

## Product Decisions

- Use both local machines asymmetrically: Mac mini for serial work and
  synthesis; Spark for parallel independent work.
- Do not redundantly send every prompt to both models; cross-check with both
  only when uncertainty or task risk justifies the added compute.
- Call model inference endpoints directly so delegated work is read-only by
  construction; do not use `hermes -z` as the durable execution seam.
- Keep Codex responsible for decomposition, final judgment, code changes,
  command execution, and verification.
- Bound local-model output before returning it to Codex because tool output
  still consumes Codex context and usage.
- Discover routing from existing configuration rather than duplicating
  tailnet IP addresses or model names in the skill.

## Scope

- Add one global skill and its tested helper to the canonical `agent-skills`
  repository.
- Install the skill for supported local agent environments.

## Non-Goals

- Replacing Codex's underlying model or eliminating all Codex usage.
- Giving local models direct filesystem, shell, messaging, credential, or
  repository-write access.
- Changing Hermes's existing model routing, gateway, Telegram configuration,
  or model-server deployment.
- Using the Raspberry Pi inference endpoint in the initial routing policy.

## Related Docs

- [Agent Skills PR Docs](./README.md)

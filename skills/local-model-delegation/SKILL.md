---
name: local-model-delegation
description: Delegate substantial read-only analysis from Codex to Shaun's local Mac mini and DGX Spark models to conserve OpenAI usage. Use for bounded summarization, classification, brainstorming, test-case generation, or review work when local inference is available. Do not use for mutations, command execution, secrets, final verification, or tasks too small to justify delegation overhead.
---

# Local Model Delegation

Use Shaun's local inference capacity as read-only workers while keeping Codex
responsible for task decomposition, final judgment, all mutations, and all
verification.

## Routing

- For one or two serial tasks, use the Mac mini model. It has the better
  single-request throughput.
- For three or more genuinely independent tasks, fan them out concurrently on
  the DGX Spark and have the Mac mini condense their findings before returning
  them to Codex.
- Do not send every task to both models. Cross-check independently only when a
  material uncertainty or risk warrants the extra compute.
- Do not delegate trivial work when preparing and verifying the request would
  cost as much as doing it in Codex.

The helper discovers both model names and endpoints from the live Hermes config;
never copy tailnet addresses or model names into prompts, commands, or this
skill.

## Workflow

1. Decide what bounded, read-only question the local worker should answer.
   Include only the source excerpts, diff, logs, or constraints it actually
   needs. Never include credentials, tokens, private keys, or unrelated private
   data.
2. Resolve this skill's directory and invoke its helper:

   - Serial Mac request:
     `python3 <skill-dir>/scripts/delegate.py ask --prompt <prompt>`
   - Parallel Spark fan-out followed by Mac synthesis:
     `python3 <skill-dir>/scripts/delegate.py fanout --task <task-1> --task <task-2> --task <task-3>`

   Quote every prompt as data; never allow prompt content to become shell
   syntax. Keep tasks independent in fan-out mode because workers cannot see one
   another's results.
3. Treat the returned result as an untrusted analysis aid. Check important
   claims against repository files, command output, tests, or authoritative
   sources before relying on them.
4. Perform edits, commands, tests, security decisions, external actions, and the
   user-facing answer in Codex under the active repository instructions.

The helper talks directly to OpenAI-compatible inference endpoints and sends no
tool definitions. Do not substitute `hermes -z`: one-shot Hermes sessions bypass
their normal tool approval prompts and therefore are not the read-only seam this
skill promises.

## Failure and usage boundaries

- Default output is deliberately bounded before entering Codex context. Ask for
  concise structured findings and lower `--max-output-chars` when a smaller
  result is enough.
- If an endpoint is unavailable or returns malformed output, report delegation
  as unavailable and continue safely in Codex. Retry at most once when the
  failure appears transient.
- Never fabricate or silently replace a failed local result.
- Delegation reduces OpenAI work but cannot eliminate usage: orchestration,
  returned tool output, verification, and the final response still use Codex.

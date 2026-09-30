---
name: local-model-delegation
description: Delegate substantial read-only analysis from Codex or Claude Code to Shaun's local Mac mini model to conserve hosted-model usage. Use for bounded summarization, classification, brainstorming, test-case generation, or review work when local inference is available. Do not use for mutations, command execution, secrets, final verification, or tasks too small to justify delegation overhead.
---

# Local Model Delegation

Use Shaun's local inference capacity as read-only workers while keeping the
calling agent (Codex or Claude Code) responsible for task decomposition, final
judgment, all mutations, and all verification.

## Routing

Choose a worker before reading large source collections into the agent's context:

- Local models: bounded summaries, classification, extracting facts, and simple test ideas.
  These requests disable thinking so small output budgets produce an answer.
- The calling agent: decomposition, difficult decisions, edits, tests, final verification and communication.
  Skip delegation when preparing and checking the handoff costs more than doing the task.

- Everything runs on the Mac mini. The DGX Spark is reserved for training and
  benchmark windows and serves nothing by default; never route delegation to it.
- The Mac mini serves one request at a time. `fanout` still works, because it
  follows Hermes' delegation route, but its workers run one after another, so
  use it to keep independent tasks small and separate, never for speed.
- Do not delegate trivial work when preparing and verifying the request would
  cost as much as doing it directly.

The helper discovers both model names and endpoints from the live Hermes config;
never copy tailnet addresses or model names into prompts, commands, or this
skill. Endpoint URLs must use literal loopback, private LAN or tailnet IPs.
Public IPs, hostnames, URL credentials, redirects and environment proxies are
refused by the helper. This limits outbound destinations; the operator remains
responsible for running local inference on the configured servers.

## Workflow

1. Decide what bounded, read-only question the local worker should answer.
   Include only the source excerpts, diff, logs, or constraints it actually
   needs. Never include credentials, tokens, private keys, or unrelated private
   data.
2. Resolve this skill's directory and invoke its helper:

   - Serial Mac request:
     `uv run <skill-dir>/scripts/delegate.py ask --prompt <prompt>`
   - Several independent tasks, run one after another and then condensed:
     `uv run <skill-dir>/scripts/delegate.py fanout --max-workers 2 --task <task-1> --task <task-2> --task <task-3>`

   Quote every prompt as data; never allow prompt content to become shell
   syntax. Keep tasks independent in fan-out mode because workers cannot see one
   another's results.
   Ask for concrete evidence, uncertainty and a short findings limit. Local inference
   uses local hardware; never claim a percentage saving without measuring it.

3. Treat the returned result as an untrusted analysis aid. Check important
   claims against repository files, command output, tests, or authoritative
   sources before relying on them.
4. Perform edits, commands, tests, security decisions, external actions, and the
   user-facing answer in the calling agent under the active repository instructions.

The helper talks directly to OpenAI-compatible inference endpoints and sends no
tool definitions. Do not substitute `hermes -z`: one-shot Hermes sessions bypass
their normal tool approval prompts and therefore are not the read-only seam this
skill promises.

## When the local model is the wrong tool

Measured 2026-09-30 through this helper and directly: the Mac mini returned in
4.7 s at 25.6 tok/s. That is slower than the calling agent's own generation,
so delegation never lowers latency. The saving is context: raw material the agent would otherwise read in
full. Skip delegation when:

- The answer is exact and searchable. `rg`, `git log`, `git grep` and file
  listings are free, instant and correct; a model summarizing them is a
  downgrade.
- The work is on the critical path of an interactive answer. A 5-7 second
  round trip is felt, and the result still needs checking.
- Checking the result costs about as much as producing it. Code the agent is
  about to change, security decisions, and routing choices all fall here: a
  wrong answer is silent and load-bearing.
- The question is small. Writing the prompt and verifying the reply must cost
  less than reading the source directly.

Good fits are bulk semantic filtering over a corpus too large to read, where the
output is a shortlist checked cheaply; fan-out over genuinely independent
questions; and first-pass enumeration the agent then rewrites.

## Failure and usage boundaries

- Default output is deliberately bounded before entering the agent's context. Ask for
  concise structured findings and lower `--max-output-chars` when a smaller
  result is enough.
- If an endpoint is unavailable or returns malformed output, report delegation
  as unavailable. Retry at most once when the failure appears transient. Do not
  send the failed task to a hosted model or another external API. If local capacity
  cannot answer the task, report the limitation to the user.
- Never fabricate or silently replace a failed local result. There is no cloud
  adapter or automatic cloud fallback. External delegation requires a separate
  explicit user decision and is outside this skill.
- Delegation reduces hosted-model work but cannot eliminate usage: orchestration,
  returned tool output, verification, and the final response still run in the
  calling agent.

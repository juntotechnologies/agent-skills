# PR 18: Local Model Delegation For Claude Code

Status: underway

Branch: `chore/delegation-for-claude-code`

## Goal

Let Claude Code use `local-model-delegation`, which was written as Codex-only,
and state plainly when local delegation is the wrong tool. The helper was already
agent-neutral; only the skill's framing kept Claude Code from triggering it.

## Context

On 2026-09-30 Claude Code invoked the installed helper from its own session:
`delegate.py ask` routed to the Mac mini and returned a usable answer in 2.1 s.
Nothing in `delegate.py` names Codex or OpenAI, and no test depends on the
skill's wording. The obstacle was the description and body, which named Codex
nine times and "OpenAI usage" as the purpose.

The same day, direct measurement gave Mac mini 4.7 s at 25.6 tok/s and Spark
ThinkingCap 6.6 s at 12.8 tok/s. Both are slower than the calling agent, so the
skill's benefit is saved context, never lower latency. The skill did not say so,
which invites delegating work where it costs more than it saves.

This replaces a proposed routing classifier. The Laya evaluation in hermes-config
(PR 24, closed) found it predicted `requires_llm: false` for every case, scoring
the same as a constant answer.

## Implementation Checklist

- [x] Name Codex and Claude Code as callers; say "hosted-model usage" instead of
  "OpenAI usage"; refer to "the calling agent" where the text meant the
  orchestrator.
- [x] Add "When the local model is the wrong tool" with the measured latency and
  the four cases to skip: exact searchable answers, interactive critical path,
  verification costing as much as the task, and small questions.
- [x] `tests/test_local_model_delegation.py` (18) and `tests/test_install.py`
  pass; wording changes only, helper untouched.

## Smoke Tests

- [ ] In a Claude Code session, ask for a bounded summary of a large file set →
  the skill is offered and the helper returns a result.
- [ ] Ask a question answerable with `rg` → the agent searches directly instead of
  delegating.

## Product Decisions

- Widen the existing skill rather than add a Claude-specific one. One helper,
  one set of endpoint safeguards, one place to change routing.
- Publish the measured latency in the skill. A delegation rule without numbers
  gets applied by reflex; the numbers are what make "skip it" obvious.

## Scope

- `skills/local-model-delegation/SKILL.md` wording and one new section.

## Non-Goals

- No helper, routing, or endpoint change.
- No fix for Spark Flash-Next dropping a connection during measurement; that is
  a Spark service matter, not a skill one.

## Related Docs

- [PR 17 drop Claude compatibility](./archive/17-drop-claude-compat.md)

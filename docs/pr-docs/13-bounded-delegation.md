# PR 13: Reliable bounded delegation

Status: in-scope work complete

Branch: `bugfix/bounded-delegation`

## Goal
Save Codex usage by making local read-only inference return usable answers and providing a bounded Claude Code review path using existing CLI authentication. Approved 2026-09-06.

## Implementation Checklist
- [x] Regress local requests spending their answer budget on thinking; disable thinking for these bounded analysis requests.
- [x] Add a tested Claude CLI adapter with no tools/customizations, timeout, output cap, and explicit failure reporting.
- [x] Document task routing and minimal context handoffs in the existing delegation skill.
- [x] Verify live local and Claude responses; run full relevant tests and install skill links.

## Smoke Tests
- [ ] Delegated review returns concise findings while Codex keeps decisions and verification.

## Product Decisions
Use local models for simple summaries/classification; Claude for substantial bounded reviews; Codex for final judgment, mutations and verification. Do not duplicate full conversation histories or use Hermes tool-enabled one-shot sessions for read-only tasks.

## Scope
Extend existing delegation helper; no persistent autonomous agent service.

Validation: 15 Python tests and both installer shell suites pass. Live local review and two Claude reviews succeeded. Installer confirms the active delegation skill is linked to this source. Default local fan-out reduced to two workers for the approved context-first allocation.

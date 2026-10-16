# PR planned: Agent-owned verification before human review

Status: underway

Branch: `chore/agent-verification-workflow`

## Goal

Keep PRs focused and make agents complete task walkthroughs and independent review before requesting human approval.

## Context

Approved by Shaun, 2026-10-16, after a review-pattern audit. Existing templates assign smoke tests to Shaun and discard completed walk definitions.

## Implementation Checklist

- [ ] Test and replace conflicting scope, smoke-test ownership, and completion rules in the repository and bootstrap instructions.
- [ ] Update both PR templates with acceptance coverage, retained walkthroughs, evidence, independent review, and correction capture.
- [ ] Run all local tests, install the global skill updates, and verify the installed copies.

## Acceptance Coverage

| Requirement | Surface | Verification |
|---|---|---|
| Focused scope | Repository and bootstrap instructions | Policy tests and independent review |
| Agent-owned walkthroughs | Both PR templates and instructions | Policy tests and template inspection |
| Complete review evidence | Both PR templates | Independent review |
| Global availability | Installed setup skill | Installer tests and installed-copy comparison |

## Smoke Tests

No application UI changes. Automated policy and installer tests cover the changed files. No browser walk applies.

## Agent Review

Result: pending

## Apply to Production

Migrations, backfills, configuration, storage, and deployment: none. Installation updates user-owned global skill copies only.

## Product Decisions

- Retain human merge approval and separate production approvals.
- Keep project guidance in its owning repository. Template installation does not overwrite existing projects.
- Keep completed walk steps and acceptance criteria for repeat verification.

## Non-Goals

- Automatic merging, a new review service, or changes to other project checkouts.

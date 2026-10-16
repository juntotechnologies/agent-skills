# PR 29: Agent-owned verification before human review

Status: in-scope work complete

Branch: `chore/agent-verification-workflow`

## Goal

Keep PRs focused and make agents complete task walkthroughs and independent review before requesting human approval.

## Context

Approved by Shaun, 2026-10-16, after a review-pattern audit. Existing templates assign smoke tests to Shaun and discard completed walk definitions.

## Implementation Checklist

- [x] Test and replace conflicting scope, smoke-test ownership, and completion rules in the repository and bootstrap instructions.
- [x] Update both PR templates with acceptance coverage, retained walkthroughs, evidence, independent review, and correction capture.
- [x] Run all local tests, install the global skill updates, and verify the installed copies.

- [x] Restore repository and bootstrap PR checklists, retain their safeguards, and test the new workflow requirements.

## Acceptance Coverage

| Requirement | Entry points | Roles and data | Persistence | Verification |
|---|---|---|---|---|
| Focused scope | Repository and bootstrap instructions | Agents and reviewers | PR scope records | Policy tests and independent review |
| Agent-owned walkthroughs | Both PR templates and instructions | Agents; UI and non-UI work | Retained walk definitions | Policy tests and template inspection |
| Complete review evidence | Both PR templates | Fresh review agent | Review record | Independent review |
| Global availability | Installed setup skill | Existing managed copies | Global skill installation | Installer tests and installed-copy comparison |

## Smoke Tests

Not applicable: instructions and templates only; policy tests, installer tests, and independent review cover this change.

## Agent Review

```json
{"reviewer": "review_global_workflow", "status": "passed", "openFindings": 0, "evidence": "Read-only review of approved requirements, full working diff, tests, and verification scope. Initial findings have regression tests and pass rereview in this session."}
```

## Verification

- Full `unittest` discovery passes. The installer wrapper tests pass.
- `scripts/install.sh` synchronizes the setup skill successfully.
- Direct file comparisons confirm installed instructions and the PR template match their sources.
- A fresh review finds no remaining blockers after the regression fix.
- Rereview confirms both restored GitHub checklists retain code quality, rollback, credential, production, and merge safeguards.

## Review Corrections

| Source | Classification | Prevention | Verification |
| Shaun review | Defect: template simplification removes review and safety checks | Preserve checklist safeguards during format changes | Template regression checks |
|---|---|---|---|
| Independent review | Defect: mocked tests can exclude required browser walks | Explicit browser-persistence rule | Policy test fails before the fix and passes after it |

## Apply to Production

Migrations, backfills, configuration, storage, and deployment: none. Installation updates user-owned global skill copies only.

## Product Decisions

- Retain human merge approval and separate production approvals.
- Keep project guidance in its owning repository. Template installation does not overwrite existing projects.
- Keep completed walk steps and acceptance criteria for repeat verification.

## Non-Goals

- Automatic merging, a new review service, or changes to other project checkouts.

# PR Checklist

Use this before merging any PR.

## Scope

- [ ] The PR has one clear purpose.
- [ ] Follow-up work is moved to issues or `docs/pr-docs`, not hidden in review comments.
- [ ] The PR description is a pointer to the PR doc: a short summary plus head-branch links, not a copy of the checklist or smoke tests.
- [ ] Related issues are linked, closed, or explicitly marked as follow-up.

## Code Quality

- [ ] Changed behavior has focused unit or integration tests.
- [ ] Concerns are reasonably separated.
- [ ] Shared truth is reused instead of duplicating policy, labels, or validation.
- [ ] No dead code, debug code, stale copy, or commented-out leftovers.
- [ ] Each function has one job, is short and flat, and no function is defined inside another.
- [ ] Every value has one named home; SQL lives in `.sql` files behind the module that owns the table.
- [ ] Data crosses module boundaries as typed objects validated once at the edge.
- [ ] Failures log a stable event name with correlating IDs, and never secrets or payloads.
- [ ] The whole diff was reread as a reviewer would, including every function it touches.

## Required Checks

<!-- When setting up a project, replace this line with its real local checks (tests, lint, typecheck, build, code-shape). -->
- [ ] The project's full local checks pass on this commit.
- [ ] CI is green, when the change touches CI or the merge needs it.

## Conditional Checks

- [ ] If production configuration, deployment or data changes: each command was named and confirmed before it ran, and the rollback is written down.
- [ ] If secrets or private paths changed: no live credentials are committed.

## Merge Readiness

- [ ] PR branch is up to date enough for a clean merge.
- [ ] Risky or irreversible changes have a rollback note.
- [ ] Machine-specific or destructive changes are called out clearly.

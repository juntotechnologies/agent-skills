# PR Checklist

Use this before merging any PR.

## Scope

- [ ] The PR has one clear purpose.
- [ ] Follow-up work is moved to issues or `docs/pr-docs`, not hidden in review comments.
- [ ] The PR description has a one-line summary plus bullets for meaningful changes.
- [ ] Related issues are linked, closed, or explicitly marked as follow-up.

## Code Quality

- [ ] Changed behavior has focused unit or integration tests.
- [ ] Concerns are reasonably separated.
- [ ] Shared truth is reused instead of duplicating policy, labels, or validation.
- [ ] Client input is validated before it reaches business logic.
- [ ] Auth, permissions, and commercial-data rules are enforced server-side, not only hidden in the UI.
- [ ] No dead code, debug code, stale copy, or commented-out leftovers.

## Required Checks

- [ ] `npm run check`
- [ ] `npm test`
- [ ] GitHub CI is green.

## Conditional Checks

- [ ] If schema changed: Drizzle migration, snapshot, and rollout notes are included.
- [ ] If schema changed: `npm run db:status:dev` confirms the expected dev ledger/schema state after migration.
- [ ] If env vars changed: `.env.example` and setup docs are updated.
- [ ] If roles changed: admin, manager, and chemist behavior is tested.
- [ ] If API behavior changed: direct API misuse is rejected server-side.

## App Smoke Tests

- [ ] Login works.
- [ ] Inventory page loads.
- [ ] Create/edit/view/delete behavior works for the changed entity.
- [ ] Transactions page loads if the PR touches inventory, transactions, chemicals, suppliers, purchasers, contacts, or permissions.
- [ ] Audit Log behavior is checked if the PR touches history, users, roles, or permissions.
- [ ] Role visibility is checked for admin, manager, and chemist when relevant.
- [ ] The changed flow is tested once through the UI, not only through unit tests.

## Merge Readiness

- [ ] PR branch is up to date enough for a clean merge.
- [ ] Risky or irreversible changes have a rollback note.
- [ ] Production-impacting migrations or env changes are called out clearly.

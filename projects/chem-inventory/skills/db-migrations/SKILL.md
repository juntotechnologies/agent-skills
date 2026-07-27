---
name: db-migrations
description: Follow chem-inventory's Drizzle/Supabase schema-change workflow whenever a change touches shared/schema.ts, changes database schema, or diagnoses dev/prod schema drift.
---

# Database migrations

Use these canonical project references:

- `docs/schema-change-checklist.md` for the end-to-end workflow.
- `docs/database-migrations.md` for exact commands.
- `docs/database-debugging.md` for ledger/schema drift.

If this skill conflicts with those project docs, the project docs win and this
skill should be updated.

## Commands

| Action | Dev | Prod |
| --- | --- | --- |
| Generate | `npm run db:generate:dev` | Generate once for both environments |
| Apply | `npm run db:migrate:dev` | `npm run db:migrate:prod` |
| Status | `npm run db:status:dev` | `npm run db:status:prod` |
| Batch-doc backfill | `npm run db:backfill-batch-documents:dev` | `npm run db:backfill-batch-documents:prod` |
| Version backfill | `npm run db:backfill-batch-document-versions:dev` | `npm run db:backfill-batch-document-versions:prod` |

Add `-- --apply` to a backfill command only when intentionally writing.
Never use bare `db:migrate`, `db:push`, or `db:push:prod` for tracked changes.

## Workflow

1. Update `shared/schema.ts`; do not handwrite DDL that Drizzle can generate.
2. Add or update focused failing tests before generating the migration.
3. Run `npm run db:generate:dev`.
4. Review generated SQL for unrelated changes, data loss, missing backfills,
   and unsafe new constraints.
5. Never edit a migration after it has been applied; generate another one.
6. Run `npm run db:migrate:dev`, focused tests, and the manual smoke tests in
   the PR doc.
7. Commit schema, code, tests, SQL, and migration metadata together.

If ledger and schema disagree, start with `npm run db:status:dev` or
`npm run db:status:prod` and follow `docs/database-debugging.md`; do not force
or improvise a repair.

## Production safety

Supabase database backups are expected daily but do not include Storage
objects. Before any production migration, Shaun must manually confirm a backup
from the last 24 hours still exists in Dashboard → Settings → Database →
Backups.

After that check, ask for a separate, explicit confirmation naming each exact
production-mutating command. Backup confirmation or general runbook approval
does not authorize `npm run db:migrate:prod` or any backfill with `--apply`.

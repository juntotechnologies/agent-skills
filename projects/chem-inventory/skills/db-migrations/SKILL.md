---
name: db-migrations
description: Follow this repo's opinionated Drizzle/Supabase schema-change workflow whenever a code change needs a database schema change — new/changed tables or columns, or diagnosing dev/prod schema drift. Use proactively whenever a task touches shared/schema.ts, not just when explicitly asked to "run a migration". Covers generating, reviewing, and applying migrations, plus the debugging commands for ledger/schema mismatches.
---

## Overview

This repo tracks schema through Drizzle migrations, not `db:push`. The full
canonical detail lives in three docs — this skill is the decision procedure
that ties them together so a schema change doesn't skip a step. Paths below
are relative to the **chem-inventory repository root**, not to this file —
this skill is symlinked into chem-inventory from multiple physical
locations (installed copy vs. the canonical copy in `agent-skills`), so a
filesystem-relative link would resolve differently depending on which one
you're reading it from:

- `docs/schema-change-checklist.md` — the end-to-end checklist (code → migration → dev → merge → prod).
- `docs/database-migrations.md` — exact `db:generate`/`db:migrate`/`db:status` commands.
- `docs/database-debugging.md` — manual checks when the ledger and schema disagree.

If any instruction here seems to conflict with those docs, the docs win —
update this skill to match rather than trusting a stale copy here.

## Command Reference (copy exactly — do not improvise variants)

Every dev/prod action is a fully self-wrapped `npm run <name>:dev` /
`npm run <name>:prod` pair — the env file is baked into the script itself, so
there is never an external `dotenv-cli` wrapper to remember or forget:

| Action | Dev | Prod |
| --- | --- | --- |
| Generate migration | `npm run db:generate:dev` | (generate once, applies to both — see Step 2) |
| Apply migration | `npm run db:migrate:dev` | `npm run db:migrate:prod` |
| Status/ledger check | `npm run db:status:dev` | `npm run db:status:prod` |
| Batch-docs backfill | `npm run db:backfill-batch-documents:dev` (add `-- --apply` to write) | `npm run db:backfill-batch-documents:prod` (add `-- --apply` to write) |
| Batch-doc-versions backfill | `npm run db:backfill-batch-document-versions:dev` (add `-- --apply` to write) | `npm run db:backfill-batch-document-versions:prod` (add `-- --apply` to write) |

The bare `db:migrate` script (no suffix) still exists but has no env baked
in — don't use it directly; it's a build block for `db:migrate:dev`/`:prod`,
not something to run on its own.

**Never** use `db:push` or `db:push:prod` for a tracked schema change — this
project uses `db:generate` + `db:migrate`, not push-based sync. `db:push` is
a Drizzle command that skips the migration-file/ledger mechanism this repo
relies on for prod parity and rollback history.

### One-off data backfills (`scripts/backfill/*.ts`)

Not every backfill has an `npm run` wrapper — most live directly under
`scripts/backfill/` (e.g. `backfill-contact-people.ts`,
`backfill-order-movement-batch-numbers.ts`) and are run with the repo's
standard env wrapper:

```bash
npx dotenv-cli -e .env.development -- tsx scripts/backfill/<name>.ts             # dry run
npx dotenv-cli -e .env.development -- tsx scripts/backfill/<name>.ts --apply     # actually write
```

Swap `.env.development` for `.env` to target prod. Every script in this
family follows the same shape: a pure, unit-tested `plan...Backfill(...)`
function with no I/O, plus a thin `main()` CLI wrapper that's dry-run by
default and only writes with `--apply`. Write new backfills the same way —
see `backfill-contact-people.ts` as the reference implementation.

## Step 1 — Change the schema in code

- Edit `shared/schema.ts` only. Never write ad hoc SQL DDL by hand for a
  change Drizzle can generate.
- Update server/client code that depends on the changed fields.
- Add or update focused tests for the changed behavior *before* generating
  the migration (TDD, per this repo's `CLAUDE.md`).

## Step 2 — Generate and review the migration

```bash
npm run db:generate:dev
```

`config/drizzle.config.ts` throws if `DATABASE_URL` is absent, but generation
itself is based on local schema + `migrations/meta/_journal.json` and does not
need to actually connect. `db:generate:dev` wraps `drizzle-kit generate` with
`dotenv -e .env.development --`, same as `db:migrate:dev`/`db:status:dev`, so
it uses the real dev `DATABASE_URL` instead of an inline placeholder.

Review the generated `migrations/*.sql` before doing anything else:

- only the intended schema change is present — no unrelated table gets
  recreated,
- existing data can survive the migration as written,
- a migration that replaces/repurposes a column for existing data includes
  explicit backfill SQL,
- a new constraint (NOT NULL, UNIQUE) has a preflight data check first.

Never edit a migration file after it has been applied anywhere (dev or
prod) — create a new migration instead.

## Step 3 — Apply to dev and test

```bash
npm run db:migrate:dev
```

Then:
- `npm run dev` and confirm the app starts and login works,
- run the focused tests from Step 1 against the real dev DB behavior,
- manually smoke-test the affected flow,
- confirm create/update/delete still persists after a restart,
- confirm validation/uniqueness failures fail loudly, not silently.

If the ledger and schema seem to disagree (e.g. a migration file exists but
its effects aren't showing up, or `db:migrate` skips something you expected
to run), stop and go to **Step 5 (Debugging)** before forcing anything.

## Step 4 — Commit and hand off

Commit code, tests, and the migration files (`migrations/*.sql` +
`migrations/meta/*`) together in one change — never split a migration file
from the schema/code change it belongs to.

This repo's `CLAUDE.md` still governs everything around the migration
itself: discuss before starting schema-touching work, branch/PR per the
normal flow, checklist item gets checked off only once its tests pass. This
skill only covers the DB-specific mechanics inside that flow. Prod
application (backups, prod-specific safety checks, deploy ordering) is a
separate, later step — do not run it as part of finishing a dev-side PR
unless explicitly asked; see `docs/schema-change-checklist.md`'s "Apply To
Prod And Deploy" section when that time comes.

## Step 4.5 — Prod backups (confirmed 2026-07-06)

Supabase takes automatic daily backups for every project on this account —
confirmed via Dashboard → project → **Settings → Database → Backups**, both
tabs:

- **Scheduled backups** (logical, pg_dump-style): one per day, ~7 days
  retained, each restorable in place from that screen.
- **Physical backups**: also daily, restorable the same way.
- This covers both the prod and dev projects.
- **Storage objects (Supabase Storage buckets, e.g. `batch-documents`) are
  NOT included** — these backups are database-only. A restore does not bring
  back deleted/changed files in storage.

This means: do not spend time improvising a manual `pg_dump`/encryption
step before a prod migration — the automatic daily backup already satisfies
`docs/schema-change-checklist.md`'s "create an encrypted prod backup" step
for schema/data changes. If a change also touches Storage objects, that's a
separate concern this backup doesn't cover.

To confirm this is still true before a prod migration (plans/settings can
change): open the same Dashboard path and check a backup exists from within
the last 24 hours before proceeding. No CLI/API access is set up in this
repo to check programmatically (`.env` only has project-level Supabase keys,
not a Management API access token) — this is a manual dashboard check only.

## Step 4.75 — Consolidate a multi-migration PR into one ordered runbook

Once a PR's migrations/backfills span more than one tier, use the
project-agnostic **`apply-to-production-runbook`** skill to consolidate
them into one ordered `## Apply to Production` section in the PR doc
before merge, using this skill's Command Reference and Step 4.5 for the
exact chem-inventory commands and confirmation rules that skill assumes
each project supplies. See
`docs/pr-docs/178-orders-workflow-usability.md`'s "Apply to Production"
section for a worked example.

## Step 5 — Debugging drift (only if something looks wrong)

Use `npm run db:status:dev` / `npm run db:status:prod` first — no `psql`
required. It prints the target host, ledger row count, and known
schema-drift indicators (see `docs/database-debugging.md` for what each
field means and the manual `psql` fallbacks). Common cases:

- ledger is missing recent rows but schema already has the columns: applied
  but untracked — do not just re-run blindly, read the interpretation table
  in `database-debugging.md` first,
- most row counts are 0 after a sync: dev may be partially truncated, fix
  the sync issue rather than assuming migrations will restore data,
- a loose `.sql` file isn't running: it's likely missing from
  `migrations/meta/_journal.json` — Drizzle only runs journaled migrations.

## Rules (do not violate even under pressure to move fast)

- Do not use `db:push` or `db:push:prod` for tracked schema changes.
- Do not apply to prod before it has been tested on dev.
- Do not edit an applied migration file in place.
- Do not treat `user_sessions` as business schema — it's runtime session
  state excluded from Drizzle.
- Never run a prod-mutating command without confirming a recent automatic
  Supabase backup exists first (Step 4.5) and an explicit, command-specific
  go-ahead naming that exact command — this includes `db:migrate:prod`
  itself, not just backfill/rewrite scripts run with `--apply`. A general
  instruction to proceed with the overall runbook/plan does not count;
  confirming the backup is not consent for the next command either. Ask
  before each individual prod-mutating command, even mid-runbook (see the
  checklist doc).

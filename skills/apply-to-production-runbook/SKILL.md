---
name: apply-to-production-runbook
description: Use before merging any PR that has accumulated multiple migrations, backfills, or other production-mutating steps across its lifetime, in any project with a dev/prod (or staging/prod) environment split. Consolidates those scattered steps into one ordered, explicit runbook instead of leaving them spread across a PR doc's history.
---

## Why this exists

A PR doc (or equivalent planning doc) gets written incrementally: each tier
or milestone adds its own migration, backfill script, or deploy step, and
each one typically only notes "applied to dev" in passing. By the time the
PR is ready to merge, the actual production apply order is scattered across
many separate entries, with no single place that says what to run, in what
order, and what depends on what. Reconstructing that order from memory or by
re-reading the whole PR doc at deploy time is exactly the kind of task that
produces an out-of-order or skipped step under time pressure.

Confirmed as a real gap on chem-inventory's PR 178, which accumulated five
migrations plus two backfill scripts across six separate tiers with no
consolidated view until asked for one directly.

## When to use this

Any project with a dev/prod (or staging/prod) split, once its
in-progress PR/planning doc has accumulated **two or more** of: schema
migrations, data backfills, storage/asset cleanup steps, or other
production-mutating operations — whichever the project's own workflow
already gates behind explicit approval before running against prod. Use
proactively; don't wait to be asked once that threshold is crossed.

## What to produce

Add one clearly-named section to the PR/planning doc (e.g.
`## Apply to Production`) — not spread across the doc's other sections —
before the PR is considered ready to merge:

1. **State plainly** that the branch/PR has made no production changes yet
   (if true), so the section reads as a forward-looking runbook, not a
   log of things already done.
2. **Number every step in true dependency order** — a step that depends on
   an earlier step's generated data or on a preceding code deploy must come
   after it, explicitly. Note the dependency inline, don't leave it
   implicit.
3. **Give the exact command for each step**, not a paraphrase — copy it
   from the project's own migration/backfill skill or docs, don't
   re-derive it from memory.
4. **Flag dev-derived numbers explicitly wherever they appear** — row
   counts, reconciliation figures, or "N records affected" figures that
   were only ever verified against dev/staging data must be called out as
   needing a fresh check against real production data before being
   trusted there. Dev/seed data volume and shape rarely match production.
5. **Preserve the project's own confirmation gates.** If the project's
   workflow requires a named, command-specific go-ahead before any
   production-mutating command (most do, or should) — state plainly that
   approving this runbook as a plan is not consent for each individual
   step, and that a prior step's confirmation doesn't carry forward to the
   next one. Restate the project's own pre-flight checks (e.g. a backup
   freshness check) as their own explicit step, not assumed.
6. **End with a concrete post-deploy verification step** — a status/ledger
   check plus a real spot-check in the running production app — not just
   "done" once the last command exits successfully.

## What this skill does not cover

The exact commands, tools, and safety mechanics for a given project's
migrations/backfills (e.g. `db:migrate:prod`, backup verification steps,
storage cleanup scripts) belong in that project's own skill — see
chem-inventory's `db-migrations` skill for a worked example of a
project-specific companion to this one. This skill only covers the shape
and discipline of consolidating those into one runbook; it intentionally
carries no project-specific command names.

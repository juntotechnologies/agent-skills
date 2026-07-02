---
name: Setup Project Repo
description: Bootstrap a project repo with my standard coding practices — copy CLAUDE.md/AGENTS.md, the docs/pr-docs/ planning-doc structure and TOC, and the .github PR description template from this skill's canonical assets. Use when starting a new project, or when I ask to "set up coding practices", "bootstrap this repo", or "add the PR docs structure" (does nothing if already set up). Also handles syncing an already-set-up repo's CLAUDE.md/AGENTS.md to the latest canonical workflow — use when I ask to "sync coding practices", "update CLAUDE.md to the latest", "bring this repo's CLAUDE.md up to speed", or similar.
---

## Overview

This skill lives in the source-of-truth repo, **agent-skills**
(`git@github.com:juntotechnologies/agent-skills`). Its `assets/` directory holds
my standard coding workflow and templates. This skill copies those assets into
the current project repo so every project has the same structure without
recreating it by hand.

Treat this skill's `assets/` directory as the only canonical place to edit
workflow and template content. Target repo copies are installed/adapted outputs,
not source of truth. If I ask to change the coding workflow, `CLAUDE.md`,
`AGENTS.md`, PR-doc templates, or PR checklist template themselves, update
`agent-skills` first rather than editing the target repo copy as canonical.
Existing repos do not update automatically when `agent-skills` changes; run this
skill again when I ask to sync a repo to the latest practices.

The files this skill installs into a target repo:

| Source (in this skill) | Destination (in target repo) |
| --- | --- |
| `assets/CLAUDE.md` | `CLAUDE.md` (repo root) |
| `assets/CLAUDE.md` | `AGENTS.md` (repo root) |
| `assets/docs/pr-docs/README.template.md` | `docs/pr-docs/README.template.md` |
| `assets/docs/pr-docs/README.template.md` | `docs/pr-docs/README.md` (adapted live TOC) |
| `assets/docs/pr-docs/template.md` | `docs/pr-docs/template.md` |
| `assets/docs/pr-docs/archive/` | `docs/pr-docs/archive/` (empty dir) |
| `assets/.github/pull_request_template.md` | `.github/pull_request_template.md` |

## Step 0 — Decide which of three things I'm asking for

1. **Changing the canonical workflow/template itself** — stop working in the
   target repo and update `agent-skills` instead. Examples:
   - "Change my coding workflow"
   - "Update CLAUDE.md instructions"
   - "Update AGENTS.md instructions"
   - "Change the PR doc template"
   - "Change the PR checklist template"
2. **Bootstrapping a repo that isn't set up yet** — go to Step 1 (Idempotency
   check), then Steps 2-5.
3. **Syncing an already-set-up repo's `CLAUDE.md`/`AGENTS.md` to the latest
   canonical version** — e.g. "sync coding practices here", "update this
   repo's CLAUDE.md to the latest", "bring CLAUDE.md up to speed". Skip
   straight to **Step 6 (Sync mode)** below; don't run the bootstrap steps.

## Step 1 — Idempotency check

Before doing anything, check whether the target repo is already set up. Consider
it **already set up** if ALL of these exist in the current repo:

- `CLAUDE.md`
- `AGENTS.md`
- `docs/pr-docs/README.md`
- `docs/pr-docs/README.template.md`
- `docs/pr-docs/template.md`
- `.github/pull_request_template.md`

If all required files exist, **stop and do nothing** except telling me it's already set
up. Do not overwrite, re-copy, or re-fetch. If only *some* exist, report which
are present and ask me before touching anything — a partial state may be
intentional.

## Step 2 — Locate the source

Prefer this skill's local `assets/` directory when available. If you need to
locate the canonical repo directly, check in order:

1. `~/Documents/GitHub/other/agent-skills`
2. Anywhere else via `find ~/Documents/GitHub -maxdepth 4 -type d -name agent-skills 2>/dev/null`

If no local clone is found, fetch the raw files from GitHub (the repo is public):

```
https://raw.githubusercontent.com/juntotechnologies/agent-skills/main/skills/setup-project-repo/assets/CLAUDE.md
https://raw.githubusercontent.com/juntotechnologies/agent-skills/main/skills/setup-project-repo/assets/docs/pr-docs/README.template.md
https://raw.githubusercontent.com/juntotechnologies/agent-skills/main/skills/setup-project-repo/assets/docs/pr-docs/template.md
https://raw.githubusercontent.com/juntotechnologies/agent-skills/main/skills/setup-project-repo/assets/.github/pull_request_template.md
```

## Step 3 — Copy the files into place

Create `docs/pr-docs/` and `docs/pr-docs/archive/` in the target repo, then copy
each source file to its destination per the table above. Create
`docs/pr-docs/README.md` from `docs/pr-docs/README.template.md`, then adapt it
as the live table of contents for the target repo's current PR docs. Follow the
same format used by `chem-inventory/docs/README.md`: a project-specific H1, a
one-sentence purpose, `## Table of Contents`, and a two-column markdown table
with `Doc` and `Description`.

`CLAUDE.md` or `AGENTS.md` at the root already existing but *different* from the
source is the one case to handle carefully: do not clobber it — show me the diff
and ask whether to merge or replace. Both should come from the same
`assets/CLAUDE.md` workflow asset so Claude and Codex receive matching
instructions.

## Step 4 — Adapt project-specific placeholders

`CLAUDE.md`, `AGENTS.md`, and `.github/pull_request_template.md` carry checks
and smoke tests from a specific prior project (e.g. `npm run check`, `npm test`, Drizzle
migrations, inventory/transactions pages). These are placeholders, not literal
requirements. After copying:

- Replace the "Required Checks" commands with the target project's real
  build/test commands (inspect `package.json`, `Makefile`, `pyproject.toml`,
  etc. to infer them).
- Replace the app-specific smoke tests with ones that match this project, or
  leave clearly-marked TODOs for me to fill in.
- Confirm `CLAUDE.md` explicitly says agents must never merge to `main`; only
  Shaun may merge PRs to `main`.
- Confirm `AGENTS.md` matches `CLAUDE.md` so Codex receives the same workflow
  instructions as Claude.
- Update `docs/pr-docs/README.md` whenever PR docs are added, completed, moved,
  or archived. Keep it as a concise TOC of active/planned PR docs, and include
  archived docs only if the project already uses that convention.
- If you can't confidently infer a command, flag it for me rather than guessing.

Do not back-propagate these project-specific adaptations into `agent-skills`
unless I explicitly ask to change the canonical template.

## Step 5 — Report

Summarize what was copied and what placeholders still need my input. Do not
commit or push unless I ask.

## Step 6 — Sync mode (existing repo, already set up)

Unlike `docs/pr-docs/template.md` and `.github/pull_request_template.md`
(which get deliberately adapted per-project — see Step 4 — and must never be
silently overwritten), `CLAUDE.md`/`AGENTS.md` are meant to stay byte-identical
to the canonical `assets/CLAUDE.md`. This mode only ever touches those two
files.

1. Locate the canonical source exactly as in Step 2 (prefer local
   `~/Documents/GitHub/other/agent-skills` clone; otherwise fetch the asset
   path from GitHub raw content — never the symlink path, see Step 2's note).
2. Diff the target repo's `CLAUDE.md` (and `AGENTS.md`, if present) against
   `assets/CLAUDE.md`. If both already match, say so and stop — nothing to do.
3. If they differ, show me the diff before touching anything.
4. On confirmation, overwrite `CLAUDE.md` with the canonical version, and
   overwrite (or create, if missing) `AGENTS.md` to match it too, so Claude and
   Codex stay in sync with each other.
5. Do not touch `docs/pr-docs/*` or `.github/pull_request_template.md` in this
   mode — those are out of scope for a sync and require the full Step 4
   adaptation judgment call, not a blind overwrite.
6. Report what changed. Do not commit or push unless I ask.

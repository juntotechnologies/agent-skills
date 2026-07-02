---
name: Setup Project Repo
description: Bootstrap a project repo with my standard coding practices — copy CLAUDE.md, the docs/pr-docs/ planning-doc structure and TOC, and the .github PR description template from this skill's canonical assets. Use when starting a new project, or when I ask to "set up coding practices", "bootstrap this repo", or "add the PR docs structure". Do nothing if the repo is already set up.
---

## Overview

This skill lives in the source-of-truth repo, **agent-skills**
(`git@github.com:juntotechnologies/agent-skills`). Its `assets/` directory holds
my standard coding workflow and templates. This skill copies those assets into
the current project repo so every project has the same structure without
recreating it by hand.

Treat this skill's `assets/` directory as the only canonical place to edit
workflow and template content. Target repo copies are installed/adapted outputs,
not source of truth. If I ask to change the coding workflow, `CLAUDE.md`, PR-doc
templates, or PR checklist template themselves, update `agent-skills` first
rather than editing the target repo copy as canonical. Existing repos do not
update automatically when `agent-skills` changes; run this skill again when I
ask to sync a repo to the latest practices.

The files this skill installs into a target repo:

| Source (in this skill) | Destination (in target repo) |
| --- | --- |
| `assets/CLAUDE.md` | `CLAUDE.md` (repo root) |
| `assets/docs/pr-docs/README.template.md` | `docs/pr-docs/README.template.md` |
| `assets/docs/pr-docs/README.template.md` | `docs/pr-docs/README.md` (adapted live TOC) |
| `assets/docs/pr-docs/template.md` | `docs/pr-docs/template.md` |
| `assets/docs/pr-docs/archive/` | `docs/pr-docs/archive/` (empty dir) |
| `assets/.github/pull_request_template.md` | `.github/pull_request_template.md` |

## Step 0 — Decide whether this is a template change or a repo sync

If I ask to change the workflow/template content itself, stop working in the
target repo and update `agent-skills` instead. Examples:

- "Change my coding workflow"
- "Update CLAUDE.md instructions"
- "Change the PR doc template"
- "Change the PR checklist template"

If I ask to set up, bootstrap, refresh, or sync a specific project repo, continue
with the steps below and copy/adapt the current templates from this skill's
`assets/` directory into that repo.

## Step 1 — Idempotency check

Before doing anything, check whether the target repo is already set up. Consider
it **already set up** if ALL of these exist in the current repo:

- `CLAUDE.md`
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

`CLAUDE.md` at the root already existing but *different* from the source is the
one case to handle carefully: do not clobber it — show me the diff and ask
whether to merge or replace.

## Step 4 — Adapt project-specific placeholders

`CLAUDE.md` and `.github/pull_request_template.md` carry checks and smoke tests
from a specific prior project (e.g. `npm run check`, `npm test`, Drizzle
migrations, inventory/transactions pages). These are placeholders, not literal
requirements. After copying:

- Replace the "Required Checks" commands with the target project's real
  build/test commands (inspect `package.json`, `Makefile`, `pyproject.toml`,
  etc. to infer them).
- Replace the app-specific smoke tests with ones that match this project, or
  leave clearly-marked TODOs for me to fill in.
- Confirm `CLAUDE.md` explicitly says agents must never merge to `main`; only
  Shaun may merge PRs to `main`.
- Update `docs/pr-docs/README.md` whenever PR docs are added, completed, moved,
  or archived. Keep it as a concise TOC of active/planned PR docs, and include
  archived docs only if the project already uses that convention.
- If you can't confidently infer a command, flag it for me rather than guessing.

Do not back-propagate these project-specific adaptations into `agent-skills`
unless I explicitly ask to change the canonical template.

## Step 5 — Report

Summarize what was copied and what placeholders still need my input. Do not
commit or push unless I ask.

---
name: PR Doc Open
description: Turn an approved, planned PR doc (docs/pr-docs/planned-<slug>.md) into a real branch + open GitHub PR, with the doc renamed to include the PR number and the TOC updated. Use when I say a PR doc is "ready", "let's do the PR route", "make the branch and open the PR", or similar, after we've already agreed on a planned PR doc's scope.
---

## Overview

This is the mechanical second half of the PR workflow described in
`AGENTS.md`: once a `docs/pr-docs/planned-<slug>.md` doc's scope is agreed,
turn it into a real branch and PR without re-litigating scope. Assumes the
planned doc already exists — if it doesn't, that's a planning conversation
first (see `AGENTS.md` sections 1-2), not this skill.

## Steps

1. **Check for a clean starting point.** Run `git status --short`. If there
   are unrelated uncommitted changes, stop and ask before branching — don't
   silently carry someone else's in-progress work into the new branch.
2. **Create the branch** off the current branch (per `AGENTS.md`'s naming
   convention: `<type>/<pithy-theme-with-dashes>`, matching whatever the
   planned doc's `Branch:` field already says, if it has one).
3. **Commit the planned PR doc** (and anything else already staged for this
   PR) with a message describing what it scopes.
4. **Push and open the PR** via `gh pr create`, with `--title` from the doc's
   title and a **pointer body** (per `AGENTS.md`'s Track Progress section): a
   short Summary drawn from the doc's Goal, then links into the doc's sections
   on the PR's head branch. Never leave the body as the bare unfilled template,
   and never copy the checklist or smoke tests into it — that duplicate is
   exactly what drifts. Link shape:

   ```
   https://github.com/<org>/<repo>/blob/<head-branch>/docs/pr-docs/<doc>.md#<anchor>
   ```

   A head-branch blob URL keeps anchors working and tracks later pushes, which
   a repo-relative path in a PR body does not — those resolve against the
   default branch.
5. **Rename the doc** from `docs/pr-docs/planned-<slug>.md` to
   `docs/pr-docs/<PR#>-<slug>.md` now that the PR number is known, update its
   `# PR planned: ...` heading to `# PR <PR#>: ...`, and set `Status:
   underway`.
6. **Update `docs/pr-docs/README.md`'s TOC** so the entry's link and label
   point at the renamed file.
7. **Re-point the PR body** (`gh pr edit`) at the renamed
   `<PR#>-<slug>.md` — the links written in step 4 still point at
   `planned-<slug>.md`, which no longer exists on the branch.
8. Commit and push the rename/TOC update as a small follow-up commit on the
   same branch.
9. Report the PR URL. Do not merge — only Shaun merges to `main` (per
   `AGENTS.md`).

This skill only covers the PR's opening moment. Because the body is a pointer
rather than a copy, there is no later re-sync burden: a doc edit becomes visible
to reviewers as soon as it is pushed, since the body links to the doc on the
head branch. The one case that still needs `gh pr edit` is a change to the doc's
*filename or section headings*, which breaks the links themselves.

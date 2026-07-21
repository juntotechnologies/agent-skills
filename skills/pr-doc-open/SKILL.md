---
name: PR Doc Open
description: Turn an approved, planned PR doc (docs/pr-docs/planned-<slug>.md) into a real branch + open GitHub PR, with the doc renamed to include the PR number and the TOC updated. Use when I say a PR doc is "ready", "let's do the PR route", "make the branch and open the PR", or similar, after we've already agreed on a planned PR doc's scope.
---

## Overview

This is the mechanical second half of the PR workflow described in
`CLAUDE.md`: once a `docs/pr-docs/planned-<slug>.md` doc's scope is agreed,
turn it into a real branch and PR without re-litigating scope. Assumes the
planned doc already exists — if it doesn't, that's a planning conversation
first (see `CLAUDE.md` sections 1-2), not this skill.

## Steps

1. **Check for a clean starting point.** Run `git status --short`. If there
   are unrelated uncommitted changes, stop and ask before branching — don't
   silently carry someone else's in-progress work into the new branch.
2. **Create the branch** off the current branch (per `CLAUDE.md`'s naming
   convention: `<type>/<pithy-theme-with-dashes>`, matching whatever the
   planned doc's `Branch:` field already says, if it has one).
3. **Commit the planned PR doc** (and anything else already staged for this
   PR) with a message describing what it scopes.
4. **Push and open the PR** via `gh pr create`, with `--title` and `--body`
   filled in from the PR doc's Goal/Summary — never leave the PR body as the
   bare unfilled template.
5. **Rename the doc** from `docs/pr-docs/planned-<slug>.md` to
   `docs/pr-docs/<PR#>-<slug>.md` now that the PR number is known, update its
   `# PR planned: ...` heading to `# PR <PR#>: ...`, and set `Status:
   underway`.
6. **Update `docs/pr-docs/README.md`'s TOC** so the entry's link and label
   point at the renamed file.
7. **Update the PR body** (`gh pr edit`) if the doc link in the body still
   points at the old `planned-<slug>.md` filename.
8. Commit and push the rename/TOC update as a small follow-up commit on the
   same branch.
9. Report the PR URL. Do not merge — only Shaun merges to `main` (per
   `CLAUDE.md`).

This skill only covers the PR's opening moment. Per `CLAUDE.md`'s Track
Progress section, the PR description and its PR doc must stay in sync for
the PR's *entire* lifetime after this — every later session that meaningfully
changes the doc (a new tier, a revised design, a struck-through known issue,
a status update) re-syncs the PR description (`gh pr edit`) in that same
pass, not just once here at creation.

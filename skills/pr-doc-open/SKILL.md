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
4. **Push and open the PR** via `gh pr create`, with a title describing its
   final scope and a body in two parts: a short ASD-STE100 description of what
   the PR does (the doc's Goal), then a flat copy of the doc's Implementation
   Checklist and Smoke Tests. Put no links in the body. Keep unrun work
   unchecked. Write multiline bodies to a file and pass `--body-file`.
5. **Rename the doc** from `docs/pr-docs/planned-<slug>.md` to
   `docs/pr-docs/<PR#>-<slug>.md` now that the PR number is known, update its
   `# PR planned: ...` heading to `# PR <PR#>: ...`, and set `Status:
   underway`.
6. **Update `docs/pr-docs/README.md`'s TOC** so the entry's link and label
   point at the renamed file.
7. **Regenerate and publish the PR body** (`gh pr edit --body-file ...`)
   from the renamed doc. Verify the remote body matches the derived local body.
8. Commit and push the rename/TOC update as a small follow-up commit on the
   same branch.
9. Report the PR URL. Do not merge — only Shaun merges to `main` (per
   `AGENTS.md`).

## Keep the description current

Whenever scope, tier progress, verification, or smoke-test status changes, update
its source in the PR doc first, derive the description again, publish it, and
read it back to verify. The body has no links. Preserve one current PR doc; move
deferred work to a separate planned doc instead of scattering the active record
across several documents. Do not maintain a second checklist by hand in the PR
body: derive it from the doc.

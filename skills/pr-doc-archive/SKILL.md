---
name: PR Doc Archive
description: Archive a merged PR's doc — mark it Status done, move it into docs/pr-docs/archive/, and update the docs/pr-docs/README.md table of contents (adding an Archive section if one doesn't exist yet). Use proactively right after confirming a PR has merged, or when I ask to "archive PR docs", "clean up docs/pr-docs", or similar.
---

## Overview

Once a PR merges, its `docs/pr-docs/<PR#>-<slug>.md` doc is done serving as
an active plan and should move out of the way so the TOC stays a clean view
of what's actually in flight — matching `CLAUDE.md` section 5's instruction
to do this proactively, without being asked.

## Steps

1. **Confirm the PR actually merged** — `gh pr view <PR#> --json
   state,mergedAt`, or check `git log` on `main` if no PR number is given.
   Don't archive a doc for a PR that's only open/in-review.
2. **Clean up the local branch**: `git checkout main`, `git fetch origin
   --prune` (drops the remote-tracking ref for the branch GitHub already
   deleted on merge), `git pull --ff-only`, then `git branch -d
   <merged-branch>`. Skip anything already done.
3. **Update the doc itself**: set `Status: done` (add a short qualifier if
   scope was cut/moved, per the doc's own template).
4. **Move it**: `git mv docs/pr-docs/<PR#>-<slug>.md
   docs/pr-docs/archive/<PR#>-<slug>.md`.
5. **Update `docs/pr-docs/README.md`**: remove the entry from the active
   table, and add it under an `### Archive` section (create that section,
   with its own `| Doc | Description |` table, if this is the first archived
   doc in this repo). Point the link at the new `./archive/...` path.
6. **Fix relative links broken by the move**: the archived doc's own
   relative links (e.g. `./planned-x.md`, `./archive/y.md`) need a `../` or
   directory adjustment now that it lives one level deeper; grep the rest of
   `docs/pr-docs/` for any other doc linking to the old un-archived path and
   repoint those too.
7. **Commit straight to `main` and push** — no new branch. Message like
   "docs: archive PR <PR#> doc now that it's merged". Per `CLAUDE.md`'s
   branching rule, routine post-merge cleanup (branch deletion, doc
   archiving, link fixes — never actual code) is the one exception to "never
   commit/push directly on `main`."
8. Report what moved. If there are multiple merged-but-unarchived PR docs,
   handle all of them in one pass rather than one at a time.

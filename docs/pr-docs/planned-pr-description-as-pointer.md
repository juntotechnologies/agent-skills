# PR <number>: PR Description As Pointer, Not Copy

Status: planned

Branch: `feature/pr-description-as-pointer`

## Goal

Make a PR's GitHub description a short summary plus links into its PR doc,
instead of a second copy of that doc's checklist and smoke tests. Today's rule
asks for manual re-sync on every meaningful doc change, which is discipline that
reliably decays — chem-inventory PR 184 had drifted to a 90-line description
against a 555-line doc, missing the entire Implementation Checklist. Removing
the duplicate removes the drift by construction.

## Context

- Triggered by PR 184: the description was missing Tiers 0–8 entirely, which is
  the exact content Shaun wanted to read from the PR page.
- The fix was applied by hand to PR 184 already; this doc makes it the rule.
- Root `AGENTS.md` is a **symlink** to
  `skills/setup-project-repo/assets/AGENTS.md`, so the canonical rule text lives
  in one file, not two.
- `projects/chem-inventory/AGENTS.md` is a separate real file that carries its
  own copy of the rule.
- Registered projects pick changes up through symlinks immediately; generic
  repos that received *copied* templates need the **Setup Project Repo** sync
  mode.

## The Replacement Rule

Both AGENTS.md copies currently carry two bullets under *Track Progress &
Follow-Ups* (canonical lines 45–46). They become:

- When a PR is opened, set its description to a **pointer** to the PR doc, not a
  copy of it: a short Summary, then links into the doc's sections on the PR's
  head branch. The created PR starts as a blank template; replace it.
- The PR doc is the single source of truth for checklist, smoke tests,
  decisions, and scope. Never duplicate those into the description — duplication
  is what drifts. Because the description links to the doc **on the head
  branch**, pushing the doc updates what reviewers see with no `gh pr edit` pass.
- Summary is the only content that lives in the description itself. Anything
  that would otherwise exist only there must move into the doc first.

## Implementation Checklist

Ordered least -> most consequential. These are prose/behavior rules, not code, so
there is no failing-test-first step for the wording itself; the one testable
surface is the installer, which these changes do not touch.

### Tier 1 - Narrowest: the skill that opens PRs

- [ ] Rewrite `skills/pr-doc-open/SKILL.md` closing paragraph (lines 41–44) so
      it stops promising lifetime re-sync and instead describes the pointer body.
- [ ] Update its step 7 — the body's doc link must point at the **head branch**
      blob URL, not a repo-relative path, so anchors resolve and it tracks pushes.

### Tier 2 - One project

- [ ] Replace the two bullets in `projects/chem-inventory/AGENTS.md` (lines
      41–42) with the rule above.

### Tier 3 - The PR template

- [ ] Update `skills/setup-project-repo/assets/.github/pull_request_template.md`
      line 9 — "one-line summary plus bullets for meaningful changes" contradicts
      the pointer rule.

### Tier 4 - Canonical, propagates everywhere

- [ ] Replace the two bullets in
      `skills/setup-project-repo/assets/AGENTS.md` (lines 45–46). This is the
      copy the root `AGENTS.md` symlink and every future bootstrap inherit.
- [ ] Run `scripts/install.sh --claude-compat` and confirm links still resolve.
- [ ] Confirm `tests/test_install.sh` still passes (no installer change expected,
      but the asset tree moved).

## Smoke Tests

Manual, in the running tools — 20% effort for 80% of the blast radius.

- [ ] Open chem-inventory's `AGENTS.md` in a fresh session -> §5 reads as the
      pointer rule, not the sync rule.
- [ ] Run **PR Doc Open** on any planned doc -> the PR it creates has a Summary
      plus head-branch links, no duplicated checklist.
- [ ] Click a section link in that PR body -> lands on the right anchor in the
      doc, rendered on the PR's branch.
- [ ] Push a doc edit without touching the PR -> reload the PR page, the linked
      doc shows the edit.

## Product Decisions

- **Pointer over generated body.** A CI job could regenerate the description
  from the doc on every push, but it needs a relative-link rewrite step that can
  silently rot, and PR-body links resolve against the default branch rather than
  the PR's. Pointing at the branch blob gives correct links for free.
- **Summary stays duplicated.** It is 2–3 lines, it is what shows in PR lists
  and notifications, and it changes rarely. Accepting that one small duplicate
  is worth not forcing a click to learn what a PR does.

## Scope

- Both AGENTS.md copies, the pr-doc-open skill, and the PR template.

## Non-Goals

- No CI automation to generate PR bodies (see Product Decisions).
- No retroactive rewrite of already-merged PRs' descriptions.
- No change to `scripts/install.sh` or the symlink layout.
- **Not** reconciling the drift found between `projects/chem-inventory/AGENTS.md`
  and the canonical asset (canonical carries orthogonality/feature-flag bullets
  the project copy lacks, and section ordering differs). Real, pre-existing,
  and its own doc — flagged for Shaun, not fixed here.

## Related Docs

- [PR 11: Codex-First Agent Layout](./archive/11-codex-first-agent-layout.md)

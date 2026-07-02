# coding-practices

Centralized coding workflow, PR docs structure, and templates I reuse across
projects. Instead of recreating a `docs/pr-docs/` tree, a PR-doc template, and a
PR description template in every new repo, I point Claude at this repo and it
copies everything into place.

## Layout

```
CLAUDE.md                           # The coding workflow (discuss → plan → branch → TDD → track)
docs/pr-docs/template.md            # Template for individual PR planning docs
docs/pr-docs/archive/               # Where closed PR docs go
.github/pull_request_template.md    # PR description checklist (GitHub auto-loads this)
```

## Bootstrap a new repo from this one

Point Claude at this repo (share the URL or clone path) and say:
**"Set up this repo's coding practices from `coding-practices`."** Claude should:

1. Copy **`CLAUDE.md`** to the target repo root (merge, don't clobber, if one
   already exists — ask first).
2. Create **`docs/pr-docs/`** and **`docs/pr-docs/archive/`** in the target repo,
   and copy **`docs/pr-docs/template.md`** into it.
3. Copy **`.github/pull_request_template.md`** to the target repo's `.github/`
   directory so new PRs are prefilled with the checklist.
4. Adapt project-specific bits to the target repo — the `CLAUDE.md` "Required
   Checks" (e.g. `npm run check`, `npm test`) and the PR template's smoke tests
   reference a specific app; swap them for the target project's real commands
   and flows, or flag them for the user to fill in.

That's it — the target repo now has the same docs structure and templates, with
`CLAUDE.md` driving the workflow.

## The commands referenced in the templates are examples

`CLAUDE.md` and `.github/pull_request_template.md` contain checks and smoke tests
from a specific project (Drizzle migrations, inventory/transactions pages, etc.).
Treat those as placeholders to replace per project, not as literal requirements.

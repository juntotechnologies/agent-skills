---
name: Setup Project Repo
description: Bootstrap repo-owned coding instructions and PR templates, or merge requested shared workflow updates into an existing repo without overwriting its local guidance.
---

## Ownership

`agent-skills/skills/setup-project-repo/assets/` provides generic starting
points. Once copied, each project's instructions and adaptations belong to that
project. Reusable template changes go here; project-specific changes stay there.
No registry, project overlays, generated project instructions, or external links.

## Bootstrap

1. Inspect `AGENTS.md`, `docs/pr-docs/{README.md,README.template.md,template.md}`,
   the archive directory, and `.github/pull_request_template.md`. If already set
   up, report that and avoid overwriting. Reconcile partial setups against the
   authorized scope; ask only about genuinely ambiguous choices.
2. Copy missing files from this skill's `assets/` as ordinary files. Adapt the
   README template into a live project TOC. Do not create Claude compatibility
   files; preserve existing internal compatibility links.
3. Replace example checks with the project's real verification commands. Keep
   project skills in `<repo>/.agents/skills/`. Never back-propagate project facts
   into these shared assets.
4. Preserve the rule that authorized work is committed, pushed, and exposed in a
   PR for review by default. Reuse an open PR only for small related changes.
   An explicit planning-doc waiver does not waive reviewable delivery.
5. Verify the adapted files and links, then publish through the authorized PR
   workflow. Do not merge or perform production/credential changes implicitly.

## Sync an existing project

1. Read the local guidance and compare it with this skill's generic defaults.
2. Merge only the requested reusable changes, preserving project-specific rules,
   local skills, and accepted exceptions. Never overwrite a project AGENTS.md
   wholesale or require byte equality with the generic template.
3. Resolve conflicts using the user's current instructions; show consequential
   unresolved choices before editing. Existing approval covers routine merging.
4. Verify and publish the diff. Sync never implicitly edits PR docs/templates or
   installs global skills unless those changes were requested too.

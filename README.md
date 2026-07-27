# agent-skills

Canonical global and project-specific agent skills, instructions, and assets.

## Layout

```text
skills/
  <global-skill>/SKILL.md
projects/
  registry.tsv
  chem-inventory/
    AGENTS.md
    skills/db-migrations/SKILL.md
scripts/
  install.sh
```

## Install

```bash
scripts/install.sh
```

The installer is idempotent. It symlinks every global skill into both
`~/.agents/skills` and `~/.claude/skills`, discovers registered projects under
`~/Documents/GitHub`, and installs their canonical instructions and skills.
Use `--workspace-root PATH` when the checkout root differs.

Existing ordinary files are never overwritten. The installer reports and
skips them so their migration can happen deliberately in the owning project's
PR.

On a new machine, the `personal-config` curl setup clones or updates this repo
and runs the installer. If links are missing, rerun:

```bash
~/.personal-config/scripts/update_agent_files.sh
```

## Setup Project Repo

`skills/setup-project-repo/SKILL.md` bootstraps a project repo with my standard
coding workflow files. Its `assets/` directory is the canonical source for:

- root `CLAUDE.md`
- root `AGENTS.md`
- PR planning docs template and TOC template
- GitHub pull request template

Generic target repos receive copied/adapted outputs. Projects registered under
`projects/` receive symlinks so their project-specific content stays canonical
here and updates immediately.

The top-level `CLAUDE.md`, `AGENTS.md`, `.github/pull_request_template.md`, and
`docs/pr-docs/` template files are symlinks into
`skills/setup-project-repo/assets/` for convenience. The asset files are the
canonical copies. `CLAUDE.md` and `AGENTS.md` both point at the same canonical
workflow asset so Claude and Codex receive the same instructions without
duplicated edits.

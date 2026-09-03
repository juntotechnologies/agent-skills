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

The installer is idempotent. It symlinks every global skill into
`~/.agents/skills`, discovers registered projects under `~/Documents/GitHub`,
and installs their canonical `AGENTS.md` instructions and `.agents/skills`.
Use `--workspace-root PATH` when the checkout root differs.

Claude compatibility is opt-in:

```bash
scripts/install.sh --claude-compat
```

That mode links `~/.claude/skills` to `~/.agents/skills`; for registered
projects it also links `CLAUDE.md` to `AGENTS.md` and `.claude/skills` to
`.agents/skills`. It never maintains duplicate content.

User-level links are absolute and machine-local. Project links are relative so
they can be committed to a project repository and remain valid when the
workspace moves to another home directory.

Existing ordinary files and directories are never overwritten. The installer
reports and skips them so their migration can happen deliberately in the owning
project's PR. Default installation does not inspect, change, or remove existing
Claude paths.

On a new machine, the `personal-config` curl setup clones or updates this repo
and runs the installer. If links are missing, rerun:

```bash
~/.personal-config/scripts/update_agent_files.sh
```

## Setup Project Repo

`skills/setup-project-repo/SKILL.md` bootstraps a project repo with my standard
coding workflow files. Its `assets/` directory is the canonical source for:

- root `AGENTS.md`
- PR planning docs template and TOC template
- GitHub pull request template

Generic target repos receive copied/adapted outputs. Projects registered under
`projects/` receive symlinks so their project-specific content stays canonical
here and updates immediately.

The top-level `AGENTS.md`, `.github/pull_request_template.md`, and
`docs/pr-docs/` template files are symlinks into
`skills/setup-project-repo/assets/` for convenience. The asset files are the
canonical copies. If Claude support is needed later, create only a
`CLAUDE.md -> AGENTS.md` compatibility symlink.

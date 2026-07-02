# agent-skills

Canonical reusable Claude/agent skills and their assets.

## Layout

```text
skills/
  setup-project-repo/
    SKILL.md
    assets/
      CLAUDE.md
      docs/pr-docs/README.template.md
      docs/pr-docs/template.md
      docs/pr-docs/archive/.gitkeep
      .github/pull_request_template.md
```

## Setup Project Repo

`skills/setup-project-repo/SKILL.md` bootstraps a project repo with my standard
coding workflow files. Its `assets/` directory is the canonical source for:

- root `CLAUDE.md`
- PR planning docs template and TOC template
- GitHub pull request template

Target repos receive copied/adapted outputs. Do not edit those target copies as
canonical unless the goal is a project-specific adaptation. To change the
workflow or templates globally, edit this repo first, then sync target repos.

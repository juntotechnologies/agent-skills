# PR 17: Drop the Claude Compatibility Install Mode

Status: underway

Branch: `chore/drop-claude-compat`

## Goal

Stop the installer and the setup skills from ever creating `CLAUDE.md` or
`.claude/` paths. `AGENTS.md` and `.agents/skills` become the only agent
surfaces this repo produces, with no opt-in exception.

## Context

[PR 11](./archive/11-codex-first-agent-layout.md) made Codex surfaces canonical
and kept Claude support as an opt-in `scripts/install.sh --claude-compat` flag.
That flag links `~/.claude/skills`, and for each registered project
`CLAUDE.md -> AGENTS.md` and `.claude/skills -> ../.agents/skills`. The
`setup-project-repo` and `update-agent-skills` skills and `README.md` still
describe how to turn it on. Its only effect today is to recreate files that are
meant to be dropped. `projects/personal-config` lives in this repo and has no
Claude references of its own.

## Implementation Checklist

Ordered least -> most consequential/complex.

### Tier 1 - Quick wins (low risk, contained)

- [x] Remove the Claude compatibility paragraphs from `README.md`, including
  the "create a `CLAUDE.md` symlink later" note.
- [x] Replace the opt-in paragraph in `skills/setup-project-repo/SKILL.md` with
  "never create Claude paths; leave any existing ones untouched".
- [x] Remove the `--claude-compat` sentence from
  `skills/update-agent-skills/SKILL.md`.

### Tier 2 - Installer

- [x] Test first: `scripts/install.sh --claude-compat` exits 2 with
  "Unknown argument", and creates nothing.
- [x] Remove the `--claude-compat` flag, `install_global_claude_compat`, the
  per-project Claude links, and the "Claude compatibility enabled." message.
- [x] Replace the compat-mode tests with one showing that a default install
  leaves pre-existing `CLAUDE.md` and `.claude/` paths untouched. The existing
  "default install creates no Claude paths" assertions stay.
- [x] Run `tests/test_install.sh`, `tests/test_compose_project_agents.sh`,
  `tests/test_relative_path.sh` and
  `uv run python -m unittest tests/test_local_model_delegation.py`.

## Smoke Tests

| Check | Covered by |
| --- | --- |
| Install creates no `CLAUDE.md` or `.claude/` anywhere | `tests/test_install.sh` |
| The old flag is refused, not silently ignored | `tests/test_install.sh` |
| Existing Claude paths are left alone | `tests/test_install.sh` |

- [ ] **Re-running the installer changes nothing unexpected** · as owner
  1. Run the installer on this Mac.

  **Pass if:**
  - It ends with "Installed agent skills."
  - No new `CLAUDE.md` or `.claude` folder appears in any project.

## Product Decisions

- The flag is removed rather than kept as a no-op. An unknown-argument error
  tells anyone with an old command in their history that the mode is gone.
- Existing `CLAUDE.md` / `.claude/` paths on disk are not deleted by the
  installer. Removing them is a manual, per-machine decision, since Claude Code
  reads them.

## Scope

- Installer flag, its tests, and the three docs that describe it.

## Non-Goals

- Deleting Claude paths already on disk (for example `~/.claude/skills` or a
  project's `CLAUDE.md` symlink).
- Rewriting archived PR docs that mention the old mode.

## Related Docs

- [PR 11: Codex-First Agent Layout](./archive/11-codex-first-agent-layout.md)

# PR 2: Cross-Agent Skill Installation

Status: in-scope work complete

Branch: `feature/cross-agent-skill-installation`

## Goal

Make `agent-skills` the canonical home for global and project-specific agent
workflows, with an idempotent installer that exposes them to Codex, Claude
Code, and project repositories through symlinks.

## Context

Global skills currently live in `skills/` and are installed only for Claude
Code by `personal-config`. The chem-inventory database migration skill lives
only inside that project. Codex discovers repository skills from
`.agents/skills`, so the current arrangement can drift and does not expose the
same workflows across harnesses.

## Implementation Checklist

### Tier 1 - Canonical layout

- [x] Add failing contract tests for canonical global/project skill discovery.
- [x] Preserve global skills and centralize chem-inventory's project-specific
      instructions and database migration skill.

### Tier 2 - Installer

- [x] Add failing tests for idempotent global and project symlink installation.
- [x] Implement a DRY installer that links global skills into both
      `~/.agents/skills` and `~/.claude/skills`, and known project content into
      its checkout.
- [x] Document installation, recovery, and the canonical-source policy.

## Smoke Tests

- [x] Run the installer twice and confirm the second run reports an already
      linked state without creating backups or duplicate links.
- [ ] Start Codex and Claude Code in chem-inventory and confirm both expose the
      database migration skill.

## Product Decisions

- `agent-skills` owns both global and project-specific agent content.
- Symlinks provide immediate synchronization; checked-in README recovery
  guidance is the fallback when a fresh environment has not run setup.
- Project checkouts are discovered beneath the configured GitHub workspace
  rather than hardcoded to one absolute home-directory path.

## Scope

- Canonical layout, installer, tests, and documentation.
- Canonical chem-inventory project agent content.

## Non-Goals

- Supporting collaborators, CI, or cloud environments without the
  `agent-skills` checkout.
- Committing symlinks to chem-inventory's unrelated active feature branch.

# PR planned: Link skills for Claude Code

Status: planned

Branch: `bugfix/claude-skill-links`

## Goal

`install.sh` only filled `~/.agents/skills`. Claude Code reads `~/.claude/skills`, so `site-taste` never loaded there.

## Implementation Checklist

- [x] Install adds missing links; keeps existing entries

## Smoke Tests

Not applicable: no UI. Repo tests pass.

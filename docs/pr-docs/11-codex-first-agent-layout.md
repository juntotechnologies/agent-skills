# PR 11: Codex-First Agent Layout

Status: in-scope work complete (manual smoke tests pending)

Branch: `refactor/codex-first-agent-layout`

## Goal

Make Codex's `AGENTS.md` and `.agents/skills` conventions the sole default and
canonical layout for this repository and its installer, while retaining an
explicit, symlink-only compatibility mode that can restore Claude support later
without duplicating maintained content.

## Context

The repository currently stores its canonical workflow in an asset named
`CLAUDE.md`, links both root instruction filenames to that asset, and installs
every skill into both `~/.agents/skills` and `~/.claude/skills`. Those installed
copies are already symlinks, so this is a naming and installer simplification,
not a meaningful disk-space reduction. Shaun no longer uses Claude and wants
Claude compatibility to become optional.

This work is intentionally separate from PR #10's local-model delegation
feature.

## Implementation Checklist

Ordered least -> most consequential/complex: tests and documentation contract
first, installer behavior and canonical path migration last.

### Tier 1 - Codex-first installation contract

- [x] Add failing tests proving default installs create global and project
  `.agents` links without creating Claude paths.
- [x] Add failing tests proving `--claude-compat` creates whole-surface symlinks
  (`CLAUDE.md` to `AGENTS.md` and `.claude/skills` to `.agents/skills`) and is
  idempotent.
- [x] Add failing tests proving existing unmanaged Claude paths are preserved
  rather than replaced or deleted.
- [x] Implement the default Codex-only installer and opt-in Claude compatibility
  mode.

### Tier 2 - Canonical instruction naming

- [x] Rename the canonical workflow asset from `CLAUDE.md` to `AGENTS.md` and
  repoint the repository's root `AGENTS.md` symlink.
- [x] Remove the repository's root `CLAUDE.md` compatibility symlink from the
  default tracked layout.
- [x] Update Setup Project Repo and Update Agent Skills so they treat
  `AGENTS.md` as canonical and create Claude symlinks only when explicitly
  requested.
- [x] Update the PR workflow skills, templates, and repository documentation to
  use `AGENTS.md` terminology.

### Tier 3 - Verification

- [x] Run all installer/path tests and validate changed skill structure. The
  current validator's naming rule still rejects four unchanged legacy display
  names; see Known Issues.
- [x] Run the installer in default mode and verify it leaves existing Claude
  paths untouched while maintaining the canonical `.agents` links.
- [x] Run compatibility mode in an isolated home/workspace and verify its
  symlinks resolve to the Codex surfaces.

## Smoke Tests

- [ ] Run the default installer in a clean environment -> only `.agents/skills`
  and project `AGENTS.md`/`.agents/skills` are created.
- [ ] Run the installer with `--claude-compat` in a clean environment -> Claude
  instruction and skill paths are symlinks to their Codex counterparts.
- [ ] Run the default installer against an environment with existing Claude
  content -> that content remains unchanged.

## Product Decisions

- `AGENTS.md` and `.agents/skills` are the only canonical/default surfaces.
- Claude support is opt-in and consists only of symlinks to Codex surfaces;
  never maintain a second copy of instructions or skills.
- Do not automatically remove or rewrite existing `~/.claude` or project
  Claude paths. Compatibility cleanup requires separately confirmed, exact
  targets.
- Keep this migration independent of PR #10 so either change can be reviewed,
  merged, or rolled back alone.

## Known Issues

- The current skill validator requires lowercase hyphen-case frontmatter names.
  Four updated global skills retain their pre-existing title-case identifiers
  (`Setup Project Repo`, `Update Agent Skills`, `PR Doc Open`, and
  `PR Doc Archive`) to avoid an unrelated identifier migration. Their
  frontmatter/body structure validates, and the project-specific
  `db-migrations` skill passes the current validator outright.

## Scope

- Update the canonical agent-skills repository, installer, tests, skills, and
  documentation for the Codex-first layout.
- Publish the change on its own branch and pull request.

## Non-Goals

- Deleting current user-level or project-level Claude configuration.
- Changing Codex configuration, Hermes routing, or PR #10 implementation.
- Maintaining native Claude-specific instructions.

## Related Docs

- [PR 10: Local Model Delegation](https://github.com/juntotechnologies/agent-skills/pull/10)

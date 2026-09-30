# Agent Skills PR Docs

## Table of Contents

| Doc | Description |
|-----|-------------|
| [PR 19: Delegation Mac only](./19-delegation-mac-only.md) | Delegation runs on the Mac mini; the Spark is reserved for training and benchmarks |

## Archive

| Doc | Description |
|-----|-------------|
| [PR 14: PR Description As Pointer](./archive/14-pr-description-as-pointer.md) | Made a PR body a summary plus links into its PR doc, ending description/doc drift |
| [PR 18: Delegation for Claude Code](./archive/18-delegation-for-claude-code.md) | Merged; Claude Code can use local-model delegation, and the skill states when it is the wrong tool with measured latency. The skip-when-searchable smoke test is unverified. |
| [PR 17: Drop Claude Compatibility](./archive/17-drop-claude-compat.md) | Merged; removed the `--claude-compat` mode and the whole `projects/` tree, so the installer only syncs global skills into `~/.agents/skills` and each project owns its own AGENTS.md. Installer idempotency verified on citmini. |
| [PR 4: Portable Project Links](./archive/4-portable-project-links.md) | Generated version-control-safe relative project symlinks |
| [PR 13: Reliable local-only delegation](archive/13-bounded-delegation.md) | Merged local reliability fixes, removed hosted delegation and restricted inference transport. |
| [PR 2: Cross-Agent Skill Installation](./archive/2-cross-agent-skill-installation.md) | Centralize global and project skills and install them for Codex, Claude Code, and known projects |
| [PR 10: Local Model Delegation](./archive/10-local-model-delegation.md) | Route bounded read-only Codex analysis across the Mac mini and DGX Spark models |
| [PR 11: Codex-First Agent Layout](./archive/11-codex-first-agent-layout.md) | Make Codex surfaces canonical and keep Claude support as opt-in symlinks |

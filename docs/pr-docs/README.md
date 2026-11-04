# Agent Skills PR Docs

## Table of Contents

| Doc | Description |
|-----|-------------|

## Archive

| Doc | Description |
|-----|-------------|
| [PR 57: uv-only fixes after the first full scan](./archive/57-uv-only-quoted-uv-lists.md) | A quoted `uv` command list is correct; a Python list that starts with an interpreter is a fault; a PEP 723 block is not a comment fault. |
| [PR 56: uv-only gate holes](./archive/56-uv-only-gate-holes.md) | Shebang rule never ran; quoted interpreters in json and plist slipped; both now fault. |
| [PR 55: Python only through uv, enforced](./archive/55-uv-only-everywhere.md) | `uv-only` flags every other way to run or install Python; one data file shared with `ops guard` |
| [PR 54: A slip adds its gate](./archive/54-slip-adds-gate-rule.md) | Global rule: patch the gate in the same change as the fix |
| [PR 53: Checker `--worktree` mode](./archive/53-lint-worktree-mode.md) | Lint uncommitted edits + untracked files, for the write-time hook |
| [Comment rule autofix](./archive/52-why-comments-fixer.md) | Fixer deletes disallowed comments |
| [Deferred tasks](./archive/50-deferred-tasks.md) | Issue, not Left |
| [Rules map](./archive/49-rules-map.md) | Where rules live |
| [Checker fails closed](./archive/48-checker-fail-closed.md) | Crash = fault |
| [Enforced rules leave prose](./archive/47-enforced-rules-leave-prose.md) | Smaller instructions |
| [Rule registry](./archive/46-rule-registry.md) | Registry + shared checker |
| [Claude skill links](./archive/45-claude-skill-links.md) | Link skills for Claude Code |
| [UI rules on demand](./archive/44-ui-rules-on-demand.md) | Query rules, UI pointer |
| [Judge denials](./archive/43-denial-judgment.md) | Narrow allow rule + retry, or stop + ask |
| [No retry creates](./archive/42-no-retry-creates.md) | Check for partial result before retrying create/send cmds |
| [Autonomy rule](./archive/41-autonomy-rule.md) | Standing decision rules so Shaun stays hands-off |
| [CLI over prose rule](./archive/40-cli-over-prose.md) | Global rule: agents build + use CLIs by default |
| [PR 33: Site taste skill](./archive/33-site-taste-skill.md) | Merged; design rules that Shaun's sites proved, as data, with a drift check against the site checkouts. |
| [PR 29: Agent-owned verification](./archive/29-agent-verification-workflow.md) | Merged; focused PR scope, agent-run walkthroughs, retained evidence, and independent review. |
| [PR 14: PR Description As Pointer](./archive/14-pr-description-as-pointer.md) | Made a PR body a summary plus links into its PR doc, ending description/doc drift |
| [PR 19: Delegation Mac only](./archive/19-delegation-mac-only.md) | Merged; delegation runs on the Mac mini and the Spark is reserved for training. Known issue: the helper still labels fan-out `spark-to-mac`. |
| [PR 18: Delegation for Claude Code](./archive/18-delegation-for-claude-code.md) | Merged; Claude Code can use local-model delegation, and the skill states when it is the wrong tool with measured latency. The skip-when-searchable smoke test is unverified. |
| [PR 17: Drop Claude Compatibility](./archive/17-drop-claude-compat.md) | Merged; removed the `--claude-compat` mode and the whole `projects/` tree, so the installer only syncs global skills into `~/.agents/skills` and each project owns its own AGENTS.md. Installer idempotency verified on citmini. |
| [PR 4: Portable Project Links](./archive/4-portable-project-links.md) | Generated version-control-safe relative project symlinks |
| [PR 13: Reliable local-only delegation](archive/13-bounded-delegation.md) | Merged local reliability fixes, removed hosted delegation and restricted inference transport. |
| [PR 2: Cross-Agent Skill Installation](./archive/2-cross-agent-skill-installation.md) | Centralize global and project skills and install them for Codex, Claude Code, and known projects |
| [PR 10: Local Model Delegation](./archive/10-local-model-delegation.md) | Route bounded read-only Codex analysis across the Mac mini and DGX Spark models |
| [PR 11: Codex-First Agent Layout](./archive/11-codex-first-agent-layout.md) | Make Codex surfaces canonical and keep Claude support as opt-in symlinks |

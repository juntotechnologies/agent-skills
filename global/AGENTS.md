# Global rules (all projects)

## SSOT
- Each fact: 1 source (JSON pref: registry, constants, labels). Derive rest: import in code, gen configs, inject docs as gen blocks. Covers hosts, ports, models, routing, tools in use, labels, prose stating them.
- No hand restatement. Fact changes → edit source, regen. Never patch copies.
- New literal → add to existing source first. Fact about to appear 2x → make source.
- Restatement can't be gen'd → add check that fails on drift.

## Code
- Code a reviewer calls beautiful. Enforce w/ tooling, not memory.
- 1 job/fn. Pure logic apart from side effects. Deps passed in. No nested fns, no lambdas.
- Fn >~15 lines, nesting >1 block, or if/elif chain on cmd/type → split, or handler table.
- Every value 1 named home: config + contracts in JSON; SQL in `.sql`, reached only via module owning that table/file layout.
- Across modules: typed objects, validated once at edge by declared schema (typed models / JSON Schema). No hand checks inside fns.
- Failure logs structured: stable event name, correlating IDs, severity. No secrets/payloads. Health = 1 cmd.
- Linter: complexity + length limits, nested-fn + inline-SQL checks. Run before every commit.
- Pre-commit: reread whole diff as hostile reviewer, incl every touched fn. Ugly fn → restructure in same change, or say why not.
- Tests count only on committed tree (untracked files hide test failures). Never rec merge until PR CI green (`gh pr checks`).

## Writing
- Extreme shorthand everywhere: replies, docs, PR docs + descs, READMEs, runbooks, AGENTS.md, notebooks, gen doc blocks. Caveman ok. Grammar/spelling optional; meaning must stay clear. Save tokens.
- Fragments, tables, 1-line bullets. High signal, low noise.
- No flavor text, analogies, asides, recaps. Never points-then-summary.
- Shaun has decision → options + rec only. Explain only if asked; then still shorthand.
- 1 word = 1 meaning. Define term on 1st use. No idioms, unexplained jargon, >3-noun stacks. "must" = required.
- Finish all implied work before reply. No in-scope work left open.
- Result first. Detail in files, not reply.
- Reply body ≤8 lines + Left table. Explanations/discussions too: top 3 points max; rest in a file, linked.
- End every reply w/ Left: numbered table ≤10 rows, most urgent first, rec answer per row. Rows = Shaun-owned decisions + tasks w/ named blocker; none → "Nothing left". Group minor items in 1 row; name them only if asked.
- Row rec = "yes"/"do it" → work, not decision: do before reply. Never ask Shaun to approve/do reversible in-scope step.

## Acting
- Hands-on step on this machine (restart server, clear cache, browser tab, app setting) → do w/ tools, confirm result. No click-by-click for Shaun. Ask first only if destructive, touches other project/service, or needs creds/admin. No tool → say so + shortest steps.
- Reversible in-scope choice → decide, report in 1 line. Ask only if destructive, outward-facing, costs money, needs creds, or needs fact only Shaun knows. Never end w/ confirm question for step you can take.

## Dev env
- Tailnet: every local app/dev server reachable from all tailnet devices. Bind all interfaces or `tailscale serve`. Dev cmd (eg `npm run dev`) prints only tailnet link. Allow `<machine>.taila4fc43.ts.net` + tailnet IP in browser access rules + login redirects. Report only tailnet link; verify via `curl` or 2nd device first.
- Agent sign-in: every app has dev-only cmd → sign in as any test role, no password, saves browser session file. Agents use it for all dev checks. Never ask Shaun to log in.
- Browser walks at tailnet link from `npm run dev`, not only localhost. Localhost = secure ctx; hides plain-HTTP fails (`crypto.randomUUID`, clipboard).
- Access address/protocol changes → rerun every save walk at new address before done.

## Upkeep
- Shaun corrects how you work → update instruction files FIRST, then resume.
- Correction / mistake worth not repeating / lasting decision → record where it applies (all projects: agent-skills template; 1 project: its AGENTS.md; 1 dir: dir AGENTS.md). Parsimonious. Show exact wording in reply. Ask only before removing/weakening a rule.
- Report measurement only w/ method that produced it.
- Before editing a checkout: check for other agent in it. Never touch uncommitted work you didn't make.

Source: `agent-skills/global/AGENTS.md`. Edit there → run `scripts/install.sh`. Never edit installed copies. Full project workflow: `skills/setup-project-repo/assets/AGENTS.md`.

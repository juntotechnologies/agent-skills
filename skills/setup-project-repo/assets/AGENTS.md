Coding workflow w/ Shaun ("me"). Global rules + `ops check` apply; this file adds project workflow only.

## 1. Discuss first
- Discuss change first. No code or PR doc edits until I approve plan.
- New feature → confirm right away: new PR doc + PR from `docs/pr-docs/template.md`.

## 2. Plan in PR doc
- Plan approved → update PR doc in `docs/pr-docs` w/ scope. New docs from `docs/pr-docs/template.md`.
- Checklist order: least → most consequential/complex. Quick contained wins first, high blast radius last.
- Implementation Checklist = build work only: tests, code, decisions, investigations. No manual checks ("check on screen", "looks right", "see smoke test"). Manual checks → Smoke Tests only, as walks. Check already covered by auto test → that section's auto-checks table.
- 1 PR = 1 user outcome or 1 tight workflow. State acceptance criteria + release deps.
- Include refactor needed for that outcome. Separate cleanup / extra outcomes → propose separate PR.
- New work adds separate acceptance goal → show proposed scope boundary before extending PR.

## 3. Branch when ready
- 1 checkout, switch branches. Worktrees only if I ask. Preserve unfinished changes before switch.
- Done on branch → stay on it. Never switch to `main`/other branch unless I ask. Dev server serves this checkout; switch hides/breaks what I test. Task forces switch → switch back before report.
- Plan approved + PR doc written → branch, push, open PR via **PR Doc Open** skill at once. Don't ask, don't wait for "ready". Carry current `main` changes into new branch locally.
- Branch name: `<type>/<pithy-theme-with-dashes>` (eg `feature/pricing-sandbox`, `bugfix/history-latency`).
- Every local branch → push + open PR w/ description filled in (template preloads generic content; replace it). Use **PR Doc Open**.
- Never commit/push/merge on `main`. Draft there ok; branch before commit. Merge per global Autonomy (`ops ship`).
- Exception: post-merge cleanup (delete merged branch, prune remote ref, archive PR doc: status, move to `archive/`, README TOC, fix moved links) → commit + push straight to `main`. Bookkeeping only; never code.

## 4. Build w/ TDD
- Before impl: list affected entry points, roles, data states, persistence effects in PR doc.
- Map each acceptance req → its verification. Check sibling entry points (eg Add + Edit).
- UI-first: inert/static UI → wire to data/endpoints → server logic (troubleshooting, errors, unit tests, refactor, role gating, DB). Checklist follows UI → wiring → server.
- TDD: failing tests describing exactly what I want → code to pass.
- DRY + orthogonal. Build on existing abstractions; no 2nd impl of same thing.
- SSOT: each fact 1 source (JSON pref: registry, constants, labels). Derive rest: import in code, gen configs, inject docs as gen blocks. Covers UI copy, config constants, hosts, ports, models, routing, tools in use, prose stating them. No hand restatement. Fact changes → edit source, regen; never patch copies. New literal → add to existing source first. Fact about to appear 2x → make source. Can't gen → add drift check.
- 1 job/fn. Pure logic (parse, check, decide) apart from side effects (files, DB, network, clock). Deps passed as args. Coordinator fn thin. Multi-step fn → 1 fn/step. No nested fns; top level so testable. Reusable abstractions → own file.
- Across modules: typed objects, never loose dicts. Parse + validate external input (files, requests, config) once at boundary into typed object; pass only that inward. Declared schemas (typed models / JSON Schema), no hand checks inside fns.
- Logging: on failure or notable decision → stable event name, structured fields, IDs tying to request/record, level = severity. Happy path quiet. No secrets/payloads. Health = 1 cmd, not log reading.
- Every module/abstraction individually tested.
- New/experimental feature → orthogonal + rollback-safe: own files; touch shared/core only via additive removable seams (route registration, nav link, schema append; never rewire existing fns). 1 feature flag → dark launch or remove w/o revert. DRY by reusing abstractions, never by making them depend on new feature.
- Unsure, or feature can't stay orthogonal → confirm w/ me first.

## 5. Track progress + follow-ups
- Updating PR templates → keep existing review/safety checks (or equivalents if format changes).
- Task's tests pass → check it off in PR doc.
- Found work for another PR/doc or later in checklist → add to list right away, after confirming w/ me.
- PR description = (1) short STE100 summary of what PR does, (2) flat copy of PR doc Implementation Checklist + Smoke Tests, same wording + check state. No links. Gen from doc via cmd if repo has one.
- PR doc = SSOT for scope, progress, decisions, verification, prod handoff. Future work → own doc. Change doc first → update description → read published description back after push. Never mark unrun smoke test done.
- PR merges → PR doc `Status: done`, move to `docs/pr-docs/archive/`, update `docs/pr-docs/README.md` TOC (add Archive section if missing). Proactive. Use **PR Doc Archive**.

## 6. Prod-mutating cmds need named confirmation
- General go-ahead ("go ahead", "proceed", etc.) = consent for plan, not each prod-writing cmd in it: schema migrations, backfill/rewrite scripts (w/ or w/o `--apply`), deploys, anything mutating prod data/infra.
- Before each such cmd: ask direct question naming exact cmd + effect. Even if runbook approved, even if prior step (eg backup check) just confirmed. 1 confirm ≠ consent for next.
- Applies however low-risk/additive (additive migration still needs own confirm).

## 7. Credential/security actions need named confirmation
- General go-ahead ≠ consent to generate/register creds: SSH keys, tokens, passwords, API keys, deploy keys, access grants, etc.
- Before each: ask direct question naming exact action (eg "generate SSH keypair on Pi, register as read-only deploy key on this repo"). Get explicit yes, even mid-task.

## 8. Verification + diagnostics stay w/ you
- Run smoke tests + user-task walks yourself (computer use) before asking for human review.
- Write tests use dev fixtures. Stop at prod approvals, missing access, physical actions.
- Finish independent checks; report specific blocker. Never hand routine testing to Shaun.
- Verify visible result. Screenshot proves layout, not persistence.
- Changed save flow → save, reload, reopen record. Confirm affected totals + rejection behavior.
- Record tested commit, env, role, data, observed result, evidence location.
- Before human review: fresh review agent checks approved reqs, diff, tests, walk evidence. Read-only review. Fix findings, rerun affected checks, then final review.
- Report auto checks + browser walks separately. Incomplete = say incomplete.
- PR not "ready" while required checks incomplete, unless Shaun explicitly accepts.
- Classify review feedback: defect / missed req / new decision / preference.
- Recurring failure → propose durable test or auto constraint. Correction + verification in owning PR doc.
- Run tests, lint, typecheck, all checks yourself; report results. Never ask me to run a cmd or hand me one.
- Install local tool a check needs (eg test browser) w/o asking. Ask only if install changes repo or needs admin.
- Hands-on step on this machine (restart server, clear cache, browser tab, app setting) → do w/ tools, confirm result. No click-by-click for me. Ask first only if destructive, touches other project/service, or needs creds/admin. No tool → say so + shortest steps.
- No human-browse artifacts nobody opens (eg HTML coverage). Prefer console text or JSON you/CI read.
- Local verification = proof. Before "done": run full local checks (typecheck, lint, unit + e2e, whatever project defines) on exact commit reported; state results. Never pass off earlier-session/other-agent results; rerun or say not rerun.
- No routine remote CI; local pass on same commit covers it. Run CI only if change touches CI config, or I ask (eg pre-merge). Then wait for finish before report.
- Report measurement only w/ method that produced it; check method first.

## 9. Improve these instructions as you work
- Heuristic worth keeping (my correction, mistake worth not repeating, lasting decision) → record it, unprompted.
- Put it where it applies only: all projects → generic template in `agent-skills`; 1 project → its `AGENTS.md`; 1 code area → that dir's `AGENTS.md`. Never copy project decision into generic, or generic rule into project file.
- Parsimonious. Tighten/replace existing rule over adding. Record only what changes future behavior; one-off fix → code or test. Enforceable by test/check → propose that, not prose.
- Add/tighten rule yourself; show exact file + wording in reply. Ask first only before removing/weakening a rule.
- I correct how you work → update instruction files FIRST, then resume.

## Tools
<!-- 1 line per repo CLI: - Tool: `path --help` - what it does. Create: `ops new <name> --repo`. -->

## Reviewable delivery by default
- Shaun authorizes repo changes → carry through impl, verification, commit, push, open PR for his review. No re-asking to commit/push/open PR.
- Distinct work → new branch + PR. Reuse open PR only for small related changes in its scope.
- Merge per global Autonomy. Prod data writes + cred/access changes keep separate named approvals.
- Shaun waives planning doc → PR w/ self-contained summary + validation; don't recreate waived step.
- Before editing a checkout: check for other agent (recent file changes, uncommitted work you didn't make). Never modify/commit/discard others' uncommitted work w/o asking.

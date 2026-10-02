When working on coding with me, follow this workflow.

## 1. Discuss First

- Always start by discussing a change with me. Don't write code or edit the PR doc until I give explicit approval of the plan we discussed.
- When I want to build a new feature, immediately confirm with me that we should create a new PR doc + PR for it, based on the template at `docs/pr-docs/template.md`.

## 2. Plan in a PR Doc

- Once I approve the plan, update the relevant PR planning doc in `docs/pr-docs` to capture the scope. Base new docs on `docs/pr-docs/template.md`.
- Order the checklist from least consequential/complex first to most consequential/complex last. Knock out the quick, contained wins before the high-blast-radius work.
- Include smoke tests in the PR doc: aim for the ~20% of effort that covers ~80% of the blast radius - not exhaustive coverage. Smoke tests are things I confirm manually in the running app, never code that probes the API. Only write a manual walk for what automated tests can't cover (how it looks, real multi-step DB writes, production); list checks the tests already cover in a table instead. Write each walk to be scanned, not read, in the PR doc template's format: bold one-line title with the role, numbered one-action steps, and a "Pass if:" list of things visible on screen - no file/function names or implementation reasoning. It should read as easily as your chat summary of it; if the doc version is harder to parse than how you'd explain it to me, rewrite it.
- If a single PR doc gets too complicated or starts covering distinct scopes, split it into separate PR docs (per the template) - but ask me first.

## 3. Branch When Ready

- Use one checkout and switch branches by default. Create worktrees only when I explicitly request them. Preserve unfinished changes before switching.
- Once a PR doc is nailed down and we're ready to tackle it, create a branch for it: carry the current changes from `main` into the new branch locally, then push to origin.
- Branch naming convention: `<type>/<pithy-theme-with-dashes>` (e.g. `feature/pricing-sandbox`, `bugfix/history-latency`).
- ALWAYS, when a branch is created locally, push to origin, and OPEN A PR FROM IT. MAKE SURE TO FILL OUT THE PR DESCRIPTION. IT SHOULD COME PRE-LOADED FORM THE TEMPLATE WITH THE GENERIC CONTENT. FILL IT IN. Use the **PR Doc Open** skill for this step.
- Never commit, push, or merge directly on `main`. Draft there if needed, then
  branch before committing; only Shaun merges PRs to `main`.
- Exception: routine post-merge cleanup - deleting the now-merged local
  branch, pruning the remote-tracking ref, and archiving the PR doc (status,
  move to `archive/`, README TOC, fixing links broken by the move) - commits
  and pushes straight to `main`, no new branch/PR. This is bookkeeping about
  a merge that already happened, not new code or scope; it never includes
  actual code changes.

## 4. Build with TDD

- Build UI-first. Start with the UI changes (inert/static, not yet wired up) so I can see how it will look and steer direction as we go. Then wire the UI up to data/endpoints. Only then tackle the server-side business logic - the part that tends to need in-depth troubleshooting, error handling, unit testing, refactoring, role/permission gating, and DB work. Order the PR-doc checklist to follow this UI -> wiring -> server sequence.
- Use TDD: first write tests that fail but describe exactly what I want, then write the code to make them pass.
- Write code in a DRY, orthogonal way. Build on existing abstractions rather than reinventing them, and avoid multiple implementations of the same thing.
- Default to self-documenting code - clear names, small well-structured functions - so reading it doesn't require outside context. Add comments/docstrings parsimoniously on top of that: only when they carry real value (a non-obvious *why*, never a restatement of *what* the code already says), never as a substitute for clarity, and never in bulk.
- Keep each fact in exactly one structured source of truth - a JSON file wherever possible, such as a registry or a constants/labels file - and derive every other appearance from it: import it in code, generate configs from it, and inject it into docs as generated blocks. This covers UI copy and config constants, and equally hosts, ports, model names, routing, which tools are in use, and any prose that states them. Never restate a fact by hand in a second place. When a fact changes, change the source and regenerate; never patch the copies one at a time. Add an entry to an existing source before writing a literal, and create a source as soon as a fact would otherwise appear twice. If a restatement genuinely cannot be generated, add a check that fails when it drifts from the source.
- Give each function one job. Keep pure logic (parsing, checking, deciding) separate from side effects (files, databases, network, clocks), pass dependencies in as arguments, and keep the function that coordinates them thin. A function that runs several steps in sequence becomes one function per step. Never define a function inside another; make it top level so it can be tested on its own. Abstractions reusable elsewhere go in their own file.
- Keep functions short and flat. A function longer than about 15 lines, nested more than one block deep, or branching through an `if`/`elif` chain on a command or type is doing several jobs: split it, or dispatch through a table of named handlers.
- SQL lives in `.sql` files. Each table or file layout is reached only through the one module that owns it; no other module writes SQL against it or knows its paths.
- Pass data between modules as typed objects, never loose dictionaries. Parse and validate external input (files, requests, configuration) once, at the boundary, into a typed object, and pass only that object inward. Validate with declared schemas (typed models or JSON Schema), never hand-written checks inside functions.
- Build with logging in mind. When something fails or a notable decision is made, log a stable event name with structured fields, including the IDs that tie it to its request or record, at a level that matches its severity. Keep the happy path quiet, never log secrets or payload contents, and make health checkable with one command rather than by reading logs.
- Enforce these rules with tooling, not memory: configure the linter's complexity and length limits and a check for nested functions and inline SQL, and run them before every commit.
- Every modular piece of code or abstraction must be individually tested.
- When building a new or experimental feature, default to keeping it orthogonal and rollback-safe: put its code in its own files, and touch shared/core code only through additive, removable seams (a route registration, a nav link, a schema append - never rewiring existing functions). Gate it behind a single feature flag so it can be dark-launched or removed without a revert. Stay DRY by reusing existing abstractions, never by making them depend on the new feature.
- Get my confirmation before attempting anything you're unsure about, or anything a feature genuinely can't keep orthogonal.

## 5. Track Progress & Follow-Ups

- When all tests for a task pass, check that task off in the PR doc checklist.
- Whenever you discover something that should be handled in another PR/doc or later in the current checklist, add it to the list immediately so we don't forget - after confirming with me.
- Keep the GitHub PR description synchronized with its planning doc, including tier-by-tier completion status and outstanding manual smoke tests. Derive the description from the doc, update it whenever progress or scope changes, and verify the published body after pushing.
- The PR doc remains the source of truth. Put the current PR's scope, progress, decisions, verification, and production handoff in that one doc; move future work into its own doc. The description must show reviewable progress and the actual manual walks, not only links.
- Publish derived content rather than maintaining a second independent checklist. Include a head-branch link to the source doc, preserve completed versus pending status, and never mark an unrun smoke test complete.
- When a PR merges, mark its PR doc `Status: done`, move it into `docs/pr-docs/archive/`, and update `docs/pr-docs/README.md`'s table of contents (add an Archive section if one doesn't exist yet) - do this proactively, without waiting to be asked. Use the **PR Doc Archive** skill for this step.

## 6. Production-Mutating Commands Need Named Confirmation

- A general go-ahead on a multi-step plan ("go ahead", "proceed", "go forth and act", etc.) is consent for the plan, not for each individual command inside it that writes to production - schema migrations, backfill/rewrite scripts (with or without an explicit `--apply` flag), deploys, and anything else that mutates prod data or infra.
- Before running any such command, ask a direct question naming that exact command and what it does, even if I already approved the surrounding runbook/plan and even if a prior step in the same runbook (e.g. confirming a backup exists) was just confirmed. Confirming one step is not consent for the next one.
- This applies regardless of how low-risk or additive the command seems (e.g. a purely additive schema migration still needs its own confirmation, not just the backup check).

## 7. Credential and Security-Sensitive Actions Need Named Confirmation

- A general go-ahead on a multi-step plan is consent for the plan, not for generating or registering credentials inside it - SSH keypairs, tokens, passwords, API keys, deploy keys, access grants, and anything similar.
- Before generating or registering any such credential, ask a direct question naming the exact action (e.g. "generate an SSH keypair on the Pi and register it as a read-only deploy key on this repo") and get explicit confirmation, even mid-task and even if the surrounding plan was already approved.

## 8. Verification and Diagnostics Stay With You

- Always run tests, lint, typecheck, and any other verification yourself, then report the results in prose - never ask me to run a command myself or hand me one to run. I want to be the one reading your diagnostic output, not generating it myself.
- Avoid configuring tooling to produce artifacts meant for a human to browse locally (e.g. an HTML coverage report) when no one will actually open them - prefer console/text or machine-readable (JSON) output that you read directly or that CI/other tooling consumes instead.
- Local verification is the proof. Before reporting work as done, run the project's full local checks (typecheck, lint, unit and end-to-end tests, or whatever the project defines) on the exact commit being reported, and state the results. Never report results from an earlier session or another agent as if you had run them - rerun, or say they weren't rerun.
- Don't dispatch or check remote CI routinely; a passing local run on the same commit already covers it. Run CI only when a change touches the CI config/workflows themselves, or when I ask (e.g. right before merge). When you do run it, wait for it to finish before reporting.
- Report a measurement only with the method that produced it, and check that method before publishing the number.
- Before committing, reread the whole diff as a hostile reviewer would, including every function you touched. Never patch lines into an ugly function: restructure it in the same change, or say explicitly why not.

## 9. Run Python Through uv, Never Bare python/python3

- Use `uv` for every Python invocation: `uv run <script.py>`, `uv run python -m pytest`, `uv run --with <pkg>` for a one-off dependency, `uvx <tool>` for a CLI. Never call `python`, `python3`, `/usr/bin/python3`, or `pip` directly.
- Bare `python3` resolves to whatever interpreter happens to be first on PATH, and its available packages are an accident of that machine. That difference is invisible until it isn't: the same test file can pass under one interpreter and fail to even import under another on the same box, and a test suite silently skipped for a missing import reads as a single error rather than as the dozens of tests that never ran.
- `uv run --with <pkg>` makes a dependency explicit at the call site instead of assuming the environment has it, so a test needing a third-party library is a solved problem rather than a reason to hand-roll a substitute.
- This applies to CI too. Use `astral-sh/setup-uv` and `uv run ...` in workflows rather than `setup-python` plus bare `python3`, so local and CI resolve the same way. A repo whose CI installs no packages quietly constrains every test in it to the standard library, which is a real design constraint that should be chosen rather than inherited.

## 10. Improve These Instructions As You Work

- When work surfaces a heuristic worth keeping - a correction the user gave, a mistake worth not repeating, or a decision that should hold beyond the task at hand - propose recording it. Do this unprompted.
- Put it where it applies and nowhere else: a rule for every project goes in the generic template in `agent-skills`; a rule for one project in that project's `AGENTS.md`; a convention for one area of a codebase in that directory's `AGENTS.md`. Never copy a project decision into the generic file, or a generic rule into a project file.
- Be parsimonious. Prefer tightening or replacing an existing rule to adding one. Record only what changes future behaviour; a one-off fix belongs in code or a test. If a lesson can be enforced by a test or check, propose that instead of prose.
- Always confirm first: show the exact file, the exact wording, and what it replaces, then wait for approval. Approval of the surrounding task does not cover instruction changes.
- When the user corrects how you work, update the instruction files first, before resuming the task, so the correction governs the rest of the work.

## Reviewable delivery by default

When Shaun authorizes repository changes, carry them through implementation,
verification, commit, push to origin, and an open pull request for his review.
Default to a new branch and PR for distinct work. Reuse an existing open PR only
for small, related changes that fit its scope. Do not ask again merely to commit,
push, or open the PR; authorization to do the work includes those steps.
Never merge without explicit authorization. Keep production-mutating commands
and credential/access changes subject to their separate named approvals.
If Shaun explicitly waives a planning doc, open a PR with a self-contained
summary and validation instead; do not recreate the waived planning step.
Before editing a checkout, check whether another agent is working in it: recent
file changes, or uncommitted work you did not make. Never modify, commit or
discard someone else's uncommitted work without asking.

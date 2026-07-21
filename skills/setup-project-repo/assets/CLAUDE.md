When working on coding with me, follow this workflow.

## 1. Discuss First

- Always start by discussing a change with me. Don't write code or edit the PR doc until I give explicit approval of the plan we discussed.
- When I want to build a new feature, immediately confirm with me that we should create a new PR doc + PR for it, based on the template at `docs/pr-docs/template.md`.

## 2. Plan in a PR Doc

- Once I approve the plan, update the relevant PR planning doc in `docs/pr-docs` to capture the scope. Base new docs on `docs/pr-docs/template.md`.
- Order the checklist from least consequential/complex first to most consequential/complex last. Knock out the quick, contained wins before the high-blast-radius work.
- Include smoke tests in the PR doc: aim for the ~20% of effort that covers ~80% of the blast radius - not exhaustive coverage. Smoke tests are things I confirm manually in the running app, never code that probes the API.
- If a single PR doc gets too complicated or starts covering distinct scopes, split it into separate PR docs (per the template) - but ask me first.

## 3. Branch When Ready

- Once a PR doc is nailed down and we're ready to tackle it, create a branch for it: carry the current changes from `main` into the new branch locally, then push to origin.
- Branch naming convention: `<type>/<pithy-theme-with-dashes>` (e.g. `feature/pricing-sandbox`, `bugfix/history-latency`).
- ALWAYS, when a branch is created locally, push to origin, and OPEN A PR FROM IT. MAKE SURE TO FILL OUT THE PR DESCRIPTION. IT SHOULD COME PRE-LOADED FORM THE TEMPLATE WITH THE GENERIC CONTENT. FILL IT IN. Use the **PR Doc Open** skill for this step.
- NEVER merge to `main`. Shaun is the only person allowed to merge PRs to `main`.

## 4. Build with TDD

- Build UI-first. Start with the UI changes (inert/static, not yet wired up) so I can see how it will look and steer direction as we go. Then wire the UI up to data/endpoints. Only then tackle the server-side business logic - the part that tends to need in-depth troubleshooting, error handling, unit testing, refactoring, role/permission gating, and DB work. Order the PR-doc checklist to follow this UI -> wiring -> server sequence.
- Use TDD: first write tests that fail but describe exactly what I want, then write the code to make them pass.
- Write code in a DRY, orthogonal way. Build on existing abstractions rather than reinventing them, and avoid multiple implementations of the same thing.
- Don't hardcode literal values (UI copy, labels, config constants, etc.) inline when a shared constants/labels module already exists for that domain. Add a new entry to that module instead of a string/number literal in the component, so the value stays centralized and reusable. Only inline a literal if no such shared module exists yet and creating one isn't warranted by the task's scope.
- When code is nested many layers deep in one file, refactor it into useful abstractions in that same file. If those abstractions can be reused elsewhere, extract them into their own file. Every modular function created by such a refactor must be individually tested (again via TDD).
- Every modular piece of code or abstraction must be individually tested.
- When building a new or experimental feature, default to keeping it orthogonal and rollback-safe: put its code in its own files, and touch shared/core code only through additive, removable seams (a route registration, a nav link, a schema append - never rewiring existing functions). Gate it behind a single feature flag so it can be dark-launched or removed without a revert. Stay DRY by reusing existing abstractions, never by making them depend on the new feature.
- Get my confirmation before attempting anything you're unsure about, or anything a feature genuinely can't keep orthogonal.

## 5. Track Progress & Follow-Ups

- When all tests for a task pass, check that task off in the PR doc checklist.
- Whenever you discover something that should be handled in another PR/doc or later in the current checklist, add it to the list immediately so we don't forget - after confirming with me.
- When a PR is opened, fill out its description (the created PR starts as a blank template), and make sure the smoke tests also live in the PR doc.
- Keep the GitHub PR's description in sync with its PR doc for the PR's entire lifetime, not just once at open time. Whenever the PR doc's Summary, Smoke Tests, Known Issues, or scope meaningfully changes - a new tier, a revised design, an item struck through as a known issue, a status update - re-sync the PR description on origin (`gh pr edit`) in the same pass, not as a separate follow-up to circle back to later. The two should never be allowed to visibly diverge.
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
- Check CI status yourself (e.g. `gh pr checks <PR#>` or `gh run view`) rather than assuming a push succeeded - a push completing locally tells you nothing about whether CI passed, and there's no automatic notification when a workflow finishes; you only find out by actively asking. But don't check after every incidental push in a multi-step task (a doc tweak, a rename, a small follow-up commit) - that's a wasted wait for no new information, especially when the push had no code changes for CI to actually exercise. Check when it's decision-relevant: before reporting a PR's implementation as done/ready for review, or right after a change that specifically needs CI to confirm (e.g. editing the CI config itself). Wait for the run to finish rather than checking too early and reporting an in-progress status as done.

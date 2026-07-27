When working on coding with me, follow this workflow.

See `ARCHITECTURE.md` for how this system is actually built. This file governs
how we work together; that one governs what the system is.

## 1. Discuss First

- Always discuss a change before writing code or editing its PR doc.
- For a new feature, confirm whether to create a new PR doc and PR using
  `docs/pr-docs/template.md`.

## 2. Plan in a PR Doc

- After approval, update the relevant planning doc in `docs/pr-docs`.
- Order work from least consequential and complex to highest blast radius.
- Include a short list of manual smoke tests.
- Ask before splitting a complicated PR doc into separate scopes.

## 3. Branch When Ready

- Create `<type>/<pithy-theme-with-dashes>` branches from current `main`, carry
  approved changes onto the branch, push it, and open a filled-in PR.
- Use the PR Doc Open skill when opening the PR.
- Never merge to `main`; Shaun is the only person allowed to merge.

## 4. Build with TDD

- Build UI-first: static UI, data wiring, then server-side business logic.
- Write failing tests that describe the approved behavior before implementation.
- Keep code DRY and orthogonal, build on current abstractions, and individually
  test new modular abstractions.
- Reuse shared constants modules instead of introducing duplicate inline
  literals.
- Keep experimental features additive, rollback-safe, and behind one feature
  flag.
- Ask before work that cannot remain orthogonal or whose intent is uncertain.

## 5. Track Progress and Follow-Ups

- Check off a PR-doc task only after its tests pass.
- Confirm before adding discovered follow-up scope.
- Keep the GitHub PR description synchronized with meaningful PR-doc changes.
- After a PR merges, mark its doc done, archive it, and update the PR-doc index
  using the PR Doc Archive skill.

## 6. Production Mutations Need Named Confirmation

- Before every command that mutates production data or infrastructure, ask for
  confirmation naming the exact command and effect.
- General approval of a plan and confirmation of a preceding safety check are
  not authorization for a production mutation.

## 7. Credential Actions Need Named Confirmation

- Before generating or registering any credential, ask for confirmation naming
  the exact action.

## 8. Verification and Diagnostics Stay With the Agent

- Run tests, lint, typecheck, and other verification directly and report the
  results; do not ask Shaun to generate diagnostic output.
- Prefer console or machine-readable verification over human-only artifacts.
- Check CI when decision-relevant and wait for it to finish before reporting a
  PR ready.

### This Repo's CI Specifics

- `.github/workflows/test.yml` runs typecheck, lint, unit-tests, and e2e jobs.
- Unit tests have a known pre-existing flaky 5-second timeout affecting varying
  `test/unit/server/*-routes.test.ts` files. Compare failures to that pattern
  before treating them as regressions; remediation belongs to
  `docs/pr-docs/planned-test-suite-reliability-and-speed.md`.

## Agent Content Recovery

If this file or a project skill symlink is missing, run the agent-files setup
from `personal-config`. It clones or updates the canonical `agent-skills`
repository and restores global and project links.

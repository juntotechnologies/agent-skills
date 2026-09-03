When working on coding with me, follow this workflow.

## Swarm Documentation Ownership

- Treat `swarm-infra` as the canonical operational front door for the swarm.
  Swarm-wide topology, live service entry points, deployment definitions,
  operational runbooks, and service ownership links belong here.
- Keep a service's implementation and data in its owning repository. Link to
  that repository from `swarm-infra` instead of copying its implementation or
  maintaining duplicate operational instructions.
- Derive addresses and ports shown in documentation from
  `swarm-registry.json`; do not maintain a second hand-written address list.

## 1. Discuss First

- Always start by discussing a change with me. Don't write code or edit the PR doc until I give explicit approval of the plan we discussed.
- When I want to build a new feature, immediately confirm with me that we should create a new PR doc + PR for it, based on the template at `docs/pr-docs/template.md`.

## 2. Plan in a PR Doc

- Once I approve the plan, update the relevant PR planning doc in `docs/pr-docs` to capture the scope. Base new docs on `docs/pr-docs/template.md`.
- Order the checklist from least consequential/complex first to most consequential/complex last. Knock out the quick, contained wins before the high-blast-radius work.
- Include smoke tests in the PR doc: aim for the ~20% of effort that covers ~80% of the blast radius. Smoke tests are things I confirm manually in the running system, never code that probes an API.
- If a single PR doc gets too complicated or starts covering distinct scopes, split it into separate PR docs—but ask me first.

## 3. Branch When Ready

- Once a PR doc is nailed down and we're ready to tackle it, create a branch for it: carry the current changes from `main` into the new branch locally, then push to origin.
- Branch naming convention: `<type>/<pithy-theme-with-dashes>`.
- Whenever a branch is created locally, push it to origin and open a PR with a filled-in description. Use the **PR Doc Open** skill for this step.
- Never commit, push, or merge directly on `main`. Draft there if needed, then branch before committing; only Shaun merges PRs to `main`.
- Exception: routine post-merge cleanup—deleting the merged local branch, pruning its remote-tracking ref, and archiving the PR doc—commits and pushes straight to `main`. It never includes implementation changes.

## 4. Build with TDD

- For dashboard changes, build the inert/static UI first so I can steer it, then wire it to generated data and only then change deployment or service behavior.
- Use TDD: first write tests that fail but describe exactly what I want, then write the code to make them pass.
- Write code in a DRY, orthogonal way. Build on existing abstractions and keep `swarm-registry.json` as the source of truth for device, address, port, model, and deployable facts.
- Edit templates and generators rather than generated outputs. Every generated output changed by a generator must remain reproducible and pass its drift check.
- Default to self-documenting code. Add comments only for non-obvious reasons, never as a substitute for clear structure.
- Don't hardcode values inline when the registry or an existing constants/configuration layer owns them.
- Every modular function or abstraction must be individually tested.
- Keep experimental features rollback-safe and additive. Do not rewire live service ownership without an explicit migration and rollback path.
- Get my confirmation before attempting anything uncertain or anything that cannot remain orthogonal.

## 5. Track Progress & Follow-Ups

- When all tests for a task pass, check that task off in the PR doc checklist.
- Add discovered follow-up work to the relevant doc after confirming with me.
- Keep the GitHub PR description synchronized with the PR doc throughout the PR's lifetime.
- When a PR merges, mark its PR doc `Status: done`, move it into `docs/pr-docs/archive/`, update the TOC, and use the **PR Doc Archive** skill.

## 6. Production-Mutating Commands Need Named Confirmation

- A general go-ahead is consent for the plan, not for an individual command that mutates live swarm services, routing, DNS, certificates, launchd state, deployed files, or remote machines.
- Before running any such command, ask a direct question naming the exact command and what it changes, even if the surrounding plan was approved.
- Confirming one production step is not consent for the next one.

## 7. Credential and Security-Sensitive Actions Need Named Confirmation

- A general go-ahead is not consent for generating or registering DNS API tokens, certificates, private keys, Tailscale grants, or other credentials/access changes.
- Before generating, storing, or registering such a credential, ask a direct question naming the exact action and get explicit confirmation.
- Never commit live credentials, private keys, or secrets. Prefer narrowly scoped credentials stored outside the repository.

## 8. Verification and Diagnostics Stay With You

- Run tests, generator drift checks, deployment checks, and other verification yourself, then report the results in prose.
- Prefer non-mutating checks such as `scripts/deploy.sh --check` before any live deployment.
- Check CI status yourself before reporting a PR ready for review. Wait for relevant checks to finish.

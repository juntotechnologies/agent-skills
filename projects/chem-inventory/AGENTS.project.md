## This Project: chem-inventory

See `ARCHITECTURE.md` for how this system is actually built (components, data flow, environments). This doc governs how we work together; that one governs what the system is.

### CI Specifics

- CI (`.github/workflows/test.yml`) is `workflow_dispatch`-only - it never runs on push - and runs as 4 parallel jobs: typecheck, lint, unit-tests, e2e. Locally: `npm run check`, `npm run lint`, `npm test`, `npm run test:e2e`.
- The unit-tests job has a known, pre-existing flaky failure: a different `test/unit/server/*-routes.test.ts` file times out (`Test timed out in 5000ms`) on roughly every other run, unrelated to whatever change is actually in flight. The same timeout can appear locally. Before treating a red run as a real regression, check whether it matches this pattern (a different file each time, same timeout symptom, on an unrelated server route) rather than assuming the change broke something. Root-causing this (probably resource contention across parallel test workers) is tracked in [planned-test-suite-reliability-and-speed.md](docs/pr-docs/planned-test-suite-reliability-and-speed.md), not something to chase ad hoc.

### Agent Content Recovery

If this file or a project skill symlink is missing, run the agent-files setup
from `personal-config`. It clones or updates the canonical `agent-skills`
repository and restores global and project links.

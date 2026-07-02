# PR Checklist

Use this before merging any PR.

## Scope

- [ ] The PR has one clear purpose.
- [ ] Follow-up work is moved to issues or `docs/pr-docs`, not hidden in review comments.
- [ ] The PR description has a one-line summary plus bullets for meaningful changes.
- [ ] Related issues are linked, closed, or explicitly marked as follow-up.

## Code Quality

- [ ] Changed behavior has focused unit or integration tests.
- [ ] Concerns are reasonably separated.
- [ ] Shared truth is reused instead of duplicating policy, labels, or validation.
- [ ] No dead code, debug code, stale copy, or commented-out leftovers.
- [ ] Shell scripts are idempotent where setup steps may be safely re-run.
- [ ] Symlink, path, and backup behavior is covered when changed.

## Required Checks

- [ ] `scripts/validate_config.sh`
- [ ] `tests/test_quickstart.sh`
- [ ] `tests/test_macos_preferences.sh`
- [ ] `tests/test_obsidian.sh`
- [ ] `tests/test_repo_setup_contract.sh`
- [ ] GitHub CI is green.

## Conditional Checks

- [ ] If setup commands changed: test a clean/re-run path or document the manual verification.
- [ ] If Homebrew packages changed: `brew bundle check --file Brewfile` behavior is understood.
- [ ] If symlinks changed: `metadata.json` and `scripts/steps/link_config.sh` agree.
- [ ] If macOS preferences changed: defaults writes are scoped and repeatable.
- [ ] If Obsidian automation changed: plugin/workflow install behavior is checked.
- [ ] If secrets or private paths changed: no live credentials are committed.

## Mac Setup Smoke Tests

- [ ] `scripts/setup_mac.sh` reaches the expected guided prompt sequence.
- [ ] `scripts/steps/link_config.sh` can be re-run without replacing correct symlinks.
- [ ] `scripts/validate_config.sh` passes from the repo root.
- [ ] The changed workflow is tested once from a normal interactive shell when practical.

## Merge Readiness

- [ ] PR branch is up to date enough for a clean merge.
- [ ] Risky or irreversible changes have a rollback note.
- [ ] Machine-specific or destructive setup changes are called out clearly.

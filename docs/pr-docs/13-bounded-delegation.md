# PR 13: Reliable local-only delegation

Status: in-scope work complete — ready for review

Branch: `bugfix/bounded-delegation`

## Goal

Keep delegated inference on Shaun's own Mac mini and DGX Spark. September 19 approval replaces the earlier cloud-delegation scope: remove the Claude adapter and routing; external services/APIs are deferred until explicitly requested.

## Implementation Checklist

- [x] Preserve bounded local answers with thinking disabled and two-worker default fan-out.
- [x] Add failing regressions for rejection of the cloud command, external endpoint URLs, proxy/redirect escape, and explicit local failure without fallback.
- [x] Remove the Claude adapter and skill instructions; restrict transport to loopback/private/tailnet IP addresses without redirects or environment proxies.
- [x] Update the active skill through the existing source link and verify installation.
- [x] Run unit/installer tests and harmless local inference checks, then sync the PR description.

## Smoke Tests

No new user UI or live-service cutover is introduced. Codex verifies real bounded local requests and the installed helper's cloud-command rejection; no cloud inference is used for validation.

## Product Decisions

Local delegation supports read-only summaries, extraction and bounded review. Failed local requests produce errors, never a hosted-model fallback. The supervising coding agent still owns edits and final verification; this skill does not make that surrounding agent local. Endpoint restrictions protect this helper's outbound requests; they do not audit how the configured servers themselves perform inference.

## Scope and Non-Goals

Existing local delegation helper, skill instructions and tests. No external API integration, provider authentication changes, new services or model-license audit. External integrations remain a future explicit choice, not planned implementation in this PR.

## Rollback

Restore a reviewed local-only helper revision if needed; do not restore the retired cloud-routing adapter as a fallback.

## Validation

- Observed failing regressions before implementation: the old cloud command was accepted and external URLs reached the mocked transport.
- All 18 Python tests pass, including a real loopback HTTP redirect refusal and environment-proxy suppression. Both installer shell suites pass.
- Harmless live Mac inference returned a bounded answer; Spark fan-out with Mac synthesis returned the expected arithmetic results using the two-worker default. No hosted-model inference was invoked.
- Ran the standard installer without Claude compatibility mode. The installed local-model-delegation symlink resolves to this revised source. Installed CLI help exposes only `ask` and `fanout`; the removed `claude` command exits with an argument error.
- This repository has no GitHub Actions workflow for these suites; local execution is the test evidence. Check the current PR's available security check separately before merge.

External services/APIs remain outside this PR. The address restrictions are an outbound helper policy, not a model-license audit or proof that all software on the tailnet is local/open source.

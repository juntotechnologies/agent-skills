# PR <number or short title>: <Human-Readable Title>

<!--
Template for pr-docs. Copy this file to either:
  - docs/pr-docs/<PR#>-<slug>.md        (active/underway PR)
  - docs/pr-docs/planned-<slug>.md      (not yet started)
Delete the HTML comments once filled in. After a PR is closed, move its
numbered doc into docs/pr-docs/archive/ and update README.md.
-->

Status: <planned | underway | in-scope work complete | done> <(add a short qualifier if scope was cut/moved)>

Branch: `<type/short-slug>`

## Goal

<One short paragraph: what this change owns and the user-visible outcome. If this
PR was split out of a larger effort, say why it stands alone.>

## Context

<Optional. Prior PRs this builds on, the current shape of the relevant code, and
the specific gap this closes. Reference concrete files/functions where useful,
e.g. `server/services/transaction-service.ts`. Delete if not needed.>

## Implementation Checklist

Ordered least -> most consequential/complex (per CLAUDE.md): quick, contained wins
first; schema-touching, cross-cutting, or high-blast-radius work last. Group into
tiers when the list is long.

<!-- Checkbox legend: [ ] not started / [x] done / [~] deferred/moved (strike through with ~~...~~ and link to where it went). Follow TDD: each item pairs a behavior with its test. -->

### Tier 1 - Quick wins (low risk, contained)

- [ ] <task> <brief note on approach / decision>
- [ ] <test that fails first and describes the desired behavior>

### Tier 2 - <name>

- [ ] <task>
- [ ] <test>

### Tier N - <most consequential / schema / cross-cutting>

- [ ] <task>
- [ ] <test>

## Smoke Tests

Per CLAUDE.md #9: 20% effort for 80% blast-radius coverage. These are **manual**
checks the user performs in the running app, not scripted API probes. Keep the
list short and focused on the paths this PR touches.

- [ ] <user action -> expected result>
- [ ] <user action -> expected result>

## Product Decisions

- <Decision and the reasoning behind it, so future readers don't relitigate it.>

## Scope

- <Issues/requirements this resolves, e.g. "Resolve issue #NNN: ...">
- <Explicitly deferred/moved items, with a link to where they went.>

## Non-Goals

- <What this PR intentionally does not do.>

## Related Docs

- [<PR / planned doc it builds on or hands off to>](./<path>.md)

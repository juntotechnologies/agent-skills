# PR 64: a recommended "yes" is never asked

Status: underway

Branch: `feature/rec-yes-no-ask`

## Goal

Slip, 2026-11-03: agent ended a reply with 4 Left rows whose rec was "yes" (merge a green PR, back up before an upgrade) and waited. A repo's "named confirmation" line outranked the global standing OK. Shaun: the goal is hands-off; obvious-rec questions must not be asked.

Rule text (source `rules/rules.json`, generated into `~/AGENTS.md`):

- `row-rec-yes-do-it`: rec yes -> do it, never ask; only stop-list items get asked, tagged `[stop: <item>]`.
- Standing OK also beats repo "named confirmation" lines; `ops ship` refuses red-zone PRs; run the repo health cmd after.

## Implementation Checklist

### Tier 1 - Rule text

- [x] Both rules edited in `rules/rules.json`; `global/AGENTS.md` regenerated (`gen_rules.py check` exit 0)

### Tier 2 - Gate

- [ ] Enforcer `ops left-check` (Stop hook; personal-config) blocks a reply whose Left row has rec yes and no `[stop: ...]` tag. Lands in its own PR; this PR then sets the rule's `enforcer`.

## Smoke Tests

Rule text only; no manual walk.

## Product Decisions

- The stop list stays Shaun's: money, creds/access, prod data writes, messages in his name, destructive without backup, patient/private data, medical/regulatory claims, another agent's uncommitted work, facts only he knows.

## Scope

- Prose + generated file.

## Non-Goals

- Per-repo `AGENTS.md` copies of the named-confirmation text (the global line outranks them).

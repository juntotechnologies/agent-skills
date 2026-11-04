# PR 61: Hosts and addresses typed into code are a fault

Status: underway

Branch: `feature/fact-literal-rule`

## Goal

Checker rule `fact-literal`: a tailnet IP, private LAN IP or `*.ts.net` name typed into a code file fails the write, commit, push and CI gates. Facts come from the registry.

## Context

Rule `north-star-literals` (PR 59) says literals belong in registries. This is its first enforcer. A full-repo scan found real cases: `PO-generator` Django settings hard-code one tailnet IP five times; `swarm-infra/scripts/doctor.sh` hard-codes one.

## Implementation Checklist

### Tier 1 - Quick wins

- [ ] Tests first: addresses and `.ts.net` names fault in py, js, ts, sh; loopback, `0.0.0.0`, versions, look-alikes, CIDR constants, tests, json, yaml and markdown do not; the rule runs through `check.text_faults`
- [ ] `checker/fact_literals.json`: suffixes + patterns (one data file, like `uv_only.json`)
- [ ] `textrules.fact_literal_faults`; wired in `check.file_text_faults`; `fact-literal` in `model.RULES`
- [ ] Registry rule `no-fact-literals` (enforcer = this rule); `gen_rules.py build`
- [ ] Full-repo scan of the repos: 1 hit in swarm-infra, 7 in PO-generator, 0 elsewhere

## Acceptance Coverage

| Requirement | Entry points | Roles and data | Persistence | Verification |
|---|---|---|---|---|
| Typed host literal fails | write hook, commit, push, CI | py js ts sh | none | `tests/test_checker.py` |
| Declared exemptions work | `ops-check.json` `exempt.fact-literal` | any repo | repo file | existing `exempt` tests |

## Smoke Tests

Not applicable: no UI.

## Product Decisions

Test paths, json, yaml and markdown are not read: data files are where facts live. Per-repo exceptions go in `ops-check.json` `exempt`.

## Scope

Hosts and addresses only. Ports, model names and inline dict facts need their own rules, added when a pattern repeats.

## Non-Goals

- Fixing the 8 existing hits (own PRs per repo).

## Rollback

Revert the commit.

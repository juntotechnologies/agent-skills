# PR 40: Add CLI over prose rule

Status: in-scope work complete

Branch: `feature/cli-over-prose`

## Goal

Add one global rule: agents move recurring procedures and exact facts into CLIs by default, without discussion. Instruction files keep a pointer only. New repos get a Tools section.

## Context

Test 2026-11-02: fresh `claude -p` in 2 repos answered that the global file loaded, and 1 replied w/ its Left table. So no new install target. Merge after personal-config `ops` PR, else the rule names a missing command.

## Implementation Checklist

- [x] `global/AGENTS.md`: CLI over prose section
- [x] Template: Tools section, 1-line format
- [x] PR doc skills: point to `ops prdoc`; steps stay as fallback

## Smoke Tests

Not applicable: no UI. Agent ran repo tests.

# PR 42: No retry loops on create cmds

Status: done

Branch: `feature/no-retry-creates`

## Goal

Stop agents retrying create/send cmds blindly: failed call can still leave a result.

## Implementation Checklist

- [x] `global/AGENTS.md` Acting: 1 line

## Smoke Tests

Not applicable: no UI. Repo tests pass.

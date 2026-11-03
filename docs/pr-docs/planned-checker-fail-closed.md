# PR planned: Checker fails closed

Status: planned

Branch: `bugfix/checker-fail-closed`

## Goal

First CI run showed: crashed lint tool passed silently; checker inside repo got linted by repo. Both break determinism.

## Implementation Checklist

- [x] Tool crash → `tool-failed` fault
- [x] CI moves checker out of repo tree before running

## Smoke Tests

Not applicable: no UI. Hub PR 24 CI proves workflow.

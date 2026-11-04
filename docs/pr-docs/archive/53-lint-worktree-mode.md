# PR 53: Checker `--worktree` mode

Status: done

Branch: `feature/lint-worktree-mode`

## Goal

Shaun, 2026-11-03: shared lint must run w/o an agent remembering. Slip: uncommitted swarm-infra code had ~29 faults; the checker only saw staged or committed lines, so nothing could lint at write time.

`check.py --worktree`: uncommitted edits (staged + unstaged) vs HEAD, plus untracked files, all lines. The write-time hook in personal-config (`ops edit-check`) calls it after each agent edit.

## Implementation Checklist

- [x] Test first: unstaged edit + untracked file are linted w/o `git add`; clean tree passes
- [x] `--worktree` flag; `worktree_lines()`; `every_line()` shared w/ `--all`
- [x] Own lint clean on the change (`check.py --worktree --lint-only`)
- [x] Full suite: 90 tests OK

## Known Limits

Needs `HEAD` (repo with 1 commit). Lints every dirty file; callers filter to the file they care about.

## Smoke Tests

Not applicable: no UI. Unit + end-to-end tests in `tests/test_checker.py`.

## Related Docs

- personal-config PR: write-time lint gate (`ops edit-check`, `ops hooks`, pre-push)

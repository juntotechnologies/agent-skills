# Rules system

Each rule: 1 place. Tool can decide it → tool enforces it, prose drops it.

## Where things live

| What | Where |
|---|---|
| All global rules | `rules/rules.json`; query: `ops rules` |
| Prose agents read | `global/AGENTS.md`: generated, only rules w/ no enforcer |
| Project workflow | `skills/setup-project-repo/assets/AGENTS.md`: restates no global rule (test) |
| UI rules | `skills/site-taste/data/principles.json`; map: `docs/ui-system.md` |
| Code checks | `checker/` here: Python, JS + TS, ruff + ESLint presets |
| CI | `.github/workflows/check.yml` here; repos call it |
| CLI + merge gate | `ops` in personal-config: check, rules, adopt, guard, ship |
| Repo-only facts | Repo `AGENTS.md`; repo commands + exemptions: `ops-check.json` |

## Same check, 4 places

| When | What runs | Stops |
|---|---|---|
| Agent tool call | `ops guard` (Claude Code hook) | direct merge, `--no-verify`, bare python, edits to generated files, raw `ssh <registered host> docker\|systemctl` mutations |
| Commit | global git hook: `ops check --staged --lint-only` | bad new lines, any repo here |
| PR | `check / check` CI, public repos | bad lines + failing repo tests |
| Merge | `ops ship` | no pass on head; UI change w/o `ops site-check` |

## Change a rule

1. Edit `rules/rules.json`. Tool can decide it → add to `checker/` + test, set `enforcer`.
2. `scripts/gen_rules.py build`, `scripts/install.sh`.
3. `ops rules --prose` = what's still memory-only.

## New repo

`ops adopt --apply`, merge, `ops adopt --protect --apply`.

## Limits

- Only changed lines checked; old code passes until touched. Audit: `ops check --all --lint-only`.
- A top-of-file comment always passes. Names + clarity stay judgment.
- Guard reads command text; scripts calling python inside aren't seen.
- Repos w/ own `core.hooksPath` skip the git hook. Private repos: no required CI on free plan; hook + `ops ship` only.

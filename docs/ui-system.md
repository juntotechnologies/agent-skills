# UI system

Goal: Shaun doesn't flag UI faults twice. Rules live in files + checks, not context.

| Layer | Where | Cost to context | Stops what |
|---|---|---|---|
| Pointer | `global/AGENTS.md` `## UI`, 2 lines | always loaded | agent not knowing tools exist |
| Rules | `skills/site-taste/data/principles.json` (60); `taste.py rules --area <a>` | ~1.6 KB per area, on demand | forgotten principles |
| Measure | `ops site-check` + `ops/site_audit.js` in personal-config | 0 unless it fails | tight buttons, thin cards, side scroll, page errors, any site |
| Site rules | site's own check (hub: `check:fit`) + CI | 0 | site-specific: one card padding, card fits phone |
| Merge gate | `ops ship` | 0 | UI PR merged w/o pass on its head commit |
| Eyes | `--long` PNGs, 1 per screen; `references/checklist.md` | when reviewing | what numbers can't judge |

## New fault

1. Fix it.
2. Add rule: `data/principles.json`, `taste.py build`.
3. Measurable → add to `site_audit.js` + bad fixture. Mark `check`.
4. Not measurable → `manual`; lands on checklist.

Rules grow; pointer doesn't. Prefer moving `manual` → `check`.

## Limits

- Measures faults, not taste. Tile review stays; a new kind of fault can still get through once.
- Pass doesn't prove URL serves head commit.
- Merge outside `ops ship` skips gate. `--no-ui "<reason>"` skips + logs.
- CI only in repos that add it (hub). `ops ship` is the gate everywhere else.

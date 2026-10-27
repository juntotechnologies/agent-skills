---
name: site-taste
description: Shaun's design rules for websites and app screens, kept as data. Use when you build, restyle or review a public site, landing page, project card or app UI for Junto, ChemInventory, Bench Bridge, shaunporwal.com or a client site. Use before you call a page done. Use when Shaun says a page looks busy, messy, off-center, flat or AI generated.
---

# Site taste

This skill holds the fundamentals: each failure that Shaun's sites already fixed, the rule that prevents it, and the check that enforces it. A site keeps its own choices (colors, type, effects, layout sizes) in its own taste doc.

## Workflow

1. Read `references/principles.md`. Each row has a rule, the failure it prevents, the fix and the check.
2. Read the taste doc of the site you change. `references/sites.md` names that doc and the commands to run.
3. Build. Take every color, size and timing from the site's tokens.
4. Run the site's commands. Walk 360, 390, 430, 820 and 1440 px, in the light and the dark theme.
5. When a new failure appears, add a principle to this skill and a note to the site's taste doc in one change.

## Where a fact lives

| Fact | Home |
| --- | --- |
| A rule that holds for every site | `data/principles.json` |
| Where a site keeps its taste, and which commands check it | `data/sites.json` |
| A site's colors, type, effects and layout sizes | That site's taste doc |
| A rule that holds for one site only | That site's taste doc |

Never edit `references/*.md`. The `build` command writes them from the JSON.

## Commands

Run each from this skill's directory.

| Command | Job |
| --- | --- |
| `uv run scripts/taste.py build` | Write `references/principles.md` and `references/sites.md`. |
| `uv run scripts/taste.py check` | Validate the data. Find stale references. |
| `uv run scripts/taste.py sites` | Compare the registry with the site checkouts on this machine. It checks taste docs, check files, command names and the pointer in `AGENTS.md`. |

`sites` reads the checkouts in `~/GitHub/projects` and `~/GitHub/sites`. Add `--root DIR` for another folder. It skips a site that has no checkout.

## Add or change a principle

1. Edit `data/principles.json`. Use a kebab-case id. Write each sentence of the rule in 20 words or fewer. Write each sentence of `why` and `fix` in 25 words or fewer.
2. Set `enforcement` to `check` only when a file in a site enforces the rule. Name that file under `checks`. Otherwise set `manual`.
3. Name the PR that fixed the failure under `evidence`.
4. Run `build`, then `check`. Open a PR in `agent-skills`.
5. Never copy a rule into a site's `AGENTS.md`. Name this skill there.

## Add a site

Add one object to `data/sites.json`. List its taste docs and its check commands. Add the line "Shared design rules: skill `site-taste`" to its `AGENTS.md`. Run `sites`.

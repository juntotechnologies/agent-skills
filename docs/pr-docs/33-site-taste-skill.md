# PR 33: Site taste skill

Status: underway

Branch: `feature/site-taste-skill`

## Goal

Add the `site-taste` skill. It holds the design rules that Shaun's sites already proved, so no future session loses them. Each rule names the failure it prevents, the fix, the check that enforces it and the PR that proved it. Each site keeps its own evolving taste in its own repository. A drift check compares the two.

## Context

On 2026-10-27 Shaun said the hub, shaunporwal.com and cheminventory.co look right. He asked to distill the decisions so they do not get lost, for example "a wall of text in a card is not acceptable". He asked for no drift between the skill and the sites.

## Decisions

| Question | Decision | Reason |
| --- | --- | --- |
| New repository or skill? | A skill in this repository | The installer already ships skills to every session. A new repository needs a second install path. |
| Where does site-specific taste live? | In each site's own design doc | The taste evolves with the site. The owner repository stays the source. |
| What does the skill hold? | Fundamentals only: failure, rule, fix, check, evidence | A fundamental changes rarely, so it can live in one place. |
| How does the skill stay true? | `taste.py sites` compares the registry with the checkouts | It finds a missing doc, check file or command, and a site that does not name the skill. |
| Which source holds a rule? | `data/principles.json`. The references are generated. | One source for each fact. |
| Is the existing lint scope widened? | No. `ruff.toml` covers the new code only. | The older scripts are out of scope. |

## Implementation Checklist

### Tier 1 - Data and models

- [x] `data/principles.json`: 7 areas and 58 principles, each with a rule, why, fix, enforcement, check files and evidence.
- [x] `data/sites.json`: the five sites, their taste docs and check commands.
- [x] `taste_model.py`: typed models. An unknown key, a missing key or a bad enum value fails at load.

### Tier 2 - Rules and renderers

- [x] `taste_rules.py`: pure checks for ids, references, enforcement, commands and sentence length (20 and 25 words).
- [x] `taste_render.py`: pure renderers for `references/principles.md` and `references/sites.md`.
- [x] Tests for each rule, each renderer and the loader.

### Tier 3 - Site comparison and command

- [x] `taste_sites.py`: compare the registry with the checkouts: taste docs, check files, npm and make commands, the `AGENTS.md` pointer.
- [x] `taste.py`: `build`, `check` and `sites`, dispatched through a table of handlers.
- [x] Tests with temporary checkouts: complete, drifted, pending and absent.

### Tier 4 - Tooling and docs

- [x] `ruff.toml` for the new code: complexity 5, 15 statements, 4 arguments, depth 1.
- [x] `tests/test_site_taste_shape.py`: no nested function and no lambda.
- [x] `SKILL.md`, `README.md` and the PR template name the new commands.
- [x] Add the lessons that the CIT site and Bench Bridge PRs report: 15 new principles and updates to 9 more.
- [x] Point `sites.json` at the taste docs that the CIT site and Bench Bridge PRs add.
- [ ] When CIT site PR 12 and shaunporwal.com PR 11 merge, remove their `pending_pr` flags. `taste.py sites` fails until then.

## Acceptance Coverage

| Requirement | Entry points | Roles and data | Persistence | Verification |
| --- | --- | --- | --- | --- |
| A session finds the rules before it builds a page | `skills/site-taste/SKILL.md` | Any agent | Files in the repository | Smoke test 1 |
| A rule has one source | `data/principles.json` | Maintainer | `references/*.md` are generated | `taste.py check` and the stale-reference test |
| A site and the skill cannot drift unseen | `taste.py sites` | Maintainer with site checkouts | None | Smoke test 2 and the temporary-checkout tests |

## Smoke Tests

Automated checks:

| Check | Command | Result |
| --- | --- | --- |
| Unit tests | `uv run python -m unittest discover -s tests -v` | 69 pass |
| Install tests | `bash tests/test_install.sh` | 8 pass |
| Lint | `ruff check .` | Pass |
| Data and references | `uv run skills/site-taste/scripts/taste.py check` | Pass |

- [ ] **Read the skill before a page change** · as an agent
  1. Start a fresh agent session after `scripts/install.sh`.
  2. Ask it to add a project card to a site.

  **Pass if:**
  - The agent loads `site-taste`.
  - The agent opens `references/principles.md` and the site's taste doc before it builds.

- [ ] **Find drift** · as a maintainer
  1. Run `uv run skills/site-taste/scripts/taste.py sites`.
  2. Rename one check file in a site checkout and run the command again.

  **Pass if:**
  - The first run shows no missing file and no missing command.
  - The second run names the renamed file and exits with code 1.

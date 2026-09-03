---
name: Update Agent Skills
description: Add a new skill, change an existing skill's behavior, or capture a generalizable coding/workflow rule into the right durable place — this repo's canonical AGENTS.md, a specific skill's SKILL.md, or the memory system — with my confirmation, so I don't have to repeat the same guidance in future sessions. Use when I ask to "add a skill", "update agent skills/abilities", "change how a skill works", or when a correction/confirmation in conversation reads as a general rule rather than a one-off fix.
---

## Overview

This skill covers two related jobs that both end up editing the same
source-of-truth repo, `agent-skills` (`git@github.com:juntotechnologies/agent-skills`):

1. **Explicit requests** — "add a skill for X", "update the Y skill",
   "change how agent skills work."
2. **Proactive capture** — noticing that a correction or confirmation in
   conversation generalizes beyond the current task, and proposing it get
   written down so it isn't relearned next session.

Corrections and confirmations that only fix the current line of code are
routine — just fix them. This skill is for the subset that generalizes: a
rule that would apply next time too, in this repo or any repo.

## Step 0 — Recognize a candidate (for proactive capture)

Treat these as signals, not just explicit "remember this" or "add a skill":
- A correction that names a pattern rather than a specific line ("don't
  hardcode X when Y already exists", "always do A before B").
- A confirmation of a non-obvious choice I made ("yes, that's right, keep
  doing it that way").
- Anything phrased as a rule ("we should always...", "never...", "make sure
  going forward...").

Don't treat a one-off bug fix, a task-specific decision, or something already
covered by an existing rule as a candidate.

## Step 1 — Classify where it belongs

Ask: is this (a) a brand-new skill, (b) a change to how an existing skill
behaves, (c) a universal coding/workflow rule that applies in any repo, or
(d) a preference/fact specific to this user or this one project?

| Scope | Destination |
| --- | --- |
| New capability worth its own skill | New `agent-skills/skills/<name>/SKILL.md` |
| Change to an existing skill's behavior | That skill's own `SKILL.md` in `agent-skills/skills/<name>/` |
| Universal coding/workflow rule (any repo, any language) | `agent-skills/skills/setup-project-repo/assets/AGENTS.md` (the canonical template — see that skill's own docs on why it's the source of truth, not a project's local copy) |
| Project-specific instructions or workflow | `agent-skills/projects/<project>/AGENTS.md` or `skills/<name>/SKILL.md` |
| User preference or feedback about how I should work with them | The active harness's supported user-level instruction system |

If it's ambiguous between the canonical AGENTS.md and memory: canonical
AGENTS.md is for rules that hold regardless of who's asking or which project;
memory is for things specific to this user or this codebase's history.

## Step 2 — Confirm before writing

Always propose the change back in one or two sentences and ask for
confirmation before editing anything. Show which destination you picked and
why. Never write to `agent-skills` or a project's `AGENTS.md` silently.

## Step 3 — Write it

- **New skill**: create `agent-skills/skills/<name>/SKILL.md` following the
  structure of existing skills (frontmatter `name`/`description`, then
  `## Overview`, `## Steps`, etc.). Pick a name that matches how I'd
  naturally ask for it later, not just what's technically precise.
- **Existing skill**: edit that skill's `SKILL.md` directly, preserving its
  structure.
- **Canonical AGENTS.md**: edit
  `agent-skills/skills/setup-project-repo/assets/AGENTS.md` directly. This is
  the only canonical copy — do not edit a project's local `AGENTS.md` and
  call it done.
- **Memory**: follow the memory system's own save procedure (frontmatter +
  `MEMORY.md` index entry).

## Step 4 — Make new/changed skills available

Run `scripts/install.sh`. It discovers global skills automatically and links
them into `~/.agents/skills/`. Registered project content under `projects/` is
linked into matching project checkouts. Only when the user explicitly wants
Claude compatibility, pass `--claude-compat`; it creates symlinks from Claude
paths to the Codex surfaces without maintaining duplicate content.

## Step 5 — Propagate generic template changes

Registered projects update immediately through symlinks. Generic repositories
that received copied template files still require the **Setup Project Repo**
skill's sync mode.

## Step 6 — Report

State what was added/changed and where, in one sentence. If nothing was
propagated because we're not inside a project repo right now, say so.

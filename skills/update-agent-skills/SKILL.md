---
name: Update Agent Skills
description: Capture reusable workflow corrections in global skills or instructions, and project-specific lessons in the owning repo. Use when asked to change skills or remember a generalizable working rule.
---

## Ownership

- Reusable global capabilities: edit `agent-skills/skills/<name>/SKILL.md`.
- Generic bootstrap defaults: edit `agent-skills/skills/setup-project-repo/assets/`.
- Project conventions: edit that project's local `AGENTS.md` or scoped directory
  instructions. Project procedures belong in its `.agents/skills/<name>/`.
- Personal defaults: update the harness's supported user instructions (Codex:
  `~/.codex/AGENTS.md`). If also a reusable bootstrap rule, update the template.

Project files are authoritative in their owning repository. Never move them into
`agent-skills`, create external project symlinks, or edit installed global copies
in `~/.agents/skills` as the source of truth. Locate the `agent-skills` checkout
before editing a global skill; its installer copies updates into the user directory.

## Capture and verify

1. Identify a recurring correction or confirmed convention. Fix one-off bugs
   normally; do not turn every task detail into a permanent rule.
2. Check current instructions for an existing rule. Reconcile or shorten it rather
   than append a duplicate. Distinguish accepted decisions from proposals/history.
3. Propose the destination and change before writing, unless the user has already
   explicitly authorized this change or an applicable capture policy. Do not ask
   for the same permission again.
4. Prefer a regression test or automated constraint when the lesson is executable;
   use concise instructions for judgment and skills for repeated procedures.
5. For new skills, follow the Skill Creator workflow. Test changed scripts and
   demonstrate that the new rule/check addresses the original failure.
6. For global skills, run `scripts/install.sh` from `agent-skills`. It synchronizes
   owned copies only and stops on local edits; reconcile conflicts rather than
   deleting user changes. Project skills require no global installation.
7. Commit, push, and open a reviewable PR by default for authorized changes. Use an
   existing PR only for small related work. Respect explicit planning-doc waivers;
   never merge or bypass named production/credential approvals.

Global template changes do not automatically overwrite project instructions.
Use Setup Project Repo's explicit sync workflow to merge requested generic
updates while preserving all project-specific guidance.

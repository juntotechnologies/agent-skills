#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
test_root="$(mktemp -d)"
trap 'rm -rf "$test_root"' EXIT

test_home="$test_root/home"
workspace_root="$test_root/workspace"
project_root="$workspace_root/projects/chem-inventory"
mkdir -p "$test_home" "$project_root"

assert_link() {
  local target="$1"
  local expected_source="$2"

  [[ -L "$target" ]] || {
    echo "Expected symlink: $target" >&2
    exit 1
  }
  [[ "$(readlink "$target")" == "$expected_source" ]] || {
    echo "Expected $target -> $expected_source, got $(readlink "$target")" >&2
    exit 1
  }
  [[ -e "$target" ]] || {
    echo "Expected symlink to resolve: $target" >&2
    exit 1
  }
}

assert_portable_link() {
  local target="$1"
  local expected_source="$2"
  local link_source resolved_source resolved_expected

  [[ -L "$target" ]] || {
    echo "Expected symlink: $target" >&2
    exit 1
  }
  link_source="$(readlink "$target")"
  [[ "$link_source" != /* ]] || {
    echo "Expected relative symlink at $target, got $link_source" >&2
    exit 1
  }
  resolved_source="$(
    cd "$(dirname "$target")/$(dirname "$link_source")"
    printf '%s/%s\n' "$(pwd -P)" "$(basename "$link_source")"
  )"
  resolved_expected="$(
    cd "$(dirname "$expected_source")"
    printf '%s/%s\n' "$(pwd -P)" "$(basename "$expected_source")"
  )"
  [[ "$resolved_source" == "$resolved_expected" ]] || {
    echo "Expected $target to resolve to $resolved_expected, got $resolved_source" >&2
    exit 1
  }
}

run_installer() {
  HOME="$test_home" "$repo_root/scripts/install.sh" \
    --workspace-root "$workspace_root"
}

run_compat_installer() {
  HOME="$compat_home" "$repo_root/scripts/install.sh" \
    --workspace-root "$compat_workspace_root" \
    --claude-compat
}

[[ -f "$repo_root/skills/setup-project-repo/assets/AGENTS.md" ]] || {
  echo "Expected canonical AGENTS.md workflow asset." >&2
  exit 1
}
[[ "$(readlink "$repo_root/AGENTS.md")" == \
  "skills/setup-project-repo/assets/AGENTS.md" ]] || {
  echo "Expected root AGENTS.md to point at the canonical AGENTS.md asset." >&2
  exit 1
}
[[ ! -e "$repo_root/CLAUDE.md" && ! -L "$repo_root/CLAUDE.md" ]] || {
  echo "Default repository layout must not include CLAUDE.md." >&2
  exit 1
}

first_output="$(run_installer)"

for skill_path in "$repo_root"/skills/*/; do
  skill_name="$(basename "$skill_path")"
  assert_link \
    "$test_home/.agents/skills/$skill_name" \
    "${skill_path%/}"
done

[[ ! -e "$test_home/.claude" && ! -L "$test_home/.claude" ]] || {
  echo "Default install unexpectedly created a Claude path." >&2
  exit 1
}

assert_portable_link \
  "$project_root/AGENTS.md" \
  "$repo_root/projects/chem-inventory/AGENTS.md"
assert_portable_link \
  "$project_root/.agents/skills/db-migrations" \
  "$repo_root/projects/chem-inventory/skills/db-migrations"
[[ ! -e "$project_root/CLAUDE.md" && ! -L "$project_root/CLAUDE.md" ]] || {
  echo "Default project install unexpectedly created CLAUDE.md." >&2
  exit 1
}
[[ ! -e "$project_root/.claude" && ! -L "$project_root/.claude" ]] || {
  echo "Default project install unexpectedly created a Claude path." >&2
  exit 1
}

second_output="$(run_installer)"
[[ "$second_output" == *"Already linked"* ]] || {
  echo "Expected idempotent second run to report existing links." >&2
  exit 1
}
[[ "$(find "$test_root" -name '*.backup-*' | wc -l | tr -d ' ')" == "0" ]] || {
  echo "Idempotent install unexpectedly created backups." >&2
  exit 1
}

printf '%s\n' "$first_output" | grep -q "Installed agent skills."

compat_home="$test_root/compat-home"
compat_workspace_root="$test_root/compat-workspace"
compat_project_root="$compat_workspace_root/projects/chem-inventory"
mkdir -p "$compat_home" "$compat_project_root"

compat_first_output="$(run_compat_installer)"
assert_link "$compat_home/.claude/skills" "../.agents/skills"
assert_link "$compat_project_root/CLAUDE.md" "AGENTS.md"
assert_link "$compat_project_root/.claude/skills" "../.agents/skills"

compat_second_output="$(run_compat_installer)"
[[ "$compat_second_output" == *"Already linked"* ]] || {
  echo "Expected idempotent Claude compatibility install." >&2
  exit 1
}
printf '%s\n' "$compat_first_output" | grep -q "Claude compatibility enabled."

conflict_home="$test_root/conflict-home"
mkdir -p "$conflict_home/.agents/skills/pr-doc-open"
printf '%s\n' "keep me" > "$conflict_home/.agents/skills/pr-doc-open/sentinel"
mkdir -p "$conflict_home/.claude/skills"
printf '%s\n' "keep Claude" > "$conflict_home/.claude/skills/sentinel"
HOME="$conflict_home" "$repo_root/scripts/install.sh" \
  --workspace-root "$test_root/missing-workspace" \
  >"$test_root/conflict-output" 2>&1
grep -q "Skipped existing path" "$test_root/conflict-output"
grep -q "keep me" "$conflict_home/.agents/skills/pr-doc-open/sentinel"
grep -q "keep Claude" "$conflict_home/.claude/skills/sentinel"

conflict_workspace="$test_root/conflict-workspace"
conflict_project="$conflict_workspace/projects/chem-inventory"
mkdir -p "$conflict_project"
printf '%s\n' "project-owned" > "$conflict_project/AGENTS.md"
HOME="$conflict_home" "$repo_root/scripts/install.sh" \
  --workspace-root "$conflict_workspace" \
  >"$test_root/project-conflict-output" 2>&1
grep -q "skipping project" "$test_root/project-conflict-output"
[[ ! -e "$conflict_project/.agents/skills/db-migrations" ]] || {
  echo "Project install must be atomic when an unmanaged path exists." >&2
  exit 1
}

claude_conflict_home="$test_root/claude-conflict-home"
claude_conflict_workspace="$test_root/claude-conflict-workspace"
claude_conflict_project="$claude_conflict_workspace/projects/chem-inventory"
mkdir -p "$claude_conflict_home/.claude/skills" \
  "$claude_conflict_project/.claude/skills"
printf '%s\n' "keep global Claude" > \
  "$claude_conflict_home/.claude/skills/sentinel"
printf '%s\n' "keep project Claude" > \
  "$claude_conflict_project/.claude/skills/sentinel"
printf '%s\n' "keep project instructions" > "$claude_conflict_project/CLAUDE.md"

HOME="$claude_conflict_home" "$repo_root/scripts/install.sh" \
  --workspace-root "$claude_conflict_workspace" \
  --claude-compat \
  >"$test_root/claude-conflict-output" 2>&1

grep -q "keep global Claude" "$claude_conflict_home/.claude/skills/sentinel"
grep -q "keep project Claude" "$claude_conflict_project/.claude/skills/sentinel"
grep -q "keep project instructions" "$claude_conflict_project/CLAUDE.md"
assert_portable_link \
  "$claude_conflict_project/AGENTS.md" \
  "$repo_root/projects/chem-inventory/AGENTS.md"
assert_portable_link \
  "$claude_conflict_project/.agents/skills/db-migrations" \
  "$repo_root/projects/chem-inventory/skills/db-migrations"

echo "test_install.sh: PASS"

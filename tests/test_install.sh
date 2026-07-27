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
}

run_installer() {
  HOME="$test_home" "$repo_root/scripts/install.sh" \
    --workspace-root "$workspace_root"
}

first_output="$(run_installer)"

for skill_path in "$repo_root"/skills/*/; do
  skill_name="$(basename "$skill_path")"
  assert_link \
    "$test_home/.agents/skills/$skill_name" \
    "${skill_path%/}"
  assert_link \
    "$test_home/.claude/skills/$skill_name" \
    "${skill_path%/}"
done

assert_link \
  "$project_root/AGENTS.md" \
  "$repo_root/projects/chem-inventory/AGENTS.md"
assert_link "$project_root/CLAUDE.md" "AGENTS.md"
assert_link \
  "$project_root/.agents/skills/db-migrations" \
  "$repo_root/projects/chem-inventory/skills/db-migrations"
assert_link \
  "$project_root/.claude/skills/db-migrations" \
  "../../.agents/skills/db-migrations"

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

conflict_home="$test_root/conflict-home"
mkdir -p "$conflict_home/.agents/skills/pr-doc-open"
printf '%s\n' "keep me" > "$conflict_home/.agents/skills/pr-doc-open/sentinel"
HOME="$conflict_home" "$repo_root/scripts/install.sh" \
  --workspace-root "$test_root/missing-workspace" \
  >"$test_root/conflict-output" 2>&1
grep -q "Skipped existing path" "$test_root/conflict-output"
grep -q "keep me" "$conflict_home/.agents/skills/pr-doc-open/sentinel"

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

echo "test_install.sh: PASS"

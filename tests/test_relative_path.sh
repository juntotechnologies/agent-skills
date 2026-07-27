#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# shellcheck source=../scripts/lib/paths.sh
source "$repo_root/scripts/lib/paths.sh"

assert_relative_path() {
  local source="$1"
  local base="$2"
  local expected="$3"
  local actual

  actual="$(relative_path "$source" "$base")"
  [[ "$actual" == "$expected" ]] || {
    echo "Expected relative_path $source $base -> $expected, got $actual" >&2
    exit 1
  }
}

assert_relative_path \
  "/workspace/other/agent-skills/projects/chem/AGENTS.md" \
  "/workspace/projects/chem" \
  "../../other/agent-skills/projects/chem/AGENTS.md"
assert_relative_path \
  "/workspace/other/agent-skills/projects/chem/skills/db" \
  "/workspace/projects/chem/.agents/skills" \
  "../../../../other/agent-skills/projects/chem/skills/db"
assert_relative_path \
  "/workspace/projects/chem/AGENTS.md" \
  "/workspace/projects/chem" \
  "AGENTS.md"

echo "test_relative_path.sh: PASS"

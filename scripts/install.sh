#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
workspace_root="${HOME}/Documents/GitHub"

usage() {
  echo "Usage: scripts/install.sh [--workspace-root PATH]"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace-root)
      [[ $# -ge 2 ]] || { usage >&2; exit 2; }
      workspace_root="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

link_path() {
  local source="$1"
  local target="$2"

  mkdir -p "$(dirname "$target")"

  if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
    echo "Already linked: $target"
    return
  fi

  if [[ -e "$target" || -L "$target" ]]; then
    echo "Skipped existing path: $target" >&2
    return
  fi

  ln -s "$source" "$target"
  echo "Linked $target -> $source"
}

install_global_skills() {
  local skill_path skill_name target_root

  for skill_path in "$repo_root"/skills/*/; do
    [[ -f "$skill_path/SKILL.md" ]] || continue
    skill_name="$(basename "$skill_path")"
    for target_root in "$HOME/.agents/skills" "$HOME/.claude/skills"; do
      link_path "${skill_path%/}" "$target_root/$skill_name"
    done
  done
}

find_project_checkout() {
  local checkout_name="$1"

  if [[ ! -d "$workspace_root" ]]; then
    return 0
  fi
  find "$workspace_root" -maxdepth 4 -type d -name "$checkout_name" -print -quit
}

install_project() {
  local project_name="$1"
  local checkout_name="$2"
  local source_root="$repo_root/projects/$project_name"
  local project_root skill_path skill_name

  project_root="$(find_project_checkout "$checkout_name")"
  if [[ -z "$project_root" ]]; then
    echo "Project checkout not found, skipping: $checkout_name"
    return
  fi

  link_path "$source_root/AGENTS.md" "$project_root/AGENTS.md"
  link_path "AGENTS.md" "$project_root/CLAUDE.md"

  for skill_path in "$source_root"/skills/*/; do
    [[ -f "$skill_path/SKILL.md" ]] || continue
    skill_name="$(basename "$skill_path")"
    link_path \
      "${skill_path%/}" \
      "$project_root/.agents/skills/$skill_name"
    link_path \
      "../../.agents/skills/$skill_name" \
      "$project_root/.claude/skills/$skill_name"
  done
}

install_projects() {
  local project_name checkout_name

  while IFS=$'\t' read -r project_name checkout_name; do
    [[ -n "$project_name" && "${project_name:0:1}" != "#" ]] || continue
    install_project "$project_name" "$checkout_name"
  done < "$repo_root/projects/registry.tsv"
}

install_global_skills
install_projects
echo "Installed agent skills."

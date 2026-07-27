#!/usr/bin/env bash

relative_path() {
  local source="${1%/}"
  local base="${2%/}"
  local source_without_root="${source#/}"
  local base_without_root="${base#/}"
  local -a source_parts base_parts
  local common_index=0
  local part_index result=""
  local IFS='/'

  if [[ "$source" != /* || "$base" != /* ]]; then
    echo "relative_path requires absolute source and base paths." >&2
    return 2
  fi

  read -r -a source_parts <<< "$source_without_root"
  read -r -a base_parts <<< "$base_without_root"

  while [[ "$common_index" -lt "${#source_parts[@]}" \
    && "$common_index" -lt "${#base_parts[@]}" \
    && "${source_parts[$common_index]}" == "${base_parts[$common_index]}" ]]; do
    common_index=$((common_index + 1))
  done

  part_index="$common_index"
  while [[ "$part_index" -lt "${#base_parts[@]}" ]]; do
    result="../$result"
    part_index=$((part_index + 1))
  done

  part_index="$common_index"
  while [[ "$part_index" -lt "${#source_parts[@]}" ]]; do
    result="${result}${source_parts[$part_index]}"
    part_index=$((part_index + 1))
    if [[ "$part_index" -lt "${#source_parts[@]}" ]]; then
      result="$result/"
    fi
  done

  printf '%s\n' "${result:-.}"
}

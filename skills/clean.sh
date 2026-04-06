#!/usr/bin/env bash
# Purpose: Remove skill symlinks from all target locations defined in map.json
# Usage:   bash skills/clean.sh

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAP="$DIR/map.json"
HOST_USER="$(hostname)/$(whoami)"

[[ -f "$MAP" ]] || { echo "error: map.json not found" >&2; exit 1; }
jq -e --arg k "$HOST_USER" '.hosts[$k]' "$MAP" > /dev/null \
    || { echo "error: no entry for '$HOST_USER' in map.json" >&2; exit 1; }

skill_count=$(find "$DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
echo "$HOST_USER — $skill_count skills"

while IFS=$'\t' read -r raw_path skill_list; do
    target="${raw_path/#\~/$HOME}"
    shopt -s nullglob; resolved=( $target ); shopt -u nullglob
    [[ ${#resolved[@]} -eq 0 ]] && { echo "warn: no match for $raw_path" >&2; continue; }

    for target_dir in "${resolved[@]}"; do
        echo ""
        echo "$target_dir"
        for skill_dir in "$DIR"/*/; do
            name=$(basename "$skill_dir")
            [[ "$skill_list" != "all" ]] && [[ ",$skill_list," != *",$name,"* ]] && continue
            link="$target_dir/$name"
            real=$(readlink -f "$skill_dir")
            if [[ -L "$link" ]] && [[ "$(readlink -f "$link")" == "$real" ]]; then
                rm "$link"
                echo "  remove  $name"
            fi
        done
    done
done < <(jq -r --arg k "$HOST_USER" \
    '.hosts[$k][] | [.location, (.skills | if . == "all" then "all" else join(",") end)] | @tsv' \
    "$MAP") || true

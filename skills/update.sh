#!/usr/bin/env bash
# Purpose: Symlink (or hard-copy with --hard) each skill into all target locations defined in map.json
# Usage:   bash skills/update.sh [--hard]

set -euo pipefail

HARD=false
if [[ "${1:-}" == "--hard" ]]; then
    HARD=true
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAP="$DIR/map.json"
HOST_USER="$(hostname)/$(whoami)"

[[ -f "$MAP" ]] || { echo "error: map.json not found" >&2; exit 1; }

command -v jq > /dev/null 2>&1 \
    || { echo "error: jq is required (install jq and rerun)" >&2; exit 1; }

jq -e --arg k "$HOST_USER" '.hosts[$k]' "$MAP" > /dev/null \
    || { echo "error: no entry for '$HOST_USER' in map.json" >&2; exit 1; }

skill_count=$(find "$DIR" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
echo "$HOST_USER — $skill_count skills${HARD:+ (hard copy mode)}"

while IFS=$'\t' read -r raw_path skill_list; do
    target="${raw_path/#\~/$HOME}"
    shopt -s nullglob; resolved=( $target ); shopt -u nullglob
    [[ ${#resolved[@]} -eq 0 ]] && { echo "warn: no match for $raw_path" >&2; continue; }

    for target_dir in "${resolved[@]}"; do
        echo ""
        echo "$target_dir"
        mkdir -p "$target_dir"
        for skill_dir in "$DIR"/*/; do
            name=$(basename "$skill_dir")
            [[ "$skill_list" != "all" ]] && [[ ",$skill_list," != *",$name,"* ]] && continue
            link="$target_dir/$name"
            real=$(readlink -f "$skill_dir")
            if $HARD; then
                if [[ -L "$link" ]]; then
                    rm "$link"
                    cp -r "$real" "$link"
                    echo "  copy  $name  (replaced symlink with hard copy)"
                elif [[ -e "$link" ]]; then
                    # Check if it's already a hard copy (not a symlink)
                    if [[ "$link" -ef "$real" ]]; then
                        echo "  skip  $name  (hard copy already up to date)"
                    else
                        rm -rf "$link"
                        cp -r "$real" "$link"
                        echo "  copy  $name  (replaced existing with hard copy)"
                    fi
                else
                    cp -r "$real" "$link"
                    echo "  copy  $name"
                fi
            else
                if [[ -L "$link" ]]; then
                    [[ "$(readlink -f "$link")" != "$real" ]] && echo "  skip  $name  (symlink points elsewhere)"
                elif [[ -e "$link" ]]; then
                    echo "  skip  $name  (exists, not a symlink)"
                else
                    ln -s "$real" "$link"
                    echo "  link  $name"
                fi
            fi
        done
    done
done < <(jq -r --arg k "$HOST_USER" \
    '.hosts[$k][] | [.location, (.skills | if . == "all" then "all" else join(",") end)] | @tsv' \
    "$MAP") || true

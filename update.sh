#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$REPO/skills"
MAP="$REPO/map.yaml"
HOST=$(hostname)
USR=$(whoami)

# Validate map.yaml exists
[[ -f "$MAP" ]] || { echo "error: map.yaml not found at $MAP"; exit 1; }

# Parse map.yaml — emit "<path>|<skill1>,<skill2>,..." per resolved location
ENTRIES=$(python3 - <<EOF
import yaml, sys, os, glob

config = yaml.safe_load(open("$MAP"))
key = "$HOST/$USR"
hc = config.get("hosts", {}).get(key)

if not hc:
    sys.exit("error: no entry for '$HOST/$USR' in map.yaml")

for entry in hc:
    raw, skills = next(iter(entry.items()))
    skill_str = "all" if skills == "all" else ",".join(skills)
    expanded = os.path.expanduser(raw)
    matches = glob.glob(expanded) if "*" in expanded else [expanded]
    if not matches:
        print(f"warn: no match for glob: {raw}", file=sys.stderr)
    for m in matches:
        print(f"{m}|{skill_str}")
EOF
) || exit 1

skill_count=$(find "$SKILLS" -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "$HOST / $USR — $skill_count skills"

while IFS='|' read -r target skill_list; do
    echo ""
    echo "$target"
    mkdir -p "$target"

    for skill in "$SKILLS"/*/; do
        name=$(basename "$skill")
        # Skip if not in this location's skill list
        if [[ "$skill_list" != "all" ]] && [[ ",${skill_list}," != *",${name},"* ]]; then
            continue
        fi
        link="$target/$name"

        if [[ -L "$link" ]]; then
            if [[ "$(readlink -f "$link")" == "$(readlink -f "$skill")" ]]; then
                :  # already correct
            else
                echo "  skip  $name  (symlink points elsewhere)"
            fi
        elif [[ -e "$link" ]]; then
            echo "  skip  $name  (exists, not a symlink)"
        else
            ln -s "$(readlink -f "$skill")" "$link"
            echo "  link  $name"
        fi
    done
done <<< "$ENTRIES"

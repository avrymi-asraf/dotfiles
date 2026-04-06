#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
SKILLS="$REPO/skills"
MAP="$REPO/map.yaml"
HOST=$(hostname)
USR=$(whoami)

# Validate map.yaml exists
[[ -f "$MAP" ]] || { echo "error: map.yaml not found at $MAP"; exit 1; }

# Resolve targets for this host/user — expands ~ and globs, validates host/user
TARGETS=$(python3 - <<EOF
import yaml, sys, os, glob

config = yaml.safe_load(open("$MAP"))
hc = config.get("hosts", {}).get("$HOST")

if not hc:
    sys.exit("error: no entry for host '$HOST' in map.yaml")

expected_user = hc.get("user")
if expected_user and expected_user != "$USR":
    sys.exit("error: host '$HOST' is mapped to user '" + expected_user + "', running as '$USR'")

for raw in hc.get("targets", []):
    expanded = os.path.expanduser(raw)
    matches = glob.glob(expanded) if "*" in expanded else [expanded]
    if not matches:
        print(f"warn: no match for glob: {raw}", file=sys.stderr)
    for m in matches:
        print(m)
EOF
) || exit 1

skill_count=$(find "$SKILLS" -mindepth 1 -maxdepth 1 -type d | wc -l)
echo "$HOST / $USR — $skill_count skills"

while IFS= read -r target; do
    echo ""
    echo "$target"
    mkdir -p "$target"

    for skill in "$SKILLS"/*/; do
        name=$(basename "$skill")
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
done <<< "$TARGETS"

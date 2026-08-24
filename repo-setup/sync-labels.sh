#!/usr/bin/env bash
set -euo pipefail

# Sync GitHub labels from a YAML config file.
# Usage: ./sync-labels.sh <owner/repo> <labels.yml> [--delete-unlisted]

REPO="${1:?Usage: $0 <owner/repo> <labels.yml> [--delete-unlisted]}"
CONFIG="${2:?Usage: $0 <owner/repo> <labels.yml> [--delete-unlisted]}"
DELETE_UNLISTED="${3:-}"

if [[ ! -f "$CONFIG" ]]; then
	echo "Error: config file not found: $CONFIG" >&2
	exit 1
fi

if ! command -v gh &>/dev/null; then
	echo "Error: gh CLI not found" >&2
	exit 1
fi

if ! command -v python3 &>/dev/null; then
	echo "Error: python3 not found" >&2
	exit 1
fi

# Parse YAML config into tab-separated lines: name\tcolor\tdescription
parse_config() {
	python3 -c "
import yaml, sys
with open(sys.argv[1]) as f:
    labels = yaml.safe_load(f)
for label in labels:
    name = label['name']
    color = label.get('color', '').lstrip('#')
    desc = label.get('description', '')
    print(f'{name}\t{color}\t{desc}')
" "$1"
}

# Get existing labels as tab-separated: name\tcolor\tdescription
get_existing() {
	gh label list --repo "$REPO" --json name,color,description --limit 100 |
		python3 -c "
import json, sys
for label in json.load(sys.stdin):
    print(f\"{label['name']}\t{label['color']}\t{label['description']}\")
"
}

echo "=== Syncing labels for $REPO ==="
echo

# Build lookup of existing labels
declare -A existing_colors existing_descs
while IFS=$'\t' read -r name color desc; do
	existing_colors["$name"]="$color"
	existing_descs["$name"]="$desc"
done < <(get_existing)

# Track which labels are in config (for --delete-unlisted)
declare -A config_labels

# Create or update labels from config
while IFS=$'\t' read -r name color desc; do
	config_labels["$name"]=1

	if [[ -v "existing_colors[$name]" ]]; then
		# Label exists — check if update needed
		if [[ "${existing_colors[$name]}" != "$color" || "${existing_descs[$name]}" != "$desc" ]]; then
			echo "  UPDATE: $name"
			gh label edit "$name" --repo "$REPO" --color "$color" --description "$desc"
		else
			echo "  OK:     $name"
		fi
	else
		echo "  CREATE: $name"
		gh label create "$name" --repo "$REPO" --color "$color" --description "$desc"
	fi
done < <(parse_config "$CONFIG")

# Optionally delete labels not in config
if [[ "$DELETE_UNLISTED" == "--delete-unlisted" ]]; then
	echo
	echo "--- Deleting unlisted labels ---"
	for name in "${!existing_colors[@]}"; do
		if [[ ! -v "config_labels[$name]" ]]; then
			echo "  DELETE: $name"
			gh label delete "$name" --repo "$REPO" --yes
		fi
	done
fi

echo
echo "=== Done ==="

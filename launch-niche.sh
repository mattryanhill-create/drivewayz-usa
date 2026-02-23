#!/bin/bash
# launch-niche.sh - Swap site config for a different niche
# Usage: ./launch-niche.sh <niche-name>
# Example: ./launch-niche.sh septic

if [ -z "$1" ]; then
  echo "Usage: ./launch-niche.sh <niche-name>"
  echo "Example: ./launch-niche.sh septic"
  exit 1
fi

NICHE="$1"
CONFIG_PATH="niches/${NICHE}/site-config.json"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "Error: ${CONFIG_PATH} does not exist."
  exit 1
fi

cp "$CONFIG_PATH" ./site-config.json
echo "Site config updated to [${NICHE}]. Run git add/commit/push to deploy."

#!/usr/bin/env bash
# deploy_code.sh - Deploys code, libs, and handles SENSOR_ID
# Assumes: CIRCUITPY mounted, settings.toml & code.py in same dir.
# Customize: BOARD_PATH if needed.

set -euo pipefail

BOARD_PATH="/Volumes/CIRCUITPY"
SETTINGS_FILE="settings.toml"
REQS_FILE="requirements-circuitpython.txt"

# Check if Pico is connected
if [[ ! -d "$BOARD_PATH" ]]; then
  echo "Error: $BOARD_PATH not found. Connect Pico and retry."
  exit 1
fi

# Check if user has created settings.toml yet
if [[ ! -f "$SETTINGS_FILE" ]]; then
  echo "Error: Copy example_settings.toml to settings.toml first."
  exit 1
fi

# Check if requirements-circuitpython.txt exists
if [[ ! -f "$REQS_FILE" ]]; then
  echo "Error: requirements-circuitpython.txt does not exist."
  exit 1
fi

# Make sure there are python files to copy
ls *.py >/dev/null 2>&1 || { echo "Error: No .py files found."; exit 1; }

# Read current SENSOR_ID from settings.toml
CURRENT_ID=$(cut -d'=' -f2 <<< "$(grep -i "SENSOR_ID" settings.toml 2>/dev/null)" | xargs || echo "none")
read -rp "Enter SENSOR_ID: [$CURRENT_ID] " NEW_ID

# Update or add SENSOR_ID in settings.toml
[[ "$NEW_ID" != "$CURRENT_ID" && -n "$NEW_ID" ]] && \
  sed -i '' "/SENSOR_ID/d" settings.toml && echo "SENSOR_ID = \"$NEW_ID\"" >> settings.toml

# Copy files to Pico
echo "=== Copying code files ==="
cp *.py settings.toml "$BOARD_PATH/"

# Install libraries on Pico
echo "=== Installing libraries ==="
circup --path "$BOARD_PATH" install -r requirements-circuitpython.txt

# Update libraries on Pico
echo "=== Updating libraries ==="
circup --path "$BOARD_PATH" update
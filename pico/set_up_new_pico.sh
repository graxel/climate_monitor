#!/usr/bin/env bash
# set_up_new_pico.sh - Downloads latest version of CircuitPython and flashes it to new Pico board.

set -euo pipefail

BOARD_PATH="/Volumes/RPI-RP2"
BOARD="raspberry_pi_pico_w"
FILENAME="circuitpython-pico-w.uf2"

# Get the latest CircuitPython version number
VERSION=$(curl -s https://api.github.com/repos/adafruit/circuitpython/releases/latest | jq -r '.tag_name')

# Download the UF2 file for Raspberry Pi Pico
echo "Downloading CircuitPython version ${VERSION} for ${BOARD}..."
curl -L -f -o "$FILENAME" \
  "https://downloads.circuitpython.org/bin/${BOARD}/en_US/adafruit-circuitpython-${BOARD}-en_US-${VERSION}.uf2"

# Check if Pico is in bootloader mode
if [[ ! -d "$BOARD_PATH" ]]; then
  echo ""
  echo "⚠️  Pico not detected at $BOARD_PATH"
  echo "Steps to put Pico in BOOTSEL mode:"
  echo "  1. Unplug the Pico from USB"
  echo "  2. Hold down the BOOTSEL button"
  echo "  3. Plug USB cable back in (keep BOOTSEL held)"
  echo "  4. Release BOOTSEL"
  echo ""
  exit 1
fi

# Copy UF2 file to the Pico
echo "Copying CircuitPython to Pico."
cp "$FILENAME" "$BOARD_PATH/"

#echo "Installing circup.
# command to install circup
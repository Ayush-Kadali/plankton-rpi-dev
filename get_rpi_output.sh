#!/bin/bash
# Retrieve output files from RPi

set -e

# Load config
source .rpi_config 2>/dev/null || {
    RPI_USER="pi"
    RPI_HOST="raspberrypi.local"
    RPI_PROJECT_DIR="~/plankton"
}

echo "========================================"
echo "📥 RETRIEVING RPi OUTPUT"
echo "========================================"
echo ""

# Create local output directory
mkdir -p rpi_output_retrieved

echo "Checking for files on RPi..."
FILE_COUNT=$(ssh "$RPI_USER@$RPI_HOST" "ls $RPI_PROJECT_DIR/rpi_output/ 2>/dev/null | wc -l" || echo "0")

if [ "$FILE_COUNT" -eq "0" ]; then
    echo "⚠️  No output files found on RPi"
    exit 0
fi

echo "Found $FILE_COUNT file(s)"
echo ""
echo "Downloading..."

# Use rsync for efficient transfer
rsync -avz --progress \
    "$RPI_USER@$RPI_HOST:$RPI_PROJECT_DIR/rpi_output/" \
    ./rpi_output_retrieved/

echo ""
echo "✅ Files retrieved to: rpi_output_retrieved/"
echo ""

# List retrieved files
echo "Downloaded files:"
ls -lh rpi_output_retrieved/ | tail -n +2

echo ""
echo "========================================"

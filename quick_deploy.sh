#!/bin/bash
# One command to sync, run, and retrieve!

set -e

# Load config
source .rpi_config 2>/dev/null || {
    RPI_USER="pi"
    RPI_HOST="raspberrypi.local"
    RPI_PROJECT_DIR="~/plankton"
    GIT_BRANCH="main"
}

echo "========================================"
echo "⚡ QUICK DEPLOY & RUN"
echo "========================================"
echo ""

# Get mode from argument
MODE="${1:-test}"  # test, headless, or interactive
COMMIT_MSG="${2:-Quick deploy - $(date '+%Y-%m-%d %H:%M:%S')}"

echo "Mode: $MODE"
echo ""

# Step 1: Sync
echo "1️⃣ Syncing to RPi..."
./sync_to_rpi.sh "$COMMIT_MSG"

# Step 2: Run
echo ""
echo "2️⃣ Running on RPi..."
./run_on_rpi.sh "$MODE" "yes"

echo ""
echo "✅ Quick deploy complete!"
echo ""
echo "========================================"

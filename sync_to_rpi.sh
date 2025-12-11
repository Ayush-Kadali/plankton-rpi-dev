#!/bin/bash
# Quick sync: Laptop → Git → RPi

set -e  # Exit on error

# Load config
source .rpi_config 2>/dev/null || {
    echo "⚠️  .rpi_config not found, using defaults"
    RPI_USER="pi"
    RPI_HOST="raspberrypi.local"
    RPI_PROJECT_DIR="~/plankton"
    GIT_BRANCH="main"
}

echo "========================================"
echo "🔄 SYNC TO RASPBERRY PI"
echo "========================================"
echo ""

# Step 1: Git add and commit
echo "1️⃣ Committing changes locally..."
git add -A

# Get commit message from argument or use default
COMMIT_MSG="${1:-Update from laptop - $(date '+%Y-%m-%d %H:%M:%S')}"
git commit -m "$COMMIT_MSG" || echo "   (No changes to commit)"

# Step 2: Push to GitHub
echo ""
echo "2️⃣ Pushing to GitHub..."
git push origin $GIT_BRANCH

# Step 3: Pull on RPi
echo ""
echo "3️⃣ Pulling on RPi ($RPI_USER@$RPI_HOST)..."
ssh "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && git pull origin $GIT_BRANCH"

echo ""
echo "✅ Sync complete!"
echo ""
echo "To run on RPi:"
echo "  ./run_on_rpi.sh"
echo ""
echo "========================================"

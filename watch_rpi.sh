#!/bin/bash
# Watch for changes and auto-sync (development mode)

set -e

# Load config
source .rpi_config 2>/dev/null || {
    RPI_USER="pi"
    RPI_HOST="raspberrypi.local"
}

echo "========================================"
echo "👀 WATCH MODE - Auto Sync"
echo "========================================"
echo ""
echo "Watching for file changes..."
echo "Press Ctrl+C to stop"
echo ""

# Function to sync
do_sync() {
    echo ""
    echo "🔄 Changes detected! Syncing..."
    ./sync_to_rpi.sh "Auto-sync: $(date '+%H:%M:%S')" 2>&1 | grep -v "Already up to date" || true
    echo "✅ Synced at $(date '+%H:%M:%S')"
}

# Check if fswatch is available
if command -v fswatch &> /dev/null; then
    # Use fswatch (better)
    fswatch -o *.py modules/*.py 2>/dev/null | while read; do
        do_sync
    done
else
    # Fallback: periodic check
    echo "💡 Tip: Install fswatch for instant sync"
    echo "   brew install fswatch (macOS)"
    echo ""
    echo "Using periodic check (every 5 seconds)..."

    LAST_HASH=$(find *.py modules/*.py -type f -exec md5 {} \; 2>/dev/null | md5)

    while true; do
        sleep 5
        CURRENT_HASH=$(find *.py modules/*.py -type f -exec md5 {} \; 2>/dev/null | md5)

        if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
            do_sync
            LAST_HASH=$CURRENT_HASH
        fi
    done
fi

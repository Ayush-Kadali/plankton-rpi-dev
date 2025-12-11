#!/bin/bash
# Execute detection on RPi and optionally retrieve output

set -e

# Load config
source .rpi_config 2>/dev/null || {
    RPI_USER="pi"
    RPI_HOST="raspberrypi.local"
    RPI_PROJECT_DIR="~/plankton"
}

echo "========================================"
echo "🚀 RUN ON RASPBERRY PI"
echo "========================================"
echo ""

# Parse arguments
MODE="${1:-interactive}"  # interactive, headless, or test
RETRIEVE="${2:-yes}"       # yes or no

case $MODE in
    interactive)
        echo "Running in interactive mode..."
        echo "Press Ctrl+C to stop"
        echo ""
        ssh -t "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && python3 DEMO_RPI.py"
        ;;

    headless)
        echo "Running in headless mode (saving output)..."
        echo "Press Ctrl+C to stop"
        echo ""
        ssh -t "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && python3 DEMO_RPI.py --no-display --save"
        ;;

    test)
        echo "Running 30-second test..."
        ssh -t "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && timeout 30 python3 DEMO_RPI.py --no-display || true"
        ;;

    *)
        echo "❌ Invalid mode: $MODE"
        echo "Usage: $0 [interactive|headless|test] [yes|no]"
        exit 1
        ;;
esac

# Retrieve output if requested
if [ "$RETRIEVE" = "yes" ]; then
    echo ""
    echo "📥 Retrieving output files..."
    ./get_rpi_output.sh
fi

echo ""
echo "✅ Done!"
echo "========================================"

#!/bin/bash
# Quick start script for plankton detection demo

echo "========================================"
echo "🔬 PLANKTON DETECTION SYSTEM"
echo "========================================"
echo ""
echo "Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi
echo "✅ Python 3 found"

# Check/install dependencies
echo ""
echo "Installing required packages..."
python3 -m pip install --quiet ultralytics opencv-python folium 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Dependencies ready"
else
    echo "⚠️  Some dependencies may already be installed"
fi

echo ""
echo "========================================"
echo "🚀 STARTING DEMO LAUNCHER"
echo "========================================"
echo ""

# Launch the demo
python3 LAUNCH_DEMO.py

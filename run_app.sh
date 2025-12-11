#!/bin/bash
# Simple launcher for the Plankton Detection Dashboard

echo "=================================================="
echo "  PLANKTON DETECTION SYSTEM - DASHBOARD"
echo "=================================================="
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not found. Installing..."
    pip3 install streamlit --quiet
fi

# Check if demo data exists
if [ ! -f "data/judge_demo.db" ]; then
    echo "⚠️  Demo data not found."
    echo "   Generating demo data first..."
    echo ""
    echo "y" | python3 judge_demo.py
    echo ""
fi

# Launch the app
echo "🚀 Launching dashboard..."
echo ""
echo "The app will open in your browser automatically."
echo "If it doesn't, open: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

streamlit run app.py

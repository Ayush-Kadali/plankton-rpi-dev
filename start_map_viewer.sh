#!/bin/bash

echo "=========================================="
echo "Starting Plankton Map Viewer"
echo "=========================================="

# Activate virtual environment
source .venv/bin/activate

# Clear Streamlit cache
rm -rf ~/.streamlit/cache 2>/dev/null
echo "✓ Cleared Streamlit cache"

# Show database info
echo ""
echo "Database: data/judge_demo.db"
sqlite3 data/judge_demo.db "SELECT COUNT(DISTINCT location_name) as locations, COUNT(*) as samples FROM samples;" | while read line; do
    echo "✓ $line locations with samples in database"
done

echo ""
echo "Starting Streamlit app..."
echo "=========================================="
echo ""

# Start streamlit
streamlit run map_viewer_app.py --server.headless=false

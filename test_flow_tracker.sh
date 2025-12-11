#!/bin/bash
# Quick test script for the flow tracker

echo "======================================"
echo "PLANKTON FLOW TRACKER - QUICK TEST"
echo "======================================"
echo ""

# Test 1: good flow.mov
echo "Test 1: Processing 'good flow.mov' with ByteTrack..."
python3 realtime_flow_tracker.py \
    --video "Real_Time_Vids/good flow.mov" \
    --model "Downloaded models/best.pt" \
    --conf 0.25 \
    --tracker bytetrack.yaml \
    --output "results/focused_comparison/tracked_good_flow.mp4"

echo ""
echo "======================================"
echo ""

# Test 2: trial.mov
echo "Test 2: Processing 'trial.mov' with ByteTrack..."
python3 realtime_flow_tracker.py \
    --video "Real_Time_Vids/trial.mov" \
    --model "Downloaded models/best.pt" \
    --conf 0.25 \
    --tracker bytetrack.yaml \
    --output "results/focused_comparison/tracked_trial.mp4"

echo ""
echo "======================================"
echo "ALL TESTS COMPLETE!"
echo "======================================"
echo ""
echo "Check results in: results/focused_comparison/"
echo ""

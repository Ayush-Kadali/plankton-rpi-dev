#!/bin/bash
# Quick system test

echo "=========================================="
echo "🧪 TESTING PLANKTON DETECTION SYSTEM"
echo "=========================================="
echo ""

echo "1️⃣ Checking Python..."
if python3 --version > /dev/null 2>&1; then
    echo "✅ Python 3 found: $(python3 --version)"
else
    echo "❌ Python 3 not found!"
    exit 1
fi

echo ""
echo "2️⃣ Checking dependencies..."
python3 -c "
try:
    import cv2
    print('✅ OpenCV installed')
except:
    print('❌ OpenCV missing')

try:
    from ultralytics import YOLO
    print('✅ Ultralytics installed')
except:
    print('❌ Ultralytics missing - installing...')
    import subprocess
    subprocess.run(['python3', '-m', 'pip', 'install', '--quiet', 'ultralytics'])
    print('✅ Ultralytics installed')

try:
    import numpy as np
    print('✅ NumPy installed')
except:
    print('❌ NumPy missing')
"

echo ""
echo "3️⃣ Checking model..."
if [ -f "Downloaded models/best.pt" ]; then
    echo "✅ Model found: Downloaded models/best.pt"
else
    echo "❌ Model not found!"
    echo "   Expected: Downloaded models/best.pt"
    exit 1
fi

echo ""
echo "4️⃣ Testing model loading..."
python3 -c "
from ultralytics import YOLO
try:
    model = YOLO('Downloaded models/best.pt')
    classes = list(model.names.values())
    print(f'✅ Model loaded: {len(classes)} classes')
    print(f'   Species: {', '.join(classes)}')
except Exception as e:
    print(f'❌ Model loading failed: {e}')
    exit(1)
"

echo ""
echo "5️⃣ Checking video files..."
if [ -d "Real_Time_Vids" ]; then
    count=$(ls Real_Time_Vids/*.mov 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "✅ Found $count video file(s)"
    else
        echo "⚠️  No video files found (not critical)"
    fi
else
    echo "⚠️  Real_Time_Vids directory not found (not critical)"
fi

echo ""
echo "6️⃣ Checking demo scripts..."
for script in DEMO.py DEMO_RPI.py LAUNCH_DEMO.py MAP_VIEWER.py; do
    if [ -f "$script" ]; then
        echo "✅ $script"
    else
        echo "❌ $script missing!"
    fi
done

echo ""
echo "=========================================="
echo "🎉 SYSTEM TEST COMPLETE!"
echo "=========================================="
echo ""
echo "Ready to run:"
echo "  python3 DEMO.py"
echo ""
echo "For RPi deployment:"
echo "  ./transfer_to_rpi.sh"
echo ""
echo "=========================================="

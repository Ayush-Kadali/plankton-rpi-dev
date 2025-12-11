#!/bin/bash
# Quick RPi Connection Test

echo "========================================"
echo "🔍 RPi CONNECTION TEST"
echo "========================================"
echo ""

# Load config
if [ -f ".rpi_config" ]; then
    source .rpi_config
    echo "Configuration:"
    echo "  User: $RPI_USER"
    echo "  Host: $RPI_HOST"
    echo ""
else
    echo "❌ No .rpi_config found"
    echo "   Run: ./setup_rpi_complete.sh"
    exit 1
fi

# Test 1: Ping
echo "Test 1: Network Connectivity"
echo "-----------------------------"
if ping -c 1 -W 2 "$RPI_HOST" > /dev/null 2>&1; then
    echo "✅ RPi is reachable on network"
else
    echo "❌ Cannot ping RPi"
    echo "   Check: Network connection, IP/hostname"
fi
echo ""

# Test 2: SSH
echo "Test 2: SSH Connection"
echo "----------------------"
if ssh -o ConnectTimeout=5 "$RPI_USER@$RPI_HOST" "echo 'SSH OK'" 2>/dev/null; then
    echo "✅ SSH connection works"
else
    echo "❌ SSH connection failed"
    echo "   Check: SSH enabled, correct credentials"
fi
echo ""

# Test 3: Project directory
echo "Test 3: Project Directory"
echo "------------------------"
if ssh "$RPI_USER@$RPI_HOST" "[ -d $RPI_PROJECT_DIR ]" 2>/dev/null; then
    echo "✅ Project directory exists"
    FILES=$(ssh "$RPI_USER@$RPI_HOST" "ls $RPI_PROJECT_DIR/*.py 2>/dev/null | wc -l")
    echo "   Found $FILES Python files"
else
    echo "❌ Project directory not found"
    echo "   Run: ./setup_rpi_complete.sh"
fi
echo ""

# Test 4: Git
echo "Test 4: Git Repository"
echo "----------------------"
if ssh "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && git status" > /dev/null 2>&1; then
    echo "✅ Git repository OK"
    BRANCH=$(ssh "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && git branch --show-current")
    echo "   Current branch: $BRANCH"
else
    echo "❌ Git repository not initialized"
fi
echo ""

# Test 5: Python packages
echo "Test 5: Python Dependencies"
echo "---------------------------"
MISSING=""

if ! ssh "$RPI_USER@$RPI_HOST" "python3 -c 'import cv2' 2>/dev/null"; then
    MISSING="$MISSING opencv"
fi

if ! ssh "$RPI_USER@$RPI_HOST" "python3 -c 'from ultralytics import YOLO' 2>/dev/null"; then
    MISSING="$MISSING ultralytics"
fi

if [ -z "$MISSING" ]; then
    echo "✅ All Python packages installed"
else
    echo "❌ Missing packages:$MISSING"
    echo "   Run: ssh $RPI_USER@$RPI_HOST 'cd ~/plankton && ./setup_rpi.sh'"
fi
echo ""

# Test 6: Camera
echo "Test 6: Camera"
echo "--------------"
CAM_STATUS=$(ssh "$RPI_USER@$RPI_HOST" "vcgencmd get_camera 2>/dev/null || echo 'unknown'")
if echo "$CAM_STATUS" | grep -q "detected=1"; then
    echo "✅ Camera detected"
else
    echo "⚠️  Camera status: $CAM_STATUS"
    echo "   Enable: sudo raspi-config → Interface Options → Camera"
fi
echo ""

# Test 7: Model file
echo "Test 7: Model File"
echo "------------------"
if ssh "$RPI_USER@$RPI_HOST" "[ -f '$RPI_PROJECT_DIR/Downloaded models/best.pt' ]" 2>/dev/null; then
    SIZE=$(ssh "$RPI_USER@$RPI_HOST" "ls -lh '$RPI_PROJECT_DIR/Downloaded models/best.pt' | awk '{print \$5}'")
    echo "✅ Model file exists ($SIZE)"
else
    echo "❌ Model file not found"
    echo "   Copy: scp 'Downloaded models/best.pt' $RPI_USER@$RPI_HOST:$RPI_PROJECT_DIR/Downloaded\\ models/"
fi
echo ""

# Test 8: System info
echo "Test 8: System Information"
echo "--------------------------"
TEMP=$(ssh "$RPI_USER@$RPI_HOST" "vcgencmd measure_temp 2>/dev/null | cut -d= -f2 | cut -d\\' -f1" || echo "unknown")
MEM=$(ssh "$RPI_USER@$RPI_HOST" "free -h | grep Mem | awk '{print \$3\"/\"\$2}'" || echo "unknown")
DISK=$(ssh "$RPI_USER@$RPI_HOST" "df -h / | tail -1 | awk '{print \$5}'" || echo "unknown")

echo "  Temperature: ${TEMP}°C"
echo "  Memory used: $MEM"
echo "  Disk used: $DISK"
echo ""

# Summary
echo "========================================"
echo "SUMMARY"
echo "========================================"
echo ""

# Count passed tests
TESTS=0
PASSED=0

# Simple check - count ✅ in output above
# (This is approximate but works for quick test)

echo "If all tests passed, you're ready to:"
echo "  ./quick_deploy.sh test 'First test'"
echo ""
echo "If tests failed, run:"
echo "  ./setup_rpi_complete.sh"
echo ""
echo "For detailed setup guide:"
echo "  cat RPi_COMPLETE_SETUP.md"
echo ""
echo "========================================"

#!/bin/bash
# Transfer project to Raspberry Pi

echo "========================================"
echo "📤 TRANSFER TO RASPBERRY PI"
echo "========================================"
echo ""

# Get RPi address
read -p "Enter RPi address (default: raspberrypi.local): " RPI_ADDR
RPI_ADDR=${RPI_ADDR:-raspberrypi.local}

# Get username
read -p "Enter username (default: pi): " RPI_USER
RPI_USER=${RPI_USER:-pi}

echo ""
echo "📦 Transferring files to $RPI_USER@$RPI_ADDR..."
echo ""

# Create directory on RPi
ssh "$RPI_USER@$RPI_ADDR" "mkdir -p ~/plankton"

# Transfer essential files
rsync -av --progress \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='demo_output' \
    --exclude='rpi_output' \
    --exclude='results' \
    --exclude='Real_Time_Vids/*.mov' \
    --exclude='aqualens' \
    --exclude='logs' \
    --include='DEMO_RPI.py' \
    --include='setup_rpi.sh' \
    --include='RPi_GUIDE.md' \
    --include='Downloaded models/best.pt' \
    --include='Downloaded models/yolov8n.pt' \
    ./ "$RPI_USER@$RPI_ADDR:~/plankton/"

echo ""
echo "✅ Transfer complete!"
echo ""
echo "Next steps:"
echo "  1. SSH into RPi:"
echo "     ssh $RPI_USER@$RPI_ADDR"
echo ""
echo "  2. Run setup:"
echo "     cd ~/plankton"
echo "     ./setup_rpi.sh"
echo ""
echo "  3. Test detection:"
echo "     python3 DEMO_RPI.py"
echo ""
echo "========================================"

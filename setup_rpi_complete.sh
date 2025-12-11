#!/bin/bash
# Complete RPi Setup Script - Run from Laptop

set -e

echo "========================================"
echo "🍓 RASPBERRY PI COMPLETE SETUP"
echo "========================================"
echo ""

# Step 1: Get RPi details
echo "Step 1: RPi Connection Details"
echo "------------------------------"
echo ""

if [ -f ".rpi_config" ]; then
    source .rpi_config
    echo "Found existing .rpi_config:"
    echo "  User: $RPI_USER"
    echo "  Host: $RPI_HOST"
    echo ""
    read -p "Use these settings? (y/n): " use_existing

    if [ "$use_existing" != "y" ]; then
        read -p "Enter RPi username (default: pi): " RPI_USER
        RPI_USER=${RPI_USER:-pi}

        read -p "Enter RPi hostname or IP (e.g., raspberrypi.local or 192.168.1.100): " RPI_HOST

        # Update .rpi_config
        cat > .rpi_config << EOF
RPI_USER="$RPI_USER"
RPI_HOST="$RPI_HOST"
RPI_PROJECT_DIR="~/plankton"
GIT_BRANCH="main"
EOF
    fi
else
    read -p "Enter RPi username (default: pi): " RPI_USER
    RPI_USER=${RPI_USER:-pi}

    read -p "Enter RPi hostname or IP: " RPI_HOST

    # Create .rpi_config
    cat > .rpi_config << EOF
RPI_USER="$RPI_USER"
RPI_HOST="$RPI_HOST"
RPI_PROJECT_DIR="~/plankton"
GIT_BRANCH="main"
EOF
fi

RPI_PROJECT_DIR="~/plankton"
GIT_BRANCH="main"

echo ""
echo "✅ Configuration saved"
echo ""

# Step 2: Test connection
echo "Step 2: Testing Connection"
echo "--------------------------"
echo ""

if ssh -o ConnectTimeout=5 "$RPI_USER@$RPI_HOST" "echo 'Connection successful'" 2>/dev/null; then
    echo "✅ SSH connection successful!"
else
    echo "❌ Cannot connect to RPi"
    echo ""
    echo "Please check:"
    echo "  1. RPi is powered on"
    echo "  2. RPi is connected to network"
    echo "  3. SSH is enabled on RPi"
    echo "  4. Hostname/IP is correct"
    echo ""
    echo "To enable SSH on RPi:"
    echo "  sudo raspi-config → Interface Options → SSH → Enable"
    exit 1
fi

echo ""

# Step 3: Setup Git on RPi
echo "Step 3: Setting Up Git"
echo "----------------------"
echo ""

REPO_URL=$(git config --get remote.origin.url)
echo "Repository: $REPO_URL"
echo ""

# Check if SSH key exists on RPi
KEY_EXISTS=$(ssh "$RPI_USER@$RPI_HOST" "[ -f ~/.ssh/id_rsa.pub ] && echo 'yes' || echo 'no'")

if [ "$KEY_EXISTS" = "no" ]; then
    echo "Generating SSH key on RPi..."
    ssh "$RPI_USER@$RPI_HOST" "ssh-keygen -t rsa -b 4096 -C 'rpi@plankton' -f ~/.ssh/id_rsa -N ''"
    echo "✅ SSH key generated"
else
    echo "SSH key already exists"
fi

echo ""
echo "📋 RPi Public Key (add this to GitHub):"
echo "========================================"
ssh "$RPI_USER@$RPI_HOST" "cat ~/.ssh/id_rsa.pub"
echo "========================================"
echo ""
echo "Instructions:"
echo "  1. Copy the key above"
echo "  2. Go to: https://github.com/settings/keys"
echo "  3. Click 'New SSH key'"
echo "  4. Paste the key and save"
echo ""
read -p "Press Enter after adding the key to GitHub..."

# Test GitHub connection
echo ""
echo "Testing GitHub connection..."
if ssh "$RPI_USER@$RPI_HOST" "ssh -o StrictHostKeyChecking=no -T git@github.com 2>&1 | grep -q 'successfully authenticated'"; then
    echo "✅ GitHub connection successful"
else
    echo "⚠️  GitHub connection test inconclusive (this might be normal)"
    echo "   Will continue with setup..."
fi

echo ""

# Step 4: Clone/Update repository
echo "Step 4: Cloning Repository"
echo "--------------------------"
echo ""

# Check if directory exists
DIR_EXISTS=$(ssh "$RPI_USER@$RPI_HOST" "[ -d $RPI_PROJECT_DIR ] && echo 'yes' || echo 'no'")

if [ "$DIR_EXISTS" = "yes" ]; then
    echo "Project directory exists. Updating..."
    ssh "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && git fetch origin && git reset --hard origin/$GIT_BRANCH"
    echo "✅ Repository updated"
else
    echo "Cloning repository..."
    ssh "$RPI_USER@$RPI_HOST" "git clone $REPO_URL $RPI_PROJECT_DIR && cd $RPI_PROJECT_DIR && git checkout $GIT_BRANCH"
    echo "✅ Repository cloned"
fi

echo ""

# Step 5: Install dependencies
echo "Step 5: Installing Dependencies"
echo "-------------------------------"
echo ""

ssh "$RPI_USER@$RPI_HOST" << 'ENDSSH'
cd ~/plankton

echo "Updating system..."
sudo apt-get update -qq

echo "Installing system dependencies..."
sudo apt-get install -y python3-pip python3-opencv python3-numpy libcap-dev

echo "Installing Python packages..."
python3 -m pip install --user --upgrade pip
python3 -m pip install --user ultralytics opencv-python dill

echo "Setting up camera..."
sudo raspi-config nonint do_camera 0

echo "✅ Dependencies installed"
ENDSSH

echo ""
echo "✅ Dependencies installed on RPi"
echo ""

# Step 6: Test detection
echo "Step 6: Testing Detection"
echo "------------------------"
echo ""

echo "Running quick detection test..."
ssh "$RPI_USER@$RPI_HOST" << 'ENDSSH'
cd ~/plankton

echo "Loading model..."
python3 -c "
from ultralytics import YOLO
import cv2
import numpy as np

print('Testing detection system...')
model = YOLO('Downloaded models/best.pt')
print('✅ Model loaded')

# Test with dummy frame
test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
results = model(test_frame, conf=0.15, verbose=False)
print('✅ Detection works')

print('')
print('Species detected by model:')
for name in model.names.values():
    print(f'  • {name}')
" 2>&1 | grep -v "WARNING"
ENDSSH

echo ""
echo "✅ Detection test complete"
echo ""

# Step 7: Summary
echo "========================================"
echo "🎉 SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Your RPi is ready to use!"
echo ""
echo "Quick commands:"
echo "  ./sync_to_rpi.sh 'message'    # Sync code"
echo "  ./run_on_rpi.sh test          # Run test"
echo "  ./quick_deploy.sh test 'msg'  # All-in-one"
echo ""
echo "To SSH into RPi:"
echo "  ssh $RPI_USER@$RPI_HOST"
echo ""
echo "To run detection on RPi:"
echo "  ssh $RPI_USER@$RPI_HOST 'cd ~/plankton && python3 DEMO_RPI.py --no-display'"
echo ""
echo "Next steps:"
echo "  1. Test camera: vcgencmd get_camera"
echo "  2. Run detection: ./quick_deploy.sh test"
echo "  3. Check output: ./get_rpi_output.sh"
echo ""
echo "See RPi_COMPLETE_SETUP.md for detailed guide"
echo "========================================"

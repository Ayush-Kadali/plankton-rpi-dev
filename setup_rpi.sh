#!/bin/bash
# Raspberry Pi 5 Setup Script for Plankton Detection

echo "========================================"
echo "🍓 RPi 5 PLANKTON DETECTOR SETUP"
echo "========================================"
echo ""

# Check if running on RPi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   Continue anyway? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        exit 1
    fi
fi

echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-opencv python3-numpy
sudo apt-get install -y libcap-dev

echo ""
echo "📸 Setting up camera support..."
sudo apt-get install -y python3-picamera2

echo ""
echo "🧠 Installing AI dependencies..."
# Install ultralytics with CPU optimizations
python3 -m pip install --user ultralytics opencv-python-headless

echo ""
echo "🔧 Optimizing for RPi 5..."
# Enable camera
sudo raspi-config nonint do_camera 0

# Increase GPU memory if needed
current_gpu_mem=$(vcgencmd get_mem gpu | cut -d= -f2 | cut -d M -f1)
if [ "$current_gpu_mem" -lt "128" ]; then
    echo "⚙️  Increasing GPU memory to 128MB..."
    echo "gpu_mem=128" | sudo tee -a /boot/config.txt
    echo "⚠️  GPU memory changed. Reboot required!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To test:"
echo "  python3 DEMO_RPI.py"
echo ""
echo "For headless mode:"
echo "  python3 DEMO_RPI.py --no-display --save"
echo ""
echo "========================================"

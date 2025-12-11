# 🍓 Raspberry Pi - Complete Setup Guide

## 🎯 Goal: Get RPi Running Detection in 15 Minutes

---

## 📋 Prerequisites

**What you need:**
- Raspberry Pi 5 (4GB+ RAM)
- MicroSD card (32GB+) with Raspberry Pi OS
- Pi Camera Module or USB webcam
- Power supply
- Internet connection (WiFi or Ethernet)
- Your laptop on same network

**Optional:**
- Monitor + keyboard + mouse (for initial setup)
- SSH enabled (easier!)

---

## 🚀 STEP-BY-STEP SETUP

### Step 1: Find Your RPi IP Address

**Option A: If you have monitor connected:**
```bash
# On RPi terminal
hostname -I
```

**Option B: From your laptop:**
```bash
# Try default hostname
ping raspberrypi.local

# Or scan network
nmap -sn 192.168.1.0/24 | grep -i raspberry
# Or
arp -a | grep -i b8:27:eb  # RPi MAC prefix
```

**Write down the IP:** `___.___.___.___`

---

### Step 2: Enable SSH (If Not Already)

**On RPi (with monitor):**
```bash
sudo raspi-config
# Interface Options → SSH → Enable
```

**Or create SSH file on SD card:**
```bash
# On laptop, if SD card is accessible
touch /Volumes/boot/ssh
```

---

### Step 3: Connect from Laptop

```bash
# Replace with your RPi IP or hostname
ssh pi@raspberrypi.local
# or
ssh pi@192.168.1.XXX

# Default password: raspberry
# (Change this later!)
```

✅ **You're now connected to RPi!**

---

### Step 4: Configure RPi Settings

```bash
# Update .rpi_config on laptop first
nano .rpi_config
```

Edit these values:
```bash
RPI_USER="pi"
RPI_HOST="raspberrypi.local"  # or your IP: 192.168.1.XXX
RPI_PROJECT_DIR="~/plankton"
GIT_BRANCH="main"
```

Save and exit (Ctrl+X, Y, Enter)

---

### Step 5: Setup Git Access on RPi

**On your laptop, run:**
```bash
./setup_rpi_git.sh
```

This will:
1. Generate SSH key on RPi
2. Show you the public key
3. Help you add it to GitHub
4. Clone the repository
5. Install dependencies

**Follow the prompts carefully!**

When you see the SSH public key:
1. Copy it
2. Go to: https://github.com/settings/keys
3. Click "New SSH key"
4. Paste the key
5. Press Enter in terminal to continue

---

### Step 6: Test the Setup

```bash
# From laptop - sync code to RPi
./sync_to_rpi.sh "Initial setup complete"

# Should see:
# ✅ Pushed to GitHub
# ✅ Pulled on RPi
```

---

### Step 7: Test Camera

**SSH to RPi:**
```bash
ssh pi@raspberrypi.local
cd ~/plankton
```

**Test Pi Camera:**
```bash
# Test if camera detected
libcamera-hello --list-cameras

# Should see: Available cameras:
# 0 : imx219 [camera module name]
```

**Test OpenCV camera:**
```bash
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Camera OK' if cap.isOpened() else '❌ Camera failed'); cap.release()"
```

---

### Step 8: Run Detection (Headless Test)

**On RPi (via SSH):**
```bash
cd ~/plankton

# Quick test (30 seconds)
timeout 30 python3 DEMO_RPI.py --no-display || true

# Should see:
# 🔬 RPi 5 PLANKTON DETECTOR
# ✅ Model loaded
# 🚀 Running detection...
# Frame 30 | FPS: X.X | Detections: X
```

---

### Step 9: Full Workflow Test

**On laptop:**
```bash
# Edit a file
echo "# Test change" >> DEMO_RPI.py

# Deploy and run
./quick_deploy.sh test "Testing full workflow"

# Should:
# 1. Commit changes
# 2. Push to GitHub
# 3. Pull on RPi
# 4. Run detection
# 5. Retrieve output
```

---

## ✅ Setup Complete Checklist

- [ ] Found RPi IP address
- [ ] SSH connection works
- [ ] Configured `.rpi_config`
- [ ] Ran `./setup_rpi_git.sh`
- [ ] Added SSH key to GitHub
- [ ] Repository cloned on RPi
- [ ] Dependencies installed
- [ ] Camera detected
- [ ] Test detection worked
- [ ] Full workflow tested

**If all checked, you're ready!** 🎉

---

## 🎮 Daily Usage

### Deploy Changes:
```bash
# On laptop
./quick_deploy.sh test "Your changes"
```

### Run on RPi:
```bash
# From laptop
./run_on_rpi.sh test        # Quick test
./run_on_rpi.sh headless    # Long run, saves output
./run_on_rpi.sh interactive # With display (if monitor)
```

### Get Results:
```bash
# From laptop
./get_rpi_output.sh
ls rpi_output_retrieved/
```

---

## 🐛 Troubleshooting

### Can't Connect via SSH

**Problem:** `ssh: connect to host raspberrypi.local port 22: Connection refused`

**Solutions:**
```bash
# Try IP instead of hostname
ssh pi@192.168.1.XXX

# Check if SSH is enabled on RPi
# (Need monitor access)
sudo systemctl status ssh
sudo systemctl enable ssh
sudo systemctl start ssh
```

---

### Camera Not Detected

**Problem:** Camera not found

**Solutions:**
```bash
# Enable camera
sudo raspi-config
# Interface Options → Legacy Camera → Enable → Reboot

# Check camera cable connection
# Check if detected
vcgencmd get_camera
# Should show: supported=1 detected=1

# List cameras
libcamera-hello --list-cameras
```

---

### Git Clone Fails

**Problem:** `Permission denied (publickey)`

**Solutions:**
```bash
# On RPi, check if key exists
ls ~/.ssh/id_rsa.pub

# If not, generate
ssh-keygen -t rsa -b 4096 -C "rpi@plankton" -N ""

# Show key
cat ~/.ssh/id_rsa.pub

# Add to GitHub: https://github.com/settings/keys

# Test connection
ssh -T git@github.com
```

---

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'ultralytics'`

**Solutions:**
```bash
# On RPi
cd ~/plankton
./setup_rpi.sh

# Or manually
python3 -m pip install --user ultralytics opencv-python
```

---

### Low Performance

**Problem:** Very slow detection

**Solutions:**
```bash
# Use lower resolution
python3 DEMO_RPI.py --resolution 320 240

# Use lighter model
python3 DEMO_RPI.py --model "Downloaded models/yolov8n.pt"

# Check temperature
vcgencmd measure_temp
# Should be < 80°C

# Add cooling if needed
```

---

## 🔧 Advanced Configuration

### Auto-Start on Boot

**Create systemd service:**
```bash
# On RPi
sudo nano /etc/systemd/system/plankton.service
```

Paste:
```ini
[Unit]
Description=Plankton Detection Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/plankton
ExecStart=/usr/bin/python3 /home/pi/plankton/DEMO_RPI.py --no-display --save
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable plankton.service
sudo systemctl start plankton.service

# Check status
sudo systemctl status plankton.service

# View logs
sudo journalctl -u plankton.service -f
```

---

### Optimize Performance

**Increase GPU memory:**
```bash
sudo nano /boot/config.txt
# Add: gpu_mem=128
sudo reboot
```

**Overclock (careful!):**
```bash
sudo nano /boot/config.txt
# Add:
# over_voltage=2
# arm_freq=2400
sudo reboot
```

---

### Remote Display (See RPi Camera on Laptop)

**Option 1: X11 Forwarding**
```bash
# From laptop
ssh -X pi@raspberrypi.local
cd ~/plankton
python3 DEMO_RPI.py
```

**Option 2: VNC**
```bash
# On RPi, enable VNC
sudo raspi-config
# Interface Options → VNC → Enable

# From laptop
# Use VNC Viewer: raspberrypi.local:5900
```

---

## 📊 Expected Performance

**RPi 5 with 640x480:**
- FPS: 4-6
- CPU: 70-90%
- RAM: ~500MB
- Temp: 50-70°C (with heatsink)

**RPi 5 with 320x240:**
- FPS: 8-10
- CPU: 60-80%
- RAM: ~400MB
- Temp: 45-60°C

**These are GOOD numbers for plankton monitoring!**

---

## 🎯 Quick Reference Commands

```bash
# LAPTOP SIDE:
./sync_to_rpi.sh "message"       # Sync code
./run_on_rpi.sh test             # Run test
./get_rpi_output.sh              # Get results
./quick_deploy.sh test "msg"     # All-in-one

# RPI SIDE (via SSH):
cd ~/plankton
python3 DEMO_RPI.py              # Interactive
python3 DEMO_RPI.py --no-display # Headless
python3 DEMO_RPI.py --resolution 320 240  # Fast
vcgencmd measure_temp            # Check temp
```

---

## 🚀 Next Steps

Once setup is complete:

1. **Test thoroughly** with different videos/cameras
2. **Optimize settings** for your use case
3. **Setup auto-start** if needed
4. **Add GPS** (optional) for real coordinates
5. **Build enclosure** for field deployment
6. **Field test** in actual environment

---

## 📞 Need Help?

**Check:**
1. This guide
2. `RPi_GUIDE.md` - Detailed reference
3. `WORKFLOW_GUIDE.md` - Development workflow

**Debug commands:**
```bash
# Check camera
vcgencmd get_camera
libcamera-hello --list-cameras

# Check temp
vcgencmd measure_temp

# Check system
htop
free -h
df -h

# Check git
git status
git remote -v

# Test connection
ping github.com
ssh -T git@github.com
```

---

## ✅ You're Ready!

Once all steps are complete, you'll have:
- ✅ RPi connected and configured
- ✅ Code syncing via GitHub
- ✅ Detection running smoothly
- ✅ Seamless laptop ↔️ RPi workflow
- ✅ Ready for field deployment

**Go build something amazing!** 🚀🍓

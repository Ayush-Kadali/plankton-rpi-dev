# 🚀 RASPBERRY PI PLANKTON DETECTION - START HERE

## ⚡ FASTEST PATH TO RUNNING DEMO

### 📍 YOU ARE HERE
You have a **complete, ready-to-deploy package** in: `rpi-quick-deploy/`

---

## 🎯 3-STEP DEPLOYMENT (10 minutes total)

### Step 1: Transfer to Pi (YOUR LAPTOP)
```bash
cd /Users/ayushkadali/Documents/university/SIH/plank-1
bash rpi-quick-deploy/DEPLOY_NOW.sh
```

### Step 2: Setup Pi (ON RASPBERRY PI)
```bash
ssh pi@raspberrypi.local
cd plankton-demo
bash SETUP_PI.sh
sudo reboot
```

### Step 3: Run Detection (After reboot)
```bash
ssh pi@raspberrypi.local
cd plankton-demo
python3 RUN_DEMO.py
```

**Press 'q' to quit. DONE!**

---

## 🎬 DEMO MODES

### Auto (Recommended)
```bash
python3 RUN_DEMO.py
```

### Fast (Best Performance)
```bash
python3 FAST_DETECT.py new_chris.pt
```

### Focus Adjustment (Run First!)
```bash
python3 CAMERA_SETUP.py
```

### High FPS (Backup)
```bash
python3 HIGH_FPS_CAPTURE.py new_chris.pt
```

---

## 📋 FULL DOCS

See `rpi-quick-deploy/COMPLETE_GUIDE.md`

---

**START: Run Step 1 above! 🚀**

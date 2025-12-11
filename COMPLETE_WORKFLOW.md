# 🎯 COMPLETE WORKFLOW - LAPTOP TO RPi

## ⚡ Super Fast Setup & Usage

---

## 🚀 ONE-TIME SETUP (5 Minutes)

### Step 1: Configure Your RPi

Edit `.rpi_config` with your RPi details:
```bash
nano .rpi_config
```

Change these values:
```bash
RPI_USER="pi"                    # Your RPi username
RPI_HOST="raspberrypi.local"     # Your RPi hostname or IP address
RPI_PROJECT_DIR="~/plankton"
GIT_BRANCH="main"
```

### Step 2: Setup Git Connection

Run the setup script:
```bash
./setup_rpi_git.sh
```

This will:
1. Generate SSH key on RPi
2. Show you the public key to add to GitHub
3. Clone repository on RPi
4. Install dependencies

**Follow the prompts!**

### Step 3: Test the Connection

```bash
./quick_deploy.sh test "Initial test"
```

If it works, you're done! ✅

---

## 💻 DAILY WORKFLOW (Super Simple)

### The Magic Command:

```bash
./quick_deploy.sh test "What you changed"
```

**That's it!** This ONE command:
1. ✅ Commits your changes
2. ✅ Pushes to GitHub
3. ✅ Pulls on RPi
4. ✅ Runs detection on RPi
5. ✅ Retrieves output files back to your laptop

**Everything in one command!** 🎉

---

## 🎮 Usage Examples

### Example 1: Quick Test
```bash
# Edit code on laptop
vim DEMO_RPI.py

# Deploy and test (30 seconds)
./quick_deploy.sh test "Improved detection"

# Check results
ls rpi_output_retrieved/
```

### Example 2: Long Test
```bash
# Edit code
vim DEMO_RPI.py

# Deploy in headless mode (saves video)
./quick_deploy.sh headless "Testing for 10 minutes"

# Results automatically retrieved
cat rpi_output_retrieved/session_*.json
```

### Example 3: Just Sync (No Run)
```bash
# Only sync changes, don't run
./sync_to_rpi.sh "Updated model"

# Later, run manually
ssh pi@raspberrypi.local
cd ~/plankton
python3 DEMO_RPI.py
```

---

## 🔄 Complete Development Cycle

### 1. Edit on Laptop
Use your favorite editor:
- VS Code
- PyCharm
- Vim
- Any editor!

### 2. Test Locally (Optional)
```bash
python3 DEMO.py --source "Real_Time_Vids/good flow.mov"
```

### 3. Deploy to RPi
```bash
./quick_deploy.sh test "Your change"
```

### 4. Check Results
```bash
# Results are in rpi_output_retrieved/
ls -lh rpi_output_retrieved/

# View session data
cat rpi_output_retrieved/session_*.json

# View video (if saved)
open rpi_output_retrieved/rpi_detection_*.mp4
```

### 5. Repeat!

**That's the complete cycle!** 🔄

---

## 🎯 Your Workflow Now

```
┌─────────────────────────────────────────┐
│  1. EDIT CODE ON LAPTOP                 │
│     (Comfortable IDE, big screen)       │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  2. RUN: ./quick_deploy.sh test         │
│     (One command!)                      │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  3. AUTOMATIC:                          │
│     • Git commit & push                 │
│     • Pull on RPi                       │
│     • Run detection                     │
│     • Retrieve results                  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  4. CHECK RESULTS ON LAPTOP             │
│     rpi_output_retrieved/               │
└─────────────────────────────────────────┘
```

**Seamless! No manual steps!** ✨

---

## 🔥 Advanced Features

### Auto-Sync Mode
```bash
# Start watching for changes
./watch_rpi.sh

# Now edit files - they auto-sync to GitHub!
# RPi will pull automatically
```

### Manual Control
```bash
# Just sync (don't run)
./sync_to_rpi.sh "My changes"

# Just run (already synced)
./run_on_rpi.sh interactive

# Just retrieve output
./get_rpi_output.sh
```

### Different Run Modes
```bash
# Interactive (see output on RPi monitor)
./quick_deploy.sh interactive

# Headless (background, saves video)
./quick_deploy.sh headless

# Test (30 seconds only)
./quick_deploy.sh test
```

---

## 📋 Command Cheat Sheet

```bash
# ONE-TIME SETUP
./setup_rpi_git.sh              # Setup git on RPi

# DAILY USE (PICK ONE)
./quick_deploy.sh test          # ALL-IN-ONE (recommended!)
./sync_to_rpi.sh               # Just sync
./run_on_rpi.sh test           # Just run
./get_rpi_output.sh            # Just retrieve

# DEVELOPMENT
./watch_rpi.sh                 # Auto-sync mode

# VIEW LIVE
./view_rpi_live.sh             # See RPi camera on laptop
```

---

## 🎓 Real Example Session

```bash
# Morning: Start work
cd ~/Documents/university/SIH/plank-1

# Edit detection code
vim DEMO_RPI.py
# ... make changes ...

# Test locally first
python3 DEMO.py --source "Real_Time_Vids/good flow.mov"
# Looks good!

# Deploy to RPi
./quick_deploy.sh test "Improved confidence threshold"

# Output:
# ========================================
# ⚡ QUICK DEPLOY & RUN
# ========================================
#
# 1️⃣ Syncing to RPi...
# ✅ Pushed to GitHub
# ✅ Pulled on RPi
#
# 2️⃣ Running on RPi...
# 🚀 Running 30-second test...
# ✅ Detection complete
#
# 📥 Retrieving output files...
# ✅ Files retrieved
#
# ✅ Quick deploy complete!
# ========================================

# Check results
ls rpi_output_retrieved/
# session_20251211_143022.json
# rpi_detection_20251211_143022.mp4

cat rpi_output_retrieved/session_*.json
# Shows detection stats!

# Done! 🎉
```

---

## 💡 Pro Tips

### 1. Create Aliases

Add to `~/.bashrc` or `~/.zshrc`:
```bash
alias deploy='./quick_deploy.sh'
alias sync='./sync_to_rpi.sh'
alias rget='./get_rpi_output.sh'
```

Then:
```bash
deploy test "My change"  # So easy!
```

### 2. Test Locally First

Always test on laptop before deploying:
```bash
python3 DEMO.py  # Quick local test
```

Saves time if there are obvious bugs!

### 3. Use Descriptive Commit Messages

```bash
./quick_deploy.sh test "Fixed bounding box color bug"
./quick_deploy.sh test "Optimized for low light"
./quick_deploy.sh test "Added new species class"
```

Helps track changes in git history!

### 4. Keep RPi Running

Leave RPi powered on with SSH enabled. Makes deployment instant!

---

## 🐛 Troubleshooting

### "Connection refused"
```bash
# Check RPi is on and connected
ping raspberrypi.local

# If fails, find IP address and update .rpi_config
# Check router or use: arp -a
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x *.sh
```

### "Git push failed"
```bash
# Add SSH key to GitHub
cat ~/.ssh/id_rsa.pub
# Add at: https://github.com/settings/keys
```

### "No such file or directory"
```bash
# Run setup first
./setup_rpi_git.sh
```

---

## ✅ Quick Checklist

**One-Time Setup:**
- [ ] Edit `.rpi_config` with RPi details
- [ ] Run `./setup_rpi_git.sh`
- [ ] Test with `./quick_deploy.sh test`

**Every Development Session:**
- [ ] Edit code on laptop
- [ ] Test locally (optional): `python3 DEMO.py`
- [ ] Deploy: `./quick_deploy.sh test "What changed"`
- [ ] Check results: `ls rpi_output_retrieved/`

---

## 🎉 You're Done!

**You now have:**
- ✅ Seamless laptop → RPi workflow
- ✅ One-command deployment
- ✅ Automatic result retrieval
- ✅ Git version control
- ✅ Professional development setup

**Just use:**
```bash
./quick_deploy.sh test "Your change"
```

**And you're golden!** 🚀

---

## 📞 Quick Reference

**Most Common Commands:**
```bash
# Deploy and test (use this 90% of the time)
./quick_deploy.sh test "Description"

# Long running test with video
./quick_deploy.sh headless "Long test"

# Just sync code
./sync_to_rpi.sh "Changes"

# Get latest results
./get_rpi_output.sh
```

**That's all you need!** 🎯

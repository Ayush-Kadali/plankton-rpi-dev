# 🔄 Development Workflow Guide

## Perfect Laptop ↔️ Raspberry Pi Workflow

---

## 🎯 Overview

This workflow lets you:
1. **Edit code on your laptop** (comfortable IDE)
2. **Push to GitHub** (version control)
3. **Auto-sync to RPi** (one command)
4. **Run on RPi** (test on actual hardware)
5. **Get results back** (automatic retrieval)

**All in seconds!** ⚡

---

## 🚀 Quick Setup (One Time)

### 1. Configure RPi Settings

Edit `.rpi_config`:
```bash
RPI_USER="pi"              # Your RPi username
RPI_HOST="raspberrypi.local"  # RPi hostname or IP
RPI_PROJECT_DIR="~/plankton"
GIT_BRANCH="main"
```

### 2. Setup Git on RPi

```bash
./setup_rpi_git.sh
```

This will:
- Generate SSH key on RPi
- Help you add it to GitHub
- Clone the repository
- Run initial setup

**Do this once, then you're set forever!**

---

## 💻 Daily Workflow

### Method 1: Quick Deploy (Recommended!)

**One command does everything:**

```bash
./quick_deploy.sh test "Your commit message"
```

This will:
1. ✅ Commit your changes
2. ✅ Push to GitHub
3. ✅ Pull on RPi
4. ✅ Run detection on RPi
5. ✅ Retrieve output files

**Boom! Done!** 🎉

### Method 2: Step-by-Step (More Control)

#### Step 1: Sync Changes
```bash
./sync_to_rpi.sh "Fixed detection bug"
```

Commits, pushes to GitHub, and pulls on RPi.

#### Step 2: Run on RPi
```bash
# Interactive mode (with display on RPi)
./run_on_rpi.sh interactive

# Headless mode (no display, saves output)
./run_on_rpi.sh headless

# Quick test (30 seconds)
./run_on_rpi.sh test
```

#### Step 3: Get Results
```bash
./get_rpi_output.sh
```

Downloads all output files to `rpi_output_retrieved/`

---

## 🔥 Advanced Workflows

### Auto-Sync Mode (Development)

Watch for changes and auto-sync:

```bash
./watch_rpi.sh
```

Now every time you save a Python file, it automatically:
1. Commits
2. Pushes to GitHub
3. Pulls on RPi

**Perfect for rapid development!** 🚀

### Live View (Real-time)

See RPi camera output on your laptop:

```bash
# Method 1: X11 forwarding (requires X server)
./view_rpi_live.sh x11

# Method 2: VNC (requires VNC viewer)
./view_rpi_live.sh vnc

# Method 3: Video streaming (requires ffmpeg)
./view_rpi_live.sh
```

---

## 📋 Common Scenarios

### Scenario 1: Quick Test
```bash
# Edit DEMO_RPI.py on laptop
vim DEMO_RPI.py

# Deploy and test
./quick_deploy.sh test "Testing new feature"

# Check output
ls rpi_output_retrieved/
```

### Scenario 2: Long Running Detection
```bash
# Sync
./sync_to_rpi.sh "Ready for long test"

# Run headless (saves video)
./run_on_rpi.sh headless no  # 'no' = don't auto-retrieve

# Later, retrieve output
./get_rpi_output.sh
```

### Scenario 3: Rapid Development
```bash
# Terminal 1: Auto-sync
./watch_rpi.sh

# Terminal 2: Edit files
vim DEMO_RPI.py
# Changes auto-sync!

# Terminal 3: Run on RPi
ssh pi@raspberrypi.local
cd ~/plankton
python3 DEMO_RPI.py
```

### Scenario 4: Multiple RPis
```bash
# Copy config for RPi #2
cp .rpi_config .rpi_config_2
# Edit with different IP

# Use specific config
RPI_HOST="192.168.1.102" ./sync_to_rpi.sh
```

---

## 🎮 Command Reference

### Sync Commands

```bash
# Basic sync
./sync_to_rpi.sh

# With custom message
./sync_to_rpi.sh "Fixed bug in detection"

# Auto-sync mode
./watch_rpi.sh
```

### Run Commands

```bash
# Interactive (see output on RPi)
./run_on_rpi.sh interactive

# Headless (background, saves video)
./run_on_rpi.sh headless

# Test mode (30 seconds)
./run_on_rpi.sh test

# Skip auto-retrieve
./run_on_rpi.sh headless no
```

### Retrieve Commands

```bash
# Get all output files
./get_rpi_output.sh

# Then view them
ls rpi_output_retrieved/
```

### Quick Deploy

```bash
# Test mode (default)
./quick_deploy.sh

# Headless mode
./quick_deploy.sh headless

# With custom message
./quick_deploy.sh test "Testing new model"
```

---

## 🔧 Configuration

### Edit RPi Settings

```bash
nano .rpi_config
```

### Multiple Configurations

```bash
# Create configs for different RPis
cp .rpi_config .rpi_config_field
cp .rpi_config .rpi_config_lab

# Use specific config
export RPI_CONFIG=".rpi_config_field"
```

---

## 🐛 Troubleshooting

### SSH Connection Issues

```bash
# Test connection
ssh pi@raspberrypi.local

# If fails, try IP address
ssh pi@192.168.1.100

# Update .rpi_config with working address
```

### Git Push Issues

```bash
# Check if SSH key is added to GitHub
ssh -T git@github.com

# If not, add key from:
cat ~/.ssh/id_rsa.pub
# Add at: https://github.com/settings/keys
```

### RPi Git Pull Fails

```bash
# SSH to RPi
ssh pi@raspberrypi.local

# Reset repository
cd ~/plankton
git fetch origin
git reset --hard origin/main
```

### Permission Denied

```bash
# Make scripts executable
chmod +x *.sh
```

---

## 📊 Workflow Comparison

| Method | Speed | Control | Use Case |
|--------|-------|---------|----------|
| `quick_deploy.sh` | ⚡⚡⚡ | Low | Quick tests |
| Step-by-step | ⚡⚡ | High | Debugging |
| `watch_rpi.sh` | ⚡⚡⚡ | Medium | Active development |
| Manual SSH | ⚡ | Highest | Complex operations |

---

## 💡 Pro Tips

### 1. Use Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias sync='./sync_to_rpi.sh'
alias rrun='./run_on_rpi.sh'
alias rget='./get_rpi_output.sh'
alias deploy='./quick_deploy.sh'
```

Then just:
```bash
deploy test "My change"
```

### 2. SSH Config

Add to `~/.ssh/config`:

```
Host rpi
    HostName raspberrypi.local
    User pi
    IdentityFile ~/.ssh/id_rsa
    ServerAliveInterval 60
```

Then:
```bash
ssh rpi  # Instead of ssh pi@raspberrypi.local
```

### 3. Auto-retrieve in Background

```bash
# Run and retrieve in one go
./run_on_rpi.sh headless yes &
```

### 4. Multiple Sessions

```bash
# Terminal 1: Watch logs
ssh pi@raspberrypi.local 'tail -f ~/plankton/*.log'

# Terminal 2: Run detection
./run_on_rpi.sh headless

# Terminal 3: Monitor output
watch ls -lh rpi_output_retrieved/
```

---

## 🎯 Recommended Workflow

For maximum efficiency:

1. **Start auto-sync:**
   ```bash
   ./watch_rpi.sh
   ```

2. **Edit code on laptop** (VS Code, PyCharm, etc.)

3. **Test locally first:**
   ```bash
   python3 DEMO.py --source "Real_Time_Vids/good flow.mov"
   ```

4. **When ready, test on RPi:**
   ```bash
   # Auto-synced already by watch_rpi.sh!
   ./run_on_rpi.sh test
   ```

5. **Check results:**
   ```bash
   ls rpi_output_retrieved/
   ```

**Repeat steps 2-5 as needed!**

---

## 📦 File Structure

```
plank-1/
├── .rpi_config              # RPi connection settings
├── sync_to_rpi.sh          # Sync changes via git
├── run_on_rpi.sh           # Execute on RPi
├── get_rpi_output.sh       # Retrieve results
├── quick_deploy.sh         # All-in-one
├── setup_rpi_git.sh        # One-time setup
├── watch_rpi.sh            # Auto-sync mode
├── view_rpi_live.sh        # Live camera view
│
├── DEMO.py                 # Laptop version
├── DEMO_RPI.py            # RPi version
│
├── demo_output/           # Laptop outputs (gitignored)
├── rpi_output/            # RPi outputs (gitignored)
└── rpi_output_retrieved/  # Retrieved from RPi (gitignored)
```

---

## ✅ Checklist

Setup (One Time):
- [ ] Edit `.rpi_config` with your RPi details
- [ ] Run `./setup_rpi_git.sh`
- [ ] Test with `./quick_deploy.sh test`

Daily Use:
- [ ] Edit code on laptop
- [ ] Test locally: `python3 DEMO.py`
- [ ] Deploy to RPi: `./quick_deploy.sh test`
- [ ] Check results in `rpi_output_retrieved/`

---

## 🎓 Example Session

```bash
# Morning: Start development
cd ~/Documents/university/SIH/plank-1
./watch_rpi.sh &  # Auto-sync in background

# Edit some files
vim DEMO_RPI.py  # Make changes

# Test locally
python3 DEMO.py --source "Real_Time_Vids/good flow.mov"

# Deploy to RPi (already synced by watch_rpi!)
./run_on_rpi.sh test

# Get results
./get_rpi_output.sh
open rpi_output_retrieved/session_*.json

# Make more changes
vim DEMO_RPI.py  # Auto-syncs!

# Quick deploy again
./quick_deploy.sh headless "Improved detection"

# Done for the day
fg  # Stop watch_rpi.sh
```

---

## 🚀 You're Ready!

**Workflow is set up and ready to use!**

Start with:
```bash
./quick_deploy.sh test "First test"
```

**Happy coding!** 🎉

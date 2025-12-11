# 🌊 Plankton Flow Tracker - Solution Guide

## 🔴 The Problem You Had

Your previous detection system was counting the **same plankton multiple times** as it flowed through the water:

```
Frame 1: Plankton A detected → Count = 1
Frame 2: Plankton A detected → Count = 2  ❌ (Same organism!)
Frame 3: Plankton A detected → Count = 3  ❌ (Same organism!)
```

This happened because you were using **pure detection** without **tracking**.

---

## ✅ The Solution: Object Tracking

The new `realtime_flow_tracker.py` script uses **YOLO + ByteTrack** to:

1. **Detect** plankton in each frame
2. **Track** each plankton across frames with a unique ID
3. **Count** each unique ID only ONCE

```
Frame 1: Plankton A (ID: 1) detected → Count = 1  ✓
Frame 2: Plankton A (ID: 1) tracked  → Count = 1  ✓ (Same ID, no increment)
Frame 3: Plankton A (ID: 1) tracked  → Count = 1  ✓ (Same ID, no increment)
Frame 4: Plankton B (ID: 2) detected → Count = 2  ✓ (New organism!)
```

---

## 🚀 Quick Start

### Method 1: Use the Test Script (Easiest)

```bash
# Run all tests
./test_flow_tracker.sh
```

### Method 2: Manual Command

```bash
# Process a single video
python3 realtime_flow_tracker.py \
    --video "Real_Time_Vids/good flow.mov" \
    --output "results/tracked_output.mp4"
```

### Method 3: Real-Time Camera

```bash
# Use webcam (camera 0)
python3 realtime_flow_tracker.py --video 0
```

---

## 📊 What You'll See

### On-Screen Display:
- **Bounding boxes** with unique Track IDs (ID: 1, ID: 2, etc.)
- **Flow direction arrows** (→ ← ↑ ↓)
- **Movement trails** showing where each plankton traveled
- **UNIQUE COUNT** - the actual number of different organisms
- **Species breakdown** in real-time

### Color Coding:
- **Thick borders** = NEW organism just detected
- **Thin borders** = Already tracked organism
- **Different colors** per species
- **Trail lines** showing movement path

---

## 🎯 Features

### 1. **Deduplication**
Each plankton gets a unique ID. Even if it appears in 100 frames, it's counted once.

### 2. **Flow Direction Detection**
The tracker analyzes movement patterns to show which direction plankton are flowing:
- → (right)
- ← (left)
- ↑ (up)
- ↓ (down)

### 3. **Species Tracking**
Separate counts for each species:
```
Copepod: 15
Diatom: 8
Dinoflagellate: 3
```

### 4. **Fast Processing**
- Uses ByteTrack (lightweight, fast)
- Can process 30+ FPS on modern hardware
- Real-time capable

---

## 🔧 Command Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--video` | Video file or camera index | Required | `"test.mov"` or `0` |
| `--model` | Path to YOLO model | `Downloaded models/best.pt` | `"models/custom.pt"` |
| `--conf` | Confidence threshold | `0.25` | `0.3` |
| `--tracker` | Tracker algorithm | `bytetrack.yaml` | `botsort.yaml` |
| `--output` | Output video path | None (no save) | `"results/out.mp4"` |
| `--no-display` | Headless mode (no window) | False | Flag |
| `--max-frames` | Limit frames (for testing) | None (all) | `300` |

---

## 📝 Usage Examples

### Basic Usage
```bash
# Process with default settings
python3 realtime_flow_tracker.py --video "Real_Time_Vids/good flow.mov"
```

### Save Output Video
```bash
# Process and save annotated video
python3 realtime_flow_tracker.py \
    --video "Real_Time_Vids/trial.mov" \
    --output "results/tracked_trial.mp4"
```

### Adjust Confidence
```bash
# Lower confidence to detect more (but more false positives)
python3 realtime_flow_tracker.py \
    --video "test.mov" \
    --conf 0.2

# Higher confidence for more accuracy (but might miss some)
python3 realtime_flow_tracker.py \
    --video "test.mov" \
    --conf 0.4
```

### Different Tracker
```bash
# Use BoT-SORT instead of ByteTrack (more accurate but slower)
python3 realtime_flow_tracker.py \
    --video "test.mov" \
    --tracker botsort.yaml
```

### Headless Mode (No Display)
```bash
# Run without showing window (for servers/automation)
python3 realtime_flow_tracker.py \
    --video "test.mov" \
    --output "results/out.mp4" \
    --no-display
```

### Test with Limited Frames
```bash
# Process only first 100 frames for quick testing
python3 realtime_flow_tracker.py \
    --video "test.mov" \
    --max-frames 100
```

---

## ⌨️ Keyboard Controls (During Playback)

| Key | Action |
|-----|--------|
| `q` | Quit/Stop processing |
| `r` | Reset all counts to zero |

---

## 📈 Output Summary

After processing, you'll see a summary like:

```
================================================================================
PROCESSING COMPLETE
================================================================================
Frames processed: 450
Total time: 15.2s
Average FPS: 29.6
Average inference: 25.3ms (39.5 FPS)

================================================================================
UNIQUE ORGANISMS DETECTED: 23
================================================================================

SPECIES BREAKDOWN:
  Copepod........................   15 ( 65.2%)
  Diatom.........................    5 ( 21.7%)
  Dinoflagellate.................    3 ( 13.0%)
```

---

## 🤔 How It Works (Technical)

### 1. YOLO Detection
Each frame is passed through your YOLO model to detect bounding boxes.

### 2. ByteTrack Algorithm
ByteTrack associates detections across frames:
- Uses IoU (Intersection over Union) to match boxes
- Handles occlusions and missed detections
- Assigns persistent IDs

### 3. Deduplication
```python
if track_id not in self.counted_organisms:
    self.counted_organisms.add(track_id)
    self.total_count += 1  # Count only once!
```

### 4. Flow Direction
Analyzes the last 10 positions of each track to determine movement direction.

---

## 🎨 Customization

### Change Colors
Edit the `_hsv_to_bgr()` method to customize class colors.

### Adjust Trail Length
Change `maxlen` in line 29:
```python
self.track_positions = defaultdict(lambda: deque(maxlen=10))  # Change 10 to more/less
```

### Modify Display Overlay
Edit the `_add_overlay()` method to show different stats.

---

## 🐛 Troubleshooting

### Issue: "No tracking IDs available"
**Cause:** Tracker initialization failed
**Solution:** Make sure you have Ultralytics installed:
```bash
pip install ultralytics
```

### Issue: Counts seem wrong
**Possible causes:**
1. **Confidence too low** → Increase `--conf` (try 0.3 or 0.4)
2. **Plankton moving too fast** → Video might be too high-speed
3. **Occlusions** → Try `--tracker botsort.yaml` (better with occlusions)

### Issue: Slow processing
**Solutions:**
1. Use a smaller YOLO model (yolov8n instead of yolov8x)
2. Reduce video resolution
3. Use ByteTrack instead of BoT-SORT
4. Process every 2nd or 3rd frame

---

## 📊 Comparing Results

### Before (No Tracking)
```bash
python3 compare_selected_videos.py
# Result: 150 detections (many duplicates!)
```

### After (With Tracking)
```bash
python3 realtime_flow_tracker.py --video "same_video.mov"
# Result: 23 unique organisms (accurate!)
```

---

## 🔬 For Your Demo/Judges

1. **Show the problem first:**
   - Run old detection → Show inflated counts

2. **Show the solution:**
   - Run `realtime_flow_tracker.py` → Show unique tracking
   - Point out the Track IDs
   - Show flow direction arrows

3. **Highlight features:**
   - Real-time processing
   - Accurate counts
   - Species breakdown
   - Flow awareness

---

## 🎯 Next Steps (Optional Improvements)

If you have time after getting this working:

1. **Virtual Counting Line**
   - Add a line in the frame
   - Count only when plankton crosses the line
   - Prevents counting plankton that exit and re-enter

2. **Concentration Calculation**
   - Track flow rate from your syringe pump
   - Calculate organisms per mL

3. **Export to Database**
   - Save each unique organism's data
   - Track timestamps, positions, confidences

4. **Re-identification (Re-ID)**
   - If a plankton exits and re-enters, recognize it
   - Use appearance features (advanced)

---

## 📚 Additional Resources

- **Ultralytics Tracking Docs:** https://docs.ultralytics.com/modes/track/
- **ByteTrack Paper:** https://arxiv.org/abs/2110.06864
- **BoT-SORT Paper:** https://arxiv.org/abs/2206.14651

---

## ✅ Summary

**Old way (Detection only):**
- Same plankton counted multiple times ❌
- No tracking ❌
- Inflated counts ❌

**New way (Detection + Tracking):**
- Each plankton counted once ✅
- Unique IDs for tracking ✅
- Accurate counts ✅
- Flow direction ✅
- Real-time capable ✅

---

**Questions?** Check the code comments in `realtime_flow_tracker.py` - it's well documented!

**Good luck with your demo!** 🚀

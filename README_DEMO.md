# 🔬 Plankton Detection System - Demo Guide

**Fast, Simple, Hardware-Ready Detection System**

---

## 🚀 Quick Start (5 Minutes!)

### Option 1: Interactive Launcher (EASIEST!)
```bash
python3 LAUNCH_DEMO.py
```
Follow the menu to select your demo mode!

### Option 2: Direct Commands

**Live Camera Detection:**
```bash
python3 DEMO.py
```

**Video File Detection:**
```bash
python3 DEMO.py --source "Real_Time_Vids/only_water_stream.mov"
```

**View Results on Map:**
```bash
python3 MAP_VIEWER.py --open
```

---

## 📋 What's Included

### Core Files (Use These!)

1. **LAUNCH_DEMO.py** - Interactive menu launcher
   - Live camera detection
   - Video file processing
   - Map visualization
   - Quick testing

2. **DEMO.py** - Real-time detection engine
   - Works with webcam or video files
   - Shows detections with bounding boxes
   - Saves session data automatically

3. **MAP_VIEWER.py** - Local map visualization
   - No cloud required!
   - Interactive HTML map
   - Shows all detection sessions

---

## 🎯 Detection Features

### Detected Species
- Platymonas
- Chlorella
- Dunaliella salina
- Effrenium
- Porphyridium
- Haematococcus

### Real-time Stats
- FPS counter
- Total detections
- Species breakdown
- Bounding boxes with confidence scores

---

## 💾 Output Files

All outputs are saved to `demo_output/`:
- `session_YYYYMMDD_HHMMSS.json` - Detection data
- `detection_YYYYMMDD_HHMMSS.mp4` - Recorded video (if --save used)
- `screenshot_YYYYMMDD_HHMMSS.jpg` - Screenshots (press 's' during detection)

---

## ⌨️ Controls

During detection:
- **'q'** - Quit
- **'s'** - Save screenshot

---

## 🔧 Advanced Usage

### Adjust Confidence Threshold
```bash
# More sensitive (more detections)
python3 DEMO.py --conf 0.10

# Less sensitive (fewer false positives)
python3 DEMO.py --conf 0.25
```

### Save Output Video
```bash
python3 DEMO.py --save
```

### Use Different Model
```bash
python3 DEMO.py --model "Downloaded models/yolov8n.pt"
```

---

## 🗺️ Map Visualization

The map viewer creates a local HTML file showing:
- Detection locations (using preset test locations)
- Number of detections per session
- Species breakdown
- Session timestamps

**Note:** Locations are currently set to default test coordinates. When integrated with hardware GPS, real coordinates will be used automatically.

---

## 🔌 Hardware Integration Notes

### For Raspberry Pi Camera:
When you connect your hardware camera, the system will automatically use it:
```bash
python3 DEMO.py --source 0
```

### For USB Cameras:
Try different camera indices:
```bash
python3 DEMO.py --source 1  # or 2, 3, etc.
```

### For GPS Integration:
GPS coordinates will be automatically added to session JSON files when GPS module is connected. The MAP_VIEWER.py will then use real coordinates instead of defaults.

---

## ⚡ Performance Tips

1. **Lower resolution = faster processing**
   - Cameras typically default to lower res automatically

2. **Skip frames for faster processing:**
   - Modify DEMO.py if needed, or process every 2nd frame

3. **Adjust confidence:**
   - Lower (0.10) = more detections but more false positives
   - Higher (0.25) = fewer but more accurate detections

---

## 📊 Session Data Format

Each session JSON contains:
```json
{
  "start_time": "2025-12-11T...",
  "end_time": "2025-12-11T...",
  "duration_seconds": 45.2,
  "frames_processed": 1234,
  "total_detections": 567,
  "species_counts": {
    "Chlorella": 234,
    "Platymonas": 189,
    ...
  }
}
```

---

## 🐛 Troubleshooting

### Camera not opening?
```bash
# Test available cameras
ls /dev/video*

# Try different camera indices
python3 DEMO.py --source 1
```

### No detections?
- Lower confidence: `--conf 0.10`
- Check if plankton are visible in frame
- Ensure lighting is adequate

### ImportError?
```bash
# Install dependencies
python3 -m pip install ultralytics opencv-python folium
```

---

## 📦 Dependencies

Minimal requirements:
- Python 3.7+
- ultralytics (YOLO)
- opencv-python
- folium (for map viewer)

All installed automatically with the demo!

---

## 🎓 For Judges/Demo

**Complete demo flow (5 minutes):**

1. Start launcher:
   ```bash
   python3 LAUNCH_DEMO.py
   ```

2. Select "Quick Test" (option 4)
   - Shows real-time detection
   - Automatic species counting
   - Bounding boxes and labels

3. Stop after ~30 seconds (press 'q')

4. View map (option 3)
   - Opens interactive map in browser
   - Shows detection statistics

**That's it! Complete plankton detection and visualization!**

---

## 🚀 Next Steps

After demo:
1. Connect hardware camera
2. Add GPS module for real locations
3. Deploy to field
4. Collect real-world data!

---

## 📞 System Status

✅ Detection model: Working
✅ Real-time processing: Working
✅ Local data storage: Working
✅ Map visualization: Working
✅ Hardware ready: Yes
❌ Cloud integration: Removed (will add later)

**Ready for hardware integration and field testing!**

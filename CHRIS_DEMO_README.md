# Chris Model Real-Time Demo

Run the best_chris YOLO model on videos with real-time overlay, FPS counter, and full RPi compatibility.

## Features

- ✅ Real-time plankton detection with Chris YOLO model
- ✅ Confidence threshold: 0.1 (configurable)
- ✅ FPS counter prominently displayed
- ✅ Bounding boxes with class labels and confidence scores
- ✅ Live statistics overlay (detections, class breakdown)
- ✅ Raspberry Pi compatible (headless mode supported)
- ✅ Save output videos
- ✅ Works with webcam or video files

## Quick Start

### On Desktop (with display)

```bash
# Run on demo video
python run_chris_demo.py --video "results/chris_model_eval/annotated_videos/good_flow_annotated_20251211_144324.mp4" --conf 0.1 --save

# Run on another demo video
python run_chris_demo.py --video "results/chris_model_eval/annotated_videos/v4_try_2_annotated_20251211_145648.mp4" --conf 0.1 --save

# Run with webcam
python run_chris_demo.py --video 0 --conf 0.1
```

### On Raspberry Pi

```bash
# With display
python rpi_chris_demo.py --video test_video.mp4 --model new_chris.pt --conf 0.1 --save

# Headless mode (no display, just processing)
python rpi_chris_demo.py --video 0 --conf 0.1 --save --headless

# With RPi camera
python rpi_chris_demo.py --video 0 --conf 0.1
```

## Available Models

The demo uses YOLO models located in:
- `Downloaded models/new_chris.pt` (default)
- `Downloaded models/chris_best.pt`
- `Downloaded models/best.pt`

## Command Line Options

### run_chris_demo.py (Full-featured)

```bash
python run_chris_demo.py [OPTIONS]

Options:
  --video PATH/INDEX    Video file path or camera index (0, 1, etc.) [REQUIRED]
  --model PATH          Path to YOLO model file
                        (default: "Downloaded models/new_chris.pt")
  --conf FLOAT          Confidence threshold (default: 0.1)
  --save                Save annotated video output
  --no-display          Run without display (headless mode)
```

### rpi_chris_demo.py (RPi-optimized)

```bash
python rpi_chris_demo.py [OPTIONS]

Options:
  --video PATH/INDEX    Video file or camera index (default: 0)
  --model PATH          Model path (default: new_chris.pt)
  --conf FLOAT          Confidence threshold (default: 0.1)
  --save                Save output video
  --headless            Run without display
```

## Keyboard Controls (when display is enabled)

- **`q`** - Quit
- **`s`** - Save snapshot (run_chris_demo.py only)
- **`SPACE`** - Pause/Resume (run_chris_demo.py only)

## What's Displayed

### On-screen Overlay:
1. **Title**: "Chris Model - Real-Time Detection"
2. **FPS**: Current frames per second (large, green)
3. **Confidence**: Current threshold setting
4. **Frame Number**: Current frame being processed
5. **Time Elapsed**: Total processing time
6. **Total Detections**: Cumulative detection count
7. **Class Breakdown**: Count per plankton class (color-coded)

### Bounding Boxes:
- Color-coded by class
- Label shows: `ClassName: 0.XX` (confidence score)

## Output Files

When `--save` is used, videos are saved to:
- Desktop version: `results/chris_demo_YYYYMMDD_HHMMSS.mp4`
- RPi version: `results/rpi_demo_YYYYMMDD_HHMMSS.mp4`

Snapshots (desktop only): `results/snapshot_NNNN.jpg`

## Performance

### Desktop:
- Expected FPS: 5-10 FPS (depends on hardware)
- GPU acceleration: Automatic if available

### Raspberry Pi 4/5:
- Expected FPS: 2-5 FPS
- Optimized for low memory usage
- Works with or without display

## Examples

### Example 1: Quick Demo on Existing Video
```bash
python run_chris_demo.py \
  --video "results/chris_model_eval/annotated_videos/good_flow_annotated_20251211_144324.mp4" \
  --conf 0.1 \
  --save
```

### Example 2: Low Confidence Detection
```bash
python run_chris_demo.py \
  --video "path/to/video.mp4" \
  --conf 0.05 \
  --save
```

### Example 3: RPi with Camera (Headless)
```bash
# On Raspberry Pi without monitor
python rpi_chris_demo.py \
  --video 0 \
  --conf 0.1 \
  --save \
  --headless
```

### Example 4: Different Model
```bash
python run_chris_demo.py \
  --video "path/to/video.mp4" \
  --model "Downloaded models/chris_best.pt" \
  --conf 0.2
```

## Troubleshooting

### "Cannot open video"
- Check video path is correct
- For camera: try different indices (0, 1, 2...)
- Ensure video file exists and is readable

### Low FPS
- Reduce video resolution
- Increase confidence threshold
- Use RPi-optimized version on Pi
- Close other applications

### Model not found
- Check model path: `ls -la "Downloaded models/"`
- Use absolute path to model file
- Ensure .pt file exists

### On RPi: Display issues
- Use `--headless` flag to run without display
- Check X11 forwarding if using SSH
- Use `DISPLAY=:0` if needed

## System Requirements

### Desktop:
- Python 3.8+
- OpenCV (cv2)
- Ultralytics (YOLO)
- NumPy

### Raspberry Pi:
- Raspberry Pi 4 or 5 recommended
- 4GB+ RAM recommended
- Same Python packages as desktop
- Optional: Picamera2 for camera support

## Installation

```bash
# Install dependencies
pip install opencv-python ultralytics numpy

# For RPi with camera
pip install picamera2
```

## Tips for Best Results

1. **Lighting**: Ensure good lighting for better detection
2. **Focus**: Keep organisms in focus
3. **Confidence**: Start with 0.1, adjust based on results
4. **Resolution**: Lower resolution = faster processing
5. **RPi**: Use headless mode for better performance
6. **Save**: Always save output for review/demonstration

## Demo Videos Available

The following demo videos are ready to use:
1. `results/chris_model_eval/annotated_videos/good_flow_annotated_20251211_144324.mp4` (59 MB, 121s)
2. `results/chris_model_eval/annotated_videos/v4_try_2_annotated_20251211_145648.mp4` (108 MB, ~180s)

## Next Steps

1. Test with your own videos
2. Deploy to Raspberry Pi
3. Adjust confidence threshold for your use case
4. Integrate with data logging system
5. Add timestamp and location metadata

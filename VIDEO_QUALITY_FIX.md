# How to Fix Video Quality for Better Detection

## The #1 Problem: Sensor Dust

**Why dust is detected**: It's SHARP and CLEAR (on the sensor, very close to lens)
**Why plankton isn't**: It's BLURRY and OUT OF FOCUS (in the water, far from sensor)

## Step-by-Step Video Quality Improvement

### 1. Clean Camera Sensor (CRITICAL!)

**What you need**:
- Air blower (rocket blower) or compressed air
- Microfiber cloth
- Lens cleaning solution (optional)

**Steps**:
```
1. Remove camera from microscope
2. Look at sensor/lens - can you see dust spots?
3. Use air blower to blow dust off gently
4. If stubborn spots, use lens cleaning solution + microfiber cloth
5. Clean microscope objective lens too!
6. Reattach camera
```

**Test immediately**:
```bash
# Take a test photo
python -c "import cv2; cap = cv2.VideoCapture(0); ret, img = cap.read(); cv2.imwrite('test_clean.jpg', img); cap.release(); print('Saved test_clean.jpg')"

# Check test_clean.jpg - is dust gone?
open test_clean.jpg
```

### 2. Achieve Sharp Focus

**The problem**: Blurry organisms = invisible to model

**Solution**:
```
1. Place sample under microscope
2. Start with LOW magnification
3. Adjust focus knob SLOWLY
4. Look for moment when edges become sharp
5. Fine-tune until maximum sharpness
6. Lock focus (don't touch during recording)
```

**How to verify good focus**:
- Capture one frame
- Zoom in on computer
- Check if edges are crisp
- If blurry, refocus and try again

**Command to test focus**:
```bash
# Capture test frame
python inspect_video.py --video "Real_Time_Vids/only_water_stream.mov" --num-frames 1

# Check it
open results/extracted_frames/frame_00000.jpg

# Is it SHARP? If no, REFOCUS and record again
```

### 3. Optimize Lighting

**Problems with current lighting**:
- Too dim → Blurry image
- Uneven → Parts too dark
- Too bright → Washed out

**Solution**:
```
1. Add MORE light (use microscope lamp)
2. Adjust lamp position for even illumination
3. No shadows or dark spots
4. Brightness should be high but not washed out
```

**Test lighting**:
```bash
# Capture frame, check brightness
python -c "import cv2; cap = cv2.VideoCapture(0); ret, img = cap.read(); cv2.imwrite('test_light.jpg', img); cap.release()"
open test_light.jpg

# Should be bright, clear, evenly lit
```

### 4. Stabilize Camera

**Problem**: Movement causes blur

**Solution**:
```
1. Mount camera FIRMLY to microscope
2. No wobbling or loose parts
3. Don't touch during recording
4. Place on stable surface
5. Avoid vibrations
```

### 5. Optimize Camera Settings

**If using USB camera**:
```python
# Create optimal_camera_setup.py
import cv2

cap = cv2.VideoCapture(0)

# Try these settings
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # Disable autofocus
cap.set(cv2.CAP_PROP_EXPOSURE, -5)  # Adjust exposure
cap.set(cv2.CAP_PROP_BRIGHTNESS, 128)
cap.set(cv2.CAP_PROP_CONTRAST, 128)
cap.set(cv2.CAP_PROP_SHARPNESS, 128)

# Capture test
ret, img = cap.read()
cv2.imwrite('optimized_test.jpg', img)
cap.release()

print("Check optimized_test.jpg")
```

```bash
python optimal_camera_setup.py
open optimized_test.jpg
```

### 6. Record New High-Quality Video

**Once everything above is done**:

```bash
# Option 1: Record with OpenCV
python -c "
import cv2
import time

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('Real_Time_Vids/high_quality_stream.mp4', fourcc, 30.0, (1280, 720))

print('Recording for 60 seconds...')
start = time.time()
while time.time() - start < 60:
    ret, frame = cap.read()
    if ret:
        out.write(frame)

cap.release()
out.release()
print('Done! Saved to Real_Time_Vids/high_quality_stream.mp4')
"
```

**Option 2: Use your phone/camera**:
```
1. Position phone over microscope eyepiece
2. Focus carefully
3. Record in HIGHEST quality
4. Transfer video to computer
5. Use that instead
```

## Quality Checklist

Before recording, verify:

- [ ] Camera sensor is clean (no dust spots)
- [ ] Microscope lens is clean
- [ ] Focus is SHARP (test with still image)
- [ ] Lighting is bright and even
- [ ] Camera is stable (no movement)
- [ ] Sample has visible organisms

**Quick test**:
```bash
# Capture one frame
python inspect_video.py --video 0 --num-frames 1

# Check quality
open results/extracted_frames/frame_00000.jpg

# If organisms are clear and sharp → GOOD TO GO
# If blurry → FIX FOCUS
# If dark spots → CLEAN SENSOR
```

## After Recording New Video

```bash
# Test with YOLO immediately
python yolo_realtime.py \
    --model "Downloaded models/best.pt" \
    --camera "Real_Time_Vids/high_quality_stream.mp4" \
    --conf 0.25 \
    --save-video

# Should see MUCH better results!
```

## If You Can't Fix Video Quality

### Plan B: Demo with Alternative Content

**Use what works**:
```bash
# Your test images are already good quality
python yolo_realtime.py \
    --model "Downloaded models/best.pt" \
    --camera "test_images/WhatsApp Image 2025-12-09 at 04.58.26.jpeg" \
    --conf 0.25
```

**Or create slideshow from test images**:
```bash
# Process all test images
for img in test_images/*.jpeg; do
    echo "Processing $img"
    python yolo_realtime.py --model "Downloaded models/best.pt" --camera "$img" --conf 0.25
done
```

## Expected Results After Improvements

**Before (current)**:
- Dust detected as plankton ❌
- Real organisms missed ❌
- Blurry, unclear ❌

**After (with quality improvements)**:
- Real organisms detected ✅
- Accurate species labels ✅
- Clear, sharp ✅
- Dust filtered out ✅

## Time Required

| Task | Time | Impact |
|------|------|--------|
| Clean sensor | 5-10 min | 🔥 HIGH |
| Improve focus | 10-15 min | 🔥 HIGH |
| Better lighting | 5 min | 🔥 MEDIUM |
| Stabilize camera | 5 min | 🔥 MEDIUM |
| Re-record | 5 min | 🔥 HIGH |
| **TOTAL** | **30-40 min** | **CRITICAL** |

## The Bottom Line

**30 minutes of hardware fixes** > **Hours of software tuning**

The model is fine. The code is fine. The video quality is the issue.

**Fix the video, everything else will work!**

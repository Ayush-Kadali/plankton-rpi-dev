# Judge Demo - Quick Start Guide

## 🎯 Run the Demo in 1 Command

### Option 1: Use One of Your Test Videos (Recommended)
```bash
python demo_for_judges.py --source "Real_Time_Vids/good flow.mov"
```

### Option 2: Use Webcam (if available)
```bash
python demo_for_judges.py --source 0
```

### Option 3: Fullscreen Mode (Best for Presentation)
```bash
python demo_for_judges.py --source "Real_Time_Vids/good flow.mov" --fullscreen
```

---

## ⌨️ Controls During Demo

| Key | Action |
|-----|--------|
| **Q** | Quit demo |
| **F** | Toggle fullscreen |
| **S** | Save current frame |

---

## 🎨 What Judges Will See

- ✅ **Live video** with real-time processing
- ✅ **Bounding boxes** around detected plankton
- ✅ **Class labels** and confidence scores
- ✅ **Live FPS counter**
- ✅ **Detection statistics**
- ✅ **Clean, professional overlay**

---

## 📊 Available Test Videos

```bash
# Good quality flow
python demo_for_judges.py --source "Real_Time_Vids/good flow.mov"

# Alternative
python demo_for_judges.py --source "Real_Time_Vids/v4 try 2.mov"
```

---

## 🎛️ Adjust Detection Sensitivity

### Lower confidence = More detections
```bash
python demo_for_judges.py --source "Real_Time_Vids/good flow.mov" --conf 0.15
```

### Higher confidence = Fewer, more accurate detections
```bash
python demo_for_judges.py --source "Real_Time_Vids/good flow.mov" --conf 0.4
```

---

## 🚀 Recommended Demo Command

```bash
python demo_for_judges.py \
    --source "Real_Time_Vids/good flow.mov" \
    --conf 0.25 \
    --fullscreen
```

**Then press 'F' to toggle fullscreen when ready to present!**

---

## ❓ Troubleshooting

### Video won't play?
Check the file path:
```bash
ls "Real_Time_Vids/"
```

### Want to use a different model?
```bash
python demo_for_judges.py --model "Downloaded models/new_chris.pt"
```

### Demo too fast/slow?
The video plays at normal speed. Press 'Q' to restart or use a different video.

---

## 💡 Pro Tips for Judges Demo

1. **Test first** - Run the demo once before presenting
2. **Use fullscreen** - Looks more professional
3. **Good lighting** - If using webcam, ensure good lighting
4. **Have backup** - Keep both videos ready
5. **Pre-save frames** - Press 'S' during demo to save impressive detections

---

## 📝 What to Tell Judges

> "This is our real-time plankton detection system using a custom-trained YOLOv8 model.
> The model identifies and classifies 6 different types of plankton species with bounding boxes.
> It processes at 8-10 frames per second and is ready for deployment on edge devices
> like Raspberry Pi for field research."

---

**That's it! Just run the command and show the judges. Good luck! 🍀**

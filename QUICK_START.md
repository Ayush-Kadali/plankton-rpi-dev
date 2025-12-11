# 🚀 SUPER QUICK START

## Just run this:

```bash
python3 DEMO.py --source "Real_Time_Vids/only_water_stream.mov"
```

## What you'll see:

✅ **Real-time annotated video** with:
- Bounding boxes around detected plankton
- Species labels with confidence scores
- Live count overlay showing:
  - FPS
  - Total detections
  - Species breakdown
  - Frame count

## Controls:

- **'q'** = Quit
- **'s'** = Save screenshot

## For webcam:

```bash
python3 DEMO.py
```

## Change model anytime:

```bash
python3 DEMO.py --model "Downloaded models/yolov8n.pt"
```

**The system automatically adapts to ANY YOLO model** - just point it to a new .pt file!

## More detections:

```bash
python3 DEMO.py --conf 0.10
```

## Save the output video:

```bash
python3 DEMO.py --save
```

---

# That's it! 🎉

The demo is **model-agnostic** - swap models without changing any code!

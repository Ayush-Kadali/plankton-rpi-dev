#!/usr/bin/env python3
"""
Simple demo: Process single image and save annotated result
"""

import cv2
import numpy as np
from pathlib import Path
import sys

def demo_detection(image_path, model_path, output_path, conf=0.20):
    """Run detection on single image and save result."""
    print(f"Loading model: {model_path}")

    # Load YOLO
    try:
        from ultralytics import YOLO
        model = YOLO(model_path)
        model_type = 'ultralytics'
    except:
        import torch
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=False)
        model_type = 'yolov5'

    print(f"✅ Model loaded ({model_type})")

    # Get classes
    if hasattr(model, 'names'):
        if isinstance(model.names, dict):
            class_names = list(model.names.values())
        else:
            class_names = model.names
    else:
        class_names = ["object"]

    print(f"Classes: {class_names}")

    # Load image
    print(f"\nLoading image: {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Failed to load image")
        return

    h, w = img.shape[:2]
    print(f"Image size: {w}x{h}")

    # Run detection
    print(f"\nRunning detection (conf={conf})...")

    if model_type == 'ultralytics':
        results = model(img, conf=conf, verbose=False)
        detections = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = class_names[cls] if cls < len(class_names) else f"class_{cls}"

                detections.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': confidence,
                    'class': class_name
                })
    else:
        results = model(img)
        pred = results.xyxy[0].cpu().numpy()
        detections = []

        for det in pred:
            x1, y1, x2, y2, conf, cls = det
            x1, y1, x2, y2, cls = map(int, [x1, y1, x2, y2, cls])
            confidence = float(conf)
            class_name = class_names[cls] if cls < len(class_names) else f"class_{cls}"

            detections.append({
                'bbox': [x1, y1, x2, y2],
                'confidence': confidence,
                'class': class_name
            })

    print(f"\n✅ Found {len(detections)} detections!")

    # Draw detections
    annotated = img.copy()

    # Colors
    np.random.seed(42)
    colors = {}
    for name in class_names:
        colors[name] = tuple(map(int, np.random.randint(50, 255, 3)))

    class_counts = {}

    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        class_name = det['class']
        conf = det['confidence']

        # Count
        class_counts[class_name] = class_counts.get(class_name, 0) + 1

        # Color
        color = colors.get(class_name, (255, 255, 255))

        # Draw box (thicker for visibility)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 4)

        # Label
        label = f"{class_name}: {conf:.2f}"
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)

        cv2.rectangle(annotated, (x1, y1 - label_h - 20), (x1 + label_w + 10, y1), color, -1)
        cv2.putText(annotated, label, (x1 + 5, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # Add summary
    y_pos = 50
    cv2.putText(annotated, f"YOLO Detection Demo", (20, y_pos),
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
    y_pos += 50

    cv2.putText(annotated, f"Total Detections: {len(detections)}", (20, y_pos),
               cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
    y_pos += 45

    if class_counts:
        cv2.putText(annotated, "Species Found:", (20, y_pos),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
        y_pos += 40

        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            color = colors.get(class_name, (255, 255, 255))
            cv2.putText(annotated, f"  {class_name}: {count}", (30, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
            y_pos += 35

    # Save
    cv2.imwrite(output_path, annotated)
    print(f"\n✅ Saved annotated image to: {output_path}")

    # Print summary
    print(f"\n{'='*60}")
    print(f"DETECTION SUMMARY")
    print(f"{'='*60}")
    print(f"Total detections: {len(detections)}")
    if class_counts:
        print(f"\nSpecies breakdown:")
        for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(detections) * 100) if len(detections) > 0 else 0
            print(f"  {class_name}: {count} ({pct:.1f}%)")
    print(f"{'='*60}")

    return annotated, detections


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python demo_single_image.py <image_path> [conf_threshold]")
        print("\nExample:")
        print('  python demo_single_image.py "test_images/image.jpeg" 0.25')
        sys.exit(1)

    image_path = sys.argv[1]
    conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.20

    # Output path
    input_path = Path(image_path)
    output_path = f"results/demo_annotated_{input_path.stem}.jpg"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Run demo
    demo_detection(
        image_path=image_path,
        model_path="Downloaded models/best.pt",
        output_path=output_path,
        conf=conf
    )

    print(f"\n🎉 Demo complete! Open the annotated image:")
    print(f"   open {output_path}")

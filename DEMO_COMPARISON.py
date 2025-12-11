#!/usr/bin/env python3
"""
MODEL COMPARISON DEMO
Show multiple models side-by-side for impressive demonstration
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import time
from datetime import datetime
import argparse

class ModelComparison:
    """Compare multiple models side-by-side"""

    def __init__(self, model_paths, confidence=0.15):
        print("=" * 80)
        print("🔬 MODEL COMPARISON DEMONSTRATION")
        print("=" * 80)

        self.models = {}
        self.confidence = confidence
        self.stats = {}

        for path in model_paths:
            name = Path(path).stem
            print(f"Loading {name}...")
            try:
                model = YOLO(path)
                self.models[name] = model
                self.stats[name] = {"detections": 0, "processing_time": []}
                print(f"  ✅ {name}: {len(model.names)} classes")
            except Exception as e:
                print(f"  ❌ Failed to load {name}: {e}")

        if not self.models:
            raise ValueError("No models loaded successfully!")

        print(f"\n✅ Loaded {len(self.models)} models")
        print(f"🎯 Confidence: {confidence}")
        print("=" * 80)

        # Colors
        np.random.seed(42)
        self.colors = {}
        for model_name, model in self.models.items():
            self.colors[model_name] = {}
            classes = list(model.names.values())
            for cls in classes:
                self.colors[model_name][cls] = tuple(np.random.randint(50, 255, 3).tolist())

    def detect_with_model(self, frame, model_name):
        """Run detection with specific model"""
        model = self.models[model_name]

        start = time.time()
        results = model(frame, conf=self.confidence, verbose=False)
        elapsed = (time.time() - start) * 1000  # ms
        self.stats[model_name]["processing_time"].append(elapsed)

        detections = []
        boxes = results[0].boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = list(model.names.values())[cls_id]

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "class": cls_name,
                "confidence": conf
            })

        self.stats[model_name]["detections"] += len(detections)
        return detections, elapsed

    def draw_detections(self, frame, detections, model_name, color_scheme):
        """Draw detections on frame"""
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            color = self.colors[model_name].get(det["class"], (255, 255, 255))

            # Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label
            label = f"{det['class'][:10]} {det['confidence']:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
            cv2.rectangle(frame, (x1, y1-h-5), (x1+w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1-3),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    def add_model_label(self, frame, model_name, detections, processing_time):
        """Add model identification label"""
        h, w = frame.shape[:2]

        # Header
        cv2.rectangle(frame, (0, 0), (w, 50), (52, 73, 94), -1)
        cv2.putText(frame, model_name.upper(), (10, 30),
                   cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)

        # Stats
        stats_text = f"Detections: {len(detections)} | {processing_time:.0f}ms"
        cv2.putText(frame, stats_text, (10, h-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def run(self, source=0):
        """Run comparison demo"""
        try:
            source = int(source)
        except:
            pass

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print("❌ Could not open video source!")
            return False

        frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        n_models = len(self.models)
        grid_cols = min(2, n_models)
        grid_rows = (n_models + grid_cols - 1) // grid_cols

        cell_w = frame_w
        cell_h = frame_h

        print(f"\n🎬 Starting comparison demo...")
        print(f"   Models: {n_models}")
        print(f"   Layout: {grid_rows}x{grid_cols}")
        print(f"   Cell size: {cell_w}x{cell_h}")
        print("\n⌨️  Press 'q' to quit, 's' for screenshot")
        print("=" * 80)

        frame_count = 0
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Process with each model
            results = {}
            for model_name in self.models.keys():
                frame_copy = frame.copy()
                detections, proc_time = self.detect_with_model(frame_copy, model_name)
                self.draw_detections(frame_copy, detections, model_name, self.colors[model_name])
                self.add_model_label(frame_copy, model_name, detections, proc_time)
                results[model_name] = frame_copy

            # Create grid
            rows = []
            model_names = list(results.keys())
            for row_idx in range(grid_rows):
                row_frames = []
                for col_idx in range(grid_cols):
                    idx = row_idx * grid_cols + col_idx
                    if idx < len(model_names):
                        row_frames.append(results[model_names[idx]])
                    else:
                        # Empty cell
                        row_frames.append(np.zeros((cell_h, cell_w, 3), dtype=np.uint8))

                if len(row_frames) > 1:
                    rows.append(np.hstack(row_frames))
                else:
                    rows.append(row_frames[0])

            if len(rows) > 1:
                grid = np.vstack(rows)
            else:
                grid = rows[0]

            # Display
            window_name = f"Model Comparison ({n_models} models)"
            cv2.imshow(window_name, grid)

            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                Path("demo_output").mkdir(exist_ok=True)
                screenshot = f"demo_output/comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(screenshot, grid)
                print(f"📸 Screenshot saved: {screenshot}")

        cap.release()
        cv2.destroyAllWindows()

        # Print summary
        elapsed = time.time() - start_time
        print("\n" + "=" * 80)
        print("📊 COMPARISON SUMMARY")
        print("=" * 80)
        print(f"Duration: {elapsed:.1f}s")
        print(f"Frames: {frame_count}")
        print(f"FPS: {frame_count/elapsed:.1f}")

        print("\n🏆 Model Performance:")
        for model_name in self.models.keys():
            total_det = self.stats[model_name]["detections"]
            avg_time = np.mean(self.stats[model_name]["processing_time"])
            print(f"   {model_name:20s}: {total_det:4d} detections | {avg_time:5.1f}ms avg")

        print("=" * 80)
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Compare Multiple Plankton Detection Models',
        epilog="""
Examples:
  # Compare 2 models
  python3 DEMO_COMPARISON.py --models "Downloaded models/best.pt" "Downloaded models/yolov8n.pt"

  # Compare 3 models
  python3 DEMO_COMPARISON.py --models "Downloaded models/best.pt" "Downloaded models/yolov8n.pt" "Downloaded models/yolov5nu.pt"
        """
    )

    parser.add_argument('--source', default=0,
                       help='Video source')
    parser.add_argument('--models', nargs='+', required=True,
                       help='Paths to model files (space-separated)')
    parser.add_argument('--conf', type=float, default=0.15,
                       help='Confidence threshold')

    args = parser.parse_args()

    if len(args.models) < 2:
        print("❌ Need at least 2 models to compare!")
        return

    comparison = ModelComparison(args.models, confidence=args.conf)
    comparison.run(source=args.source)


if __name__ == "__main__":
    main()

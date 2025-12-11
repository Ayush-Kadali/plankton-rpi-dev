#!/usr/bin/env python3
"""
PLANKTON DETECTION DEMO
Real-time plankton detection with local data storage and map visualization
Simple, fast, and ready for hardware integration!
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import time
from datetime import datetime
import json
import argparse

class PlanktonDemo:
    """Simple real-time plankton detection system"""

    def __init__(self, model_path="Downloaded models/best.pt", confidence=0.15):
        print("=" * 80)
        print("🔬 PLANKTON DETECTION SYSTEM - DEMO MODE")
        print("=" * 80)
        print(f"Loading model: {model_path}")

        self.model = YOLO(model_path)
        self.confidence = confidence
        self.classes = list(self.model.names.values())

        print(f"✅ Model loaded!")
        print(f"🦠 Species detected: {', '.join(self.classes)}")
        print(f"🎯 Confidence threshold: {confidence}")

        # Stats
        self.session_data = {
            "start_time": datetime.now().isoformat(),
            "detections": [],
            "species_counts": {name: 0 for name in self.classes},
            "total_detections": 0,
            "frames_processed": 0
        }

        # Colors for each species
        np.random.seed(42)
        self.colors = {name: tuple(np.random.randint(50, 255, 3).tolist())
                      for name in self.classes}

        self.start_time = time.time()

    def detect_frame(self, frame):
        """Run detection on a single frame"""
        results = self.model(frame, conf=self.confidence, verbose=False)
        detections = []

        boxes = results[0].boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = self.classes[cls_id]

            detections.append({
                "class": cls_name,
                "confidence": conf,
                "bbox": [x1, y1, x2, y2]
            })

            # Update stats
            self.session_data["species_counts"][cls_name] += 1

        self.session_data["total_detections"] += len(detections)
        self.session_data["frames_processed"] += 1

        return detections

    def draw_detections(self, frame, detections):
        """Draw bounding boxes and labels"""
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cls_name = det["class"]
            conf = det["confidence"]
            color = self.colors[cls_name]

            # Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label background
            label = f"{cls_name} {conf:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1-20), (x1+w, y1), color, -1)
            cv2.putText(frame, label, (x1, y1-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    def draw_overlay(self, frame):
        """Draw stats overlay"""
        h, w = frame.shape[:2]
        overlay = frame.copy()

        # Background
        cv2.rectangle(overlay, (10, 10), (400, 250), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Stats
        elapsed = time.time() - self.start_time
        fps = self.session_data["frames_processed"] / elapsed if elapsed > 0 else 0

        y = 35
        cv2.putText(frame, "PLANKTON DETECTOR", (20, y),
                   cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 2)
        y += 30

        cv2.putText(frame, f"FPS: {fps:.1f}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y += 25

        cv2.putText(frame, f"Frames: {self.session_data['frames_processed']}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y += 25

        cv2.putText(frame, f"Total: {self.session_data['total_detections']}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        y += 35

        # Species counts
        cv2.putText(frame, "Species:", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
        y += 20

        for name, count in sorted(self.session_data["species_counts"].items(),
                                 key=lambda x: x[1], reverse=True):
            if count > 0:
                color = self.colors[name]
                cv2.putText(frame, f"  {name}: {count}", (20, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
                y += 20

        # Controls
        y = h - 15
        cv2.putText(frame, "Press 'q' to quit | 's' to save", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    def run(self, source=0, save_output=False):
        """Run detection on camera or video"""
        print("\n" + "=" * 80)
        print(f"📹 Opening source: {source}")

        # Try to convert to int for camera
        try:
            source = int(source)
            print("   Using camera")
        except:
            print("   Using video file")

        cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            print("❌ Could not open video source!")
            return False

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps_source = cap.get(cv2.CAP_PROP_FPS)

        print(f"   Resolution: {width}x{height}")
        print(f"   FPS: {fps_source:.2f}")
        print("\n🚀 Starting detection... (Press 'q' to quit)")
        print("=" * 80)

        # Video writer
        writer = None
        if save_output:
            output_dir = Path("demo_output")
            output_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"detection_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(str(output_path), fourcc, 20.0, (width, height))
            print(f"💾 Recording to: {output_path}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Detect
                detections = self.detect_frame(frame)

                # Draw
                self.draw_detections(frame, detections)
                self.draw_overlay(frame)

                # Display
                cv2.imshow('Plankton Detection', frame)

                # Save
                if writer:
                    writer.write(frame)

                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\n⏹️  Stopped by user")
                    break
                elif key == ord('s'):
                    screenshot = f"demo_output/screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    Path("demo_output").mkdir(exist_ok=True)
                    cv2.imwrite(screenshot, frame)
                    print(f"📸 Saved: {screenshot}")

        except KeyboardInterrupt:
            print("\n⏹️  Interrupted")

        finally:
            cap.release()
            if writer:
                writer.release()
            cv2.destroyAllWindows()

            # Save session data
            self.save_session()
            self.print_summary()

        return True

    def save_session(self):
        """Save session data to JSON"""
        output_dir = Path("demo_output")
        output_dir.mkdir(exist_ok=True)

        self.session_data["end_time"] = datetime.now().isoformat()
        self.session_data["duration_seconds"] = time.time() - self.start_time

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = output_dir / f"session_{timestamp}.json"

        with open(json_path, 'w') as f:
            json.dump(self.session_data, f, indent=2)

        print(f"\n💾 Session data saved: {json_path}")

    def print_summary(self):
        """Print session summary"""
        elapsed = time.time() - self.start_time

        print("\n" + "=" * 80)
        print("📊 SESSION SUMMARY")
        print("=" * 80)
        print(f"Duration: {elapsed:.1f}s")
        print(f"Frames: {self.session_data['frames_processed']}")
        print(f"Average FPS: {self.session_data['frames_processed']/elapsed:.1f}")
        print(f"Total detections: {self.session_data['total_detections']}")

        if self.session_data['total_detections'] > 0:
            avg_per_frame = self.session_data['total_detections'] / self.session_data['frames_processed']
            print(f"Avg detections/frame: {avg_per_frame:.2f}")

            print("\n🦠 Species breakdown:")
            for name, count in sorted(self.session_data['species_counts'].items(),
                                     key=lambda x: x[1], reverse=True):
                if count > 0:
                    pct = count / self.session_data['total_detections'] * 100
                    print(f"   {name:20s}: {count:4d} ({pct:5.1f}%)")

        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Plankton Detection Demo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use webcam
  python DEMO.py

  # Use video file
  python DEMO.py --source "Real_Time_Vids/only_water_stream.mov"

  # Save output video
  python DEMO.py --source 0 --save

  # Lower confidence for more detections
  python DEMO.py --conf 0.10
        """
    )

    parser.add_argument('--source', default=0,
                       help='Video source (0 for webcam, or path to video)')
    parser.add_argument('--model', default='Downloaded models/best.pt',
                       help='Path to YOLO model')
    parser.add_argument('--conf', type=float, default=0.15,
                       help='Confidence threshold (0.01-0.50)')
    parser.add_argument('--save', action='store_true',
                       help='Save output video')

    args = parser.parse_args()

    # Create and run demo
    demo = PlanktonDemo(model_path=args.model, confidence=args.conf)
    demo.run(source=args.source, save_output=args.save)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
RASPBERRY PI 5 OPTIMIZED PLANKTON DETECTION
Lightweight, efficient, hardware-accelerated detection
"""

import cv2
import numpy as np
from pathlib import Path
import time
from datetime import datetime
import json
import argparse

try:
    # Try to use Picamera2 for RPi camera
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    print("⚠️  Picamera2 not available, using OpenCV")

try:
    # Try ultralytics YOLO (lighter on RPi with optimizations)
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("❌ Ultralytics not installed!")


class PlanktonDetectorRPi:
    """Raspberry Pi optimized plankton detection"""

    def __init__(self, model_path="Downloaded models/best.pt", confidence=0.15, resolution=(640, 480)):
        print("=" * 60)
        print("🔬 RPi 5 PLANKTON DETECTOR")
        print("=" * 60)

        self.resolution = resolution
        self.confidence = confidence

        # Load model with RPi optimizations
        print(f"Loading model: {model_path}")
        self.model = YOLO(model_path)

        # Set to use INT8 quantization if available (faster on RPi)
        self.model.fuse()  # Fuse layers for speed

        self.classes = list(self.model.names.values())
        print(f"✅ Model loaded: {len(self.classes)} classes")
        print(f"🎯 Resolution: {resolution[0]}x{resolution[1]}")
        print(f"🎯 Confidence: {confidence}")

        # Stats
        self.stats = {
            "frames": 0,
            "detections": 0,
            "species_counts": {c: 0 for c in self.classes},
            "start_time": time.time()
        }

        # Colors
        np.random.seed(42)
        self.colors = {name: tuple(np.random.randint(50, 255, 3).tolist())
                      for name in self.classes}

    def init_picamera(self):
        """Initialize Raspberry Pi camera"""
        if not PICAMERA_AVAILABLE:
            return None

        try:
            picam = Picamera2()
            config = picam.create_preview_configuration(
                main={"size": self.resolution, "format": "RGB888"}
            )
            picam.configure(config)
            picam.start()
            time.sleep(2)  # Warm up
            print("✅ Pi Camera initialized")
            return picam
        except Exception as e:
            print(f"⚠️  Could not init Pi camera: {e}")
            return None

    def detect_frame(self, frame):
        """Optimized detection for RPi"""
        # Run inference with optimizations
        results = self.model(
            frame,
            conf=self.confidence,
            verbose=False,
            device='cpu',  # RPi uses CPU
            half=False,  # No FP16 on RPi CPU
            imgsz=self.resolution[0]  # Match input size
        )

        detections = []
        boxes = results[0].boxes

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = self.classes[cls_id]

            detections.append({
                "bbox": [x1, y1, x2, y2],
                "class": cls_name,
                "conf": conf
            })

            self.stats["species_counts"][cls_name] += 1

        self.stats["detections"] += len(detections)
        self.stats["frames"] += 1

        return detections

    def draw_minimal(self, frame, detections):
        """Minimal drawing for speed"""
        # Draw boxes only (no fancy overlays)
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            color = self.colors[det["class"]]

            # Box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label (compact)
            label = f"{det['class'][:3]} {det['conf']:.2f}"
            cv2.putText(frame, label, (x1, y1-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    def draw_stats_minimal(self, frame):
        """Minimal stats overlay"""
        h, w = frame.shape[:2]
        elapsed = time.time() - self.stats["start_time"]
        fps = self.stats["frames"] / elapsed if elapsed > 0 else 0

        # Black background for text
        cv2.rectangle(frame, (5, 5), (200, 80), (0, 0, 0), -1)

        # Text
        y = 20
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        y += 20
        cv2.putText(frame, f"Total: {self.stats['detections']}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 20

        # Top species
        top_species = sorted(self.stats["species_counts"].items(),
                           key=lambda x: x[1], reverse=True)[:2]
        for name, count in top_species:
            if count > 0:
                cv2.putText(frame, f"{name[:8]}: {count}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors[name], 1)
                y += 15

    def run_picamera(self, display=False, save=False):
        """Run with Pi camera"""
        picam = self.init_picamera()
        if not picam:
            print("❌ Could not initialize Pi camera")
            return False

        print("\n🚀 Running detection on Pi camera...")
        print("   Press Ctrl+C to stop")

        writer = None
        if save:
            Path("rpi_output").mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"rpi_output/rpi_detection_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output, fourcc, 10.0, self.resolution)
            print(f"💾 Recording to: {output}")

        try:
            while True:
                # Capture frame
                frame = picam.capture_array()

                # Detect
                detections = self.detect_frame(frame)

                # Draw
                self.draw_minimal(frame, detections)
                self.draw_stats_minimal(frame)

                # Display (if not headless)
                if display:
                    cv2.imshow('RPi Detection', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                # Save
                if writer:
                    writer.write(frame)

                # Print progress every 30 frames
                if self.stats["frames"] % 30 == 0:
                    elapsed = time.time() - self.stats["start_time"]
                    fps = self.stats["frames"] / elapsed
                    print(f"Frame {self.stats['frames']} | FPS: {fps:.1f} | "
                          f"Detections: {len(detections)} | "
                          f"Total: {self.stats['detections']}")

        except KeyboardInterrupt:
            print("\n⏹️  Stopped")
        finally:
            picam.close()
            if writer:
                writer.release()
            cv2.destroyAllWindows()
            self.save_stats()

        return True

    def run_opencv(self, source=0, display=True, save=False):
        """Run with OpenCV camera (fallback)"""
        print(f"\n🚀 Running detection with OpenCV camera: {source}")

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print("❌ Could not open camera")
            return False

        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

        writer = None
        if save:
            Path("rpi_output").mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"rpi_output/rpi_detection_{timestamp}.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output, fourcc, 10.0, self.resolution)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize if needed
                if frame.shape[1] != self.resolution[0]:
                    frame = cv2.resize(frame, self.resolution)

                # Detect
                detections = self.detect_frame(frame)

                # Draw
                self.draw_minimal(frame, detections)
                self.draw_stats_minimal(frame)

                # Display
                if display:
                    cv2.imshow('RPi Detection', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                # Save
                if writer:
                    writer.write(frame)

                # Progress
                if self.stats["frames"] % 30 == 0:
                    elapsed = time.time() - self.stats["start_time"]
                    fps = self.stats["frames"] / elapsed
                    print(f"Frame {self.stats['frames']} | FPS: {fps:.1f} | "
                          f"Detections: {len(detections)}")

        except KeyboardInterrupt:
            print("\n⏹️  Stopped")
        finally:
            cap.release()
            if writer:
                writer.release()
            cv2.destroyAllWindows()
            self.save_stats()

        return True

    def save_stats(self):
        """Save session statistics"""
        Path("rpi_output").mkdir(exist_ok=True)

        elapsed = time.time() - self.stats["start_time"]
        data = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": elapsed,
            "frames_processed": self.stats["frames"],
            "total_detections": self.stats["detections"],
            "fps": self.stats["frames"] / elapsed if elapsed > 0 else 0,
            "species_counts": self.stats["species_counts"]
        }

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = f"rpi_output/session_{timestamp}.json"

        with open(json_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n💾 Stats saved: {json_path}")

        # Print summary
        print("\n" + "=" * 60)
        print("📊 SESSION SUMMARY")
        print("=" * 60)
        print(f"Duration: {elapsed:.1f}s")
        print(f"Frames: {self.stats['frames']}")
        print(f"FPS: {data['fps']:.1f}")
        print(f"Total detections: {self.stats['detections']}")

        if self.stats['detections'] > 0:
            print("\n🦠 Species:")
            for name, count in sorted(self.stats['species_counts'].items(),
                                     key=lambda x: x[1], reverse=True):
                if count > 0:
                    pct = count / self.stats['detections'] * 100
                    print(f"   {name}: {count} ({pct:.1f}%)")

        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='RPi 5 Optimized Plankton Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use Pi camera (auto-detect)
  python3 DEMO_RPI.py

  # Use USB camera
  python3 DEMO_RPI.py --opencv --source 0

  # Headless mode (no display)
  python3 DEMO_RPI.py --no-display

  # Save output
  python3 DEMO_RPI.py --save

  # Lower resolution for speed
  python3 DEMO_RPI.py --resolution 320 240
        """
    )

    parser.add_argument('--model', default='Downloaded models/best.pt',
                       help='Path to YOLO model')
    parser.add_argument('--conf', type=float, default=0.15,
                       help='Confidence threshold')
    parser.add_argument('--opencv', action='store_true',
                       help='Force OpenCV instead of Picamera2')
    parser.add_argument('--source', type=int, default=0,
                       help='Camera source for OpenCV')
    parser.add_argument('--resolution', type=int, nargs=2, default=[640, 480],
                       help='Camera resolution (width height)')
    parser.add_argument('--no-display', action='store_true',
                       help='Headless mode (no GUI)')
    parser.add_argument('--save', action='store_true',
                       help='Save output video')

    args = parser.parse_args()

    # Create detector
    detector = PlanktonDetectorRPi(
        model_path=args.model,
        confidence=args.conf,
        resolution=tuple(args.resolution)
    )

    # Run detection
    if args.opencv or not PICAMERA_AVAILABLE:
        detector.run_opencv(
            source=args.source,
            display=not args.no_display,
            save=args.save
        )
    else:
        detector.run_picamera(
            display=not args.no_display,
            save=args.save
        )


if __name__ == "__main__":
    main()

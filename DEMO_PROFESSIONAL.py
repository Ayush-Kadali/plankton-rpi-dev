#!/usr/bin/env python3
"""
PROFESSIONAL PLANKTON DETECTION DEMO
Impressive visual presentation for judges and stakeholders
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import time
from datetime import datetime
import json
import argparse
from collections import deque

class ProfessionalPlanktonDemo:
    """Professional demo with enhanced visualizations"""

    def __init__(self, model_path="Downloaded models/best.pt", confidence=0.15):
        print("=" * 80)
        print("🔬 PROFESSIONAL PLANKTON DETECTION SYSTEM")
        print("   Marine Life AI Monitoring Platform")
        print("=" * 80)

        self.model = YOLO(model_path)
        self.confidence = confidence
        self.classes = list(self.model.names.values())

        # Enhanced stats
        self.stats = {
            "total_detections": 0,
            "frames_processed": 0,
            "species_counts": {name: 0 for name in self.classes},
            "detection_history": deque(maxlen=100),  # Last 100 frames
            "fps_history": deque(maxlen=30),  # Last 30 FPS readings
            "confidence_scores": {name: [] for name in self.classes},
            "start_time": time.time()
        }

        # Color scheme (professional)
        np.random.seed(42)
        self.colors = {}
        palette = [
            (255, 99, 71),   # Tomato
            (50, 205, 50),   # Lime Green
            (30, 144, 255),  # Dodger Blue
            (255, 165, 0),   # Orange
            (186, 85, 211),  # Medium Orchid
            (255, 215, 0),   # Gold
        ]
        for i, name in enumerate(self.classes):
            self.colors[name] = palette[i % len(palette)]

        print(f"✅ System initialized")
        print(f"🦠 Species monitored: {len(self.classes)}")
        print(f"🎯 Confidence threshold: {confidence}")
        print(f"🎨 Enhanced visualization mode")
        print("=" * 80)

    def detect_frame(self, frame):
        """Enhanced detection with confidence tracking"""
        results = self.model(frame, conf=self.confidence, verbose=False)
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
                "confidence": conf
            })

            # Update stats
            self.stats["species_counts"][cls_name] += 1
            self.stats["confidence_scores"][cls_name].append(conf)

        self.stats["total_detections"] += len(detections)
        self.stats["frames_processed"] += 1
        self.stats["detection_history"].append(len(detections))

        return detections

    def draw_enhanced_boxes(self, frame, detections):
        """Draw professional-looking bounding boxes"""
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            color = self.colors[det["class"]]
            conf = det["confidence"]

            # Draw thick border with shadow effect
            shadow_color = tuple([c // 2 for c in color])
            cv2.rectangle(frame, (x1+2, y1+2), (x2+2, y2+2), shadow_color, 3)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)

            # Draw corner markers (professional look)
            corner_len = 15
            thickness = 4
            # Top-left
            cv2.line(frame, (x1, y1), (x1+corner_len, y1), color, thickness)
            cv2.line(frame, (x1, y1), (x1, y1+corner_len), color, thickness)
            # Top-right
            cv2.line(frame, (x2, y1), (x2-corner_len, y1), color, thickness)
            cv2.line(frame, (x2, y1), (x2, y1+corner_len), color, thickness)
            # Bottom-left
            cv2.line(frame, (x1, y2), (x1+corner_len, y2), color, thickness)
            cv2.line(frame, (x1, y2), (x1, y2-corner_len), color, thickness)
            # Bottom-right
            cv2.line(frame, (x2, y2), (x2-corner_len, y2), color, thickness)
            cv2.line(frame, (x2, y2), (x2, y2-corner_len), color, thickness)

            # Label with gradient background
            label = f"{det['class']}"
            conf_text = f"{conf:.2%}"

            (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.6, 2)
            (conf_w, conf_h), _ = cv2.getTextSize(conf_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            total_w = max(label_w, conf_w) + 10
            total_h = label_h + conf_h + 15

            # Draw label background with transparency
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1-total_h-5), (x1+total_w, y1), color, -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

            # Draw text
            cv2.putText(frame, label, (x1+5, y1-conf_h-10),
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, conf_text, (x1+5, y1-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    def create_dashboard(self, width=400, height=720):
        """Create professional statistics dashboard"""
        dashboard = np.ones((height, width, 3), dtype=np.uint8) * 240

        elapsed = time.time() - self.stats["start_time"]
        fps = self.stats["frames_processed"] / elapsed if elapsed > 0 else 0
        self.stats["fps_history"].append(fps)

        y = 30

        # Title
        cv2.rectangle(dashboard, (0, 0), (width, 60), (41, 128, 185), -1)
        cv2.putText(dashboard, "LIVE ANALYTICS", (20, 40),
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

        y = 80

        # Key metrics
        metrics = [
            ("Total Detections", self.stats["total_detections"], (46, 204, 113)),
            ("Frames Processed", self.stats["frames_processed"], (52, 152, 219)),
            ("Current FPS", f"{fps:.1f}", (155, 89, 182)),
        ]

        for label, value, color in metrics:
            cv2.rectangle(dashboard, (10, y), (width-10, y+60), color, -1)
            cv2.rectangle(dashboard, (10, y), (width-10, y+60), (255, 255, 255), 2)
            cv2.putText(dashboard, label, (20, y+25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(dashboard, str(value), (20, y+50),
                       cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2)
            y += 75

        # Detection history graph
        y += 10
        cv2.rectangle(dashboard, (10, y), (width-10, y+120), (255, 255, 255), -1)
        cv2.rectangle(dashboard, (10, y), (width-10, y+120), (100, 100, 100), 2)
        cv2.putText(dashboard, "Detection Rate", (20, y+20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        if len(self.stats["detection_history"]) > 1:
            history = list(self.stats["detection_history"])
            max_det = max(history) if max(history) > 0 else 1
            graph_h = 80
            graph_w = width - 40

            for i in range(1, len(history)):
                x1 = 20 + int((i-1) * graph_w / len(history))
                x2 = 20 + int(i * graph_w / len(history))
                y1 = y + 110 - int(history[i-1] * graph_h / max_det)
                y2 = y + 110 - int(history[i] * graph_h / max_det)
                cv2.line(dashboard, (x1, y1), (x2, y2), (52, 152, 219), 2)

        y += 135

        # Species breakdown
        cv2.rectangle(dashboard, (10, y), (width-10, y+30), (52, 73, 94), -1)
        cv2.putText(dashboard, "SPECIES DISTRIBUTION", (20, y+20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 40

        total = self.stats["total_detections"]
        sorted_species = sorted(self.stats["species_counts"].items(),
                               key=lambda x: x[1], reverse=True)

        for name, count in sorted_species:
            if count > 0:
                percentage = (count / total * 100) if total > 0 else 0
                color = self.colors[name]

                # Bar
                bar_width = int((width-40) * percentage / 100)
                cv2.rectangle(dashboard, (20, y), (20+bar_width, y+25), color, -1)
                cv2.rectangle(dashboard, (20, y), (width-20, y+25), (200, 200, 200), 1)

                # Text
                text = f"{name[:12]}: {count} ({percentage:.1f}%)"
                cv2.putText(dashboard, text, (25, y+17),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
                y += 30

        # Footer
        y = height - 40
        cv2.rectangle(dashboard, (0, y), (width, height), (44, 62, 80), -1)
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(dashboard, f"Last Update: {timestamp}", (20, y+25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

        return dashboard

    def run(self, source=0, window_name="Professional Plankton Detection"):
        """Run professional demo"""
        try:
            source = int(source)
        except:
            pass

        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print("❌ Could not open video source!")
            return False

        # Get dimensions
        frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate dashboard size
        dashboard_w = 400
        total_w = frame_w + dashboard_w
        total_h = max(frame_h, 720)

        print(f"\n🎬 Starting professional demo...")
        print(f"   Resolution: {frame_w}x{frame_h}")
        print(f"   Dashboard: {dashboard_w}x{total_h}")
        print("\n⌨️  Controls:")
        print("   'q' - Quit")
        print("   's' - Screenshot")
        print("   'r' - Reset stats")
        print("=" * 80)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Detect
            detections = self.detect_frame(frame)

            # Draw enhanced boxes
            self.draw_enhanced_boxes(frame, detections)

            # Add watermark
            cv2.putText(frame, "Marine Life AI Monitor v1.0", (10, frame_h-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            # Create dashboard
            dashboard = self.create_dashboard(dashboard_w, frame_h)

            # Combine
            if frame_h != dashboard.shape[0]:
                dashboard_resized = cv2.resize(dashboard, (dashboard_w, frame_h))
            else:
                dashboard_resized = dashboard

            combined = np.hstack([frame, dashboard_resized])

            # Display
            cv2.imshow(window_name, combined)

            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                screenshot_path = f"demo_output/professional_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                Path("demo_output").mkdir(exist_ok=True)
                cv2.imwrite(screenshot_path, combined)
                print(f"📸 Screenshot saved: {screenshot_path}")
            elif key == ord('r'):
                print("🔄 Resetting statistics...")
                self.stats["total_detections"] = 0
                self.stats["species_counts"] = {name: 0 for name in self.classes}

        cap.release()
        cv2.destroyAllWindows()
        self.print_summary()
        return True

    def print_summary(self):
        """Print professional summary"""
        elapsed = time.time() - self.stats["start_time"]

        print("\n" + "=" * 80)
        print("📊 SESSION SUMMARY REPORT")
        print("=" * 80)
        print(f"Duration: {elapsed:.1f}s")
        print(f"Frames: {self.stats['frames_processed']}")
        print(f"Avg FPS: {self.stats['frames_processed']/elapsed:.1f}")
        print(f"Total detections: {self.stats['total_detections']}")

        if self.stats['total_detections'] > 0:
            print(f"Detections/frame: {self.stats['total_detections']/self.stats['frames_processed']:.2f}")

            print("\n🦠 Species Analysis:")
            for name, count in sorted(self.stats['species_counts'].items(),
                                     key=lambda x: x[1], reverse=True):
                if count > 0:
                    pct = count / self.stats['total_detections'] * 100
                    avg_conf = np.mean(self.stats['confidence_scores'][name]) if self.stats['confidence_scores'][name] else 0
                    print(f"   {name:20s}: {count:4d} ({pct:5.1f}%) | Avg confidence: {avg_conf:.2%}")

        print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Professional Plankton Detection Demo',
        epilog="""
Examples:
  python3 DEMO_PROFESSIONAL.py
  python3 DEMO_PROFESSIONAL.py --source "Real_Time_Vids/good flow.mov"
  python3 DEMO_PROFESSIONAL.py --conf 0.10
        """
    )

    parser.add_argument('--source', default=0,
                       help='Video source (0 for webcam or video path)')
    parser.add_argument('--model', default='Downloaded models/best.pt',
                       help='Path to YOLO model')
    parser.add_argument('--conf', type=float, default=0.15,
                       help='Confidence threshold')

    args = parser.parse_args()

    demo = ProfessionalPlanktonDemo(
        model_path=args.model,
        confidence=args.conf
    )

    demo.run(source=args.source)


if __name__ == "__main__":
    main()

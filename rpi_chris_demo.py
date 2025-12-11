#!/usr/bin/env python3
"""
RPi-Optimized Chris Model Demo
Lightweight version for Raspberry Pi with minimal dependencies
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from pathlib import Path
from datetime import datetime
import sys


class RPiChrisDemo:
    def __init__(self, model_path="new_chris.pt", conf=0.1):
        """Initialize RPi demo with Chris model"""
        print(f"\n{'='*60}")
        print(f"RPi Chris Model Demo")
        print(f"Model: {model_path}")
        print(f"Confidence: {conf}")
        print(f"{'='*60}\n")

        self.model = YOLO(model_path)
        self.conf = conf
        self.colors = self._generate_colors()

        # Stats
        self.frame_count = 0
        self.total_detections = 0
        self.class_counts = {}
        self.fps_values = []
        self.start_time = None

    def _generate_colors(self):
        """Generate colors for classes"""
        return [
            (0, 255, 0), (255, 0, 0), (0, 165, 255),
            (255, 0, 255), (0, 255, 255), (255, 128, 0)
        ]

    def process_frame(self, frame):
        """Process frame with YOLO model"""
        t_start = time.time()

        # Inference
        results = self.model(frame, conf=self.conf, verbose=False)

        # Annotate
        annotated = frame.copy()
        num_detections = 0

        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Extract box info
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.model.names[cls]

                # Draw
                color = self.colors[cls % len(self.colors)]
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

                # Label
                label = f"{class_name}: {conf:.2f}"
                (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(annotated, (x1, y1-lh-10), (x1+lw+5, y1), color, -1)
                cv2.putText(annotated, label, (x1+2, y1-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Update stats
                self.class_counts[class_name] = self.class_counts.get(class_name, 0) + 1
                num_detections += 1

        self.total_detections += num_detections

        # Calculate FPS
        frame_time = time.time() - t_start
        fps = 1.0 / frame_time if frame_time > 0 else 0
        self.fps_values.append(fps)
        if len(self.fps_values) > 30:
            self.fps_values.pop(0)

        return annotated, num_detections, fps

    def draw_overlay(self, frame, fps):
        """Draw minimal overlay for RPi"""
        h, w = frame.shape[:2]
        elapsed = time.time() - self.start_time if self.start_time else 0
        avg_fps = np.mean(self.fps_values) if self.fps_values else 0

        # Semi-transparent background
        overlay = frame.copy()
        overlay_h = 150 + (len(self.class_counts) * 20)
        cv2.rectangle(overlay, (10, 10), (300, overlay_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Stats
        y = 35
        font = cv2.FONT_HERSHEY_SIMPLEX

        cv2.putText(frame, "Chris Model", (20, y), font, 0.7, (0, 255, 255), 2)
        y += 30

        # FPS - Large
        cv2.putText(frame, f"FPS: {avg_fps:.1f}", (20, y), font, 0.8, (0, 255, 0), 2)
        y += 30

        cv2.putText(frame, f"Frame: {self.frame_count}", (20, y), font, 0.5, (255, 255, 255), 1)
        y += 25

        cv2.putText(frame, f"Detections: {self.total_detections}", (20, y), font, 0.6, (0, 255, 255), 1)
        y += 25

        # Classes
        for cls_name, count in sorted(self.class_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
            cv2.putText(frame, f"{cls_name}: {count}", (20, y), font, 0.5, (255, 255, 0), 1)
            y += 20

        # Instructions
        cv2.putText(frame, "Press 'q' to quit", (20, h-20), font, 0.4, (255, 255, 0), 1)

    def run(self, video_source, save=False, headless=False):
        """Run detection"""
        print(f"Opening: {video_source}")

        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            print(f"ERROR: Cannot open {video_source}")
            return

        # Video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"Resolution: {w}x{h}, FPS: {fps}, Frames: {total}\n")

        # Video writer
        writer = None
        if save:
            out_path = f"results/rpi_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            Path(out_path).parent.mkdir(parents=True, exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
            print(f"Saving to: {out_path}\n")

        self.start_time = time.time()

        print("="*60)
        print("RUNNING DETECTION")
        print("="*60)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                self.frame_count += 1

                # Process
                annotated, num_det, current_fps = self.process_frame(frame)

                # Overlay
                self.draw_overlay(annotated, current_fps)

                # Save
                if writer:
                    writer.write(annotated)

                # Display (if not headless)
                if not headless:
                    cv2.imshow('RPi Chris Demo', annotated)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break

                # Progress
                if self.frame_count % 30 == 0:
                    avg_fps = np.mean(self.fps_values[-30:]) if self.fps_values else 0
                    progress = (self.frame_count / total * 100) if total > 0 else 0
                    print(f"Frame {self.frame_count}/{total} ({progress:.1f}%) | "
                          f"FPS: {avg_fps:.1f} | Detections: {num_det}")

        except KeyboardInterrupt:
            print("\nInterrupted")

        finally:
            cap.release()
            if writer:
                writer.release()
            if not headless:
                cv2.destroyAllWindows()

            # Summary
            elapsed = time.time() - self.start_time
            avg_fps = np.mean(self.fps_values) if self.fps_values else 0

            print("\n" + "="*60)
            print("COMPLETE")
            print("="*60)
            print(f"Frames: {self.frame_count}")
            print(f"Time: {elapsed:.1f}s")
            print(f"Avg FPS: {avg_fps:.1f}")
            print(f"Total Detections: {self.total_detections}")
            print("\nClasses:")
            for cls, cnt in sorted(self.class_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cls}: {cnt}")
            print("="*60)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='RPi Chris Model Demo')
    parser.add_argument('--video', default='0', help='Video file or camera index')
    parser.add_argument('--model', default='new_chris.pt', help='Model path')
    parser.add_argument('--conf', type=float, default=0.1, help='Confidence threshold')
    parser.add_argument('--save', action='store_true', help='Save output video')
    parser.add_argument('--headless', action='store_true', help='Run without display')

    args = parser.parse_args()

    # Parse video source
    try:
        video = int(args.video)
    except ValueError:
        video = args.video

    # Run demo
    demo = RPiChrisDemo(model_path=args.model, conf=args.conf)
    demo.run(video_source=video, save=args.save, headless=args.headless)

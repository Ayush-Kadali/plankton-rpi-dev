#!/usr/bin/env python3
"""
Real-Time Plankton Detection with Chris Model
Run on demo videos with overlay, FPS counter, and RPi compatibility
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from pathlib import Path
from datetime import datetime
import argparse


class ChrisRealtimeDemo:
    def __init__(self, model_path, conf_threshold=0.1):
        """
        Initialize the demo with Chris YOLO model

        Args:
            model_path: Path to YOLO model (.pt file)
            conf_threshold: Confidence threshold for detections
        """
        self.model_path = Path(model_path)
        self.conf_threshold = conf_threshold

        print(f"\n{'='*80}")
        print(f"Loading Chris Model: {self.model_path.name}")
        print(f"Confidence Threshold: {self.conf_threshold}")
        print(f"{'='*80}\n")

        # Load YOLO model
        self.model = YOLO(str(self.model_path))

        # Display model info
        if hasattr(self.model, 'names'):
            print(f"✓ Model loaded successfully!")
            print(f"  Classes: {list(self.model.names.values())}\n")

        # Colors for different classes (BGR format)
        self.colors = self._generate_colors()

        # Stats
        self.frame_count = 0
        self.total_detections = 0
        self.class_counts = {}
        self.fps_history = []
        self.start_time = None

    def _generate_colors(self):
        """Generate distinct colors for each class"""
        colors = [
            (0, 255, 0),      # Green
            (255, 0, 0),      # Blue
            (0, 165, 255),    # Orange
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Yellow
            (255, 128, 0),    # Sky blue
            (128, 0, 128),    # Purple
            (0, 128, 255),    # Light orange
        ]
        return colors

    def process_frame(self, frame):
        """
        Process frame with YOLO model

        Args:
            frame: Input frame (BGR)

        Returns:
            annotated_frame: Frame with detections
            detections: List of detection results
        """
        frame_start = time.time()

        # Run inference
        results = self.model(frame, conf=self.conf_threshold, verbose=False)

        # Annotate frame
        annotated_frame = frame.copy()
        detections = []

        # Process results
        for result in results:
            boxes = result.boxes

            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                # Get confidence and class
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.model.names[cls]

                # Get color for this class
                color = self.colors[cls % len(self.colors)]

                # Draw bounding box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)

                # Prepare label
                label = f"{class_name}: {conf:.2f}"

                # Get label size for background
                (label_w, label_h), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )

                # Draw label background
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1 - label_h - 10),
                    (x1 + label_w + 5, y1),
                    color,
                    -1
                )

                # Draw label text
                cv2.putText(
                    annotated_frame,
                    label,
                    (x1 + 2, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

                # Update stats
                if class_name not in self.class_counts:
                    self.class_counts[class_name] = 0
                self.class_counts[class_name] += 1

                detections.append({
                    'class': class_name,
                    'confidence': conf,
                    'bbox': (x1, y1, x2, y2)
                })

        # Calculate frame time
        frame_time = time.time() - frame_start
        fps = 1.0 / frame_time if frame_time > 0 else 0
        self.fps_history.append(fps)

        # Keep only last 30 FPS values for smooth average
        if len(self.fps_history) > 30:
            self.fps_history.pop(0)

        self.total_detections += len(detections)

        return annotated_frame, detections, fps

    def draw_overlay(self, frame, fps, frame_num):
        """
        Draw stats overlay on frame

        Args:
            frame: Frame to draw on
            fps: Current FPS
            frame_num: Current frame number
        """
        h, w = frame.shape[:2]

        # Calculate average FPS
        avg_fps = np.mean(self.fps_history) if self.fps_history else 0

        # Calculate elapsed time
        elapsed = time.time() - self.start_time if self.start_time else 0

        # Create semi-transparent overlay background
        overlay = frame.copy()

        # Determine overlay height based on number of classes
        num_classes = len(self.class_counts)
        overlay_height = 220 + (num_classes * 25)

        cv2.rectangle(overlay, (10, 10), (450, overlay_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw stats
        font = cv2.FONT_HERSHEY_SIMPLEX
        y = 40
        line_height = 30

        # Title
        cv2.putText(frame, "Chris Model - Real-Time Detection", (20, y),
                   font, 0.8, (0, 255, 255), 2)
        y += line_height

        # FPS - Large and prominent
        cv2.putText(frame, f"FPS: {avg_fps:.1f}", (20, y),
                   font, 0.9, (0, 255, 0), 2)
        y += line_height

        # Confidence threshold
        cv2.putText(frame, f"Confidence: {self.conf_threshold}", (20, y),
                   font, 0.6, (255, 255, 255), 1)
        y += line_height

        # Frame counter
        cv2.putText(frame, f"Frame: {frame_num}", (20, y),
                   font, 0.6, (255, 255, 255), 1)
        y += line_height

        # Time elapsed
        cv2.putText(frame, f"Time: {elapsed:.1f}s", (20, y),
                   font, 0.6, (255, 255, 255), 1)
        y += line_height

        # Total detections
        cv2.putText(frame, f"Total Detections: {self.total_detections}", (20, y),
                   font, 0.7, (0, 255, 255), 2)
        y += line_height

        # Class breakdown
        if self.class_counts:
            cv2.putText(frame, "Class Breakdown:", (20, y),
                       font, 0.6, (255, 255, 0), 1)
            y += line_height - 5

            for i, (class_name, count) in enumerate(sorted(
                self.class_counts.items(), key=lambda x: x[1], reverse=True
            )):
                color = self.colors[i % len(self.colors)]
                cv2.putText(frame, f"  {class_name}: {count}", (30, y),
                           font, 0.55, color, 1)
                y += 25

        # Instructions at bottom
        y = h - 40
        cv2.putText(frame, "Press 'q' to quit | 's' to save snapshot | SPACE to pause",
                   (20, y), font, 0.5, (255, 255, 0), 1)

    def run(self, video_source, save_output=False, display=True):
        """
        Run detection on video source

        Args:
            video_source: Video file path or camera index
            save_output: Save annotated video
            display: Display video window (set False for RPi headless mode)
        """
        print(f"Opening video: {video_source}")

        # Open video
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            print(f"❌ Error: Could not open video: {video_source}")
            return

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"\n✓ Video opened successfully!")
        print(f"  Resolution: {width}x{height}")
        print(f"  FPS: {fps}")
        print(f"  Total Frames: {total_frames}")
        print(f"  Duration: {total_frames/fps:.1f}s\n")

        # Setup video writer
        video_writer = None
        if save_output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"results/chris_demo_{timestamp}.mp4"
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            print(f"✓ Saving output to: {output_path}\n")

        self.start_time = time.time()
        paused = False
        snapshot_count = 0

        print("="*80)
        print("PROCESSING VIDEO")
        print("="*80)

        try:
            while True:
                if not paused:
                    ret, frame = cap.read()
                    if not ret:
                        print("\n✓ Video processing complete!")
                        break

                    self.frame_count += 1

                    # Process frame
                    annotated_frame, detections, current_fps = self.process_frame(frame)

                    # Draw overlay
                    self.draw_overlay(annotated_frame, current_fps, self.frame_count)

                    # Save video
                    if video_writer:
                        video_writer.write(annotated_frame)

                    # Display
                    if display:
                        cv2.imshow('Chris Model - Real-Time Detection', annotated_frame)

                    # Print progress every 30 frames
                    if self.frame_count % 30 == 0:
                        avg_fps = np.mean(self.fps_history[-30:]) if self.fps_history else 0
                        progress = (self.frame_count / total_frames * 100) if total_frames > 0 else 0
                        print(f"Frame {self.frame_count}/{total_frames} ({progress:.1f}%) | "
                              f"FPS: {avg_fps:.1f} | Detections: {len(detections)}")

                # Handle keyboard input (only if displaying)
                if display:
                    key = cv2.waitKey(1) & 0xFF

                    if key == ord('q'):
                        print("\n⚠ Quit requested by user")
                        break
                    elif key == ord('s'):
                        snapshot_path = f"results/snapshot_{snapshot_count:04d}.jpg"
                        cv2.imwrite(snapshot_path, annotated_frame)
                        print(f"  📸 Saved snapshot: {snapshot_path}")
                        snapshot_count += 1
                    elif key == ord(' '):
                        paused = not paused
                        status = "PAUSED" if paused else "RESUMED"
                        print(f"  ⏸ {status}")
                else:
                    # For headless mode (RPi), just continue
                    pass

        except KeyboardInterrupt:
            print("\n⚠ Interrupted by user")

        finally:
            # Cleanup
            cap.release()
            if video_writer:
                video_writer.release()
            if display:
                cv2.destroyAllWindows()

            # Print summary
            self._print_summary()

    def _print_summary(self):
        """Print final summary"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        avg_fps = np.mean(self.fps_history) if self.fps_history else 0

        print("\n" + "="*80)
        print("PROCESSING COMPLETE")
        print("="*80)
        print(f"Total Frames: {self.frame_count}")
        print(f"Duration: {elapsed:.1f}s")
        print(f"Average FPS: {avg_fps:.1f}")
        print(f"Total Detections: {self.total_detections}")
        print(f"\nClass Breakdown:")

        for class_name, count in sorted(
            self.class_counts.items(), key=lambda x: x[1], reverse=True
        ):
            pct = (count / self.total_detections * 100) if self.total_detections > 0 else 0
            print(f"  {class_name}: {count} ({pct:.1f}%)")

        print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Run Chris YOLO model on demo videos with real-time overlay',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run on demo video with default settings
  python run_chris_demo.py --video results/chris_model_eval/annotated_videos/good_flow_annotated_20251211_144324.mp4

  # Use specific model and confidence
  python run_chris_demo.py --video path/to/video.mp4 --model "Downloaded models/new_chris.pt" --conf 0.1

  # Save output and run headless (for RPi)
  python run_chris_demo.py --video path/to/video.mp4 --save --no-display

  # Use camera (RPi)
  python run_chris_demo.py --video 0 --conf 0.1
        """
    )

    parser.add_argument(
        '--video',
        type=str,
        required=True,
        help='Path to video file or camera index (0, 1, etc.)'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='Downloaded models/new_chris.pt',
        help='Path to YOLO model file (default: Downloaded models/new_chris.pt)'
    )

    parser.add_argument(
        '--conf',
        type=float,
        default=0.1,
        help='Confidence threshold (default: 0.1)'
    )

    parser.add_argument(
        '--save',
        action='store_true',
        help='Save annotated video output'
    )

    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Run without display window (headless mode for RPi)'
    )

    args = parser.parse_args()

    # Convert video argument to int if it's a camera index
    try:
        video_source = int(args.video)
    except ValueError:
        video_source = args.video

    # Create demo and run
    demo = ChrisRealtimeDemo(
        model_path=args.model,
        conf_threshold=args.conf
    )

    demo.run(
        video_source=video_source,
        save_output=args.save,
        display=not args.no_display
    )


if __name__ == '__main__':
    main()

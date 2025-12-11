#!/usr/bin/env python3
"""
Real-Time Plankton Flow Tracker with Deduplication
Handles flowing water - tracks each plankton and counts it only ONCE
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from datetime import datetime
from collections import defaultdict, deque
import argparse
import time


class FlowPlanktonTracker:
    """Tracks plankton in flowing water, counts each organism only once."""

    def __init__(self, model_path, conf_threshold=0.25, tracker="bytetrack.yaml"):
        """
        Initialize tracker.

        Args:
            model_path: Path to YOLO model (.pt file)
            conf_threshold: Confidence threshold for detections
            tracker: Tracker config (bytetrack.yaml or botsort.yaml)
        """
        print(f"Loading model: {model_path}")
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.tracker = tracker

        # Tracking state
        self.tracked_organisms = {}  # track_id -> {first_seen, last_seen, class, confidences}
        self.counted_organisms = set()  # IDs we've already counted
        self.species_counts = defaultdict(int)
        self.total_count = 0

        # Flow direction detection
        self.track_positions = defaultdict(lambda: deque(maxlen=10))  # track_id -> positions

        # Colors for visualization (one per class)
        self.class_colors = {}
        if hasattr(self.model, 'names'):
            num_classes = len(self.model.names)
            for i, class_name in self.model.names.items():
                # Generate distinct colors
                hue = int((i * 360 / num_classes) % 360)
                color = self._hsv_to_bgr(hue, 0.8, 0.9)
                self.class_colors[class_name] = color

        print(f"✓ Tracker initialized: {tracker}")
        print(f"✓ Confidence threshold: {conf_threshold}")
        if hasattr(self.model, 'names'):
            print(f"✓ Detecting {len(self.model.names)} classes: {list(self.model.names.values())}")

    def _hsv_to_bgr(self, h, s, v):
        """Convert HSV to BGR for OpenCV."""
        import colorsys
        r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
        return (int(b*255), int(g*255), int(r*255))

    def process_video(self, video_source, output_path=None, display=True, max_frames=None):
        """
        Process video with tracking.

        Args:
            video_source: Video file path or camera index (0, 1, etc.)
            output_path: Path to save annotated video (optional)
            display: Show live display window
            max_frames: Maximum frames to process (None = all)
        """
        # Open video
        try:
            video_source = int(video_source)  # Try as camera index
        except ValueError:
            pass  # It's a file path

        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise ValueError(f"Failed to open video source: {video_source}")

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        print(f"\nVideo: {width}x{height} @ {fps}fps")
        if total_frames > 0:
            print(f"Total frames: {total_frames} ({total_frames/fps:.1f}s)")

        # Setup output video
        out = None
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            print(f"Recording to: {output_path}")

        print("\n" + "="*80)
        print("PROCESSING STARTED")
        print("="*80)
        if display:
            print("Press 'q' to quit, 'r' to reset counts")
        print()

        frame_count = 0
        start_time = time.time()
        processing_times = []

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                if max_frames and frame_count > max_frames:
                    break

                # Track objects in frame
                frame_start = time.time()
                results = self.model.track(
                    frame,
                    conf=self.conf_threshold,
                    persist=True,  # Persist tracks between frames
                    tracker=self.tracker,
                    verbose=False
                )
                inference_time = (time.time() - frame_start) * 1000
                processing_times.append(inference_time)

                # Process tracking results
                annotated_frame = self._process_tracks(frame.copy(), results)

                # Add stats overlay
                annotated_frame = self._add_overlay(
                    annotated_frame,
                    frame_count,
                    inference_time,
                    fps
                )

                # Write to output video
                if out:
                    out.write(annotated_frame)

                # Display
                if display:
                    cv2.imshow('Plankton Flow Tracker', annotated_frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("\nStopped by user")
                        break
                    elif key == ord('r'):
                        print("\nResetting counts...")
                        self._reset_counts()

                # Progress update
                if frame_count % 30 == 0 or frame_count == 1:
                    elapsed = time.time() - start_time
                    avg_fps = frame_count / elapsed if elapsed > 0 else 0
                    print(f"Frame {frame_count}/{total_frames if total_frames > 0 else '?'} | "
                          f"FPS: {avg_fps:.1f} | "
                          f"Inference: {inference_time:.1f}ms | "
                          f"Unique count: {self.total_count}")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")

        finally:
            cap.release()
            if out:
                out.release()
            if display:
                cv2.destroyAllWindows()

            # Print final stats
            self._print_summary(frame_count, time.time() - start_time, processing_times)
            if output_path:
                print(f"\n✓ Output saved: {output_path}")

    def _process_tracks(self, frame, results):
        """Process tracking results and update counts."""
        current_frame_time = time.time()

        if results[0].boxes is None or len(results[0].boxes) == 0:
            return frame

        boxes = results[0].boxes

        # Check if tracking IDs are available
        if boxes.id is None:
            # No tracking, fall back to simple detection
            return self._draw_detections_only(frame, results)

        for box in boxes:
            # Get tracking ID
            track_id = int(box.id[0])

            # Get bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2

            # Get class and confidence
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = self.model.names[cls]

            # Track this organism
            if track_id not in self.tracked_organisms:
                # New organism detected
                self.tracked_organisms[track_id] = {
                    'first_seen': current_frame_time,
                    'last_seen': current_frame_time,
                    'class': class_name,
                    'confidences': [conf],
                    'bbox_history': [(x1, y1, x2, y2)]
                }

                # Count it (first time seeing this ID)
                if track_id not in self.counted_organisms:
                    self.counted_organisms.add(track_id)
                    self.species_counts[class_name] += 1
                    self.total_count += 1
                    status = "NEW"
                else:
                    status = "TRACKED"
            else:
                # Update existing track
                self.tracked_organisms[track_id]['last_seen'] = current_frame_time
                self.tracked_organisms[track_id]['confidences'].append(conf)
                self.tracked_organisms[track_id]['bbox_history'].append((x1, y1, x2, y2))
                status = "TRACKED"

            # Store position for flow direction
            self.track_positions[track_id].append((center_x, center_y))

            # Get flow direction
            direction = self._get_flow_direction(track_id)

            # Draw bounding box
            color = self.class_colors.get(class_name, (0, 255, 0))

            # Thicker box for NEW detections
            thickness = 3 if status == "NEW" else 2
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            # Draw track ID and info
            label = f"ID:{track_id} {class_name} {conf:.2f}"
            if direction:
                label += f" {direction}"

            # Label background
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            # Draw center point
            cv2.circle(frame, (center_x, center_y), 3, color, -1)

            # Draw trail for movement
            if len(self.track_positions[track_id]) > 1:
                points = list(self.track_positions[track_id])
                for i in range(len(points) - 1):
                    cv2.line(frame, points[i], points[i+1], color, 1)

        return frame

    def _draw_detections_only(self, frame, results):
        """Fallback: draw detections without tracking."""
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            class_name = self.model.names[cls]

            color = self.class_colors.get(class_name, (0, 255, 0))
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            label = f"{class_name} {conf:.2f} (NO TRACKING)"
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        return frame

    def _get_flow_direction(self, track_id):
        """Determine flow direction from position history."""
        positions = self.track_positions[track_id]
        if len(positions) < 3:
            return None

        # Calculate movement vector
        start = positions[0]
        end = positions[-1]

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        # Determine dominant direction
        if abs(dx) < 5 and abs(dy) < 5:
            return None  # Not moving enough

        if abs(dx) > abs(dy):
            return "→" if dx > 0 else "←"
        else:
            return "↓" if dy > 0 else "↑"

    def _add_overlay(self, frame, frame_num, inference_time, fps):
        """Add stats overlay to frame."""
        h, w = frame.shape[:2]

        # Dark background panel
        panel_height = 180
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, panel_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Title
        cv2.putText(frame, "PLANKTON FLOW TRACKER", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 3)

        # Stats
        y = 60
        cv2.putText(frame, f"Frame: {frame_num}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        y += 25
        cv2.putText(frame, f"Inference: {inference_time:.1f}ms ({1000/inference_time:.1f} FPS)",
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

        y += 25
        cv2.putText(frame, f"UNIQUE COUNT: {self.total_count}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 3)

        y += 25
        cv2.putText(frame, f"Active Tracks: {len(self.tracked_organisms)}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Species breakdown (right side)
        if self.species_counts:
            x_offset = w - 300
            y = 30
            cv2.putText(frame, "SPECIES:", (x_offset, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            y += 25
            for species, count in sorted(self.species_counts.items(),
                                        key=lambda x: x[1], reverse=True):
                color = self.class_colors.get(species, (255, 255, 255))
                cv2.putText(frame, f"{species}: {count}", (x_offset, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y += 20

        return frame

    def _reset_counts(self):
        """Reset all counts."""
        self.tracked_organisms.clear()
        self.counted_organisms.clear()
        self.species_counts.clear()
        self.total_count = 0
        self.track_positions.clear()
        print("✓ Counts reset")

    def _print_summary(self, total_frames, elapsed_time, processing_times):
        """Print final summary."""
        print("\n" + "="*80)
        print("PROCESSING COMPLETE")
        print("="*80)
        print(f"Frames processed: {total_frames}")
        print(f"Total time: {elapsed_time:.1f}s")
        print(f"Average FPS: {total_frames/elapsed_time:.1f}")

        if processing_times:
            avg_inference = np.mean(processing_times)
            print(f"Average inference: {avg_inference:.1f}ms ({1000/avg_inference:.1f} FPS)")
            print(f"Min/Max inference: {min(processing_times):.1f}ms / {max(processing_times):.1f}ms")

        print(f"\n{'='*80}")
        print(f"UNIQUE ORGANISMS DETECTED: {self.total_count}")
        print(f"{'='*80}")

        if self.species_counts:
            print("\nSPECIES BREAKDOWN:")
            for species, count in sorted(self.species_counts.items(),
                                        key=lambda x: x[1], reverse=True):
                pct = (count / self.total_count * 100) if self.total_count > 0 else 0
                print(f"  {species:.<30} {count:>4} ({pct:>5.1f}%)")

        print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Real-time plankton tracker for flowing water',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process video file with default settings
  python realtime_flow_tracker.py --video "Real_Time_Vids/good flow.mov"

  # Use webcam (camera 0)
  python realtime_flow_tracker.py --video 0

  # Process with output video
  python realtime_flow_tracker.py --video "Real_Time_Vids/trial.mov" --output results/tracked.mp4

  # Use specific model with custom confidence
  python realtime_flow_tracker.py --model "Downloaded models/chris_best.pt" --conf 0.3 --video test.mov

  # Different tracker (BoT-SORT instead of ByteTrack)
  python realtime_flow_tracker.py --video test.mov --tracker botsort.yaml
        """
    )

    parser.add_argument('--video', type=str, required=True,
                       help='Video file path or camera index (0, 1, etc.)')
    parser.add_argument('--model', type=str, default='Downloaded models/best.pt',
                       help='Path to YOLO model')
    parser.add_argument('--conf', type=float, default=0.25,
                       help='Confidence threshold (0.0-1.0)')
    parser.add_argument('--tracker', type=str, default='bytetrack.yaml',
                       choices=['bytetrack.yaml', 'botsort.yaml'],
                       help='Tracker algorithm')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video path (optional)')
    parser.add_argument('--no-display', action='store_true',
                       help='Disable live display (headless mode)')
    parser.add_argument('--max-frames', type=int, default=None,
                       help='Maximum frames to process (for testing)')

    args = parser.parse_args()

    # Create tracker
    tracker = FlowPlanktonTracker(
        model_path=args.model,
        conf_threshold=args.conf,
        tracker=args.tracker
    )

    # Process video
    tracker.process_video(
        video_source=args.video,
        output_path=args.output,
        display=not args.no_display,
        max_frames=args.max_frames
    )


if __name__ == '__main__':
    main()

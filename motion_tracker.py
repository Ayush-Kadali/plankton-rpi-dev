#!/usr/bin/env python3
"""
Simple Motion-Based Tracker for Flowing Water
Detects ANY moving object and tracks it - no ML needed!
"""

import cv2
import numpy as np
from collections import defaultdict, deque
from pathlib import Path
import argparse
import time


class CentroidTracker:
    """Simple centroid-based tracker."""

    def __init__(self, max_disappeared=30, min_distance=30):
        self.next_object_id = 0
        self.objects = {}  # id -> centroid
        self.disappeared = defaultdict(int)
        self.max_disappeared = max_disappeared
        self.min_distance = min_distance

        # History
        self.object_history = defaultdict(lambda: deque(maxlen=20))
        self.object_first_seen = {}

    def register(self, centroid):
        """Register a new object."""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.object_first_seen[self.next_object_id] = True
        self.next_object_id += 1
        return self.next_object_id - 1

    def deregister(self, object_id):
        """Remove an object."""
        del self.objects[object_id]
        del self.disappeared[object_id]
        if object_id in self.object_history:
            del self.object_history[object_id]

    def update(self, input_centroids):
        """Update tracked objects with new detections."""
        # If no detections, mark all as disappeared
        if len(input_centroids) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects, {}

        # If no existing objects, register all
        if len(self.objects) == 0:
            new_ids = {}
            for centroid in input_centroids:
                obj_id = self.register(centroid)
                new_ids[obj_id] = True
            return self.objects, new_ids

        # Match existing objects to new centroids
        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())

        # Compute distance matrix
        D = np.zeros((len(object_centroids), len(input_centroids)))
        for i, obj_centroid in enumerate(object_centroids):
            for j, input_centroid in enumerate(input_centroids):
                D[i, j] = np.linalg.norm(np.array(obj_centroid) - np.array(input_centroid))

        # Find minimum distances
        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]

        used_rows = set()
        used_cols = set()
        new_ids = {}

        # Match based on minimum distance
        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue

            if D[row, col] > self.min_distance:
                continue

            object_id = object_ids[row]
            self.objects[object_id] = input_centroids[col]
            self.disappeared[object_id] = 0
            self.object_history[object_id].append(input_centroids[col])
            self.object_first_seen[object_id] = False

            used_rows.add(row)
            used_cols.add(col)

        # Register new objects
        unused_rows = set(range(D.shape[0])) - used_rows
        unused_cols = set(range(D.shape[1])) - used_cols

        # Mark unused existing objects as disappeared
        for row in unused_rows:
            object_id = object_ids[row]
            self.disappeared[object_id] += 1
            if self.disappeared[object_id] > self.max_disappeared:
                self.deregister(object_id)

        # Register new detections
        for col in unused_cols:
            obj_id = self.register(input_centroids[col])
            new_ids[obj_id] = True

        return self.objects, new_ids


class MotionTracker:
    """Motion-based tracker for flowing particles."""

    def __init__(self, min_area=20, max_area=5000, blur_size=5):
        self.min_area = min_area
        self.max_area = max_area
        self.blur_size = blur_size

        # Background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=100,
            varThreshold=40,
            detectShadows=False
        )

        # Tracker
        self.tracker = CentroidTracker(max_disappeared=30, min_distance=50)

        # Stats
        self.total_unique_count = 0
        self.counted_ids = set()
        self.frame_count = 0

        # Colors
        self.colors = {}

    def _get_color(self, object_id):
        """Get consistent color for object ID."""
        if object_id not in self.colors:
            # Generate color based on ID
            np.random.seed(object_id)
            self.colors[object_id] = tuple(map(int, np.random.randint(50, 255, 3)))
        return self.colors[object_id]

    def detect_motion(self, frame):
        """Detect moving objects in frame."""
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame)

        # Blur to reduce noise
        fg_mask = cv2.GaussianBlur(fg_mask, (self.blur_size, self.blur_size), 0)

        # Threshold
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Extract centroids and bounding boxes
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area or area > self.max_area:
                continue

            # Get centroid
            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)

            detections.append({
                'centroid': (cx, cy),
                'bbox': (x, y, w, h),
                'area': area,
                'contour': contour
            })

        return detections, fg_mask

    def process_frame(self, frame):
        """Process a single frame."""
        self.frame_count += 1

        # Detect motion
        detections, fg_mask = self.detect_motion(frame)

        # Extract centroids
        centroids = [d['centroid'] for d in detections]

        # Update tracker
        objects, new_ids = self.tracker.update(centroids)

        # Count new objects
        for obj_id in new_ids:
            if obj_id not in self.counted_ids:
                self.counted_ids.add(obj_id)
                self.total_unique_count += 1

        # Draw on frame
        annotated = self._draw_tracks(frame.copy(), detections, objects, new_ids)

        return annotated, fg_mask, len(detections)

    def _draw_tracks(self, frame, detections, objects, new_ids):
        """Draw tracking information on frame."""
        # Create detection lookup by centroid
        detection_by_centroid = {d['centroid']: d for d in detections}

        # Draw each tracked object
        for obj_id, centroid in objects.items():
            color = self._get_color(obj_id)

            # Find matching detection
            detection = detection_by_centroid.get(centroid)

            # Draw bounding box if we have detection
            if detection:
                x, y, w, h = detection['bbox']

                # Thicker box for new detections
                thickness = 4 if obj_id in new_ids else 2
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, thickness)

                # Label
                label = f"ID:{obj_id}"
                if obj_id in new_ids:
                    label += " NEW"

                # Draw label background
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
                cv2.rectangle(frame, (x, y-label_size[1]-10),
                            (x+label_size[0], y), color, -1)
                cv2.putText(frame, label, (x, y-5),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Draw center point
            cv2.circle(frame, centroid, 4, color, -1)

            # Draw trail
            if obj_id in self.tracker.object_history:
                points = list(self.tracker.object_history[obj_id])
                if len(points) > 1:
                    for i in range(len(points) - 1):
                        cv2.line(frame, points[i], points[i+1], color, 2)

        return frame

    def add_overlay(self, frame, inference_time):
        """Add stats overlay."""
        h, w = frame.shape[:2]

        # Dark panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 160), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Title
        cv2.putText(frame, "MOTION-BASED TRACKER", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 3)

        # Stats
        y = 65
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        y += 30
        cv2.putText(frame, f"Processing: {inference_time:.1f}ms ({1000/inference_time:.1f} FPS)",
                   (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

        y += 30
        cv2.putText(frame, f"UNIQUE COUNT: {self.total_unique_count}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 3)

        y += 30
        cv2.putText(frame, f"Active Tracks: {len(self.tracker.objects)}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        return frame

    def reset(self):
        """Reset all counts."""
        self.total_unique_count = 0
        self.counted_ids.clear()
        self.tracker = CentroidTracker(max_disappeared=30, min_distance=50)


def process_video(video_path, output_path=None, display=True,
                 min_area=20, max_area=5000, show_mask=False):
    """Process video with motion tracking."""

    print(f"\nOpening video: {video_path}")

    # Open video
    try:
        video_source = int(video_path)
    except ValueError:
        video_source = video_path

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        raise ValueError(f"Failed to open: {video_path}")

    # Get properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video: {width}x{height} @ {fps}fps")
    if total_frames > 0:
        print(f"Total frames: {total_frames} ({total_frames/fps:.1f}s)")

    # Setup output
    out = None
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        print(f"Recording to: {output_path}")

    # Create tracker
    tracker = MotionTracker(min_area=min_area, max_area=max_area)

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

            # Process
            frame_start = time.time()
            annotated, fg_mask, detections = tracker.process_frame(frame)
            inference_time = (time.time() - frame_start) * 1000
            processing_times.append(inference_time)

            # Add overlay
            annotated = tracker.add_overlay(annotated, inference_time)

            # Write output
            if out:
                out.write(annotated)

            # Display
            if display:
                if show_mask:
                    # Show side-by-side
                    fg_mask_color = cv2.cvtColor(fg_mask, cv2.COLOR_GRAY2BGR)
                    combined = np.hstack([annotated, fg_mask_color])
                    cv2.imshow('Motion Tracker | Foreground Mask', combined)
                else:
                    cv2.imshow('Motion Tracker', annotated)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("\nStopped by user")
                    break
                elif key == ord('r'):
                    print("\nResetting counts...")
                    tracker.reset()
                elif key == ord('m'):
                    show_mask = not show_mask

            # Progress
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                avg_fps = frame_count / elapsed
                print(f"Frame {frame_count}/{total_frames if total_frames > 0 else '?'} | "
                      f"FPS: {avg_fps:.1f} | "
                      f"Processing: {inference_time:.1f}ms | "
                      f"Detections: {detections} | "
                      f"Unique: {tracker.total_unique_count}")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")

    finally:
        cap.release()
        if out:
            out.release()
        if display:
            cv2.destroyAllWindows()

        # Print summary
        elapsed = time.time() - start_time
        print("\n" + "="*80)
        print("PROCESSING COMPLETE")
        print("="*80)
        print(f"Frames processed: {frame_count}")
        print(f"Total time: {elapsed:.1f}s")
        print(f"Average FPS: {frame_count/elapsed:.1f}")

        if processing_times:
            avg_time = np.mean(processing_times)
            print(f"Average processing: {avg_time:.1f}ms ({1000/avg_time:.1f} FPS)")

        print(f"\n{'='*80}")
        print(f"UNIQUE OBJECTS DETECTED: {tracker.total_unique_count}")
        print(f"{'='*80}\n")

        if output_path:
            print(f"✓ Output saved: {output_path}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Motion-based tracker for flowing water',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process video
  python motion_tracker.py --video "Real_Time_Vids/good flow.mov"

  # Save output
  python motion_tracker.py --video "test.mov" --output "results/tracked.mp4"

  # Adjust sensitivity
  python motion_tracker.py --video "test.mov" --min-area 10 --max-area 1000

  # Show motion mask
  python motion_tracker.py --video "test.mov" --show-mask

  # Webcam
  python motion_tracker.py --video 0
        """
    )

    parser.add_argument('--video', type=str, required=True,
                       help='Video file or camera index')
    parser.add_argument('--output', type=str, default=None,
                       help='Output video path')
    parser.add_argument('--min-area', type=int, default=20,
                       help='Minimum object area (pixels)')
    parser.add_argument('--max-area', type=int, default=5000,
                       help='Maximum object area (pixels)')
    parser.add_argument('--no-display', action='store_true',
                       help='Headless mode')
    parser.add_argument('--show-mask', action='store_true',
                       help='Show foreground mask')

    args = parser.parse_args()

    process_video(
        video_path=args.video,
        output_path=args.output,
        display=not args.no_display,
        min_area=args.min_area,
        max_area=args.max_area,
        show_mask=args.show_mask
    )


if __name__ == '__main__':
    main()

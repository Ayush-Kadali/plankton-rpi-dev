#!/usr/bin/env python3
"""
Hybrid Tracker: YOLO Detection + Better Tracking
Uses YOLO to find objects, tracks them properly, counts once
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from collections import defaultdict, deque
import argparse
import time


def main():
    parser = argparse.ArgumentParser(description='Hybrid tracker with adjustable settings')

    parser.add_argument('--video', type=str, required=True)
    parser.add_argument('--model', type=str, default='Downloaded models/best.pt')
    parser.add_argument('--output', type=str, default=None)
    parser.add_argument('--conf', type=float, default=0.05,
                       help='VERY LOW confidence to catch everything')
    parser.add_argument('--iou', type=float, default=0.3,
                       help='IoU threshold for NMS')
    parser.add_argument('--no-display', action='store_true')

    args = parser.parse_args()

    print(f"\nLoading model: {args.model}")
    model = YOLO(args.model)

    # Open video
    try:
        video_source = int(args.video)
    except ValueError:
        video_source = args.video

    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        raise ValueError(f"Failed to open: {args.video}")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames")
    print(f"Confidence threshold: {args.conf}")
    print(f"IoU threshold: {args.iou}")

    # Setup output
    out = None
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(args.output, fourcc, fps, (width, height))
        print(f"Recording to: {args.output}")

    print("\n" + "="*80)
    print("PROCESSING STARTED")
    print("="*80)
    if not args.no_display:
        print("Press 'q' to quit")
    print()

    frame_count = 0
    unique_count = 0
    counted_ids = set()
    start_time = time.time()

    # Track statistics
    species_counts = defaultdict(int)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Run YOLO tracking with very low confidence
            frame_start = time.time()
            results = model.track(
                frame,
                conf=args.conf,
                iou=args.iou,
                persist=True,
                tracker="bytetrack.yaml",
                verbose=False,
                agnostic_nms=True  # Class-agnostic NMS
            )
            inference_time = (time.time() - frame_start) * 1000

            # Process results
            annotated = frame.copy()

            if results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes

                if boxes.id is not None:
                    for box in boxes:
                        # Get tracking ID
                        track_id = int(box.id[0])

                        # Count if new
                        if track_id not in counted_ids:
                            counted_ids.add(track_id)
                            unique_count += 1

                            # Count species if available
                            cls = int(box.cls[0])
                            class_name = model.names[cls]
                            species_counts[class_name] += 1

                            is_new = True
                        else:
                            is_new = False

                        # Draw
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        class_name = model.names[cls]

                        # Color: green for new, blue for tracked
                        color = (0, 255, 0) if is_new else (255, 128, 0)
                        thickness = 3 if is_new else 2

                        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, thickness)

                        label = f"ID:{track_id}"
                        if is_new:
                            label += " NEW"
                        label += f" {class_name[:4]} {conf:.2f}"

                        # Label background
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                        cv2.rectangle(annotated, (x1, y1-label_size[1]-8),
                                    (x1+label_size[0], y1), color, -1)
                        cv2.putText(annotated, label, (x1, y1-4),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

            # Add overlay
            overlay = annotated.copy()
            cv2.rectangle(overlay, (0, 0), (width, 120), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, annotated, 0.3, 0, annotated)

            cv2.putText(annotated, f"HYBRID TRACKER (YOLO + ByteTrack)", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(annotated, f"Frame: {frame_count}/{total_frames}", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(annotated, f"FPS: {1000/inference_time:.1f} ({inference_time:.1f}ms)", (10, 70),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(annotated, f"UNIQUE COUNT: {unique_count}", (10, 95),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Species counts
            if species_counts:
                x_offset = width - 250
                y = 25
                cv2.putText(annotated, "SPECIES:", (x_offset, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y += 20
                for sp, cnt in sorted(species_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    cv2.putText(annotated, f"{sp[:10]}: {cnt}", (x_offset, y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                    y += 18

            # Write
            if out:
                out.write(annotated)

            # Display
            if not args.no_display:
                cv2.imshow('Hybrid Tracker', annotated)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopped by user")
                    break

            # Progress
            if frame_count % 60 == 0:
                elapsed = time.time() - start_time
                avg_fps = frame_count / elapsed
                print(f"Frame {frame_count}/{total_frames} | FPS: {avg_fps:.1f} | Unique: {unique_count}")

    except KeyboardInterrupt:
        print("\n\nInterrupted")

    finally:
        cap.release()
        if out:
            out.release()
        if not args.no_display:
            cv2.destroyAllWindows()

        elapsed = time.time() - start_time
        print("\n" + "="*80)
        print("PROCESSING COMPLETE")
        print("="*80)
        print(f"Frames: {frame_count}")
        print(f"Time: {elapsed:.1f}s ({frame_count/elapsed:.1f} FPS)")
        print(f"\n{'='*80}")
        print(f"UNIQUE ORGANISMS DETECTED: {unique_count}")
        print(f"{'='*80}\n")

        if species_counts:
            print("SPECIES BREAKDOWN:")
            for sp, cnt in sorted(species_counts.items(), key=lambda x: x[1], reverse=True):
                pct = (cnt / unique_count * 100) if unique_count > 0 else 0
                print(f"  {sp:.<30} {cnt:>4} ({pct:>5.1f}%)")

        if args.output:
            print(f"\n✓ Output saved: {args.output}\n")


if __name__ == '__main__':
    main()

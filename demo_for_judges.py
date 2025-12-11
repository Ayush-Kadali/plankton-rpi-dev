#!/usr/bin/env python3
"""
SIMPLE JUDGE DEMO - Plankton Detection
Shows real-time detection with bounding boxes
"""

import cv2
from ultralytics import YOLO
from pathlib import Path
import argparse
import time

def run_demo(model_path, source=0, conf=0.25, fullscreen=False):
    """
    Simple demo - just show detections with bounding boxes

    Args:
        model_path: Path to model
        source: 0 for webcam, or path to video file
        conf: Confidence threshold
        fullscreen: Run in fullscreen mode
    """

    print("\n" + "="*80)
    print("PLANKTON DETECTION - JUDGE DEMO")
    print("="*80)
    print(f"Model: {Path(model_path).name}")
    print(f"Source: {'Webcam' if source == 0 else source}")
    print(f"Confidence: {conf}")
    print("="*80)
    print("\nPress 'q' to quit, 'f' for fullscreen, 's' to save frame")
    print("="*80 + "\n")

    # Load model
    print("Loading model...")
    model = YOLO(model_path)
    print(f"✓ Model loaded - Detecting {len(model.names)} classes\n")

    # Open video source
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        print(f"❌ Error: Cannot open source: {source}")
        return

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"✓ Video opened: {width}x{height}\n")

    # Stats
    frame_count = 0
    total_detections = 0
    start_time = time.time()

    # Create window
    window_name = "Plankton Detection - Press Q to Quit"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    if fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    print("🎥 DEMO RUNNING...\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                if source != 0:
                    # Video ended, loop it
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    print("❌ Cannot read from camera")
                    break

            frame_count += 1

            # Run detection
            results = model(frame, conf=conf, verbose=False)

            # Get annotated frame with bounding boxes
            annotated_frame = results[0].plot()

            # Count detections
            frame_dets = len(results[0].boxes)
            total_detections += frame_dets

            # Calculate FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0

            # Add clean stats overlay
            overlay_y = 40
            overlay_color = (0, 255, 0)  # Green
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0
            thickness = 2

            # Background for text
            cv2.rectangle(annotated_frame, (10, 10), (400, 150), (0, 0, 0), -1)
            cv2.rectangle(annotated_frame, (10, 10), (400, 150), overlay_color, 2)

            # Stats text
            cv2.putText(annotated_frame, f"FPS: {fps:.1f}",
                       (20, overlay_y), font, font_scale, overlay_color, thickness)
            cv2.putText(annotated_frame, f"Detections: {total_detections}",
                       (20, overlay_y + 40), font, font_scale, overlay_color, thickness)
            cv2.putText(annotated_frame, f"Current: {frame_dets}",
                       (20, overlay_y + 80), font, font_scale, overlay_color, thickness)

            # Show frame
            cv2.imshow(window_name, annotated_frame)

            # Handle key presses
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("\n✓ Demo stopped by user")
                break
            elif key == ord('f'):
                # Toggle fullscreen
                current_state = cv2.getWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN)
                if current_state == cv2.WINDOW_FULLSCREEN:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                else:
                    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            elif key == ord('s'):
                # Save current frame
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"demo_frame_{timestamp}.jpg"
                cv2.imwrite(filename, annotated_frame)
                print(f"✓ Saved frame: {filename}")

    except KeyboardInterrupt:
        print("\n✓ Demo stopped (Ctrl+C)")

    finally:
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()

        # Final stats
        elapsed = time.time() - start_time
        print("\n" + "="*80)
        print("DEMO SUMMARY")
        print("="*80)
        print(f"Runtime: {elapsed:.1f}s")
        print(f"Frames: {frame_count}")
        print(f"Average FPS: {fps:.1f}")
        print(f"Total Detections: {total_detections}")
        print("="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Simple Plankton Detection Demo for Judges')
    parser.add_argument('--model', type=str, default='Downloaded models/new_chris.pt',
                       help='Path to model file')
    parser.add_argument('--source', type=str, default='0',
                       help='Video source: 0 for webcam, or path to video file')
    parser.add_argument('--conf', type=float, default=0.25,
                       help='Confidence threshold (default: 0.25)')
    parser.add_argument('--fullscreen', action='store_true',
                       help='Start in fullscreen mode')

    args = parser.parse_args()

    # Check if model exists
    if not Path(args.model).exists():
        print(f"❌ Model not found: {args.model}")
        print("\nAvailable models:")
        for p in Path('Downloaded models').glob('*.pt'):
            print(f"  - {p}")
        return

    # Parse source (0 for webcam, else file path)
    source = 0 if args.source == '0' else args.source

    # Check if video file exists
    if source != 0 and not Path(source).exists():
        print(f"❌ Video file not found: {source}")
        print("\nAvailable videos:")
        for p in Path('Real_Time_Vids').glob('*.mov'):
            print(f"  - {p}")
        return

    # Run demo
    run_demo(args.model, source, args.conf, args.fullscreen)


if __name__ == "__main__":
    main()

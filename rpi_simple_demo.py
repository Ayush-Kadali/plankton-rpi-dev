#!/usr/bin/env python3
"""
Simple Raspberry Pi Demo - Real-time Plankton Detection
Copy this entire file to your Raspberry Pi and run it!
"""

import cv2
from ultralytics import YOLO
import time

# ============================================================================
# CONFIGURATION - CHANGE THESE IF NEEDED
# ============================================================================
MODEL_PATH = "models/new_chris.pt"  # Change to your model path
CAMERA_ID = 0  # 0 for default camera
CONFIDENCE = 0.25  # Detection confidence threshold
SHOW_DISPLAY = True  # Set False for headless mode
SAVE_VIDEO = False  # Set True to save video

# ============================================================================
# MAIN DEMO CODE
# ============================================================================

print("="*80)
print("RASPBERRY PI - REAL-TIME PLANKTON DETECTION")
print("="*80)

# Load model
print(f"\nLoading model: {MODEL_PATH}")
try:
    model = YOLO(MODEL_PATH)
    print(f"✓ Model loaded - Detecting {len(model.names)} classes")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("\nMake sure model file exists!")
    exit(1)

# Open camera
print(f"Opening camera {CAMERA_ID}...")
cap = cv2.VideoCapture(CAMERA_ID)

if not cap.isOpened():
    print(f"❌ Cannot open camera {CAMERA_ID}")
    print("\nTry:")
    print("  - Check camera is connected")
    print("  - Run: ls /dev/video*")
    print("  - Try different CAMERA_ID (1, 2, etc.)")
    exit(1)

# Get camera properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

print(f"✓ Camera opened: {width}x{height} @ {fps} FPS")

# Setup video writer if saving
video_writer = None
if SAVE_VIDEO:
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"detection_{timestamp}.mp4"
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_file, fourcc, 10, (width, height))
    print(f"✓ Saving video to: {output_file}")

# Create window if display enabled
if SHOW_DISPLAY:
    cv2.namedWindow('Plankton Detection', cv2.WINDOW_NORMAL)
    print("\n✓ Display enabled - Press 'q' to quit")
else:
    print("\n✓ Headless mode - Press Ctrl+C to quit")

print("="*80)
print("🎥 DETECTION RUNNING...")
print("="*80)

# Stats
frame_count = 0
total_detections = 0
start_time = time.time()

try:
    while True:
        # Read frame
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to read frame")
            break

        frame_count += 1

        # Run detection
        results = model(frame, conf=CONFIDENCE, verbose=False)

        # Get annotated frame with bounding boxes
        annotated_frame = results[0].plot()

        # Count detections this frame
        num_detections = len(results[0].boxes)
        total_detections += num_detections

        # Calculate FPS
        elapsed = time.time() - start_time
        current_fps = frame_count / elapsed if elapsed > 0 else 0

        # Add stats overlay
        cv2.rectangle(annotated_frame, (5, 5), (350, 100), (0, 0, 0), -1)
        cv2.rectangle(annotated_frame, (5, 5), (350, 100), (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"FPS: {current_fps:.1f}",
                   (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"Total: {total_detections}",
                   (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(annotated_frame, f"Current: {num_detections}",
                   (15, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Save to video if enabled
        if video_writer:
            video_writer.write(annotated_frame)

        # Display if enabled
        if SHOW_DISPLAY:
            cv2.imshow('Plankton Detection', annotated_frame)

            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\n✓ Quit by user")
                break

        # Print stats every 30 frames
        if frame_count % 30 == 0:
            print(f"Frame {frame_count} | FPS: {current_fps:.1f} | "
                  f"Detections: {total_detections} | Current: {num_detections}")

except KeyboardInterrupt:
    print("\n✓ Stopped by user (Ctrl+C)")

finally:
    # Cleanup
    cap.release()
    if video_writer:
        video_writer.release()
    if SHOW_DISPLAY:
        cv2.destroyAllWindows()

    # Final stats
    elapsed = time.time() - start_time
    avg_fps = frame_count / elapsed if elapsed > 0 else 0

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Frames Processed: {frame_count}")
    print(f"Runtime: {elapsed:.1f}s")
    print(f"Average FPS: {avg_fps:.1f}")
    print(f"Total Detections: {total_detections}")
    print(f"Avg Detections/Frame: {total_detections/frame_count:.2f}")

    if video_writer:
        print(f"\n✓ Video saved: {output_file}")

    print("="*80)

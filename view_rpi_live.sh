#!/bin/bash
# View RPi camera output in real-time on your laptop

set -e

# Load config
source .rpi_config 2>/dev/null || {
    RPI_USER="pi"
    RPI_HOST="raspberrypi.local"
    RPI_PROJECT_DIR="~/plankton"
}

echo "========================================"
echo "📺 LIVE VIEW FROM RPi"
echo "========================================"
echo ""

# Method 1: X11 Forwarding (if RPi has display enabled)
if [ "$1" = "x11" ]; then
    echo "Using X11 forwarding..."
    ssh -X "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && python3 DEMO_RPI.py"
    exit 0
fi

# Method 2: VNC (if you have VNC server on RPi)
if [ "$1" = "vnc" ]; then
    echo "Opening VNC viewer..."
    echo "Connect to: $RPI_HOST:5900"
    open "vnc://$RPI_HOST" 2>/dev/null || echo "Open VNC Viewer and connect to $RPI_HOST"
    exit 0
fi

# Method 3: Video streaming via SSH (recommended)
echo "Starting video stream from RPi..."
echo "This will open a window showing the detection in real-time"
echo ""

# Create named pipe
FIFO="/tmp/rpi_stream_$$"
mkfifo $FIFO

# Start ffplay in background
ffplay -i $FIFO -window_title "RPi Live Detection" &
FFPLAY_PID=$!

# Cleanup on exit
trap "rm -f $FIFO; kill $FFPLAY_PID 2>/dev/null" EXIT

# Stream from RPi
ssh "$RPI_USER@$RPI_HOST" "cd $RPI_PROJECT_DIR && \
    python3 -c \"
import cv2
import sys
from DEMO_RPI import PlanktonDetectorRPi

detector = PlanktonDetectorRPi()
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    detections = detector.detect_frame(frame)
    detector.draw_minimal(frame, detections)
    detector.draw_stats_minimal(frame)

    # Encode and write to stdout
    _, encoded = cv2.imencode('.jpg', frame)
    sys.stdout.buffer.write(encoded.tobytes())
    sys.stdout.buffer.flush()
\"" > $FIFO

echo ""
echo "✅ Stream ended"
echo "========================================"

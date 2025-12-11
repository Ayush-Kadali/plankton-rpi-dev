#!/bin/bash
# Quick launcher for Chris Model Demo

echo "======================================================================"
echo "Chris Model Real-Time Demo Launcher"
echo "======================================================================"
echo ""
echo "Select a demo to run:"
echo ""
echo "1) Demo video 1 (good_flow) - Desktop"
echo "2) Demo video 2 (v4_try_2) - Desktop"
echo "3) Webcam - Desktop"
echo "4) RPi mode (video file - you provide path)"
echo "5) RPi mode with camera"
echo "6) Custom (manual options)"
echo ""
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        echo "Running demo on good_flow video..."
        python run_chris_demo.py \
            --video "results/chris_model_eval/annotated_videos/good_flow_annotated_20251211_144324.mp4" \
            --model "Downloaded models/new_chris.pt" \
            --conf 0.1 \
            --save
        ;;
    2)
        echo "Running demo on v4_try_2 video..."
        python run_chris_demo.py \
            --video "results/chris_model_eval/annotated_videos/v4_try_2_annotated_20251211_145648.mp4" \
            --model "Downloaded models/new_chris.pt" \
            --conf 0.1 \
            --save
        ;;
    3)
        echo "Running demo with webcam..."
        python run_chris_demo.py \
            --video 0 \
            --model "Downloaded models/new_chris.pt" \
            --conf 0.1 \
            --save
        ;;
    4)
        read -p "Enter video file path: " video_path
        echo "Running RPi demo on $video_path..."
        python rpi_chris_demo.py \
            --video "$video_path" \
            --model "Downloaded models/new_chris.pt" \
            --conf 0.1 \
            --save
        ;;
    5)
        echo "Running RPi demo with camera..."
        python rpi_chris_demo.py \
            --video 0 \
            --model "Downloaded models/new_chris.pt" \
            --conf 0.1 \
            --save
        ;;
    6)
        echo "Custom mode - edit the script or run manually:"
        echo ""
        echo "Desktop:"
        echo "  python run_chris_demo.py --video <path> --conf 0.1 --save"
        echo ""
        echo "RPi:"
        echo "  python rpi_chris_demo.py --video <path> --conf 0.1 --save [--headless]"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
echo "Done! Check the results/ directory for output videos."
echo "======================================================================"

#!/bin/bash
# PRESENTATION MODE - For Judges Demo

clear
echo "========================================"
echo "🎓 PLANKTON DETECTION - PRESENTATION MODE"
echo "========================================"
echo ""
echo "Select demo mode:"
echo ""
echo "  1. 🌟 Professional Demo (RECOMMENDED)"
echo "     → Enhanced UI with live dashboard"
echo "     → Real-time statistics"
echo "     → Perfect for presentation"
echo ""
echo "  2. ⚡ Quick Demo"
echo "     → Clean and fast"
echo "     → Basic detection"
echo ""
echo "  3. 🔬 Model Comparison"
echo "     → Side-by-side comparison"
echo "     → Show multiple models"
echo ""
echo "  4. 📹 Select Custom Video"
echo ""
echo "  0. ❌ Exit"
echo ""
echo "========================================"
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🌟 Starting Professional Demo..."
        echo ""
        echo "Select video:"
        echo "  1. Good Flow (recommended)"
        echo "  2. Trial"
        echo "  3. Good Flow v2"
        echo "  4. Use webcam"
        read -p "Select [1-4]: " video_choice

        case $video_choice in
            1) VIDEO="Real_Time_Vids/good flow.mov" ;;
            2) VIDEO="Real_Time_Vids/trial.mov" ;;
            3) VIDEO="Real_Time_Vids/v4 try 2.mov" ;;
            4) VIDEO="0" ;;
            *) VIDEO="Real_Time_Vids/good flow.mov" ;;
        esac

        echo ""
        echo "🎬 Launching..."
        echo "   Video: $VIDEO"
        echo "   Mode: Professional with Dashboard"
        echo ""
        echo "Controls:"
        echo "   'q' - Quit"
        echo "   's' - Screenshot"
        echo "   'r' - Reset stats"
        echo ""
        sleep 2
        python3 DEMO_PROFESSIONAL.py --source "$VIDEO"
        ;;

    2)
        echo ""
        echo "⚡ Starting Quick Demo..."
        read -p "Video file or '0' for webcam: " VIDEO
        [ -z "$VIDEO" ] && VIDEO="Real_Time_Vids/good flow.mov"

        python3 DEMO.py --source "$VIDEO"
        ;;

    3)
        echo ""
        echo "🔬 Model Comparison Mode"
        echo ""
        echo "Available models:"
        echo "  1. best.pt"
        echo "  2. yolov8n.pt"
        echo "  3. yolov5nu.pt"
        echo ""
        read -p "Select video file: " VIDEO
        [ -z "$VIDEO" ] && VIDEO="Real_Time_Vids/good flow.mov"

        echo ""
        echo "Comparing: best.pt vs yolov8n.pt"
        python3 DEMO_COMPARISON.py \
            --models "Downloaded models/best.pt" "Downloaded models/yolov8n.pt" \
            --source "$VIDEO"
        ;;

    4)
        echo ""
        echo "📹 Available videos:"
        ls -1 Real_Time_Vids/*.mov 2>/dev/null | nl
        echo ""
        read -p "Enter video path: " VIDEO

        if [ -f "$VIDEO" ]; then
            python3 DEMO_PROFESSIONAL.py --source "$VIDEO"
        else
            echo "❌ File not found"
        fi
        ;;

    0)
        echo "Goodbye!"
        exit 0
        ;;

    *)
        echo "❌ Invalid choice"
        ;;
esac

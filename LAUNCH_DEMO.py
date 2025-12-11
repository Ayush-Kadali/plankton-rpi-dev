#!/usr/bin/env python3
"""
PLANKTON DEMO LAUNCHER
One-stop launcher for all demo functions
"""

import subprocess
import sys
from pathlib import Path

def print_header():
    print("\n" + "=" * 80)
    print("🔬 PLANKTON DETECTION SYSTEM - DEMO LAUNCHER")
    print("=" * 80)

def print_menu():
    print("\n📋 Select demo mode:\n")
    print("  1. 📹 Live Camera Detection (Webcam)")
    print("  2. 🎬 Video File Detection")
    print("  3. 🗺️  View Detection Map")
    print("  4. 🧪 Quick Test (10 seconds)")
    print("  5. ⚙️  Settings")
    print("  0. ❌ Exit\n")

def run_command(cmd):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def get_video_files():
    """Get list of available video files"""
    video_dir = Path("Real_Time_Vids")
    if not video_dir.exists():
        return []

    videos = list(video_dir.glob("*.mov")) + list(video_dir.glob("*.mp4"))
    return sorted(videos)

def select_video():
    """Let user select a video file"""
    videos = get_video_files()

    if not videos:
        print("\n❌ No video files found in Real_Time_Vids/")
        return None

    print("\n📁 Available videos:\n")
    for i, video in enumerate(videos, 1):
        size_mb = video.stat().st_size / (1024*1024)
        print(f"  {i}. {video.name} ({size_mb:.1f} MB)")

    print("\n  0. Back")

    try:
        choice = int(input("\nSelect video: "))
        if choice == 0:
            return None
        if 1 <= choice <= len(videos):
            return videos[choice-1]
    except:
        pass

    print("Invalid selection")
    return None

def show_settings():
    """Show and modify settings"""
    print("\n" + "=" * 80)
    print("⚙️  SETTINGS")
    print("=" * 80)

    # Default settings
    settings = {
        "model": "Downloaded models/best.pt",
        "confidence": 0.15,
        "save_output": False
    }

    print("\nCurrent settings:")
    print(f"  Model: {settings['model']}")
    print(f"  Confidence threshold: {settings['confidence']}")
    print(f"  Save output: {settings['save_output']}")

    print("\n1. Change confidence threshold")
    print("2. Toggle save output")
    print("0. Back")

    try:
        choice = int(input("\nSelect option: "))

        if choice == 1:
            new_conf = float(input("Enter confidence (0.01-0.50): "))
            if 0.01 <= new_conf <= 0.50:
                settings['confidence'] = new_conf
                print(f"✅ Confidence set to {new_conf}")
            else:
                print("❌ Invalid confidence value")

        elif choice == 2:
            settings['save_output'] = not settings['save_output']
            print(f"✅ Save output: {settings['save_output']}")

    except:
        pass

    return settings

def main():
    settings = {
        "model": "Downloaded models/best.pt",
        "confidence": 0.15,
        "save_output": False
    }

    while True:
        print_header()
        print_menu()

        try:
            choice = input("Enter your choice: ").strip()

            if choice == "0":
                print("\n👋 Goodbye!")
                sys.exit(0)

            elif choice == "1":
                # Live camera
                print("\n📹 Starting live camera detection...")
                print("   Press 'q' to quit, 's' to save screenshot")
                save_flag = "--save" if settings['save_output'] else ""
                cmd = f"python3 DEMO.py --source 0 --conf {settings['confidence']} {save_flag}"
                run_command(cmd)

            elif choice == "2":
                # Video file
                video = select_video()
                if video:
                    print(f"\n🎬 Processing video: {video.name}")
                    print("   Press 'q' to quit, 's' to save screenshot")
                    save_flag = "--save" if settings['save_output'] else ""
                    cmd = f"python3 DEMO.py --source \"{video}\" --conf {settings['confidence']} {save_flag}"
                    run_command(cmd)

            elif choice == "3":
                # View map
                print("\n🗺️  Creating map visualization...")
                if Path("demo_output").exists():
                    cmd = "python3 MAP_VIEWER.py --open"
                    run_command(cmd)
                else:
                    print("\n❌ No detection data found!")
                    print("   Run a detection session first (option 1 or 2)")

            elif choice == "4":
                # Quick test
                print("\n🧪 Running 10-second test...")
                videos = get_video_files()
                if videos:
                    video = videos[0]
                    print(f"   Using: {video.name}")
                    # Just run for a bit - user can press 'q' to stop
                    cmd = f"python3 DEMO.py --source \"{video}\" --conf {settings['confidence']}"
                    run_command(cmd)
                else:
                    print("   Using webcam")
                    cmd = f"python3 DEMO.py --source 0 --conf {settings['confidence']}"
                    run_command(cmd)

            elif choice == "5":
                # Settings
                settings = show_settings()

            else:
                print("\n❌ Invalid choice!")

            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Check if required files exist
    if not Path("DEMO.py").exists():
        print("❌ Error: DEMO.py not found!")
        sys.exit(1)

    if not Path("Downloaded models/best.pt").exists():
        print("❌ Error: Model file not found!")
        print("   Expected: Downloaded models/best.pt")
        sys.exit(1)

    main()

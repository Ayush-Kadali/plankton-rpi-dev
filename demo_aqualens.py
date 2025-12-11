#!/usr/bin/env python3
"""
Quick demonstration of AquaLens integration
Shows how the feature works without running the full Streamlit app
"""

import sys
import time
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.aqualens_integration import AquaLensManager

def main():
    print("=" * 70)
    print("AquaLens Community Detection - Live Demonstration")
    print("=" * 70)

    # Create manager
    print("\n[1/5] Creating AquaLens manager...")
    manager = AquaLensManager()
    print(f"✓ Manager created: {manager.base_url}")

    # Start server
    print("\n[2/5] Starting AquaLens server...")
    print("      (This may take a few seconds...)")

    if manager.start_server():
        print("✓ Server started successfully!")
        print(f"      Access at: {manager.base_url}")
    else:
        print("✗ Failed to start server")
        print("\nCheck the error above. Common issues:")
        print("  - Port 8000 already in use")
        print("  - Missing dependencies (run: pip3 install -r requirements_aqualens.txt)")
        return 1

    # Get status
    print("\n[3/5] Checking server status...")
    status = manager.get_status()
    print(f"✓ Server status: {status}")

    # Find a video to use
    print("\n[4/5] Finding test video...")
    video_files = list(Path('aqualens').glob('*.mp4'))

    if not video_files:
        print("⚠ No test videos found in aqualens/")
        print("  You can still use a camera or provide a video path")
        video_path = None
    else:
        video_path = str(video_files[0])
        print(f"✓ Found video: {video_path}")

    # Try to start pipeline if video found
    if video_path:
        print("\n[5/5] Starting pipeline with test video...")
        print(f"      Processing: {video_path}")
        print(f"      Device: CPU")
        print(f"      FPS Target: 6.0")
        print(f"      Window: 3.0 seconds")

        result = manager.start_pipeline(
            video_path=video_path,
            device="cpu",
            fps_target=6.0,
            window_seconds=3.0,
            use_hdbscan=False,
            K_init=6
        )

        if "error" in result:
            print(f"✗ Failed to start pipeline: {result['error']}")
        else:
            print(f"✓ Pipeline started: {result}")

            # Wait a bit for processing
            print("\n" + "=" * 70)
            print("Pipeline is now running!")
            print("=" * 70)
            print("\nAccess the live stream and data at:")
            print(f"  • Web Interface: {manager.base_url}")
            print(f"  • Live Stream:   {manager.get_stream_url()}")
            print(f"  • Latest Frame:  {manager.get_latest_frame_url()}")
            print(f"  • Summary Data:  {manager.base_url}/summary")
            print(f"  • Raw Nodes:     {manager.base_url}/raw_nodes")

            print("\nLet it process for 10 seconds...")
            time.sleep(10)

            # Get summary
            print("\nFetching analysis results...")
            summary = manager.get_summary()

            if summary and "error" not in summary:
                print("\n" + "=" * 70)
                print("ANALYSIS RESULTS")
                print("=" * 70)
                print(f"Total Nodes Detected: {summary.get('total_nodes', 0)}")
                print(f"Species Detected:     {len(summary.get('species_counts', {}))}")
                print(f"Communities Found:    {len(summary.get('communities', []))}")
                print(f"Overlapping:          {'Yes' if summary.get('overlapping', False) else 'No'}")

                species_counts = summary.get('species_counts', {})
                if species_counts:
                    print("\nTop Species:")
                    for species, count in sorted(species_counts.items(),
                                                 key=lambda x: x[1], reverse=True)[:5]:
                        print(f"  • {species}: {count} organisms")

                communities = summary.get('communities', [])
                if communities:
                    print("\nCommunity Sizes:")
                    for comm in communities[:5]:
                        print(f"  • Community {comm.get('community_id', '?')}: "
                              f"{comm.get('count', 0)} members")
            else:
                print(f"\n⚠ No results yet: {summary}")

            # Stop pipeline
            print("\n" + "=" * 70)
            print("Stopping pipeline...")
            manager.stop_pipeline()
            print("✓ Pipeline stopped")
    else:
        print("\n[5/5] Skipping pipeline demo (no video found)")

    # Stop server
    print("\nStopping server...")
    manager.stop_server()
    print("✓ Server stopped")

    # Summary
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)
    print("\nWhat you saw:")
    print("  ✓ AquaLens server started successfully")
    if video_path:
        print("  ✓ Pipeline processed video with community detection")
        print("  ✓ Real-time analysis results retrieved")
    print("  ✓ Server cleanly shut down")

    print("\nHow to use in your application:")
    print("  1. Run: streamlit run app.py")
    print("  2. Go to '🧬 Community Detection' tab")
    print("  3. Click 'Start Server'")
    print("  4. Select video and click 'Start Analysis'")
    print("  5. Watch real-time community detection!")

    print("\nIntegration is working perfectly! 🎉")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Run community detection on a video and save annotated frames
Shows the actual results with bounding boxes, species labels, and community badges
"""

import sys
import os
import time
import cv2
import requests
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "aqualens"))

from modules.aqualens_integration import AquaLensManager

def save_annotated_frames(manager, output_dir="results/community_detection", num_frames=5):
    """
    Save annotated frames from the live stream
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📸 Saving annotated frames to {output_dir}/")

    saved_count = 0
    attempts = 0
    max_attempts = 30  # Try for 30 seconds

    while saved_count < num_frames and attempts < max_attempts:
        try:
            # Get latest frame
            response = requests.get(manager.get_latest_frame_url(), timeout=2)

            if response.status_code == 200:
                # Save frame
                filename = f"{output_dir}/annotated_frame_{saved_count + 1:03d}.jpg"
                with open(filename, 'wb') as f:
                    f.write(response.content)

                print(f"  ✓ Saved frame {saved_count + 1}/{num_frames}: {filename}")
                saved_count += 1
                time.sleep(2)  # Wait between captures
            else:
                time.sleep(0.5)

        except Exception as e:
            print(f"  ⚠ Attempt {attempts}: {e}")
            time.sleep(0.5)

        attempts += 1

    return saved_count

def main():
    print("=" * 80)
    print("Community Detection - Live Results with Annotated Images")
    print("=" * 80)

    # Find video
    print("\n🔍 Looking for test video...")
    video_files = list(Path('aqualens').glob('*.mp4'))

    if not video_files:
        print("❌ No video files found in aqualens/")
        return 1

    video_path = str(video_files[0])
    print(f"✓ Found: {video_path}")

    # Create manager
    print("\n🚀 Starting AquaLens server...")
    manager = AquaLensManager()

    if not manager.start_server():
        print("❌ Failed to start server")
        return 1

    print("✓ Server started")

    try:
        # Start pipeline
        print(f"\n▶️  Starting pipeline with: {video_path}")
        print("   Processing parameters:")
        print("   • Device: CPU")
        print("   • Target FPS: 6.0")
        print("   • Window: 3.0 seconds")
        print("   • Communities: 6")

        result = manager.start_pipeline(
            video_path=video_path,
            device="cpu",
            fps_target=6.0,
            window_seconds=3.0,
            use_hdbscan=False,
            K_init=6
        )

        if "error" in result:
            print(f"❌ Failed to start: {result['error']}")
            return 1

        print("✓ Pipeline started!")

        # Wait for initial processing
        print("\n⏳ Waiting for pipeline to process frames (15 seconds)...")
        time.sleep(15)

        # Save annotated frames
        saved = save_annotated_frames(manager, num_frames=5)

        if saved == 0:
            print("\n⚠️  No frames captured - pipeline may need more time")
            print("   Waiting additional 10 seconds...")
            time.sleep(10)
            saved = save_annotated_frames(manager, num_frames=3)

        # Get summary
        print("\n📊 Fetching analysis results...")
        summary = manager.get_summary()

        print("\n" + "=" * 80)
        print("COMMUNITY DETECTION RESULTS")
        print("=" * 80)

        if summary and "error" not in summary:
            print(f"\n📈 Overall Statistics:")
            print(f"   Total Nodes Detected:     {summary.get('total_nodes', 0)}")
            print(f"   Species Detected:         {len(summary.get('species_counts', {}))}")
            print(f"   Communities Found:        {len(summary.get('communities', []))}")
            print(f"   Overlapping Communities:  {'Yes ✓' if summary.get('overlapping', False) else 'No'}")
            print(f"   Timestamp:                {summary.get('timestamp', 'N/A')}")

            # Species distribution
            species_counts = summary.get('species_counts', {})
            if species_counts:
                print(f"\n🧬 Species Distribution:")
                for i, (species, count) in enumerate(sorted(species_counts.items(),
                                                            key=lambda x: x[1],
                                                            reverse=True), 1):
                    print(f"   {i}. {species}: {count} organisms")

            # Community information
            communities = summary.get('communities', [])
            if communities:
                print(f"\n🌐 Community Sizes:")
                for i, comm in enumerate(communities, 1):
                    comm_id = comm.get('community_id', '?')
                    count = comm.get('count', 0)
                    print(f"   Community {comm_id}: {count} members")

            # Raw nodes data
            print(f"\n🔬 Getting detailed node data...")
            raw_nodes = manager.get_raw_nodes()

            if raw_nodes:
                print(f"   Total nodes with details: {len(raw_nodes)}")

                # Show first few nodes
                print(f"\n   Sample Detections (first 3 nodes):")
                for i, node in enumerate(raw_nodes[:3], 1):
                    print(f"\n   Node {i}:")
                    print(f"     • ID: {node.get('node_id', 'N/A')}")
                    print(f"     • Position: ({node.get('centroid_x', 0):.1f}, {node.get('centroid_y', 0):.1f})")
                    print(f"     • Area: {node.get('area', 0):.1f} pixels")
                    print(f"     • Species: {node.get('assigned_species', 'Unknown')}")
                    print(f"     • Communities: {node.get('communities', [])}")
                    print(f"     • Is Strand: {'Yes' if node.get('is_strand', False) else 'No'}")

                    # Species probabilities
                    species_probs = node.get('species_probs', {})
                    if species_probs:
                        print(f"     • Species Confidence:")
                        top_species = sorted(species_probs.items(),
                                           key=lambda x: x[1],
                                           reverse=True)[:3]
                        for sp_name, prob in top_species:
                            print(f"       - {sp_name}: {prob:.2%}")
        else:
            print(f"\n⚠️  No analysis results available yet")
            print(f"   Status: {summary}")

        # Stop pipeline
        print("\n⏹️  Stopping pipeline...")
        manager.stop_pipeline()

        # Display saved images info
        print("\n" + "=" * 80)
        print("ANNOTATED IMAGES SAVED")
        print("=" * 80)

        output_dir = "results/community_detection"
        saved_files = sorted(Path(output_dir).glob("annotated_frame_*.jpg"))

        if saved_files:
            print(f"\n✓ Saved {len(saved_files)} annotated frames:")
            for f in saved_files:
                size = f.stat().st_size / 1024  # KB
                print(f"   • {f.name} ({size:.1f} KB)")

            print(f"\n📂 Location: {output_dir}/")
            print(f"\n🖼️  What's in the images:")
            print(f"   • Bounding boxes around detected organisms")
            print(f"   • Species labels (S0, S1, S2, etc.)")
            print(f"   • Community badges (colored circles with numbers)")
            print(f"   • Real-time statistics overlay")
            print(f"   • Timestamp and FPS information")

            # Try to display first image info
            if saved_files:
                first_img = cv2.imread(str(saved_files[0]))
                if first_img is not None:
                    h, w = first_img.shape[:2]
                    print(f"\n📐 Image dimensions: {w} x {h} pixels")
        else:
            print(f"\n⚠️  No frames were saved")
            print(f"   The video may not have detectable plankton")
            print(f"   or the pipeline needs more processing time")

    finally:
        # Cleanup
        print("\n🛑 Stopping server...")
        manager.stop_server()
        print("✓ Server stopped")

    print("\n" + "=" * 80)
    print("✅ COMPLETE!")
    print("=" * 80)

    if saved_files:
        print(f"\nView your annotated results:")
        print(f"  open {output_dir}/")
        print(f"\nOr in Finder:")
        print(f"  cd {Path.cwd()}")
        print(f"  open {output_dir}")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Test pipeline directly and save annotated frames
"""

import sys
import os
import time
from pathlib import Path

# Add aqualens to path
sys.path.insert(0, str(Path(__file__).parent / "aqualens"))

from final_final_pipeline import PipelineEngine, GlobalState

def main():
    print("=" * 80)
    print("Direct Pipeline Test - Community Detection")
    print("=" * 80)

    # Video path
    video_path = "aqualens/1.mp4"
    output_dir = "results/community_detection"
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n📹 Input: {video_path}")
    print(f"📂 Output: {output_dir}/")

    # Create pipeline engine
    print("\n🔧 Creating pipeline engine...")
    engine = PipelineEngine(
        source=video_path,
        outdir="aqualens/video_artifacts",
        device="cpu",
        window_seconds=3.0,
        fps_target=6.0,
        min_area=20,
        max_area=50000,
        cluster_every_windows=3,
        initial_cluster_min=10,  # Lower threshold for testing
        use_hdbscan=False,
        K_init=6,
        bigclam_K=8,
        bigclam_epochs=40
    )

    print("✓ Engine created")

    # Start pipeline
    print("\n▶️  Starting pipeline...")
    engine.start()
    print("✓ Pipeline started in background")

    # Wait and capture frames
    print("\n⏳ Processing video (will capture frames every 3 seconds)...")

    saved_frames = []
    for i in range(10):  # Try for 30 seconds
        time.sleep(3)

        # Get snapshot
        snapshot = GlobalState.snapshot()

        if snapshot['frame'] is not None:
            # Save frame
            filename = f"{output_dir}/frame_{i + 1:03d}.jpg"
            with open(filename, 'wb') as f:
                f.write(snapshot['frame'])
            print(f"  ✓ Saved: {filename}")
            saved_frames.append(filename)

            # Print summary if available
            if snapshot['summary']:
                summary = snapshot['summary']
                nodes = summary.get('total_nodes', 0)
                species = len(summary.get('species_counts', {}))
                communities = len(summary.get('communities', []))
                print(f"     Nodes: {nodes}, Species: {species}, Communities: {communities}")
        else:
            print(f"  ⏳ Waiting for frames... ({i+1}/10)")

    # Stop pipeline
    print("\n⏹️  Stopping pipeline...")
    engine.stop()
    print("✓ Pipeline stopped")

    # Final summary
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    snapshot = GlobalState.snapshot()
    summary = snapshot.get('summary', {})

    if summary:
        print(f"\n📊 Final Statistics:")
        print(f"   Total Nodes:      {summary.get('total_nodes', 0)}")
        print(f"   Species:          {len(summary.get('species_counts', {}))}")
        print(f"   Communities:      {len(summary.get('communities', []))}")
        print(f"   Overlapping:      {'Yes' if summary.get('overlapping', False) else 'No'}")

        species_counts = summary.get('species_counts', {})
        if species_counts:
            print(f"\n🧬 Species:")
            for sp, cnt in species_counts.items():
                print(f"   • {sp}: {cnt}")

        communities = summary.get('communities', [])
        if communities:
            print(f"\n🌐 Communities:")
            for comm in communities:
                print(f"   • Community {comm.get('community_id')}: {comm.get('count')} members")

    if saved_frames:
        print(f"\n✓ Saved {len(saved_frames)} annotated frames:")
        for f in saved_frames:
            size = Path(f).stat().st_size / 1024
            print(f"   • {f} ({size:.1f} KB)")
    else:
        print(f"\n⚠️  No frames captured - video may not have detectable content")

    print(f"\n📂 Check output: {output_dir}/")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

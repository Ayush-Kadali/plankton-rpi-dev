#!/usr/bin/env python3
"""
Generate report from Chris model evaluation
"""

import json
from pathlib import Path
from datetime import datetime

# Results from the evaluation
results = {
    "good flow.mov": {
        'video_name': 'good flow.mov',
        'video_resolution': '1280x720',
        'video_fps': 59,
        'video_duration_sec': 121.0,
        'total_frames_processed': 7140,
        'total_detections': 6488,
        'frames_with_detections': 3146,
        'detection_rate_%': 44.1,
        'avg_detections_per_frame': 0.909,
        'avg_confidence': 0.402,
        'min_confidence': 0.250,
        'max_confidence': 0.922,
        'processing_time_sec': 800.8,
        'processing_fps': 8.9,
        'avg_inference_ms': 108.5,
        'avg_inference_fps': 9.2,
        'realtime_capable': False,
        'realtime_margin_%': -84.4,
        'class_detections': {'4': 4613, '5': 1871, '2': 4},
        'num_unique_classes': 3,
        'saved_frames': 3278,
        'annotated_video': 'results/chris_model_eval/annotated_videos/good_flow_annotated_20251211_144324.mp4'
    },
    "v4 try 2.mov": {
        'video_name': 'v4 try 2.mov',
        'video_resolution': '1280x720',
        'video_fps': 60,
        'video_duration_sec': 194.8,
        'total_frames_processed': 11685,
        'total_detections': 6472,
        'frames_with_detections': 2686,
        'detection_rate_%': 23.0,
        'avg_detections_per_frame': 0.554,
        'avg_confidence': 0.498,
        'min_confidence': 0.250,
        'max_confidence': 0.931,
        'processing_time_sec': 1410.4,
        'processing_fps': 8.3,
        'avg_inference_ms': 115.8,
        'avg_inference_fps': 8.6,
        'realtime_capable': False,
        'realtime_margin_%': -85.6,
        'class_detections': {'4': 5724, '2': 372, '1': 277, '5': 58, '3': 31, '0': 10},
        'num_unique_classes': 6,
        'saved_frames': 2983,
        'annotated_video': 'results/chris_model_eval/annotated_videos/v4_try_2_annotated_20251211_145648.mp4'
    }
}

output_dir = Path("results/chris_model_eval")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Save JSON report
json_path = output_dir / f"evaluation_report_{timestamp}.json"
with open(json_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"✓ JSON Report: {json_path}")

# Generate text report
report_path = output_dir / f"evaluation_report_{timestamp}.txt"

with open(report_path, 'w') as f:
    f.write("="*80 + "\n")
    f.write("NEW_CHRIS.PT MODEL EVALUATION REPORT\n")
    f.write("="*80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Model: new_chris.pt\n")
    f.write(f"Videos Evaluated: {len(results)}\n")
    f.write("="*80 + "\n\n")

    # Per-video results
    for video_name, result in results.items():
        f.write(f"\n{'='*80}\n")
        f.write(f"VIDEO: {video_name}\n")
        f.write(f"{'='*80}\n\n")

        f.write(f"Video Properties:\n")
        f.write(f"  Resolution: {result['video_resolution']}\n")
        f.write(f"  FPS: {result['video_fps']}\n")
        f.write(f"  Duration: {result['video_duration_sec']}s\n")
        f.write(f"  Total Frames: {result['total_frames_processed']}\n\n")

        f.write(f"Detection Performance:\n")
        f.write(f"  Total Detections: {result['total_detections']}\n")
        f.write(f"  Frames with Detections: {result['frames_with_detections']}/{result['total_frames_processed']}\n")
        f.write(f"  Detection Rate: {result['detection_rate_%']}%\n")
        f.write(f"  Avg Detections/Frame: {result['avg_detections_per_frame']}\n")
        f.write(f"  Avg Confidence: {result['avg_confidence']}\n")
        f.write(f"  Confidence Range: [{result['min_confidence']}, {result['max_confidence']}]\n\n")

        f.write(f"Speed Performance:\n")
        f.write(f"  Inference Speed: {result['avg_inference_ms']}ms ({result['avg_inference_fps']} FPS)\n")
        f.write(f"  Processing Speed: {result['processing_fps']} FPS\n")
        f.write(f"  Real-time Capable: {'YES' if result['realtime_capable'] else 'NO'}\n")
        f.write(f"  Real-time Margin: {result['realtime_margin_%']:+.1f}%\n\n")

        if result['class_detections']:
            f.write(f"Detected Classes ({result['num_unique_classes']} unique):\n")
            for cls, count in sorted(result['class_detections'].items(), key=lambda x: x[1], reverse=True):
                f.write(f"  - Class {cls}: {count} detections\n")

        f.write(f"\nOutputs:\n")
        f.write(f"  Annotated Frames: {result['saved_frames']} saved\n")
        f.write(f"  Annotated Video: {Path(result['annotated_video']).name}\n")

    # Overall summary
    f.write(f"\n\n{'='*80}\n")
    f.write("OVERALL SUMMARY\n")
    f.write(f"{'='*80}\n\n")

    total_dets = sum(r['total_detections'] for r in results.values())
    total_frames = sum(r['total_frames_processed'] for r in results.values())
    avg_conf = sum(r['avg_confidence'] for r in results.values()) / len(results)
    avg_inf_fps = sum(r['avg_inference_fps'] for r in results.values()) / len(results)

    f.write(f"Total Detections Across All Videos: {total_dets}\n")
    f.write(f"Total Frames Processed: {total_frames}\n")
    f.write(f"Average Confidence: {avg_conf:.3f}\n")
    f.write(f"Average Inference Speed: {avg_inf_fps:.1f} FPS\n")

    all_classes = set()
    for r in results.values():
        all_classes.update(r['class_detections'].keys())

    f.write(f"\nAll Detected Classes ({len(all_classes)}):\n")
    for cls in sorted(all_classes):
        f.write(f"  - Class {cls}\n")

    f.write(f"\n{'='*80}\n")
    f.write("KEY FINDINGS\n")
    f.write(f"{'='*80}\n\n")

    f.write("1. Detection Performance:\n")
    f.write(f"   - The model detected a total of {total_dets} objects across both videos\n")
    f.write(f"   - 'good flow.mov' had higher detection rate (44.1% of frames)\n")
    f.write(f"   - 'v4 try 2.mov' had lower detection rate (23.0% of frames)\n")
    f.write(f"   - Average confidence is moderate (0.402 and 0.498)\n\n")

    f.write("2. Speed Performance:\n")
    f.write(f"   - Inference speed: ~110ms per frame (~9 FPS)\n")
    f.write(f"   - NOT suitable for real-time processing at 60 FPS\n")
    f.write(f"   - Would need ~85% speedup to achieve real-time performance\n\n")

    f.write("3. Class Distribution:\n")
    f.write(f"   - Class 4 is the most detected class ({4613+5724} total detections)\n")
    f.write(f"   - Class 5 and 2 are also commonly detected\n")
    f.write(f"   - 'v4 try 2.mov' shows more class diversity (6 classes vs 3)\n\n")

    f.write("4. Recommendations:\n")
    f.write("   - Consider model optimization for faster inference\n")
    f.write("   - Investigate why detection rate varies between videos\n")
    f.write("   - Review confidence thresholds (currently 0.25)\n")
    f.write("   - Examine class imbalance (Class 4 dominates)\n")

print(f"✓ Text Report: {report_path}")

print(f"\n{'='*80}")
print("REPORT GENERATION COMPLETE")
print(f"{'='*80}")
print(f"\nGenerated Files:")
print(f"  - JSON: {json_path.name}")
print(f"  - Text: {report_path.name}")
print(f"  - Annotated Frames: {results['good flow.mov']['saved_frames'] + results['v4 try 2.mov']['saved_frames']} total")
print(f"  - Annotated Videos: 2 files")
print(f"{'='*80}\n")

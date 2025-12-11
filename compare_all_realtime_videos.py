#!/usr/bin/env python3
"""
Complete Model Comparison on ALL Real-Time Videos
Quick analysis with metrics - NO video output to save time
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

class QuickModelComparison:
    def __init__(self):
        self.models_dir = Path("Downloaded models")
        self.videos_dir = Path("Real_Time_Vids")
        self.results_dir = Path("results/all_videos_comparison")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Models to test
        self.models = {
            "best.pt": "Custom Best Model",
            "chris_best.pt": "Chris Best Model",
            "yolov5nu.pt": "YOLOv5n-u",
            "yolov8n.pt": "YOLOv8n"
        }

        # Get ALL videos
        self.videos = list(self.videos_dir.glob("*.mov"))

        self.results = []

    def process_video_quick(self, model_path, model_name, video_path):
        """Quick processing - metrics only, no video output"""
        print(f"\n{'='*80}")
        print(f"Testing: {model_name} on {video_path.name}")
        print(f"{'='*80}")

        # Load model
        try:
            model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"Error opening video {video_path}")
            return None

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames ({duration:.1f}s)")

        # Metrics
        frame_count = 0
        detection_count = 0
        total_detections = 0
        total_confidence = 0.0
        inference_times = []
        confidence_scores = []
        class_detections = {}

        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Inference timing
            inf_start = time.time()
            results = model(frame, verbose=False, conf=0.25)
            inf_time = (time.time() - inf_start) * 1000
            inference_times.append(inf_time)

            # Process detections
            frame_dets = 0
            for result in results:
                for box in result.boxes:
                    frame_dets += 1
                    total_detections += 1

                    conf = float(box.conf[0])
                    total_confidence += conf
                    confidence_scores.append(conf)

                    cls = int(box.cls[0])
                    class_name = model.names[cls]

                    if class_name not in class_detections:
                        class_detections[class_name] = 0
                    class_detections[class_name] += 1

            if frame_dets > 0:
                detection_count += 1

            # Progress every 10%
            if frame_count % max(1, total_frames // 10) == 0:
                progress = (frame_count / total_frames) * 100
                avg_fps = frame_count / (time.time() - start_time)
                print(f"Progress: {progress:.0f}% - Avg FPS: {avg_fps:.1f} - Detections: {total_detections}")

        total_time = time.time() - start_time
        cap.release()

        # Calculate metrics
        avg_inf_time = np.mean(inference_times)
        avg_inf_fps = 1000 / avg_inf_time if avg_inf_time > 0 else 0
        processing_fps = frame_count / total_time if total_time > 0 else 0
        avg_confidence = total_confidence / total_detections if total_detections > 0 else 0
        detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0

        result = {
            'model_name': model_name,
            'model_file': model_path.name,
            'video_name': video_path.name,
            'video_resolution': f"{width}x{height}",
            'video_fps': fps,
            'video_duration_sec': round(duration, 1),
            'total_frames': frame_count,
            'total_detections': total_detections,
            'frames_with_detections': detection_count,
            'detection_rate_%': round(detection_rate, 2),
            'avg_detections_per_frame': round(total_detections / frame_count, 3) if frame_count > 0 else 0,
            'avg_confidence': round(avg_confidence, 4),
            'min_confidence': round(min(confidence_scores), 4) if confidence_scores else 0,
            'max_confidence': round(max(confidence_scores), 4) if confidence_scores else 0,
            'processing_time_sec': round(total_time, 1),
            'processing_fps': round(processing_fps, 1),
            'avg_inference_ms': round(avg_inf_time, 2),
            'avg_inference_fps': round(avg_inf_fps, 1),
            'min_inference_ms': round(min(inference_times), 2),
            'max_inference_ms': round(max(inference_times), 2),
            'realtime_capable': avg_inf_fps >= fps,
            'realtime_margin_%': round((avg_inf_fps / fps - 1) * 100, 1) if fps > 0 else 0,
            'class_detections': class_detections,
            'num_unique_classes': len(class_detections)
        }

        # Print summary
        print(f"\n{'='*80}")
        print(f"RESULTS:")
        print(f"  Detections: {total_detections} ({detection_rate:.1f}% of frames)")
        print(f"  Confidence: {avg_confidence:.3f}")
        print(f"  Inference: {avg_inf_time:.1f}ms ({avg_inf_fps:.1f} FPS)")
        print(f"  Processing: {processing_fps:.1f} FPS")
        print(f"  Real-time: {'✓ YES' if result['realtime_capable'] else '✗ NO'} ({result['realtime_margin_%']:+.1f}%)")

        if class_detections:
            print(f"  Classes: {', '.join(sorted(class_detections.keys(), key=lambda x: class_detections[x], reverse=True)[:3])}")

        return result

    def run_all(self):
        """Run all comparisons"""
        total_tests = len(self.models) * len(self.videos)
        current = 0

        print(f"\n{'#'*80}")
        print(f"COMPLETE MODEL COMPARISON - ALL VIDEOS")
        print(f"{'#'*80}")
        print(f"Models: {len(self.models)}")
        print(f"Videos: {len(self.videos)}")
        print(f"Total tests: {total_tests}")
        print(f"Mode: QUICK (no video output)")
        print(f"{'#'*80}\n")

        for model_file, model_name in self.models.items():
            model_path = self.models_dir / model_file

            if not model_path.exists():
                print(f"WARNING: Model not found: {model_path}")
                continue

            for video_path in sorted(self.videos):
                current += 1
                print(f"\n{'#'*80}")
                print(f"TEST {current}/{total_tests}")
                print(f"{'#'*80}")

                result = self.process_video_quick(model_path, model_name, video_path)
                if result:
                    self.results.append(result)

    def generate_report(self):
        """Generate comprehensive report"""
        if not self.results:
            print("No results!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON
        json_path = self.results_dir / f"all_videos_results_{timestamp}.json"
        with open(json_path, 'w') as f:
            # Convert dict values to serializable format
            serializable_results = []
            for r in self.results:
                r_copy = r.copy()
                # Convert numpy bool to python bool
                if 'realtime_capable' in r_copy:
                    r_copy['realtime_capable'] = bool(r_copy['realtime_capable'])
                serializable_results.append(r_copy)
            json.dump(serializable_results, f, indent=2)
        print(f"\n✓ JSON: {json_path}")

        # Create DataFrame
        df = pd.DataFrame(self.results)
        df_simple = df.drop(columns=['class_detections'], errors='ignore')

        # Save CSV
        csv_path = self.results_dir / f"all_videos_results_{timestamp}.csv"
        df_simple.to_csv(csv_path, index=False)
        print(f"✓ CSV: {csv_path}")

        # Generate text report
        report_path = self.results_dir / f"all_videos_report_{timestamp}.txt"

        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("COMPLETE MODEL COMPARISON - ALL REAL-TIME VIDEOS\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Models: {len(self.models)}\n")
            f.write(f"Videos: {len(self.videos)}\n")
            f.write(f"Total Tests: {len(self.results)}\n")
            f.write("="*80 + "\n\n")

            # Overall model performance
            f.write("OVERALL MODEL PERFORMANCE\n")
            f.write("-"*80 + "\n\n")

            model_summary = df.groupby('model_name').agg({
                'total_detections': 'sum',
                'detection_rate_%': 'mean',
                'avg_confidence': 'mean',
                'avg_inference_fps': 'mean',
                'avg_inference_ms': 'mean',
                'realtime_capable': 'sum'
            }).round(2)

            f.write(model_summary.to_string())
            f.write("\n\n")

            # Per-video breakdown
            f.write("="*80 + "\n")
            f.write("PERFORMANCE BY VIDEO\n")
            f.write("="*80 + "\n\n")

            for video in sorted(df['video_name'].unique()):
                f.write(f"\n{video}:\n")
                f.write("-"*80 + "\n")

                video_df = df[df['video_name'] == video].sort_values('total_detections', ascending=False)

                for _, row in video_df.iterrows():
                    f.write(f"\n  {row['model_name']}:\n")
                    f.write(f"    Detections: {row['total_detections']} ({row['detection_rate_%']}%)\n")
                    f.write(f"    Confidence: {row['avg_confidence']:.3f}\n")
                    f.write(f"    Speed: {row['avg_inference_ms']}ms ({row['avg_inference_fps']} FPS)\n")
                    f.write(f"    Real-time: {'YES' if row['realtime_capable'] else 'NO'}\n")

            # Best performers
            f.write("\n\n" + "="*80 + "\n")
            f.write("BEST PERFORMERS\n")
            f.write("="*80 + "\n\n")

            best_detections = df.loc[df['total_detections'].idxmax()]
            fastest = df.loc[df['avg_inference_fps'].idxmax()]
            best_overall = model_summary.loc[model_summary['total_detections'].idxmax()]

            f.write(f"Most Detections (single video):\n")
            f.write(f"  {best_detections['model_name']} on {best_detections['video_name']}\n")
            f.write(f"  {best_detections['total_detections']} detections\n\n")

            f.write(f"Fastest Processing:\n")
            f.write(f"  {fastest['model_name']} on {fastest['video_name']}\n")
            f.write(f"  {fastest['avg_inference_fps']} FPS\n\n")

            f.write(f"Best Overall Model:\n")
            f.write(f"  {best_overall.name}\n")
            f.write(f"  Total Detections: {best_overall['total_detections']:.0f}\n")
            f.write(f"  Avg Detection Rate: {best_overall['detection_rate_%']:.1f}%\n")
            f.write(f"  Avg Inference FPS: {best_overall['avg_inference_fps']:.1f}\n")

        print(f"✓ Report: {report_path}")

        # Print summary to console
        print("\n" + "="*80)
        print("OVERALL MODEL PERFORMANCE SUMMARY")
        print("="*80 + "\n")
        print(model_summary.to_string())

        print("\n" + "="*80)
        print("BEST PERFORMERS")
        print("="*80)
        print(f"\nMost Detections: {best_detections['model_name']} on {best_detections['video_name']}")
        print(f"  ({best_detections['total_detections']} detections)")
        print(f"\nFastest: {fastest['model_name']} ({fastest['avg_inference_fps']} FPS)")
        print(f"\nBest Overall: {best_overall.name}")

def main():
    comparator = QuickModelComparison()
    comparator.run_all()
    comparator.generate_report()

    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    main()

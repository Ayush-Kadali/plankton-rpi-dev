#!/usr/bin/env python3
"""
Focused Model Comparison on Selected Videos
Tests all models on 3 key videos with comprehensive metrics
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
import os
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

class FocusedModelComparison:
    def __init__(self):
        self.models_dir = Path("Downloaded models")
        self.videos_dir = Path("Real_Time_Vids")
        self.results_dir = Path("results/focused_comparison")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Models to test
        self.models = {
            "best.pt": "Custom Best Model",
            "chris_best.pt": "Chris Best Model",
            "yolov5nu.pt": "YOLOv5n-u",
            "yolov8n.pt": "YOLOv8n"
        }

        # Selected videos
        self.selected_videos = [
            "good flow.mov",
            "v4 try 2.mov",
            "trial.mov"
        ]

        self.results = []

    def process_video(self, model_path, model_name, video_path, save_output=True):
        """Process a single video with detailed metrics"""
        print(f"\n{'='*80}")
        print(f"Testing: {model_name} on {video_path.name}")
        print(f"{'='*80}")

        # Load model
        try:
            model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading model {model_path}: {e}")
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
        video_duration = total_frames / fps if fps > 0 else 0

        print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames ({video_duration:.1f}s)")

        # Setup output video
        output_path = None
        out = None
        if save_output:
            output_filename = f"{model_path.stem}_{video_path.stem}.mp4"
            output_path = self.results_dir / output_filename
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        # Metrics
        frame_count = 0
        detection_count = 0
        total_detections = 0
        total_confidence = 0.0
        processing_times = []
        confidence_scores = []
        detections_per_frame = []
        frame_inference_times = []

        # Detection tracking
        class_detections = {}

        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Inference timing
            inference_start = time.time()
            results = model(frame, verbose=False, conf=0.25)
            inference_time = (time.time() - inference_start) * 1000  # ms
            frame_inference_times.append(inference_time)

            # Total frame processing time (including drawing)
            frame_start = time.time()

            # Process results
            frame_detections = 0
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    frame_detections += 1
                    total_detections += 1

                    conf = float(box.conf[0])
                    total_confidence += conf
                    confidence_scores.append(conf)

                    cls = int(box.cls[0])
                    class_name = model.names[cls]

                    # Track class counts
                    if class_name not in class_detections:
                        class_detections[class_name] = 0
                    class_detections[class_name] += 1

                    # Draw on frame
                    if save_output:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        # Color based on class
                        color = (0, 255, 0)  # Green default

                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                        label = f'{class_name} {conf:.2f}'
                        label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)

                        # Draw label background
                        cv2.rectangle(frame, (x1, y1-label_size[1]-10),
                                    (x1+label_size[0], y1), color, -1)
                        cv2.putText(frame, label, (x1, y1-5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

            detections_per_frame.append(frame_detections)

            if frame_detections > 0:
                detection_count += 1

            # Add info overlay
            if save_output and out:
                # Info panel
                info_y = 30
                cv2.rectangle(frame, (0, 0), (width, 120), (0, 0, 0), -1)

                cv2.putText(frame, f"Model: {model_name}", (10, info_y),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                cv2.putText(frame, f"Frame: {frame_count}/{total_frames}", (10, info_y+25),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                cv2.putText(frame, f"Detections: {frame_detections} (Total: {total_detections})",
                          (10, info_y+50),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                cv2.putText(frame, f"Inference: {inference_time:.1f}ms ({1000/inference_time:.1f} FPS)",
                          (10, info_y+75),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                out.write(frame)

            frame_time = (time.time() - frame_start) * 1000
            processing_times.append(frame_time)

            # Progress
            if frame_count % 30 == 0 or frame_count == total_frames:
                progress = (frame_count / total_frames) * 100
                avg_fps_so_far = frame_count / (time.time() - start_time)
                print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames}) - "
                      f"Avg FPS: {avg_fps_so_far:.1f} - Detections: {frame_detections}")

        total_time = time.time() - start_time

        # Release resources
        cap.release()
        if out:
            out.release()

        # Calculate metrics
        avg_processing_fps = frame_count / total_time if total_time > 0 else 0
        avg_inference_time = np.mean(frame_inference_times)
        avg_inference_fps = 1000 / avg_inference_time if avg_inference_time > 0 else 0
        avg_total_time = np.mean(processing_times)
        avg_confidence = total_confidence / total_detections if total_detections > 0 else 0
        detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0
        avg_detections = np.mean(detections_per_frame)
        max_detections = max(detections_per_frame) if detections_per_frame else 0

        result = {
            'model_name': model_name,
            'model_file': model_path.name,
            'video_name': video_path.name,
            'video_stem': video_path.stem,

            # Video properties
            'video_resolution': f"{width}x{height}",
            'video_fps': fps,
            'video_duration_sec': round(video_duration, 2),
            'total_frames': frame_count,

            # Detection metrics
            'total_detections': total_detections,
            'frames_with_detections': detection_count,
            'detection_rate_%': round(detection_rate, 2),
            'avg_detections_per_frame': round(avg_detections, 3),
            'max_detections_per_frame': max_detections,

            # Confidence metrics
            'avg_confidence': round(avg_confidence, 4),
            'min_confidence': round(min(confidence_scores), 4) if confidence_scores else 0,
            'max_confidence': round(max(confidence_scores), 4) if confidence_scores else 0,
            'confidence_std': round(np.std(confidence_scores), 4) if confidence_scores else 0,

            # Performance metrics
            'total_processing_time_sec': round(total_time, 2),
            'avg_processing_fps': round(avg_processing_fps, 2),
            'avg_inference_time_ms': round(avg_inference_time, 2),
            'avg_inference_fps': round(avg_inference_fps, 2),
            'min_inference_time_ms': round(min(frame_inference_times), 2),
            'max_inference_time_ms': round(max(frame_inference_times), 2),
            'inference_std_ms': round(np.std(frame_inference_times), 2),

            # Class breakdown
            'class_detections': class_detections,
            'num_unique_classes': len(class_detections),

            # Output
            'output_video': str(output_path) if output_path else None,

            # Real-time capability
            'realtime_capable': avg_inference_fps >= fps,
            'realtime_margin_%': round((avg_inference_fps / fps - 1) * 100, 1) if fps > 0 else 0
        }

        # Print summary
        print(f"\n{'='*80}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*80}")
        print(f"Total Detections: {total_detections}")
        print(f"Detection Rate: {detection_rate:.1f}%")
        print(f"Avg Detections/Frame: {avg_detections:.2f}")
        print(f"Avg Confidence: {avg_confidence:.3f}")
        print(f"\nPerformance:")
        print(f"  Total Time: {total_time:.1f}s")
        print(f"  Avg Inference: {avg_inference_time:.1f}ms ({avg_inference_fps:.1f} FPS)")
        print(f"  Avg Total Processing: {avg_total_time:.1f}ms ({avg_processing_fps:.1f} FPS)")
        print(f"  Real-time Capable: {'✓ YES' if result['realtime_capable'] else '✗ NO'}")
        if fps > 0:
            print(f"  Real-time Margin: {result['realtime_margin_%']:+.1f}%")

        if class_detections:
            print(f"\nClass Breakdown:")
            for class_name, count in sorted(class_detections.items(), key=lambda x: x[1], reverse=True):
                print(f"  {class_name}: {count}")

        if output_path:
            print(f"\nOutput: {output_path}")

        return result

    def run_comparison(self, save_videos=True):
        """Run comparison on selected videos"""
        total_tests = len(self.models) * len(self.selected_videos)
        current_test = 0

        print(f"\n{'#'*80}")
        print(f"FOCUSED MODEL COMPARISON")
        print(f"{'#'*80}")
        print(f"Models: {len(self.models)}")
        print(f"Videos: {len(self.selected_videos)}")
        print(f"Total tests: {total_tests}")
        print(f"Save videos: {save_videos}")
        print(f"{'#'*80}\n")

        for model_file, model_name in self.models.items():
            model_path = self.models_dir / model_file

            if not model_path.exists():
                print(f"WARNING: Model not found: {model_path}")
                continue

            for video_name in self.selected_videos:
                video_path = self.videos_dir / video_name

                if not video_path.exists():
                    print(f"WARNING: Video not found: {video_path}")
                    continue

                current_test += 1
                print(f"\n\n{'#'*80}")
                print(f"TEST {current_test}/{total_tests}")
                print(f"{'#'*80}")

                result = self.process_video(model_path, model_name, video_path, save_videos)

                if result:
                    self.results.append(result)

    def generate_report(self):
        """Generate comprehensive report"""
        if not self.results:
            print("No results to report!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON
        json_path = self.results_dir / f"comparison_results_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nJSON saved: {json_path}")

        # Save CSV
        df = pd.DataFrame(self.results)
        # Remove complex nested data for CSV
        df_simple = df.drop(columns=['class_detections'], errors='ignore')
        csv_path = self.results_dir / f"comparison_results_{timestamp}.csv"
        df_simple.to_csv(csv_path, index=False)
        print(f"CSV saved: {csv_path}")

        # Generate detailed report
        report_path = self.results_dir / f"comparison_report_{timestamp}.txt"

        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("FOCUSED MODEL COMPARISON REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tests: {len(self.results)}\n")
            f.write("="*80 + "\n\n")

            # Overall comparison table
            f.write("OVERALL PERFORMANCE COMPARISON\n")
            f.write("-"*80 + "\n\n")

            # Group by model
            model_stats = df.groupby('model_name').agg({
                'total_detections': 'sum',
                'detection_rate_%': 'mean',
                'avg_confidence': 'mean',
                'avg_inference_fps': 'mean',
                'avg_inference_time_ms': 'mean',
                'realtime_capable': 'sum'
            }).round(2)

            f.write(model_stats.to_string())
            f.write("\n\n")

            # Per-video breakdown
            f.write("="*80 + "\n")
            f.write("PERFORMANCE BY VIDEO\n")
            f.write("="*80 + "\n\n")

            for video in df['video_name'].unique():
                f.write(f"\n{video}:\n")
                f.write("-"*80 + "\n")

                video_df = df[df['video_name'] == video]

                for _, row in video_df.iterrows():
                    f.write(f"\n{row['model_name']}:\n")
                    f.write(f"  Detections: {row['total_detections']}\n")
                    f.write(f"  Detection Rate: {row['detection_rate_%']}%\n")
                    f.write(f"  Avg Confidence: {row['avg_confidence']:.3f}\n")
                    f.write(f"  Inference Speed: {row['avg_inference_time_ms']}ms ({row['avg_inference_fps']} FPS)\n")
                    f.write(f"  Real-time: {'YES' if row['realtime_capable'] else 'NO'}\n")

                    if row['class_detections']:
                        f.write(f"  Classes detected: {', '.join(row['class_detections'].keys())}\n")

            # Recommendations
            f.write("\n\n" + "="*80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("="*80 + "\n\n")

            best_overall = model_stats.loc[model_stats['total_detections'].idxmax()]
            fastest = model_stats.loc[model_stats['avg_inference_fps'].idxmax()]

            f.write(f"Most Detections: {best_overall.name}\n")
            f.write(f"  Total: {best_overall['total_detections']:.0f}\n")
            f.write(f"  Avg Detection Rate: {best_overall['detection_rate_%']:.1f}%\n\n")

            f.write(f"Fastest Processing: {fastest.name}\n")
            f.write(f"  Inference FPS: {fastest['avg_inference_fps']:.1f}\n")
            f.write(f"  Inference Time: {fastest['avg_inference_time_ms']:.1f}ms\n\n")

            # Real-time capable models
            realtime_models = model_stats[model_stats['realtime_capable'] == len(self.selected_videos)]
            if not realtime_models.empty:
                f.write("Real-time Capable Models (all videos):\n")
                for model in realtime_models.index:
                    f.write(f"  - {model}\n")

        print(f"Report saved: {report_path}")

        # Console summary
        print("\n" + "="*80)
        print("COMPARISON SUMMARY")
        print("="*80 + "\n")
        print(model_stats.to_string())

def main():
    import sys

    comparator = FocusedModelComparison()

    # Check if save videos argument provided
    save_videos = True
    if len(sys.argv) > 1:
        save_videos = sys.argv[1].lower() in ['y', 'yes', 'true', '1']

    print(f"\nSave output videos: {save_videos}")

    comparator.run_comparison(save_videos=save_videos)
    comparator.generate_report()

    print("\n" + "="*80)
    print("COMPARISON COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    main()

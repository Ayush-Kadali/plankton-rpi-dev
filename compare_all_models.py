#!/usr/bin/env python3
"""
Comprehensive Model Comparison Script
Runs all available models on all real-time videos and generates performance metrics
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

class ModelVideoComparison:
    def __init__(self):
        self.models_dir = Path("Downloaded models")
        self.videos_dir = Path("Real_Time_Vids")
        self.results_dir = Path("results/model_comparison")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Define models to test
        self.models = {
            "best.pt": "Custom Best Model",
            "chris_best.pt": "Chris Best Model",
            "yolov5nu.pt": "YOLOv5n-u",
            "yolov8n.pt": "YOLOv8n"
        }

        # Get all videos
        self.videos = list(self.videos_dir.glob("*.mov"))

        # Results storage
        self.results = []

    def process_video(self, model_path, model_name, video_path, save_output=True):
        """Process a single video with a single model"""
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

        # Setup output video if requested
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

        print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames")

        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            frame_start = time.time()

            # Run detection
            results = model(frame, verbose=False, conf=0.25)

            frame_time = time.time() - frame_start
            processing_times.append(frame_time)

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

                    # Draw on frame if saving
                    if save_output:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cls = int(box.cls[0])
                        label = f'{model.names[cls]} {conf:.2f}'

                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, label, (x1, y1-10),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if frame_detections > 0:
                detection_count += 1

            # Add info overlay if saving
            if save_output and out:
                info_text = f"Model: {model_name} | Frame: {frame_count}/{total_frames} | Detections: {frame_detections}"
                cv2.putText(frame, info_text, (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                out.write(frame)

            # Progress update
            if frame_count % 30 == 0:
                progress = (frame_count / total_frames) * 100
                print(f"Progress: {progress:.1f}% ({frame_count}/{total_frames}) - "
                      f"Detections this frame: {frame_detections}")

        total_time = time.time() - start_time

        # Release resources
        cap.release()
        if out:
            out.release()

        # Calculate metrics
        avg_fps = frame_count / total_time if total_time > 0 else 0
        avg_frame_time = np.mean(processing_times) if processing_times else 0
        std_frame_time = np.std(processing_times) if processing_times else 0
        avg_confidence = total_confidence / total_detections if total_detections > 0 else 0
        detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0

        result = {
            'model_name': model_name,
            'model_file': model_path.name,
            'video_name': video_path.name,
            'video_stem': video_path.stem,
            'total_frames': frame_count,
            'frames_with_detections': detection_count,
            'total_detections': total_detections,
            'detection_rate_%': round(detection_rate, 2),
            'avg_detections_per_frame': round(total_detections / frame_count, 2) if frame_count > 0 else 0,
            'avg_confidence': round(avg_confidence, 4),
            'min_confidence': round(min(confidence_scores), 4) if confidence_scores else 0,
            'max_confidence': round(max(confidence_scores), 4) if confidence_scores else 0,
            'processing_time_sec': round(total_time, 2),
            'avg_fps': round(avg_fps, 2),
            'avg_frame_time_ms': round(avg_frame_time * 1000, 2),
            'std_frame_time_ms': round(std_frame_time * 1000, 2),
            'output_video': str(output_path) if output_path else None
        }

        print(f"\nResults:")
        print(f"  Total Detections: {total_detections}")
        print(f"  Detection Rate: {detection_rate:.1f}%")
        print(f"  Avg Confidence: {avg_confidence:.3f}")
        print(f"  Processing Time: {total_time:.1f}s")
        print(f"  Avg FPS: {avg_fps:.1f}")
        print(f"  Avg Frame Time: {avg_frame_time*1000:.1f}ms")
        if output_path:
            print(f"  Output saved to: {output_path}")

        return result

    def run_all_comparisons(self, save_videos=True):
        """Run all model-video combinations"""
        total_tests = len(self.models) * len(self.videos)
        current_test = 0

        print(f"\n{'='*80}")
        print(f"STARTING COMPREHENSIVE MODEL COMPARISON")
        print(f"{'='*80}")
        print(f"Models: {len(self.models)}")
        print(f"Videos: {len(self.videos)}")
        print(f"Total tests: {total_tests}")
        print(f"Save videos: {save_videos}")
        print(f"Results directory: {self.results_dir}")
        print(f"{'='*80}\n")

        for model_file, model_name in self.models.items():
            model_path = self.models_dir / model_file

            if not model_path.exists():
                print(f"WARNING: Model not found: {model_path}")
                continue

            for video_path in self.videos:
                current_test += 1
                print(f"\n\n{'#'*80}")
                print(f"TEST {current_test}/{total_tests}")
                print(f"{'#'*80}")

                result = self.process_video(model_path, model_name, video_path, save_videos)

                if result:
                    self.results.append(result)

        return self.results

    def generate_report(self):
        """Generate comprehensive comparison report"""
        if not self.results:
            print("No results to report!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed JSON
        json_path = self.results_dir / f"comparison_results_{timestamp}.json"
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed results saved to: {json_path}")

        # Create DataFrame for analysis
        df = pd.DataFrame(self.results)

        # Save CSV
        csv_path = self.results_dir / f"comparison_results_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        print(f"CSV results saved to: {csv_path}")

        # Generate summary report
        report_path = self.results_dir / f"comparison_report_{timestamp}.txt"

        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PLANKTON DETECTION MODEL COMPARISON REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tests: {len(self.results)}\n")
            f.write(f"Models Tested: {len(self.models)}\n")
            f.write(f"Videos Tested: {len(self.videos)}\n")
            f.write("="*80 + "\n\n")

            # Overall model performance
            f.write("OVERALL MODEL PERFORMANCE (averaged across all videos)\n")
            f.write("-"*80 + "\n")

            model_summary = df.groupby('model_name').agg({
                'total_detections': 'sum',
                'detection_rate_%': 'mean',
                'avg_confidence': 'mean',
                'avg_fps': 'mean',
                'avg_frame_time_ms': 'mean'
            }).round(2)

            f.write(model_summary.to_string())
            f.write("\n\n")

            # Performance by video
            f.write("PERFORMANCE BY VIDEO\n")
            f.write("-"*80 + "\n")

            for video in df['video_name'].unique():
                f.write(f"\n{video}:\n")
                video_data = df[df['video_name'] == video][
                    ['model_name', 'total_detections', 'detection_rate_%',
                     'avg_confidence', 'avg_fps']
                ].sort_values('total_detections', ascending=False)
                f.write(video_data.to_string(index=False))
                f.write("\n")

            # Best performers
            f.write("\n" + "="*80 + "\n")
            f.write("BEST PERFORMERS\n")
            f.write("="*80 + "\n\n")

            best_detections = df.loc[df['total_detections'].idxmax()]
            f.write(f"Most Detections:\n")
            f.write(f"  Model: {best_detections['model_name']}\n")
            f.write(f"  Video: {best_detections['video_name']}\n")
            f.write(f"  Detections: {best_detections['total_detections']}\n\n")

            best_confidence = df.loc[df['avg_confidence'].idxmax()]
            f.write(f"Highest Confidence:\n")
            f.write(f"  Model: {best_confidence['model_name']}\n")
            f.write(f"  Video: {best_confidence['video_name']}\n")
            f.write(f"  Confidence: {best_confidence['avg_confidence']:.3f}\n\n")

            best_fps = df.loc[df['avg_fps'].idxmax()]
            f.write(f"Fastest Processing:\n")
            f.write(f"  Model: {best_fps['model_name']}\n")
            f.write(f"  Video: {best_fps['video_name']}\n")
            f.write(f"  FPS: {best_fps['avg_fps']:.1f}\n\n")

            # Recommendations
            f.write("="*80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("="*80 + "\n\n")

            overall_best = model_summary.loc[
                model_summary['total_detections'].idxmax()
            ]
            f.write(f"Best Overall Model: {overall_best.name}\n")
            f.write(f"  Total Detections: {overall_best['total_detections']:.0f}\n")
            f.write(f"  Avg Detection Rate: {overall_best['detection_rate_%']:.1f}%\n")
            f.write(f"  Avg Confidence: {overall_best['avg_confidence']:.3f}\n")
            f.write(f"  Avg FPS: {overall_best['avg_fps']:.1f}\n")

        print(f"Summary report saved to: {report_path}")

        # Print summary to console
        print("\n" + "="*80)
        print("QUICK SUMMARY")
        print("="*80)
        print("\nOverall Model Performance:")
        print(model_summary.to_string())

        print("\n" + "="*80)
        print("BEST PERFORMERS")
        print("="*80)
        print(f"\nMost Detections: {best_detections['model_name']} on {best_detections['video_name']}")
        print(f"  ({best_detections['total_detections']} detections)")
        print(f"\nHighest Confidence: {best_confidence['model_name']} on {best_confidence['video_name']}")
        print(f"  ({best_confidence['avg_confidence']:.3f})")
        print(f"\nFastest Processing: {best_fps['model_name']} on {best_fps['video_name']}")
        print(f"  ({best_fps['avg_fps']:.1f} FPS)")

def main():
    import sys

    print("Initializing Model Comparison...")
    comparator = ModelVideoComparison()

    # Check command line argument for saving videos
    save_videos = True
    if len(sys.argv) > 1:
        save_videos = sys.argv[1].lower() in ['y', 'yes', 'true', '1']

    print("\nWARNING: Saving output videos will take significant disk space.")
    print(f"You have {len(comparator.models)} models and {len(comparator.videos)} videos.")
    print(f"This will create {len(comparator.models) * len(comparator.videos)} output videos.")
    print(f"Save videos: {save_videos}")
    print(f"(Use: python compare_all_models.py [y/n] to change)")
    print()

    # Run all comparisons
    print("\nStarting comparison tests...")
    comparator.run_all_comparisons(save_videos=save_videos)

    # Generate report
    print("\nGenerating comparison report...")
    comparator.generate_report()

    print("\n" + "="*80)
    print("COMPARISON COMPLETE!")
    print("="*80)
    print(f"Results saved in: {comparator.results_dir}")

if __name__ == "__main__":
    main()

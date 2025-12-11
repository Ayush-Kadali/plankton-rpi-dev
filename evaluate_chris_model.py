#!/usr/bin/env python3
"""
Evaluate new_chris.pt Model on Flowing Videos
Generates annotated images and videos with comprehensive metrics
"""

import cv2
import numpy as np
from ultralytics import YOLO
import time
from pathlib import Path
from datetime import datetime
import json

class ChrisModelEvaluator:
    def __init__(self, model_path, output_dir="results/chris_model_eval"):
        self.model_path = Path(model_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.frames_dir = self.output_dir / "annotated_frames"
        self.videos_dir = self.output_dir / "annotated_videos"
        self.frames_dir.mkdir(exist_ok=True)
        self.videos_dir.mkdir(exist_ok=True)

        print(f"\n{'='*80}")
        print(f"Loading model: {self.model_path.name}")
        print(f"{'='*80}")

        self.model = YOLO(str(self.model_path))

        # Display model classes
        if hasattr(self.model, 'names'):
            print(f"\n✓ Model loaded successfully!")
            print(f"  Classes: {list(self.model.names.values())}")

        self.results = {}

    def process_video(self, video_path, save_video=True, save_frames=True, frame_interval=30):
        """
        Process video with model and generate annotated outputs

        Args:
            video_path: Path to video file
            save_video: Save annotated video output
            save_frames: Save sample annotated frames
            frame_interval: Save every Nth frame (default 30)
        """
        video_path = Path(video_path)
        print(f"\n{'='*80}")
        print(f"Processing: {video_path.name}")
        print(f"{'='*80}")

        # Open video
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            print(f"❌ Error opening video: {video_path}")
            return None

        # Get video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if fps > 0 else 0

        print(f"\nVideo Properties:")
        print(f"  Resolution: {width}x{height}")
        print(f"  FPS: {fps}")
        print(f"  Total Frames: {total_frames}")
        print(f"  Duration: {duration:.1f}s")

        # Setup video writer if needed
        video_writer = None
        if save_video:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_name = video_path.stem.replace(" ", "_")
            output_video_path = self.videos_dir / f"{video_name}_annotated_{timestamp}.mp4"

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(
                str(output_video_path),
                fourcc,
                fps,
                (width, height)
            )
            print(f"\n✓ Saving annotated video to: {output_video_path.name}")

        # Metrics
        frame_count = 0
        detection_count = 0
        total_detections = 0
        total_confidence = 0.0
        inference_times = []
        confidence_scores = []
        class_detections = {}
        saved_frames = []

        start_time = time.time()

        print(f"\n{'='*80}")
        print("Processing frames...")
        print(f"{'='*80}\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Run inference
            inf_start = time.time()
            results = self.model(frame, verbose=False, conf=0.25)
            inf_time = (time.time() - inf_start) * 1000
            inference_times.append(inf_time)

            # Get annotated frame
            annotated_frame = results[0].plot()

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
                    class_name = self.model.names[cls]

                    if class_name not in class_detections:
                        class_detections[class_name] = 0
                    class_detections[class_name] += 1

            if frame_dets > 0:
                detection_count += 1

            # Save annotated video frame
            if video_writer:
                video_writer.write(annotated_frame)

            # Save sample frames
            if save_frames and (frame_count % frame_interval == 0 or frame_dets > 0):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_name = video_path.stem.replace(" ", "_")
                frame_path = self.frames_dir / f"{video_name}_frame_{frame_count:05d}_dets_{frame_dets}.jpg"
                cv2.imwrite(str(frame_path), annotated_frame)
                saved_frames.append(str(frame_path))

            # Progress updates
            if frame_count % max(1, total_frames // 20) == 0:
                progress = (frame_count / total_frames) * 100
                avg_fps = frame_count / (time.time() - start_time)
                print(f"  Progress: {progress:.0f}% | Processed: {frame_count}/{total_frames} frames | "
                      f"Avg FPS: {avg_fps:.1f} | Detections: {total_detections}")

        # Cleanup
        cap.release()
        if video_writer:
            video_writer.release()

        processing_time = time.time() - start_time

        # Calculate metrics
        avg_inf_time = np.mean(inference_times) if inference_times else 0
        avg_inf_fps = 1000 / avg_inf_time if avg_inf_time > 0 else 0
        processing_fps = frame_count / processing_time if processing_time > 0 else 0
        avg_confidence = total_confidence / total_detections if total_detections > 0 else 0
        detection_rate = (detection_count / frame_count * 100) if frame_count > 0 else 0

        result = {
            'video_name': video_path.name,
            'video_resolution': f"{width}x{height}",
            'video_fps': fps,
            'video_duration_sec': round(duration, 1),
            'total_frames_processed': frame_count,
            'total_detections': total_detections,
            'frames_with_detections': detection_count,
            'detection_rate_%': round(detection_rate, 2),
            'avg_detections_per_frame': round(total_detections / frame_count, 3) if frame_count > 0 else 0,
            'avg_confidence': round(avg_confidence, 4),
            'min_confidence': round(min(confidence_scores), 4) if confidence_scores else 0,
            'max_confidence': round(max(confidence_scores), 4) if confidence_scores else 0,
            'processing_time_sec': round(processing_time, 1),
            'processing_fps': round(processing_fps, 1),
            'avg_inference_ms': round(avg_inf_time, 2),
            'avg_inference_fps': round(avg_inf_fps, 1),
            'min_inference_ms': round(min(inference_times), 2) if inference_times else 0,
            'max_inference_ms': round(max(inference_times), 2) if inference_times else 0,
            'realtime_capable': avg_inf_fps >= fps,
            'realtime_margin_%': round((avg_inf_fps / fps - 1) * 100, 1) if fps > 0 else 0,
            'class_detections': class_detections,
            'num_unique_classes': len(class_detections),
            'saved_frames': saved_frames,
            'annotated_video': str(output_video_path) if save_video else None
        }

        # Print summary
        print(f"\n{'='*80}")
        print("RESULTS SUMMARY:")
        print(f"{'='*80}")
        print(f"  Total Detections: {total_detections}")
        print(f"  Frames with Detections: {detection_count}/{frame_count} ({detection_rate:.1f}%)")
        print(f"  Avg Detections/Frame: {result['avg_detections_per_frame']:.3f}")
        print(f"  Avg Confidence: {avg_confidence:.3f}")
        print(f"  Confidence Range: [{result['min_confidence']:.3f}, {result['max_confidence']:.3f}]")
        print(f"\n  Processing Speed:")
        print(f"    Inference: {avg_inf_time:.1f}ms ({avg_inf_fps:.1f} FPS)")
        print(f"    Overall: {processing_fps:.1f} FPS")
        print(f"    Real-time Capable: {'✓ YES' if result['realtime_capable'] else '✗ NO'} ({result['realtime_margin_%']:+.1f}%)")

        if class_detections:
            print(f"\n  Detected Classes:")
            for cls, count in sorted(class_detections.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {cls}: {count} detections")

        if save_frames:
            print(f"\n  ✓ Saved {len(saved_frames)} annotated frames to: {self.frames_dir}")

        if save_video:
            print(f"  ✓ Saved annotated video to: {output_video_path}")

        self.results[video_path.name] = result
        return result

    def generate_report(self):
        """Generate comprehensive evaluation report"""
        if not self.results:
            print("\n❌ No results to report!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON report
        json_path = self.output_dir / f"evaluation_report_{timestamp}.json"
        with open(json_path, 'w') as f:
            # Convert numpy types to native Python types for JSON serialization
            serializable_results = {}
            for key, result in self.results.items():
                result_copy = result.copy()
                # Convert numpy bool to python bool
                if 'realtime_capable' in result_copy:
                    result_copy['realtime_capable'] = bool(result_copy['realtime_capable'])
                serializable_results[key] = result_copy
            json.dump(serializable_results, f, indent=2)

        # Generate text report
        report_path = self.output_dir / f"evaluation_report_{timestamp}.txt"

        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("NEW_CHRIS.PT MODEL EVALUATION REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Model: {self.model_path.name}\n")
            f.write(f"Videos Evaluated: {len(self.results)}\n")
            f.write("="*80 + "\n\n")

            # Per-video results
            for video_name, result in self.results.items():
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
                        f.write(f"  - {cls}: {count}\n")

                f.write(f"\nOutputs:\n")
                f.write(f"  Annotated Frames: {len(result['saved_frames'])} saved\n")
                if result['annotated_video']:
                    f.write(f"  Annotated Video: {Path(result['annotated_video']).name}\n")

            # Overall summary
            f.write(f"\n\n{'='*80}\n")
            f.write("OVERALL SUMMARY\n")
            f.write(f"{'='*80}\n\n")

            total_dets = sum(r['total_detections'] for r in self.results.values())
            total_frames = sum(r['total_frames_processed'] for r in self.results.values())
            avg_conf = np.mean([r['avg_confidence'] for r in self.results.values()])
            avg_inf_fps = np.mean([r['avg_inference_fps'] for r in self.results.values()])

            f.write(f"Total Detections Across All Videos: {total_dets}\n")
            f.write(f"Total Frames Processed: {total_frames}\n")
            f.write(f"Average Confidence: {avg_conf:.3f}\n")
            f.write(f"Average Inference Speed: {avg_inf_fps:.1f} FPS\n")

            all_classes = set()
            for r in self.results.values():
                all_classes.update(r['class_detections'].keys())

            f.write(f"\nAll Detected Classes ({len(all_classes)}):\n")
            for cls in sorted(all_classes):
                f.write(f"  - {cls}\n")

        print(f"\n{'='*80}")
        print("REPORT GENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"✓ JSON Report: {json_path}")
        print(f"✓ Text Report: {report_path}")
        print(f"✓ Annotated Frames: {self.frames_dir}")
        print(f"✓ Annotated Videos: {self.videos_dir}")
        print(f"{'='*80}\n")


def main():
    print("\n" + "#"*80)
    print("NEW_CHRIS.PT MODEL EVALUATION")
    print("#"*80 + "\n")

    # Initialize evaluator
    model_path = "Downloaded models/new_chris.pt"
    evaluator = ChrisModelEvaluator(model_path)

    # Videos to evaluate
    videos = [
        "Real_Time_Vids/good flow.mov",
        "Real_Time_Vids/v4 try 2.mov"
    ]

    # Process each video
    for video in videos:
        if Path(video).exists():
            evaluator.process_video(
                video,
                save_video=True,
                save_frames=True,
                frame_interval=30  # Save every 30th frame + frames with detections
            )
        else:
            print(f"\n❌ Video not found: {video}")

    # Generate final report
    evaluator.generate_report()

    print("\n" + "#"*80)
    print("EVALUATION COMPLETE!")
    print("#"*80 + "\n")


if __name__ == "__main__":
    main()

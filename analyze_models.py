#!/usr/bin/env python3
"""
Model Analysis Script
Analyzes model specifications, size, parameters, and computational requirements
"""

import os
from pathlib import Path
from ultralytics import YOLO
import time
import numpy as np
import cv2
import psutil
import json
from datetime import datetime

class ModelAnalyzer:
    def __init__(self):
        self.models_dir = Path("Downloaded models")
        self.results = []

    def get_model_size(self, model_path):
        """Get model file size in MB"""
        size_bytes = model_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        return round(size_mb, 2)

    def analyze_model(self, model_path, model_name):
        """Analyze a single model's specifications"""
        print(f"\n{'='*80}")
        print(f"ANALYZING: {model_name}")
        print(f"{'='*80}")

        # File size
        file_size_mb = self.get_model_size(model_path)
        print(f"File Size: {file_size_mb} MB")

        # Load model
        try:
            model = YOLO(model_path)
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

        # Get model info
        model_info = {
            'model_name': model_name,
            'model_file': model_path.name,
            'file_size_mb': file_size_mb,
        }

        # Try to get model details
        try:
            # Get task type
            model_info['task'] = model.task if hasattr(model, 'task') else 'detection'

            # Get model names/classes
            if hasattr(model, 'names'):
                model_info['classes'] = list(model.names.values())
                model_info['num_classes'] = len(model.names)
                print(f"Classes ({len(model.names)}): {list(model.names.values())}")

            # Model architecture
            if hasattr(model, 'model'):
                # Count parameters
                total_params = sum(p.numel() for p in model.model.parameters())
                trainable_params = sum(p.numel() for p in model.model.parameters() if p.requires_grad)

                model_info['total_parameters'] = total_params
                model_info['trainable_parameters'] = trainable_params
                model_info['parameters_millions'] = round(total_params / 1_000_000, 2)

                print(f"Total Parameters: {total_params:,} ({model_info['parameters_millions']}M)")
                print(f"Trainable Parameters: {trainable_params:,}")

                # Count layers
                num_layers = len(list(model.model.modules()))
                model_info['num_layers'] = num_layers
                print(f"Number of Layers: {num_layers}")
        except Exception as e:
            print(f"Could not extract detailed model info: {e}")

        # Benchmark inference speed
        print(f"\nBenchmarking inference speed...")

        # Create test images of different sizes
        test_sizes = [
            (640, 480),   # VGA
            (1280, 720),  # HD
            (1920, 1080)  # Full HD
        ]

        benchmark_results = {}

        for size in test_sizes:
            width, height = size
            test_image = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)

            # Warm up
            for _ in range(3):
                _ = model(test_image, verbose=False)

            # Benchmark
            times = []
            memory_usage = []

            for _ in range(10):
                # Memory before
                process = psutil.Process(os.getpid())
                mem_before = process.memory_info().rss / 1024 / 1024  # MB

                start = time.time()
                results = model(test_image, verbose=False, conf=0.25)
                end = time.time()

                # Memory after
                mem_after = process.memory_info().rss / 1024 / 1024  # MB

                times.append((end - start) * 1000)  # ms
                memory_usage.append(mem_after - mem_before)

            avg_time = np.mean(times)
            std_time = np.std(times)
            avg_fps = 1000 / avg_time if avg_time > 0 else 0
            avg_memory = np.mean(memory_usage)

            size_key = f"{width}x{height}"
            benchmark_results[size_key] = {
                'avg_time_ms': round(avg_time, 2),
                'std_time_ms': round(std_time, 2),
                'min_time_ms': round(min(times), 2),
                'max_time_ms': round(max(times), 2),
                'avg_fps': round(avg_fps, 2),
                'avg_memory_delta_mb': round(avg_memory, 2)
            }

            print(f"  {size_key}: {avg_time:.1f}ms ± {std_time:.1f}ms ({avg_fps:.1f} FPS)")

        model_info['benchmark'] = benchmark_results

        # Overall speed rating
        avg_640_time = benchmark_results['640x480']['avg_time_ms']
        if avg_640_time < 20:
            speed_rating = "Very Fast"
        elif avg_640_time < 40:
            speed_rating = "Fast"
        elif avg_640_time < 80:
            speed_rating = "Medium"
        else:
            speed_rating = "Slow"

        model_info['speed_rating'] = speed_rating
        print(f"\nSpeed Rating: {speed_rating}")

        # Memory footprint estimate
        current_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
        model_info['estimated_memory_mb'] = round(current_memory, 2)
        print(f"Estimated Memory Usage: {model_info['estimated_memory_mb']} MB")

        return model_info

    def analyze_all_models(self):
        """Analyze all available models"""
        models = {
            "best.pt": "Custom Best Model",
            "chris_best.pt": "Chris Best Model",
            "yolov5nu.pt": "YOLOv5n-u",
            "yolov8n.pt": "YOLOv8n"
        }

        print(f"\n{'#'*80}")
        print(f"MODEL ANALYSIS")
        print(f"{'#'*80}")
        print(f"\nAnalyzing {len(models)} models...")

        for model_file, model_name in models.items():
            model_path = self.models_dir / model_file

            if not model_path.exists():
                print(f"\nWARNING: Model not found: {model_path}")
                continue

            result = self.analyze_model(model_path, model_name)
            if result:
                self.results.append(result)

        return self.results

    def generate_report(self):
        """Generate comprehensive model comparison report"""
        if not self.results:
            print("No results to report!")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save JSON
        json_path = Path("results") / f"model_analysis_{timestamp}.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)

        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed analysis saved to: {json_path}")

        # Generate text report
        report_path = Path("results") / f"model_analysis_{timestamp}.txt"

        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("PLANKTON DETECTION MODEL ANALYSIS REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Models Analyzed: {len(self.results)}\n")
            f.write("="*80 + "\n\n")

            # Summary table
            f.write("MODEL COMPARISON SUMMARY\n")
            f.write("-"*80 + "\n\n")

            # Create comparison table
            f.write(f"{'Model':<25} {'Size (MB)':<12} {'Params (M)':<12} {'Speed@640p':<15} {'FPS@640p':<10}\n")
            f.write("-"*80 + "\n")

            for result in self.results:
                name = result['model_name'][:24]
                size = f"{result['file_size_mb']}"
                params = f"{result.get('parameters_millions', 'N/A')}"
                speed = f"{result['benchmark']['640x480']['avg_time_ms']} ms"
                fps = f"{result['benchmark']['640x480']['avg_fps']}"

                f.write(f"{name:<25} {size:<12} {params:<12} {speed:<15} {fps:<10}\n")

            f.write("\n\n")

            # Detailed specs for each model
            f.write("DETAILED MODEL SPECIFICATIONS\n")
            f.write("="*80 + "\n\n")

            for result in self.results:
                f.write(f"{result['model_name']}\n")
                f.write("-"*80 + "\n")
                f.write(f"File: {result['model_file']}\n")
                f.write(f"File Size: {result['file_size_mb']} MB\n")
                f.write(f"Parameters: {result.get('total_parameters', 'N/A'):,} ({result.get('parameters_millions', 'N/A')}M)\n")
                f.write(f"Layers: {result.get('num_layers', 'N/A')}\n")
                f.write(f"Classes: {result.get('num_classes', 'N/A')}\n")
                f.write(f"Speed Rating: {result['speed_rating']}\n")
                f.write(f"Memory Usage: {result['estimated_memory_mb']} MB\n")
                f.write(f"\nBenchmark Results:\n")

                for size, metrics in result['benchmark'].items():
                    f.write(f"  {size}:\n")
                    f.write(f"    Avg Time: {metrics['avg_time_ms']} ms\n")
                    f.write(f"    Std Dev: {metrics['std_time_ms']} ms\n")
                    f.write(f"    Range: {metrics['min_time_ms']}-{metrics['max_time_ms']} ms\n")
                    f.write(f"    FPS: {metrics['avg_fps']}\n")

                f.write("\n")

                if 'classes' in result:
                    f.write(f"Classes: {', '.join(result['classes'])}\n")

                f.write("\n\n")

            # Recommendations
            f.write("="*80 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("="*80 + "\n\n")

            # Find best for different criteria
            fastest = min(self.results, key=lambda x: x['benchmark']['640x480']['avg_time_ms'])
            smallest = min(self.results, key=lambda x: x['file_size_mb'])

            f.write(f"Fastest Model: {fastest['model_name']}\n")
            f.write(f"  {fastest['benchmark']['640x480']['avg_time_ms']} ms per frame\n")
            f.write(f"  {fastest['benchmark']['640x480']['avg_fps']} FPS\n\n")

            f.write(f"Smallest Model: {smallest['model_name']}\n")
            f.write(f"  {smallest['file_size_mb']} MB\n\n")

            f.write("\nFor Real-Time Applications:\n")
            f.write("  - Prioritize models with >20 FPS at your target resolution\n")
            f.write("  - Consider memory constraints on embedded devices\n")
            f.write("  - Balance speed vs detection accuracy\n\n")

            f.write("For Raspberry Pi Deployment:\n")
            f.write("  - Use smaller models (<10M parameters)\n")
            f.write("  - Target models with <50ms inference time\n")
            f.write("  - Consider using INT8 quantization for further speedup\n")

        print(f"Summary report saved to: {report_path}")

        # Print to console
        print("\n" + "="*80)
        print("MODEL COMPARISON SUMMARY")
        print("="*80 + "\n")

        print(f"{'Model':<25} {'Size (MB)':<12} {'Params (M)':<12} {'Speed@640p':<15} {'FPS@640p':<10}")
        print("-"*80)

        for result in self.results:
            name = result['model_name'][:24]
            size = f"{result['file_size_mb']}"
            params = f"{result.get('parameters_millions', 'N/A')}"
            speed = f"{result['benchmark']['640x480']['avg_time_ms']} ms"
            fps = f"{result['benchmark']['640x480']['avg_fps']}"

            print(f"{name:<25} {size:<12} {params:<12} {speed:<15} {fps:<10}")

        print("\n" + "="*80)
        print("BEST PERFORMERS")
        print("="*80)
        print(f"\nFastest: {fastest['model_name']} ({fastest['benchmark']['640x480']['avg_fps']} FPS)")
        print(f"Smallest: {smallest['model_name']} ({smallest['file_size_mb']} MB)")

def main():
    analyzer = ModelAnalyzer()
    analyzer.analyze_all_models()
    analyzer.generate_report()

if __name__ == "__main__":
    main()

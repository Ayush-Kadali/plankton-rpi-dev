#!/usr/bin/env python3
"""
YOLOv8 Plankton Detection - Inference Script
Tests the fine-tuned model on a single image and displays results
"""

from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
from pathlib import Path

# Model path - update this to the actual trained model path
MODEL_PATH = "runs/detect/train14/weights/best.pt"
# MODEL_PATH = "runs/detect/train3/weights/best (1).pt"
IMAGE_PATH = "img2.jpeg"

def load_and_test_model(model_path, image_path):
    """
    Load the fine-tuned YOLOv8 model and run inference on an image
    
    Args:
        model_path: Path to the trained model weights
        image_path: Path to the input image
    """
    # Check if model exists
    if not Path(model_path).exists():
        print(f"❌ Model not found at: {model_path}")
        print("Please ensure the model has been trained and the path is correct.")
        return
    
    # Check if image exists
    if not Path(image_path).exists():
        print(f"❌ Image not found at: {image_path}")
        return
    
    # Load the trained model
    print(f"📦 Loading model from: {model_path}")
    model = YOLO(model_path)
    
    # Run inference
    print(f"🔍 Running inference on: {image_path}")
    results = model(image_path)
    
    # Get the first result (since we're processing one image)
    result = results[0]
    
    # Print detection results
    print(f"\n✅ Detection complete!")
    print(f"📊 Number of detections: {len(result.boxes)}")
    
    if len(result.boxes) > 0:
        print("\n🔎 Detected objects:")
        for i, box in enumerate(result.boxes):
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            class_name = model.names[cls_id]
            print(f"  {i+1}. {class_name} (confidence: {conf:.2%})")
    else:
        print("ℹ️  No objects detected in the image")
    
    # Save annotated image
    output_path = "output_detection.jpg"
    annotated_img = result.plot()
    cv2.imwrite(output_path, annotated_img)
    print(f"\n💾 Annotated image saved to: {output_path}")
    
    # Display the result using matplotlib
    print("📺 Displaying result...")
    img_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(img_rgb)
    plt.axis('off')
    plt.title(f'YOLOv8 Plankton Detection - {len(result.boxes)} objects detected', 
              fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig("output_detection_plot.png", dpi=150, bbox_inches='tight')
    plt.show()
    
    print(f"✨ Detection plot saved to: output_detection_plot.png")
    
    return results

if __name__ == "__main__":
    print("=" * 60)
    print("YOLOv8 Plankton Detection - Inference Script")
    print("=" * 60)
    
    results = load_and_test_model(MODEL_PATH, IMAGE_PATH)
    
    print("\n" + "=" * 60)
    print("✅ Inference complete!")
    print("=" * 60)

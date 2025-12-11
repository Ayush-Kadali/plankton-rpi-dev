#!/usr/bin/env python3
"""
Fix and convert the best model to TFLite
Uses Phase 1 model which had best results
"""

import tensorflow as tf
import pickle
import json
from pathlib import Path

print("=" * 80)
print("FIXING AND CONVERTING MODEL")
print("=" * 80)

# Load the best model from Phase 1
print("\n[1/3] Loading best model...")
model = tf.keras.models.load_model('models/plankton_mobilenet_v2_best.keras')
print(f"  ✓ Loaded: models/plankton_mobilenet_v2_best.keras")

# Save class names and metadata
print("\n[2/3] Saving metadata...")
class_names = [
    'Alexandrium', 'Asterionellopsis glacialis', 'Cerataulina', 'Ceratium',
    'Chaetoceros', 'Entomoneis', 'Guinardia', 'Hemiaulus',
    'Lauderia annulata', 'Nitzschia', 'Noctiluca', 'Ornithocercus magnificus',
    'Pinnularia', 'Pleurosigma', 'Prorocentrum', 'Protoperidinium',
    'Pyrodinium', 'Thalassionema', 'Thalassiosira'
]

with open('models/plankton_mobilenet_v2_classes.pkl', 'wb') as f:
    pickle.dump(class_names, f)
print(f"  ✓ Saved: models/plankton_mobilenet_v2_classes.pkl")

metadata = {
    'model_name': 'plankton_mobilenet_v2',
    'num_classes': len(class_names),
    'class_names': class_names,
    'input_shape': [128, 128, 3],
    'architecture': 'MobileNetV2 + Custom Head',
    'training_stage': 'Phase 1 (Transfer Learning)',
    'note': 'Best Phase 1 model (14% val accuracy)'
}

with open('models/plankton_mobilenet_v2_metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"  ✓ Saved: models/plankton_mobilenet_v2_metadata.json")

# Convert to TFLite with proper method
print("\n[3/3] Converting to TFLite...")
try:
    # Create converter with concrete function
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Optimizations for edge deployment
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Convert
    tflite_model = converter.convert()

    # Save
    tflite_path = 'models/plankton_mobilenet_v2.tflite'
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)

    size_kb = len(tflite_model) / 1024
    print(f"  ✓ TFLite model saved: {tflite_path} ({size_kb:.1f} KB)")

except Exception as e:
    print(f"  ⚠ TFLite conversion failed: {e}")
    print("  → The .keras model can still be used for inference")

print("\n" + "=" * 80)
print("MODEL READY!")
print("=" * 80)
print("\nAvailable models:")
print("  1. models/plankton_mobilenet_v2_best.keras (Phase 1, 14% val acc)")
print("  2. models/plankton_classifier.keras (Original, ~40% confidence on real images)")
print("\nNext: Create multi-model system to switch or ensemble them")
print("=" * 80)

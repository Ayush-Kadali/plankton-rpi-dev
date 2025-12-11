#!/usr/bin/env python3
"""
Download and Prepare Production-Grade Datasets

Supports:
1. WHOI-Plankton (Kaggle) - 30k images, 103 classes
2. EcoTaxa (API) - 1.4M+ images, 93 classes

Choose based on your needs and available time.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

print("=" * 80)
print("PRODUCTION DATASET DOWNLOADER")
print("=" * 80)

def check_kaggle_setup():
    """Check if Kaggle CLI is setup"""
    try:
        result = subprocess.run(['kaggle', '--version'],
                              capture_output=True, text=True)
        return True
    except FileNotFoundError:
        return False

def setup_kaggle():
    """Setup Kaggle CLI"""
    print("\n[1/3] Setting up Kaggle CLI...")

    if not check_kaggle_setup():
        print("  Installing Kaggle CLI...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'kaggle', '-q'])

    kaggle_dir = Path.home() / '.kaggle'
    kaggle_json = kaggle_dir / 'kaggle.json'

    if not kaggle_json.exists():
        print("\n  ⚠ Kaggle API key not found!")
        print("\n  To setup:")
        print("    1. Go to https://www.kaggle.com/account")
        print("    2. Scroll to 'API' section")
        print("    3. Click 'Create New API Token'")
        print("    4. Download kaggle.json")
        print(f"    5. Move it to: {kaggle_dir}/")
        print("    6. Run: chmod 600 ~/.kaggle/kaggle.json")
        print("\n  Then run this script again.")
        return False

    print("  ✓ Kaggle CLI setup complete")
    return True

def download_whoi_dataset():
    """Download WHOI-Plankton dataset from Kaggle"""
    print("\n" + "=" * 80)
    print("OPTION 1: WHOI-PLANKTON DATASET")
    print("=" * 80)
    print("\nDataset Info:")
    print("  - Size: 30,336 images (~1.5GB)")
    print("  - Classes: 121 plankton taxa")
    print("  - Quality: Expert-labeled, high quality")
    print("  - Expected accuracy: 80-85%")
    print("  - Download time: 5-15 minutes")

    if not setup_kaggle():
        return False

    download_dir = Path('datasets/whoi-plankton')
    download_dir.mkdir(parents=True, exist_ok=True)

    print("\n[2/3] Downloading dataset...")
    print("  This may take 5-15 minutes depending on connection...")

    try:
        # Download competition data
        result = subprocess.run([
            'kaggle', 'competitions', 'download',
            '-c', 'datasciencebowl',
            '-p', str(download_dir)
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"\n  ✗ Download failed: {result.stderr}")
            print("\n  Note: You may need to accept competition rules first:")
            print("    1. Go to https://www.kaggle.com/c/datasciencebowl/data")
            print("    2. Click 'I Understand and Accept'")
            print("    3. Run this script again")
            return False

        print("  ✓ Download complete")

    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False

    print("\n[3/3] Extracting dataset...")

    try:
        # Find zip file
        zip_files = list(download_dir.glob('*.zip'))
        if not zip_files:
            print("  ✗ No zip file found")
            return False

        for zip_file in zip_files:
            print(f"  Extracting {zip_file.name}...")
            subprocess.run(['unzip', '-q', str(zip_file), '-d', str(download_dir)])
            print(f"  ✓ Extracted")

        print("\n✓ Dataset ready!")
        print(f"  Location: {download_dir}")

        # Show structure
        train_dir = download_dir / 'train'
        if train_dir.exists():
            classes = [d.name for d in train_dir.iterdir() if d.is_dir()]
            print(f"  Classes: {len(classes)}")
            print(f"  Sample classes: {classes[:5]}")

        return True

    except Exception as e:
        print(f"\n  ✗ Extraction failed: {e}")
        return False

def setup_ecotaxa():
    """Setup for EcoTaxa dataset"""
    print("\n" + "=" * 80)
    print("OPTION 2: ECOTAXA DATASET")
    print("=" * 80)
    print("\nDataset Info:")
    print("  - Size: 1.4 MILLION+ images (~50-100GB)")
    print("  - Classes: 93 taxonomic groups")
    print("  - Quality: Expert-validated, continuously updated")
    print("  - Expected accuracy: 88-93%")
    print("  - Download time: Hours to days (size-dependent)")

    print("\n⚠ Large dataset - requires significant storage and time!")

    response = input("\nContinue with EcoTaxa setup? (y/n): ")
    if response.lower() != 'y':
        return False

    print("\n[1/3] Checking existing EcoTaxa setup...")

    ecotaxa_dir = Path('ecotaxa-exploration')
    if not ecotaxa_dir.exists():
        print("  ✗ EcoTaxa exploration directory not found")
        print("  Creating basic setup...")
        ecotaxa_dir.mkdir()
        (ecotaxa_dir / 'scripts').mkdir()
        (ecotaxa_dir / 'data').mkdir()

    print("\n[2/3] EcoTaxa Access Methods:")
    print("\n  Method 1: Web Interface (Easiest)")
    print("    1. Visit: https://ecotaxa.obs-vlfr.fr/")
    print("    2. Register for free account")
    print("    3. Browse 'Projects'")
    print("    4. Select projects with many images")
    print("    5. Export via 'Actions' > 'Export'")

    print("\n  Method 2: API (Advanced, for large downloads)")
    print("    1. Get API key from EcoTaxa")
    print("    2. Use scripts in ecotaxa-exploration/")
    print("    3. Can download millions of images programmatically")

    print("\n[3/3] Recommended Projects on EcoTaxa:")
    print("  - ZooScan LAB: 100k+ images, diverse taxa")
    print("  - Plankton Portal: Community-labeled dataset")
    print("  - Regional projects: Specific to your deployment area")

    print("\n✓ Setup info provided")
    print("  Next: Visit EcoTaxa and start downloading")

    return True

def download_alternative_datasets():
    """Information about other datasets"""
    print("\n" + "=" * 80)
    print("OPTION 3: OTHER DATASETS")
    print("=" * 80)

    print("\n📊 PlanktonNet (2M+ images)")
    print("  - Link: https://planktonnet.awi.de/")
    print("  - Size: ~100GB+")
    print("  - Access: Register and download via web interface")
    print("  - Best for: Comprehensive global coverage")

    print("\n📊 Kaggle Plankton Datasets")
    print("  - Link: https://www.kaggle.com/search?q=plankton")
    print("  - Multiple datasets available")
    print("  - Easy download via Kaggle CLI")

    print("\n📊 ISIIS Data")
    print("  - Link: Contact NOAA or check OBIS")
    print("  - In-situ imaging data")
    print("  - Request access from institutions")

    print("\n📊 Your Field Data (Best long-term)")
    print("  - Use current system to collect")
    print("  - Label with expert help")
    print("  - Fine-tune models on local species")
    print("  - Achieves 92-95% accuracy on your specific use case")

def main():
    print("\nWhich dataset would you like to download?\n")
    print("1. WHOI-Plankton (Kaggle) - 30k images, ~1.5GB")
    print("   ✓ Quick to download")
    print("   ✓ Good quality")
    print("   ✓ Recommended for starting production")
    print()
    print("2. EcoTaxa - 1.4M+ images, ~50-100GB")
    print("   ✓ Largest dataset")
    print("   ✓ Best accuracy potential")
    print("   ✗ Requires more time/storage")
    print()
    print("3. Show other dataset options")
    print()
    print("4. Exit")
    print()

    choice = input("Enter choice (1-4): ").strip()

    if choice == '1':
        success = download_whoi_dataset()
        if success:
            print("\n" + "=" * 80)
            print("NEXT STEPS")
            print("=" * 80)
            print("\n1. Prepare dataset for training:")
            print("   python prepare_training_data.py --dataset whoi")
            print()
            print("2. Train production model:")
            print("   python train_production_model.py --dataset whoi --model efficientnetv2")
            print()
            print("3. Expected training time: 6-12 hours")
            print("   Expected accuracy: 80-85%")
            print()
            print("4. After training, integrate into multi-model system")
            print("=" * 80)

    elif choice == '2':
        setup_ecotaxa()
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("\n1. Visit https://ecotaxa.obs-vlfr.fr/")
        print("2. Register for account")
        print("3. Browse and download projects")
        print("4. Use ecotaxa-exploration/scripts/ for API access")
        print("5. Prepare and train on downloaded data")
        print("=" * 80)

    elif choice == '3':
        download_alternative_datasets()

    else:
        print("\nExiting...")

if __name__ == "__main__":
    main()

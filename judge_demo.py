#!/usr/bin/env python3
"""
COMPLETE JUDGE DEMO
One command to generate everything for demonstration
"""

import subprocess
import sys
from pathlib import Path

print("=" * 80)
print("PLANKTON DETECTION SYSTEM - COMPLETE JUDGE DEMO")
print("=" * 80)

print("\nThis will:")
print("  1. ✅ Generate realistic data across 7 Indian coastal locations")
print("  2. ✅ Create interactive map with color-coded markers")
print("  3. ✅ Enable location-based data export")
print("  4. ✅ Show 30 days of monitoring data")
print("")

response = input("Continue? (y/n): ")

if response.lower() != 'y':
    print("Demo cancelled")
    sys.exit(0)

# Clean previous demo data
print("\n" + "=" * 80)
print("STEP 1: Cleaning previous demo data...")
print("=" * 80)

demo_files = [
    "data/judge_demo.db",
    "results/maps/judge_demo_professional.html"
]

for file in demo_files:
    file_path = Path(file)
    if file_path.exists():
        file_path.unlink()
        print(f"   🗑️ Removed {file}")

# Generate demo data
print("\n" + "=" * 80)
print("STEP 2: Generating realistic sample data...")
print("=" * 80)

result = subprocess.run(
    ["python3", "generate_demo_data.py"],
    capture_output=False
)

if result.returncode != 0:
    print("\n❌ Data generation failed!")
    sys.exit(1)

# Create professional map
print("\n" + "=" * 80)
print("STEP 3: Creating professional interactive map...")
print("=" * 80)

result = subprocess.run(
    ["python3", "create_judge_demo_map.py"],
    capture_output=False
)

if result.returncode != 0:
    print("\n❌ Map creation failed!")
    sys.exit(1)

# Success summary
print("\n" + "=" * 80)
print("✅ JUDGE DEMO COMPLETE!")
print("=" * 80)

print("\n📂 Generated Files:")
print("   🗄️ Database: data/judge_demo.db")
print("   🗺️ Interactive Map: results/maps/judge_demo_professional.html")

print("\n🌐 VIEW THE DEMO:")
print("   1. Open: results/maps/judge_demo_professional.html")
print("   2. Click any marker to see detailed statistics")
print("   3. Note the color-coded markers:")
print("      - Red/Orange: Algae bloom activity")
print("      - Dark Blue: Research stations (high frequency)")
print("      - Blue/Light Blue: Regular monitoring")
print("      - Green: Low frequency sites")

print("\n📥 EXPORT LOCATION DATA:")
print("   List all locations:")
print("      python3 export_location_data.py --list")
print("")
print("   Export specific location:")
print("      python3 export_location_data.py --location \"Mumbai Harbor\"")
print("")
print("   Interactive export:")
print("      python3 export_location_data.py")

print("\n🎯 KEY FEATURES FOR JUDGES:")
print("   ✅ 7 diverse sampling locations across India")
print("   ✅ Mumbai to West Bengal coverage")
print("   ✅ 108+ total samples across 30 days")
print("   ✅ Algae bloom detection (Kochi, Sundarbans)")
print("   ✅ Biodiversity hotspot (Gulf of Mannar)")
print("   ✅ Research station demo (Mumbai - 25 samples)")
print("   ✅ Color-coded monitoring frequency")
print("   ✅ Click-to-view detailed statistics")
print("   ✅ Location-based CSV export")
print("   ✅ Realistic species distributions")

print("\n💡 DEMONSTRATION POINTS:")
print("   1. Show the map - explain color coding")
print("   2. Click Mumbai (blue) - high frequency research station")
print("   3. Click Kochi (red/orange) - show bloom detection")
print("   4. Click Gulf of Mannar - biodiversity hotspot")
print("   5. Export data for any location to CSV")
print("   6. Explain cloud sync capability (when online)")

print("\n🚀 NEXT: Integration with Your Pipeline")
print("   Use modules/data_collector.py to:")
print("   - Capture GPS during video recording")
print("   - Store inference results with location")
print("   - Auto-sync to cloud when internet available")

print("\n" + "=" * 80)
print("Ready for demonstration! Open the HTML file in your browser.")
print("=" * 80)

#!/usr/bin/env python3
"""
Quick Demo - Test Cloud & Map Integration
Creates sample data, database, and interactive map
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Create directories
Path("data").mkdir(exist_ok=True)
Path("results/maps").mkdir(parents=True, exist_ok=True)
Path("config").mkdir(exist_ok=True)

print("=" * 80)
print("PLANKTON MAP INTEGRATION - QUICK DEMO")
print("=" * 80)

# Import modules directly (avoiding modules/__init__.py)
print("\n1. Importing modules...")
sys.path.insert(0, str(Path(__file__).parent))

# Import database module directly
import importlib.util
spec = importlib.util.spec_from_file_location("database", "modules/database.py")
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)

spec = importlib.util.spec_from_file_location("location", "modules/location.py")
location = importlib.util.module_from_spec(spec)
spec.loader.exec_module(location)

spec = importlib.util.spec_from_file_location("map_viewer", "modules/map_viewer.py")
map_viewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(map_viewer)

print("   ✅ Modules imported successfully!")

# Create location manager
print("\n2. Setting up locations...")
loc_mgr = location.LocationManager()

# Load preset locations
with open("config/preset_locations.json") as f:
    loc_mgr.preset_locations = json.load(f)

print(f"   ✅ Loaded {len(loc_mgr.preset_locations)} preset locations")

# Create database
print("\n3. Creating database...")
db = database.PlanktonDatabase("data/demo_plankton.db")
print("   ✅ Database created: data/demo_plankton.db")

# Create sample data
print("\n4. Creating sample data...")

locations = [
    ("Mumbai Harbor", 45, 8),
    ("Chennai Marina", 32, 6),
    ("Goa Coast", 78, 12),
    ("Kochi Backwaters", 105, 15)
]

sample_ids = []

for loc_name, total_orgs, species_count in locations:
    # Get location data
    loc_data = loc_mgr.get_location_preset(loc_name)

    # Create sample with unique timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    sample_data = {
        'sample_id': f'DEMO_{loc_name.replace(" ", "_").upper()}_{timestamp}',
        'timestamp': datetime.now().isoformat(),
        **loc_data,
        'operator_id': 'demo_user',
        'session_id': 'DEMO_SESSION',
        'magnification': 2.5,
        'exposure_ms': 100,
        'total_organisms': total_orgs,
        'species_richness': species_count
    }

    db.insert_sample(sample_data)
    sample_ids.append(sample_data['sample_id'])

    # Add some detections
    for i in range(min(total_orgs, 3)):
        detection = {
            'organism_id': i + 1,
            'class_name': ['Copepod', 'Diatom', 'Dinoflagellate'][i % 3],
            'confidence': 0.85 + (i * 0.05),
            'bbox': [100 + i*50, 100 + i*50, 150 + i*50, 150 + i*50],
            'size_px': 50.0 + i * 10
        }
        db.insert_detection(sample_data['sample_id'], detection)

    print(f"   ✅ {loc_name}: {total_orgs} organisms, {species_count} species")

# Get all samples
print("\n5. Querying samples...")
samples = db.get_all_samples_with_location()
print(f"   ✅ Retrieved {len(samples)} samples with location data")

# Create map
print("\n6. Creating interactive map...")
viewer = map_viewer.PlanktonMapViewer()

m = viewer.create_map_with_samples(
    samples,
    use_clustering=True,
    add_heatmap=False,
    auto_center=True
)

map_path = "results/maps/demo_map.html"
viewer.save_map(m, map_path)

print(f"   ✅ Map created: {map_path}")

# Create heatmap
print("\n7. Creating heatmap...")
m_heat = viewer.create_map_with_samples(
    samples,
    use_clustering=False,
    add_heatmap=True,
    auto_center=True
)

heatmap_path = "results/maps/demo_heatmap.html"
viewer.save_map(m_heat, heatmap_path)

print(f"   ✅ Heatmap created: {heatmap_path}")

# Export to CSV
print("\n8. Exporting to CSV...")
csv_path = db.export_to_csv("exports/demo_samples.csv")
print(f"   ✅ Exported to: {csv_path}")

# Statistics
print("\n9. Database statistics...")
stats = db.get_statistics()
for key, value in stats.items():
    print(f"   {key}: {value}")

print("\n" + "=" * 80)
print("✅ DEMO COMPLETED SUCCESSFULLY!")
print("=" * 80)

print("\n📂 Results:")
print(f"   🗺️ Interactive Map: {map_path}")
print(f"   🔥 Heatmap: {heatmap_path}")
print(f"   💾 CSV Export: {csv_path}")
print(f"   🗄️ Database: data/demo_plankton.db")

print("\n🌐 Open the HTML files in your browser to view the interactive maps!")
print("\n📍 Samples on map:")
for sample in samples:
    print(f"   • {sample.get('location_name', 'Unknown')}: {sample.get('total_organisms', 0)} organisms")

print("\n" + "=" * 80)
print("Next: Run 'streamlit run map_viewer_app.py' for the full web interface!")
print("=" * 80)

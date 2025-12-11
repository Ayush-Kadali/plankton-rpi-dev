#!/usr/bin/env python3
"""
Demo: Cloud & Map Integration
Demonstrates the complete workflow of location tracking, cloud storage, and map visualization
"""

import logging
from datetime import datetime
from pathlib import Path

# Import our modules
from modules.database import PlanktonDatabase
from modules.location import LocationManager
from modules.cloud_storage import FirebaseStorageManager
from modules.map_viewer import PlanktonMapViewer, create_quick_map

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_location_management():
    """Demo: Creating and managing locations"""
    print("\n" + "="*80)
    print("DEMO 1: Location Management")
    print("="*80)

    # Initialize location manager
    location_mgr = LocationManager()

    # Create default preset locations
    print("\n1. Creating default preset locations...")
    location_mgr.create_default_presets("config/preset_locations.json")
    print(f"   ✅ Created {len(location_mgr.preset_locations)} preset locations")

    # Manual location entry
    print("\n2. Creating manual location...")
    loc_manual = location_mgr.get_location_manual(
        latitude=19.0760,
        longitude=72.8777,
        location_name="Mumbai Test Site",
        water_body="Arabian Sea",
        depth_meters=5.0
    )
    print(f"   ✅ Location: {loc_manual['location_name']}")
    print(f"   📍 Coordinates: {loc_manual['latitude']}, {loc_manual['longitude']}")

    # Preset location
    print("\n3. Using preset location...")
    loc_preset = location_mgr.get_location_preset("Kochi Backwaters", depth_meters=2.5)
    print(f"   ✅ Location: {loc_preset['location_name']}")
    print(f"   📍 Coordinates: {loc_preset['latitude']}, {loc_preset['longitude']}")

    # Distance calculation
    print("\n4. Calculating distance between locations...")
    distance = location_mgr.calculate_distance(
        loc_manual['latitude'], loc_manual['longitude'],
        loc_preset['latitude'], loc_preset['longitude']
    )
    print(f"   📏 Distance: {distance:.2f} km")

    # Coordinate formatting
    print("\n5. Coordinate formatting examples...")
    print(f"   Decimal: {location_mgr.format_coordinates(19.0760, 72.8777, 'decimal')}")
    print(f"   DMS: {location_mgr.format_coordinates(19.0760, 72.8777, 'dms')}")

    return location_mgr


def demo_database_operations():
    """Demo: Database operations with location data"""
    print("\n" + "="*80)
    print("DEMO 2: Database Operations")
    print("="*80)

    # Initialize database
    db = PlanktonDatabase("data/demo_plankton.db")

    location_mgr = LocationManager()
    location_mgr.create_default_presets()

    print("\n1. Creating sample data with locations...")

    # Create multiple samples at different locations
    locations = [
        ("Mumbai Harbor", 45, 8),
        ("Chennai Marina", 32, 6),
        ("Goa Coast", 78, 12),
        ("Kochi Backwaters", 105, 15)
    ]

    sample_ids = []

    for loc_name, total_orgs, species_count in locations:
        # Get preset location
        loc_data = location_mgr.get_location_preset(loc_name)

        # Create sample
        sample_data = {
            'sample_id': f'DEMO_{loc_name.replace(" ", "_").upper()}_{datetime.now().strftime("%H%M%S")}',
            'timestamp': datetime.now().isoformat(),
            **loc_data,
            'operator_id': 'demo_user',
            'session_id': 'DEMO_SESSION',
            'magnification': 2.5,
            'exposure_ms': 100,
            'total_organisms': total_orgs,
            'species_richness': species_count
        }

        sample_id = db.insert_sample(sample_data)
        sample_ids.append(sample_data['sample_id'])

        # Add some detections
        for i in range(min(total_orgs, 3)):  # Add up to 3 detections
            detection = {
                'organism_id': i + 1,
                'class_name': ['Copepod', 'Diatom', 'Dinoflagellate'][i % 3],
                'confidence': 0.85 + (i * 0.05),
                'bbox': [100 + i*50, 100 + i*50, 150 + i*50, 150 + i*50],
                'size_px': 50.0 + i * 10
            }
            db.insert_detection(sample_data['sample_id'], detection)

        print(f"   ✅ {loc_name}: {total_orgs} organisms, {species_count} species")

    print(f"\n2. Querying samples...")
    all_samples = db.get_all_samples_with_location()
    print(f"   📊 Total samples with location: {len(all_samples)}")

    # Query by bounding box (samples around Mumbai)
    print(f"\n3. Querying samples in Mumbai region...")
    mumbai_samples = db.get_samples_by_bbox(
        min_lat=18.8,
        max_lat=19.3,
        min_lon=72.6,
        max_lon=73.0
    )
    print(f"   📍 Samples in Mumbai bbox: {len(mumbai_samples)}")

    # Get species distribution
    print(f"\n4. Species distribution...")
    species_dist = db.get_species_distribution()
    for species, count in species_dist.items():
        print(f"   🧬 {species}: {count}")

    # Get statistics
    print(f"\n5. Database statistics...")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # Export to CSV
    print(f"\n6. Exporting to CSV...")
    csv_path = db.export_to_csv("exports/demo_samples.csv")
    print(f"   💾 Exported to: {csv_path}")

    return db, sample_ids


def demo_cloud_storage():
    """Demo: Firebase cloud storage (if configured)"""
    print("\n" + "="*80)
    print("DEMO 3: Cloud Storage (Firebase)")
    print("="*80)

    # Initialize Firebase
    firebase = FirebaseStorageManager()

    if not firebase.enabled:
        print("\n⚠️  Firebase not configured")
        print("   To enable Firebase:")
        print("   1. Copy config/firebase_config_template.json to config/firebase_config.json")
        print("   2. Add your Firebase credentials")
        print("   3. Install firebase-admin: pip install firebase-admin")
        print("\n   Skipping cloud storage demo...")
        return None

    print("\n✅ Firebase connected!")

    # Get storage stats
    print("\n1. Getting storage statistics...")
    stats = firebase.get_storage_stats()

    if 'error' not in stats:
        print(f"   📦 Bucket: {stats.get('bucket_name')}")
        print(f"   📁 Total files: {stats.get('total_files', 0)}")
        print(f"   💾 Total size: {stats.get('total_size_mb', 0):.2f} MB")

    # Note: We won't actually upload in demo mode to avoid cluttering storage
    print("\n2. Upload capabilities available:")
    print("   ✅ Upload images to Firebase Storage")
    print("   ✅ Upload videos to Firebase Storage")
    print("   ✅ Store metadata in Firestore")
    print("   ✅ Sync samples with local database")

    return firebase


def demo_map_visualization():
    """Demo: Creating interactive maps"""
    print("\n" + "="*80)
    print("DEMO 4: Interactive Map Visualization")
    print("="*80)

    # Get samples from database
    db = PlanktonDatabase("data/demo_plankton.db")
    samples = db.get_all_samples_with_location()

    if not samples:
        print("\n⚠️  No samples found. Run demo_database_operations() first.")
        return

    print(f"\n1. Creating map with {len(samples)} samples...")

    # Create map viewer
    viewer = PlanktonMapViewer()

    # Create map with clustering
    m = viewer.create_map_with_samples(
        samples,
        use_clustering=True,
        add_heatmap=False,
        auto_center=True
    )

    # Save map
    output_dir = Path("results/maps")
    output_dir.mkdir(parents=True, exist_ok=True)

    map_path = output_dir / "demo_plankton_map.html"
    viewer.save_map(m, str(map_path))

    print(f"   ✅ Map created!")
    print(f"   📍 Samples plotted: {len(samples)}")
    print(f"   💾 Saved to: {map_path}")

    # Create map with heatmap
    print(f"\n2. Creating map with heatmap...")
    m_heatmap = viewer.create_map_with_samples(
        samples,
        use_clustering=False,
        add_heatmap=True,
        auto_center=True
    )

    heatmap_path = output_dir / "demo_heatmap.html"
    viewer.save_map(m_heatmap, str(heatmap_path))

    print(f"   ✅ Heatmap created!")
    print(f"   💾 Saved to: {heatmap_path}")

    print(f"\n3. Map features:")
    print(f"   ✅ Click markers to view sample details")
    print(f"   ✅ Marker clustering for dense areas")
    print(f"   ✅ Heatmap showing sampling density")
    print(f"   ✅ Search and filter tools")
    print(f"   ✅ Measurement tools")
    print(f"   ✅ Drawing tools for region selection")
    print(f"   ✅ Multiple base map layers")
    print(f"   ✅ Fullscreen mode")

    print(f"\n🌐 Open the map files in your browser to interact with them!")

    return viewer


def demo_complete_workflow():
    """Demo: Complete workflow from sample to cloud to map"""
    print("\n" + "="*80)
    print("DEMO 5: Complete Workflow")
    print("="*80)

    print("\nThis demonstrates the complete workflow:")
    print("1. Capture location data")
    print("2. Store sample in database")
    print("3. Upload to cloud (if configured)")
    print("4. Visualize on map")
    print("5. Export filtered data")

    # Initialize components
    db = PlanktonDatabase("data/demo_plankton.db")
    location_mgr = LocationManager()
    location_mgr.create_default_presets()
    firebase = FirebaseStorageManager() if Path("config/firebase_config.json").exists() else None

    # 1. Create location
    print("\n1. Creating location...")
    location = location_mgr.get_location_preset("Mumbai Harbor")
    print(f"   ✅ Location: {location['location_name']}")

    # 2. Create sample
    print("\n2. Creating sample...")
    sample_id = f"WORKFLOW_DEMO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    sample_data = {
        'sample_id': sample_id,
        'timestamp': datetime.now().isoformat(),
        **location,
        'operator_id': 'demo_workflow',
        'total_organisms': 50,
        'species_richness': 10
    }

    db.insert_sample(sample_data)
    print(f"   ✅ Sample created: {sample_id}")

    # 3. Upload to cloud
    if firebase and firebase.enabled:
        print("\n3. Uploading to cloud...")
        success = firebase.upload_sample_data(sample_id, sample_data)

        if success:
            db.mark_firebase_uploaded(sample_id)
            print(f"   ✅ Uploaded to Firebase")
    else:
        print("\n3. Skipping cloud upload (Firebase not configured)")

    # 4. Create map
    print("\n4. Creating map...")
    samples = db.get_all_samples_with_location()
    m = create_quick_map(samples, "results/maps/workflow_demo.html")
    print(f"   ✅ Map created with {len(samples)} samples")

    # 5. Export data
    print("\n5. Exporting data...")
    csv_path = db.export_to_csv("exports/workflow_demo.csv")
    print(f"   ✅ Exported to: {csv_path}")

    print("\n✅ Workflow complete!")


def main():
    """Run all demos"""
    print("\n" + "="*80)
    print("PLANKTON DETECTION - CLOUD & MAP INTEGRATION DEMO")
    print("="*80)

    print("\nThis demo will showcase:")
    print("  📍 Location/GPS management")
    print("  🗄️ SQLite database with location support")
    print("  ☁️ Firebase cloud storage")
    print("  🗺️ Interactive Folium maps")
    print("  💾 CSV exports with location filtering")

    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("exports").mkdir(exist_ok=True)
    Path("results/maps").mkdir(parents=True, exist_ok=True)
    Path("config").mkdir(exist_ok=True)

    try:
        # Run demos
        demo_location_management()
        demo_database_operations()
        demo_cloud_storage()
        demo_map_visualization()
        demo_complete_workflow()

        print("\n" + "="*80)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)

        print("\n📂 Check these locations for results:")
        print("  📊 Database: data/demo_plankton.db")
        print("  🗺️ Maps: results/maps/")
        print("  💾 Exports: exports/")
        print("  ⚙️ Config: config/")

        print("\n🚀 Next Steps:")
        print("  1. Open results/maps/*.html in your browser to view interactive maps")
        print("  2. Run the standalone map viewer: streamlit run map_viewer_app.py")
        print("  3. Configure Firebase (see CLOUD_MAP_INTEGRATION_GUIDE.md)")
        print("  4. Integrate into your existing pipeline")

        print("\n📖 For detailed documentation, see:")
        print("   CLOUD_MAP_INTEGRATION_GUIDE.md")

    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\nCheck the logs for details")


if __name__ == "__main__":
    main()

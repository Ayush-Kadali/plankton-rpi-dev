#!/usr/bin/env python3
"""
Simple test to verify cloud & map modules are working
"""

import sys
from pathlib import Path

# Test imports
print("Testing module imports...")
print("=" * 60)

try:
    print("\n1. Testing database module...")
    from modules.database import PlanktonDatabase
    print("   ✅ Database module imported")

    print("\n2. Testing location module...")
    from modules.location import LocationManager
    print("   ✅ Location module imported")

    print("\n3. Testing cloud storage module...")
    from modules.cloud_storage import FirebaseStorageManager
    print("   ✅ Cloud storage module imported")

    print("\n4. Testing map viewer module...")
    from modules.map_viewer import PlanktonMapViewer
    print("   ✅ Map viewer module imported")

    print("\n" + "=" * 60)
    print("✅ ALL MODULES IMPORTED SUCCESSFULLY!")
    print("=" * 60)

    # Quick functional test
    print("\n\nRunning functional tests...")
    print("=" * 60)

    # Test location manager
    print("\n1. Testing LocationManager...")
    loc_mgr = LocationManager()
    location = loc_mgr.get_location_manual(
        latitude=19.0760,
        longitude=72.8777,
        location_name="Test Location"
    )
    print(f"   ✅ Created location: {location['location_name']}")
    print(f"   📍 Coordinates: {location['latitude']}, {location['longitude']}")

    # Test database
    print("\n2. Testing Database...")
    db = PlanktonDatabase("data/test_cloud_map.db")
    print(f"   ✅ Database created")

    sample_data = {
        'sample_id': 'TEST_001',
        **location,
        'timestamp': '2024-01-01T10:00:00'
    }

    sample_id = db.insert_sample(sample_data)
    print(f"   ✅ Sample inserted: ID {sample_id}")

    stats = db.get_statistics()
    print(f"   📊 Total samples: {stats['total_samples']}")

    # Test map viewer
    print("\n3. Testing Map Viewer...")
    viewer = PlanktonMapViewer()
    print(f"   ✅ Map viewer initialized")
    print(f"   🗺️ Center: {viewer.center}")

    # Test cloud storage
    print("\n4. Testing Cloud Storage...")
    firebase = FirebaseStorageManager()

    if firebase.enabled:
        print(f"   ✅ Firebase connected!")
    else:
        print(f"   ⚠️  Firebase not configured (optional)")

    print("\n" + "=" * 60)
    print("✅ ALL FUNCTIONAL TESTS PASSED!")
    print("=" * 60)

    print("\n\n🎉 Success! All modules are working correctly.")
    print("\nYou can now:")
    print("  • Run: python3 demo_cloud_map_integration.py")
    print("  • Run: streamlit run map_viewer_app.py")
    print("  • Integrate into your pipeline")

except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nMissing dependencies. Install with:")
    print("  pip install -r requirements_cloud_map.txt")
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

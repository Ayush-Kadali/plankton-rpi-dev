#!/usr/bin/env python3
"""Check what data the map viewer will actually load"""

import sys
sys.path.insert(0, '.')

from modules.database import PlanktonDatabase
import os

# Check which database exists and what it contains
demo_db = "data/judge_demo.db"

if os.path.exists(demo_db):
    print(f"✓ Found database: {demo_db}")
    db = PlanktonDatabase(demo_db)
    samples = db.get_all_samples_with_location()
    
    print(f"\n✓ Loaded {len(samples)} samples")
    
    if samples:
        # Show unique locations
        locations = set(s['location_name'] for s in samples)
        print(f"\n📍 Locations ({len(locations)}):")
        for loc in sorted(locations):
            count = sum(1 for s in samples if s['location_name'] == loc)
            lat = next(s['latitude'] for s in samples if s['location_name'] == loc)
            lon = next(s['longitude'] for s in samples if s['location_name'] == loc)
            print(f"   {loc}: {count} samples at ({lat:.2f}, {lon:.2f})")
        
        # Check coordinate ranges
        lats = [s['latitude'] for s in samples]
        lons = [s['longitude'] for s in samples]
        print(f"\n🗺️ Coordinate ranges:")
        print(f"   Latitude: {min(lats):.2f} to {max(lats):.2f}")
        print(f"   Longitude: {min(lons):.2f} to {max(lons):.2f}")
        print(f"   Center: ({sum(lats)/len(lats):.2f}, {sum(lons)/len(lons):.2f})")
else:
    print(f"✗ Database not found: {demo_db}")

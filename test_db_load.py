#!/usr/bin/env python3
"""Quick test to verify database loading"""

from modules.database import PlanktonDatabase

print("Testing database loading...")
db = PlanktonDatabase("data/judge_demo.db")

samples = db.get_all_samples_with_location()

print(f"\n✓ Loaded {len(samples)} samples")

if samples:
    # Check first sample
    sample = samples[0]
    print(f"\nSample example:")
    print(f"  Location: {sample.get('location_name')}")
    print(f"  Organisms: {sample.get('total_organisms', 'MISSING!')}")
    print(f"  Species: {sample.get('species_richness', 'MISSING!')}")
    print(f"  Lat/Lon: {sample.get('latitude')}, {sample.get('longitude')}")
    
    # Count by density
    gray = sum(1 for s in samples if s.get('total_organisms', 0) == 0)
    green = sum(1 for s in samples if 1 <= s.get('total_organisms', 0) < 10)
    blue = sum(1 for s in samples if 10 <= s.get('total_organisms', 0) < 50)
    orange = sum(1 for s in samples if 50 <= s.get('total_organisms', 0) < 100)
    red = sum(1 for s in samples if s.get('total_organisms', 0) >= 100)
    
    print(f"\nMarker color distribution:")
    print(f"  Gray (0): {gray}")
    print(f"  Green (1-9): {green}")
    print(f"  Blue (10-49): {blue}")
    print(f"  Orange (50-99): {orange}")
    print(f"  Red (100+): {red}")
    
    print(f"\n✓ Database is ready for map viewer!")
else:
    print("✗ No samples found!")

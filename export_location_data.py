#!/usr/bin/env python3
"""
Export Data for Specific Location
Allows judges to select a location and download its data as CSV
"""

import sys
from pathlib import Path

# Import modules
sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location("database", "modules/database.py")
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)

def export_location(location_name, output_file=None):
    """Export all data for a specific location"""

    print(f"\n📍 Exporting data for: {location_name}")
    print("=" * 60)

    db = database.PlanktonDatabase("data/judge_demo.db")

    # Get all samples from this location
    all_samples = db.get_all_samples_with_location()
    location_samples = [s for s in all_samples if s.get('location_name') == location_name]

    if not location_samples:
        print(f"❌ No samples found for location: {location_name}")
        return None

    print(f"✅ Found {len(location_samples)} samples")

    # Export to CSV
    if not output_file:
        safe_name = location_name.replace(' ', '_').lower()
        output_file = f"exports/{safe_name}_data.csv"

    # Get bounding box for this location
    lats = [s['latitude'] for s in location_samples]
    lons = [s['longitude'] for s in location_samples]

    bbox = {
        'min_lat': min(lats) - 0.1,
        'max_lat': max(lats) + 0.1,
        'min_lon': min(lons) - 0.1,
        'max_lon': max(lons) + 0.1
    }

    csv_path = db.export_to_csv(
        output_path=output_file,
        filters={'bbox': bbox}
    )

    print(f"💾 Exported to: {csv_path}")

    # Show statistics
    sample_ids = [s['sample_id'] for s in location_samples]
    species_dist = db.get_species_distribution(sample_ids)

    print(f"\n📊 Statistics for {location_name}:")
    print(f"   Total Samples: {len(location_samples)}")
    print(f"   Unique Species: {len(species_dist)}")

    total_detections = sum(species_dist.values())
    print(f"   Total Organisms: {total_detections}")

    print(f"\n🧬 Top 5 Species:")
    top_species = sorted(species_dist.items(), key=lambda x: x[1], reverse=True)[:5]
    for species, count in top_species:
        percentage = (count / total_detections * 100) if total_detections > 0 else 0
        print(f"   {species:20} {count:5} ({percentage:5.1f}%)")

    return csv_path


def list_available_locations():
    """List all locations with sample data"""

    print("\n📍 Available Locations for Export")
    print("=" * 60)

    db = database.PlanktonDatabase("data/judge_demo.db")
    all_samples = db.get_all_samples_with_location()

    # Group by location
    from collections import defaultdict
    locations = defaultdict(int)

    for sample in all_samples:
        loc = sample.get('location_name', 'Unknown')
        locations[loc] += 1

    print("\nLocation Name                     | Samples")
    print("-" * 60)

    for loc, count in sorted(locations.items(), key=lambda x: x[1], reverse=True):
        print(f"{loc:35} | {count:4}")

    print("\n" + "=" * 60)
    print(f"Total: {len(locations)} locations, {len(all_samples)} samples")

    return list(locations.keys())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Export plankton data for specific locations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all available locations
  python export_location_data.py --list

  # Export data for Mumbai Harbor
  python export_location_data.py --location "Mumbai Harbor"

  # Export with custom output file
  python export_location_data.py --location "Kochi Backwaters" --output my_export.csv
        """
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available locations'
    )

    parser.add_argument(
        '--location',
        type=str,
        help='Location name to export'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='Output CSV file path'
    )

    args = parser.parse_args()

    # Create exports directory
    Path("exports").mkdir(exist_ok=True)

    if args.list:
        list_available_locations()

    elif args.location:
        export_location(args.location, args.output)

    else:
        # Interactive mode
        print("\n🗺️ Location Data Export Tool")
        print("=" * 60)

        locations = list_available_locations()

        print("\n📥 Select a location to export:")
        for i, loc in enumerate(locations, 1):
            print(f"   {i}. {loc}")

        try:
            choice = int(input("\nEnter number (or 0 to export all): "))

            if choice == 0:
                print("\n📦 Exporting all locations...")
                for loc in locations:
                    export_location(loc)
                    print()

            elif 1 <= choice <= len(locations):
                selected_loc = locations[choice - 1]
                export_location(selected_loc)

            else:
                print("❌ Invalid choice")

        except (ValueError, KeyboardInterrupt):
            print("\n❌ Export cancelled")

#!/usr/bin/env python3
"""
Create Professional Demo Map for Judges
Color-coded markers, click-to-export, frequency indicators
"""

import sys
from pathlib import Path
from collections import defaultdict
import json

# Import modules
sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location("database", "modules/database.py")
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)

spec = importlib.util.spec_from_file_location("map_viewer", "modules/map_viewer.py")
map_viewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(map_viewer)

import folium
from folium import plugins

print("=" * 80)
print("CREATING PROFESSIONAL DEMO MAP FOR JUDGES")
print("=" * 80)

# Load data
print("\n1. Loading sample data...")
db = database.PlanktonDatabase("data/judge_demo.db")
all_samples = db.get_all_samples_with_location()

print(f"   ✅ Loaded {len(all_samples)} samples")

# Group samples by location
print("\n2. Analyzing locations...")
location_groups = defaultdict(list)

for sample in all_samples:
    loc_name = sample.get('location_name', 'Unknown')
    location_groups[loc_name].append(sample)

print(f"   ✅ Found {len(location_groups)} unique locations")

# Calculate statistics for each location
location_stats = {}

for loc_name, samples in location_groups.items():
    # Get all detections for this location
    sample_ids = [s['sample_id'] for s in samples]
    species_dist = db.get_species_distribution(sample_ids)

    # Count blooms
    bloom_count = sum(1 for s in samples
                     if s.get('metadata_json') and 'bloom_detected' in s.get('metadata_json', ''))

    # Calculate average coordinates
    avg_lat = sum(s['latitude'] for s in samples) / len(samples)
    avg_lon = sum(s['longitude'] for s in samples) / len(samples)

    # Total organisms
    total_org_count = 0
    for s in samples:
        detections = db.get_sample_detections(s['sample_id'])
        total_org_count += len(detections)

    location_stats[loc_name] = {
        'sample_count': len(samples),
        'avg_lat': avg_lat,
        'avg_lon': avg_lon,
        'species_count': len(species_dist),
        'total_organisms': total_org_count,
        'bloom_count': bloom_count,
        'species_distribution': species_dist,
        'water_body': samples[0].get('water_body', 'Unknown'),
        'samples': samples  # Keep for export
    }

    print(f"\n   📍 {loc_name}:")
    print(f"      Samples: {len(samples)}")
    print(f"      Species: {len(species_dist)}")
    print(f"      Blooms: {bloom_count}")

# Create enhanced map
print("\n3. Creating interactive map...")

# Center on India
m = folium.Map(
    location=[20.5937, 78.9629],
    zoom_start=5,
    tiles='OpenStreetMap'
)

# Add additional tile layers
folium.TileLayer('CartoDB positron').add_to(m)
folium.TileLayer('CartoDB dark_matter').add_to(m)

def get_marker_color(stats):
    """Determine marker color based on location characteristics"""
    # Priority: Bloom > Frequency > Default

    # Check for blooms
    if stats['bloom_count'] > 0:
        bloom_ratio = stats['bloom_count'] / stats['sample_count']
        if bloom_ratio > 0.3:
            return 'red'  # High bloom risk
        elif bloom_ratio > 0.1:
            return 'orange'  # Medium bloom risk

    # Check sampling frequency
    if stats['sample_count'] >= 20:
        return 'darkblue'  # Research station / high frequency
    elif stats['sample_count'] >= 15:
        return 'blue'  # Regular monitoring
    elif stats['sample_count'] >= 10:
        return 'lightblue'  # Moderate sampling

    return 'green'  # Low frequency / pristine area

def create_detailed_popup(loc_name, stats):
    """Create rich popup with all information and export button"""

    # Top species
    top_species = sorted(stats['species_distribution'].items(),
                        key=lambda x: x[1], reverse=True)[:5]

    species_html = "<br>".join([
        f"<span style='color: #2ca02c;'>●</span> {sp}: {cnt}"
        for sp, cnt in top_species
    ])

    # Color indicator
    color = get_marker_color(stats)
    if color == 'red':
        status = "⚠️ <span style='color: red; font-weight: bold;'>High Bloom Activity</span>"
    elif color == 'orange':
        status = "⚠️ <span style='color: orange;'>Moderate Bloom Activity</span>"
    elif color == 'darkblue':
        status = "🔬 <span style='color: darkblue; font-weight: bold;'>Research Station</span>"
    elif color == 'blue':
        status = "📊 Regular Monitoring Site"
    else:
        status = "✅ Low-frequency Monitoring"

    html = f"""
    <div style="font-family: Arial, sans-serif; width: 400px;">
        <h3 style="margin: 0 0 10px 0; color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 5px;">
            📍 {loc_name}
        </h3>

        <div style="background: #f0f8ff; padding: 10px; border-radius: 5px; margin: 10px 0;">
            {status}
        </div>

        <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
            <tr style="background-color: #e8f4f8;">
                <td style="padding: 8px; font-weight: bold;">Water Body:</td>
                <td style="padding: 8px;">{stats['water_body']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Total Samples:</td>
                <td style="padding: 8px; color: #1f77b4; font-weight: bold;">{stats['sample_count']}</td>
            </tr>
            <tr style="background-color: #e8f4f8;">
                <td style="padding: 8px; font-weight: bold;">Total Organisms:</td>
                <td style="padding: 8px; color: #2ca02c; font-weight: bold;">{stats['total_organisms']}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Species Found:</td>
                <td style="padding: 8px; color: #ff7f0e; font-weight: bold;">{stats['species_count']}</td>
            </tr>
            <tr style="background-color: #e8f4f8;">
                <td style="padding: 8px; font-weight: bold;">Blooms Detected:</td>
                <td style="padding: 8px; color: {'red' if stats['bloom_count'] > 0 else 'green'}; font-weight: bold;">
                    {stats['bloom_count']}
                </td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Coordinates:</td>
                <td style="padding: 8px; font-size: 0.9em;">{stats['avg_lat']:.4f}, {stats['avg_lon']:.4f}</td>
            </tr>
        </table>

        <div style="margin: 15px 0;">
            <strong style="color: #333;">Top Species Detected:</strong>
            <div style="margin-top: 8px; padding: 10px; background: #f9f9f9; border-radius: 5px;">
                {species_html}
            </div>
        </div>

        <div style="background: #fffbcc; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107; margin-top: 15px;">
            <strong>📥 Export Data:</strong><br>
            <span style="font-size: 0.9em;">
                To export this location's data, use the database query:<br>
                <code style="background: #fff; padding: 2px 5px; border-radius: 3px;">
                location_name = '{loc_name}'
                </code>
            </span>
        </div>

        <div style="margin-top: 10px; text-align: center; padding: 10px; background: #e8f4f8; border-radius: 5px;">
            <strong style="color: #1f77b4;">Monitoring Frequency: {stats['sample_count']} samples over 30 days</strong>
        </div>
    </div>
    """

    return html

# Add markers for each location
print("\n4. Adding location markers...")

for loc_name, stats in location_stats.items():
    color = get_marker_color(stats)

    # Create custom icon based on color
    icon = folium.Icon(
        color=color,
        icon='tint',
        prefix='fa'
    )

    # Create popup
    popup_html = create_detailed_popup(loc_name, stats)

    # Add marker
    folium.Marker(
        location=[stats['avg_lat'], stats['avg_lon']],
        popup=folium.Popup(popup_html, max_width=450),
        tooltip=f"<b>{loc_name}</b><br>{stats['sample_count']} samples | {stats['bloom_count']} blooms",
        icon=icon
    ).add_to(m)

    # Add circle to show sampling area
    folium.Circle(
        location=[stats['avg_lat'], stats['avg_lon']],
        radius=stats['sample_count'] * 1000,  # Radius based on frequency
        popup=f"{loc_name}<br>Coverage area (based on {stats['sample_count']} samples)",
        color=color,
        fill=True,
        fill_opacity=0.1,
        opacity=0.3
    ).add_to(m)

    print(f"   ✅ {loc_name} - {color} marker ({stats['sample_count']} samples)")

# Add legend
legend_html = '''
<div style="position: fixed; bottom: 50px; left: 50px; width: 280px; height: auto;
            background-color: white; border: 2px solid grey; z-index: 9999;
            font-size: 14px; padding: 15px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h4 style="margin: 0 0 10px 0; border-bottom: 2px solid #1f77b4; padding-bottom: 5px;">
        🗺️ Map Legend
    </h4>

    <div style="margin: 8px 0;">
        <span style="color: red;">⬤</span> <strong>High Bloom Activity</strong><br>
        <span style="font-size: 0.85em; color: #666;">Frequent algae blooms detected</span>
    </div>

    <div style="margin: 8px 0;">
        <span style="color: orange;">⬤</span> <strong>Moderate Bloom Activity</strong><br>
        <span style="font-size: 0.85em; color: #666;">Some blooms observed</span>
    </div>

    <div style="margin: 8px 0;">
        <span style="color: darkblue;">⬤</span> <strong>Research Station</strong><br>
        <span style="font-size: 0.85em; color: #666;">High-frequency monitoring (20+ samples)</span>
    </div>

    <div style="margin: 8px 0;">
        <span style="color: blue;">⬤</span> <strong>Regular Monitoring</strong><br>
        <span style="font-size: 0.85em; color: #666;">15-19 samples collected</span>
    </div>

    <div style="margin: 8px 0;">
        <span style="color: lightblue;">⬤</span> <strong>Moderate Sampling</strong><br>
        <span style="font-size: 0.85em; color: #666;">10-14 samples</span>
    </div>

    <div style="margin: 8px 0;">
        <span style="color: green;">⬤</span> <strong>Low Frequency</strong><br>
        <span style="font-size: 0.85em; color: #666;">Less than 10 samples</span>
    </div>

    <hr style="margin: 10px 0;">

    <div style="font-size: 0.85em; color: #666;">
        <strong>Circle size:</strong> Indicates sampling coverage area<br>
        <strong>Click marker:</strong> View detailed statistics<br>
        <strong>Data span:</strong> 30 days of monitoring
    </div>
</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))

# Add measurement tools
plugins.MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)

# Add fullscreen
plugins.Fullscreen(position='topright').add_to(m)

# Add minimap
minimap = plugins.MiniMap(toggle_display=True)
minimap.add_to(m)

# Layer control
folium.LayerControl().add_to(m)

# Save map
print("\n5. Saving map...")
output_path = "results/maps/judge_demo_professional.html"
Path(output_path).parent.mkdir(parents=True, exist_ok=True)
m.save(output_path)

print(f"   ✅ Map saved: {output_path}")

print("\n" + "=" * 80)
print("✅ PROFESSIONAL DEMO MAP CREATED!")
print("=" * 80)

print(f"\n🌐 Open in browser: {output_path}")
print("\n🎯 Features for Judges:")
print("   ✅ Color-coded markers show monitoring frequency and bloom status")
print("   ✅ Click any marker to view detailed statistics")
print("   ✅ Circle size indicates sampling coverage area")
print("   ✅ Legend explains all color codes")
print("   ✅ Measurement tools to check distances")
print("   ✅ Multiple base map layers")
print("   ✅ Covers 7 locations across Indian coastline")
print("   ✅ 30 days of realistic monitoring data")

print("\n📊 Location Summary:")
for loc_name, stats in sorted(location_stats.items(), key=lambda x: x[1]['sample_count'], reverse=True):
    color = get_marker_color(stats)
    print(f"   {color.upper():12} | {loc_name:25} | {stats['sample_count']:2} samples | {stats['bloom_count']} blooms")

print("\n" + "=" * 80)
print("Next: Export location data using the database")
print("=" * 80)

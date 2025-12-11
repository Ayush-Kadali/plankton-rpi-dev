#!/usr/bin/env python3
"""
LOCAL MAP VIEWER
View plankton detection data on an interactive map
No cloud required - pure local visualization!
"""

import folium
from folium import plugins
import json
from pathlib import Path
from datetime import datetime
import webbrowser

# Default locations (can be customized)
DEFAULT_LOCATIONS = {
    "Lab Test 1": {"lat": 19.0760, "lon": 72.8777, "name": "Mumbai Lab"},
    "Field Site A": {"lat": 15.2993, "lon": 74.1240, "name": "Goa Coast"},
    "Field Site B": {"lat": 11.9416, "lon": 79.8083, "name": "Puducherry"},
}

def load_session_data(data_dir="demo_output"):
    """Load all session JSON files"""
    data_dir = Path(data_dir)
    if not data_dir.exists():
        print(f"No data directory found: {data_dir}")
        return []

    sessions = []
    for json_file in data_dir.glob("session_*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)
                data["file"] = json_file.name
                sessions.append(data)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")

    return sessions

def create_map(sessions, output_file="map.html", center_lat=15.0, center_lon=77.0):
    """Create interactive map with session data"""

    if not sessions:
        print("No session data to display!")
        return False

    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=5,
        tiles='OpenStreetMap'
    )

    # Add title
    title_html = '''
    <div style="position: fixed;
                top: 10px; left: 50px; width: 400px; height: 90px;
                background-color: white; border:2px solid grey; z-index:9999;
                font-size:16px; padding: 10px">
        <h3 style="margin:0">🔬 Plankton Detection Map</h3>
        <p style="margin:5px 0"><b>Sessions:</b> {}</p>
        <p style="margin:5px 0"><b>Total Detections:</b> {}</p>
    </div>
    '''.format(
        len(sessions),
        sum(s.get('total_detections', 0) for s in sessions)
    )
    m.get_root().html.add_child(folium.Element(title_html))

    # Add markers for each session
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred',
              'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple',
              'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

    for i, session in enumerate(sessions):
        # Use default location (rotate through them) or allow custom
        loc_keys = list(DEFAULT_LOCATIONS.keys())
        loc_key = loc_keys[i % len(loc_keys)]
        location = DEFAULT_LOCATIONS[loc_key]

        # Prepare popup content
        species_html = "<br>".join([
            f"{name}: {count}"
            for name, count in session.get('species_counts', {}).items()
            if count > 0
        ])

        start_time = session.get('start_time', 'Unknown')
        if start_time != 'Unknown':
            try:
                dt = datetime.fromisoformat(start_time)
                start_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass

        popup_html = f"""
        <div style="width:250px">
            <h4>{location['name']}</h4>
            <p><b>Session:</b> {session.get('file', 'Unknown')}</p>
            <p><b>Time:</b> {start_time}</p>
            <p><b>Duration:</b> {session.get('duration_seconds', 0):.1f}s</p>
            <p><b>Frames:</b> {session.get('frames_processed', 0)}</p>
            <p><b>Total Detections:</b> {session.get('total_detections', 0)}</p>
            <hr>
            <p><b>Species:</b></p>
            {species_html}
        </div>
        """

        # Add marker
        folium.Marker(
            location=[location['lat'], location['lon']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{location['name']} - {session.get('total_detections', 0)} detections",
            icon=folium.Icon(color=colors[i % len(colors)], icon='tint', prefix='fa')
        ).add_to(m)

        # Add circle to show detection intensity
        folium.Circle(
            location=[location['lat'], location['lon']],
            radius=session.get('total_detections', 0) * 100,  # Scale radius by detections
            color=colors[i % len(colors)],
            fill=True,
            fillOpacity=0.3,
            popup=f"{session.get('total_detections', 0)} detections"
        ).add_to(m)

    # Add layer control
    folium.LayerControl().add_to(m)

    # Save map
    m.save(output_file)
    print(f"\n✅ Map created: {output_file}")
    return True

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='View plankton detection data on map',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create map from demo_output folder
  python MAP_VIEWER.py

  # Specify custom data directory
  python MAP_VIEWER.py --data my_data/

  # Custom output file
  python MAP_VIEWER.py --output results/my_map.html

  # Auto-open in browser
  python MAP_VIEWER.py --open
        """
    )

    parser.add_argument('--data', default='demo_output',
                       help='Directory containing session JSON files')
    parser.add_argument('--output', default='map.html',
                       help='Output HTML file')
    parser.add_argument('--open', action='store_true',
                       help='Open map in browser after creating')

    args = parser.parse_args()

    print("=" * 80)
    print("🗺️  PLANKTON DETECTION MAP VIEWER")
    print("=" * 80)

    # Load data
    print(f"\n📂 Loading data from: {args.data}")
    sessions = load_session_data(args.data)

    if not sessions:
        print("\n❌ No session data found!")
        print(f"   Run DEMO.py first to generate detection data")
        return

    print(f"✅ Loaded {len(sessions)} session(s)")

    # Show summary
    total_detections = sum(s.get('total_detections', 0) for s in sessions)
    total_frames = sum(s.get('frames_processed', 0) for s in sessions)

    print(f"\n📊 Summary:")
    print(f"   Total frames: {total_frames}")
    print(f"   Total detections: {total_detections}")

    # Create map
    print(f"\n🗺️  Creating map...")
    success = create_map(sessions, args.output)

    if success and args.open:
        print(f"\n🌐 Opening in browser...")
        webbrowser.open(args.output)

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

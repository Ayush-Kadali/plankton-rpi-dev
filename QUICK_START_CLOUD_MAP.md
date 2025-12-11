# 🚀 Quick Start: Cloud & Map Integration

Get up and running with cloud storage and interactive maps in 5 minutes!

## ⚡ Installation

```bash
# Install new dependencies
pip install -r requirements_cloud_map.txt

# This installs:
# - firebase-admin (for cloud storage)
# - folium (for interactive maps)
# - Additional utilities
```

## 🎯 Option 1: Run the Demo (Fastest!)

```bash
# Run the comprehensive demo
python demo_cloud_map_integration.py
```

This will:
- ✅ Create sample location data
- ✅ Set up database with GPS coordinates
- ✅ Generate interactive maps
- ✅ Show you all the features

**After running**, open these files in your browser:
- `results/maps/demo_plankton_map.html` - Interactive map with markers
- `results/maps/demo_heatmap.html` - Heatmap showing sampling density

## 🎨 Option 2: Run the Map Viewer App

```bash
# Launch the standalone map viewer
streamlit run map_viewer_app.py
```

Then:
1. Click "🔄 Refresh Data" to load samples
2. Use filters to narrow down samples
3. Click map markers to view details
4. Export filtered data as CSV

## 🔧 Option 3: Add to Your Existing Code

### Step 1: Add Location to Your Samples

```python
from modules.database import PlanktonDatabase
from modules.location import LocationManager
from datetime import datetime

# Initialize
db = PlanktonDatabase()
location_mgr = LocationManager()

# Create default locations (Mumbai, Chennai, Goa, etc.)
location_mgr.create_default_presets()

# Option A: Use a preset location
location = location_mgr.get_location_preset("Mumbai Harbor")

# Option B: Enter coordinates manually
location = location_mgr.get_location_manual(
    latitude=19.0760,
    longitude=72.8777,
    location_name="My Sampling Site",
    water_body="Arabian Sea",
    depth_meters=5.0
)

# Create sample with location
sample_data = {
    'sample_id': f'SAMPLE_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
    'timestamp': datetime.now().isoformat(),
    **location,  # Add all location fields
    'operator_id': 'your_name',
    'total_organisms': 45,
    'species_richness': 8
}

# Save to database
db.insert_sample(sample_data)
```

### Step 2: View on Map

```python
from modules.map_viewer import create_quick_map

# Get all samples with location
samples = db.get_all_samples_with_location()

# Create interactive map
m = create_quick_map(samples, "results/my_map.html")

print(f"Map created! Open results/my_map.html in your browser")
```

### Step 3: Export Data

```python
# Export all samples to CSV
csv_path = db.export_to_csv("exports/all_samples.csv")

# Export samples in a specific area (e.g., Mumbai region)
csv_path = db.export_to_csv(
    "exports/mumbai_samples.csv",
    filters={
        'bbox': {
            'min_lat': 18.8,
            'max_lat': 19.3,
            'min_lon': 72.6,
            'max_lon': 73.0
        }
    }
)
```

## ☁️ Optional: Enable Firebase Cloud Storage

If you want automatic cloud backup:

### 1. Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click "Add Project"
3. Name it (e.g., "plankton-detection")
4. Create project

### 2. Enable Services

1. Click "Storage" → "Get Started"
2. Click "Firestore Database" → "Create database"

### 3. Download Credentials

1. Go to Project Settings (gear icon)
2. Select "Service accounts" tab
3. Click "Generate new private key"
4. Save the JSON file

### 4. Configure

```bash
# Copy template
cp config/firebase_config_template.json config/firebase_config.json

# Edit config/firebase_config.json and paste your credentials

# Add to .gitignore (important!)
echo "config/firebase_config.json" >> .gitignore
```

### 5. Use Cloud Storage

```python
from modules.cloud_storage import FirebaseStorageManager

firebase = FirebaseStorageManager()

if firebase.enabled:
    # Upload sample to cloud
    result = firebase.sync_sample(
        sample_id=sample_data['sample_id'],
        sample_data=sample_data,
        image_path='path/to/image.jpg'
    )

    print(f"Uploaded to cloud: {result['image_url']}")
```

## 📍 Preset Locations (Indian Coastal Sites)

The system comes with these preset locations:

- **Mumbai Harbor** (Arabian Sea)
- **Chennai Marina** (Bay of Bengal)
- **Kochi Backwaters** (Vembanad Lake)
- **Goa Coast** (Arabian Sea)
- **Visakhapatnam Port** (Bay of Bengal)
- **Gulf of Mannar** (Marine biodiversity hotspot)
- **Sundarbans** (Ganges Delta)
- **Laboratory Test** (For lab samples)

Add your own in `config/preset_locations.json`!

## 🗺️ Map Features

Your interactive maps include:

✅ **Click Markers** - View sample details in popup
✅ **Clustering** - Automatic grouping of nearby samples
✅ **Heatmap** - Visualize sampling density
✅ **Search** - Find specific locations
✅ **Filters** - By date, location, organism count
✅ **Drawing Tools** - Select regions for analysis
✅ **Measurement Tools** - Measure distances
✅ **Multiple Base Maps** - OpenStreetMap, Terrain, etc.
✅ **Fullscreen Mode** - For presentations

## 📊 What Each Module Does

| Module | Purpose | Key Functions |
|--------|---------|--------------|
| `modules/database.py` | SQLite database with GPS | `insert_sample()`, `get_all_samples_with_location()`, `export_to_csv()` |
| `modules/location.py` | GPS/location management | `get_location_manual()`, `get_location_preset()`, `calculate_distance()` |
| `modules/cloud_storage.py` | Firebase integration | `upload_image()`, `sync_sample()`, `get_samples_by_location()` |
| `modules/map_viewer.py` | Interactive maps | `create_map_with_samples()`, `save_map()` |
| `map_viewer_app.py` | Standalone map viewer | Run with `streamlit run` |
| `demo_cloud_map_integration.py` | Complete demo | Run to see everything in action |

## 🎓 Learning Path

1. **Start Here**: Run `python demo_cloud_map_integration.py`
2. **Explore**: Open the generated maps in your browser
3. **Try the App**: Run `streamlit run map_viewer_app.py`
4. **Integrate**: Add location tracking to your existing pipeline
5. **Go Cloud**: Configure Firebase for automatic backups
6. **Advanced**: Read `CLOUD_MAP_INTEGRATION_GUIDE.md` for details

## 🆘 Common Issues

### "No samples to display"
**Fix**: Run the demo first to create sample data, or add location data to your existing samples.

### "Firebase not configured"
**Fix**: This is optional! The system works fine without Firebase. Only set it up if you need cloud backup.

### "Map not showing markers"
**Fix**: Make sure samples have `latitude` and `longitude` fields. Check with:
```python
samples = db.get_all_samples_with_location()
print(f"Found {len(samples)} samples with location")
```

### "ModuleNotFoundError"
**Fix**: Install dependencies:
```bash
pip install -r requirements_cloud_map.txt
```

## ✅ Verify Installation

```python
# Quick test
python -c "
from modules.database import PlanktonDatabase
from modules.location import LocationManager
from modules.map_viewer import PlanktonMapViewer

print('✅ All modules imported successfully!')
"
```

## 🎉 You're Ready!

Now you can:
- ✅ Track GPS coordinates for all samples
- ✅ Store everything in a local database
- ✅ Visualize samples on interactive maps
- ✅ Filter and export by location
- ✅ (Optional) Backup to Firebase cloud

**Next**: Check out the full guide at `CLOUD_MAP_INTEGRATION_GUIDE.md`

Happy mapping! 🗺️🔬

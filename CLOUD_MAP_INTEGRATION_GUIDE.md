# 🗺️ Cloud & Map Integration Guide

Complete guide for the integrated cloud storage and interactive map visualization system for plankton detection.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Setup Instructions](#setup-instructions)
4. [Usage Examples](#usage-examples)
5. [Dashboard Integration](#dashboard-integration)
6. [API Reference](#api-reference)

---

## 🎯 Overview

This integration adds comprehensive cloud storage and geographic visualization capabilities to your plankton detection system:

- **Cloud Storage**: Automatic upload of images, videos, and metadata to Firebase
- **Database**: Local SQLite database with full location/GPS support
- **Interactive Maps**: Folium-based map viewer with filtering and search
- **CSV Export**: Location-aware data exports
- **Real-time Sync**: Automatic synchronization between local and cloud storage

---

## ✨ Features

### 🌐 Cloud Storage (Firebase)
- ✅ Upload images and videos to Firebase Storage
- ✅ Store sample metadata in Firestore
- ✅ Public or private file access
- ✅ Automatic URL generation
- ✅ Bandwidth-efficient uploads

### 🗄️ Database (SQLite)
- ✅ Comprehensive schema for samples, detections, sessions
- ✅ Full GPS/location support
- ✅ Efficient queries and indexing
- ✅ Export to CSV/JSON
- ✅ Cloud sync tracking

### 🗺️ Interactive Maps
- ✅ Folium-based interactive visualization
- ✅ Marker clustering for dense areas
- ✅ Heatmap overlay for sampling density
- ✅ Click markers to view sample details
- ✅ Search and filter by location, date, species
- ✅ Bounding box selection
- ✅ Measurement tools
- ✅ Fullscreen mode

### 📍 Location/GPS Module
- ✅ Manual coordinate entry
- ✅ Preset locations (Indian coastal regions)
- ✅ GPS sensor integration (placeholder for future hardware)
- ✅ Distance calculations
- ✅ Coordinate formatting (decimal, DMS)
- ✅ Bounding box calculations

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
# Install required packages
pip install firebase-admin folium pandas streamlit

# Or install from requirements
pip install -r requirements_cloud_map.txt
```

### 2. Firebase Setup

#### 2.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add Project"
3. Enter project name: `plankton-detection`
4. Enable Google Analytics (optional)
5. Create project

#### 2.2 Enable Firebase Services

1. **Firebase Storage**:
   - Go to Storage in sidebar
   - Click "Get Started"
   - Choose "Start in production mode"
   - Select a region (e.g., `asia-south1` for India)
   - Click "Done"

2. **Cloud Firestore**:
   - Go to Firestore Database in sidebar
   - Click "Create database"
   - Choose "Start in production mode"
   - Select same region as Storage
   - Click "Enable"

#### 2.3 Get Service Account Credentials

1. Go to Project Settings (gear icon)
2. Select "Service accounts" tab
3. Click "Generate new private key"
4. Save the JSON file
5. Copy `config/firebase_config_template.json` to `config/firebase_config.json`
6. Replace placeholder values with your credentials from the downloaded JSON

#### 2.4 Security (Important!)

```bash
# Add firebase config to .gitignore
echo "config/firebase_config.json" >> .gitignore

# Never commit your Firebase credentials!
```

### 3. Database Setup

The database will be automatically created on first use:

```python
from modules.database import PlanktonDatabase

# Creates database at data/plankton_samples.db
db = PlanktonDatabase()

# Verify setup
stats = db.get_statistics()
print(stats)
```

### 4. Location Presets

Create default coastal location presets:

```python
from modules.location import LocationManager

manager = LocationManager()
manager.create_default_presets("config/preset_locations.json")
```

---

## 💡 Usage Examples

### Example 1: Basic Sample with Location

```python
from modules.database import PlanktonDatabase
from modules.location import LocationManager
from datetime import datetime

# Initialize
db = PlanktonDatabase()
location_mgr = LocationManager()

# Create location data
location = location_mgr.get_location_manual(
    latitude=19.0760,
    longitude=72.8777,
    location_name="Mumbai Harbor",
    water_body="Arabian Sea",
    depth_meters=5.0
)

# Create sample data
sample_data = {
    'sample_id': f'SAMPLE_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
    'timestamp': datetime.now().isoformat(),
    **location,  # Add location data
    'operator_id': 'researcher_1',
    'session_id': 'SESSION_001',
    'image_path': 'path/to/image.jpg',
    'magnification': 2.5,
    'exposure_ms': 100
}

# Insert into database
sample_id = db.insert_sample(sample_data)
print(f"Sample created: {sample_id}")
```

### Example 2: Add Detection Results

```python
# Add detection to the sample
detection = {
    'organism_id': 1,
    'class_name': 'Copepod',
    'confidence': 0.95,
    'bbox': [100, 100, 200, 200],
    'size_px': 50.5,
    'centroid_x': 150.0,
    'centroid_y': 150.0
}

det_id = db.insert_detection(sample_data['sample_id'], detection)
print(f"Detection added: {det_id}")
```

### Example 3: Upload to Firebase

```python
from modules.cloud_storage import FirebaseStorageManager

# Initialize Firebase
firebase = FirebaseStorageManager()

if firebase.enabled:
    # Upload image
    image_url = firebase.upload_image(
        local_path='results/sample_image.jpg',
        metadata={'sample_id': sample_data['sample_id']}
    )

    # Upload sample metadata to Firestore
    firebase.upload_sample_data(
        sample_id=sample_data['sample_id'],
        sample_data=sample_data,
        detections=[detection]
    )

    # Mark as uploaded in local DB
    db.mark_firebase_uploaded(
        sample_id=sample_data['sample_id'],
        image_url=image_url
    )

    print(f"✅ Uploaded to Firebase: {image_url}")
else:
    print("⚠️ Firebase not configured")
```

### Example 4: Complete Workflow with Auto-Sync

```python
from modules.database import PlanktonDatabase
from modules.location import LocationManager
from modules.cloud_storage import FirebaseStorageManager
from pipeline.manager import PipelineManager
from config.config_loader import load_config
from datetime import datetime

def process_and_upload_sample(image_path: str, latitude: float, longitude: float,
                               location_name: str = None):
    """
    Complete workflow: Process image, store locally, upload to cloud
    """

    # 1. Initialize components
    db = PlanktonDatabase()
    location_mgr = LocationManager()
    firebase = FirebaseStorageManager()

    # Load pipeline
    config = load_config()
    pipeline = PipelineManager(config)

    # 2. Get location data
    location = location_mgr.get_location_manual(
        latitude=latitude,
        longitude=longitude,
        location_name=location_name
    )

    # 3. Run detection pipeline
    acquisition_params = {
        'mode': 'file',
        'image_path': image_path,
        'magnification': 2.5,
        'exposure_ms': 100,
        'capture_metadata': {
            'timestamp': datetime.now().isoformat(),
            'operator_id': 'auto',
            **location
        }
    }

    result = pipeline.execute_pipeline(acquisition_params)

    if result['status'] != 'success':
        print(f"❌ Pipeline failed: {result.get('error_message')}")
        return None

    # 4. Store in local database
    sample_id = f"SAMPLE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    sample_data = {
        'sample_id': sample_id,
        'timestamp': datetime.now().isoformat(),
        **location,
        'image_path': image_path,
        'operator_id': 'auto',
        'total_organisms': result['summary'].get('total_organisms', 0),
        'species_richness': result['summary'].get('species_richness', 0)
    }

    db.insert_sample(sample_data)

    # Add detections
    detections = []
    for org in result['detailed_results'].get('organisms', []):
        detection = {
            'organism_id': org.get('id'),
            'class_name': org.get('class_name'),
            'confidence': org.get('confidence'),
            'bbox': [org.get('x1'), org.get('y1'), org.get('x2'), org.get('y2')],
            'size_px': org.get('size_px')
        }
        db.insert_detection(sample_id, detection)
        detections.append(detection)

    # 5. Upload to Firebase
    if firebase.enabled:
        sync_result = firebase.sync_sample(
            sample_id=sample_id,
            sample_data=sample_data,
            detections=detections,
            image_path=image_path
        )

        if sync_result['success']:
            db.mark_firebase_uploaded(
                sample_id=sample_id,
                image_url=sync_result['image_url']
            )
            print(f"✅ Synced to cloud: {sync_result['image_url']}")

    print(f"✅ Complete! Sample ID: {sample_id}")
    print(f"   Organisms: {sample_data['total_organisms']}")
    print(f"   Species: {sample_data['species_richness']}")

    return sample_id


# Usage
sample_id = process_and_upload_sample(
    image_path='test_images/plankton_sample.jpeg',
    latitude=19.0760,
    longitude=72.8777,
    location_name="Mumbai Harbor"
)
```

### Example 5: Create Interactive Map

```python
from modules.database import PlanktonDatabase
from modules.map_viewer import PlanktonMapViewer

# Get all samples with location
db = PlanktonDatabase()
samples = db.get_all_samples_with_location()

# Create map
viewer = PlanktonMapViewer()
m = viewer.create_map_with_samples(
    samples,
    use_clustering=True,
    add_heatmap=True,
    auto_center=True
)

# Save to file
viewer.save_map(m, "results/maps/all_samples.html")

print(f"✅ Map created with {len(samples)} samples")
print("   Open results/maps/all_samples.html in your browser!")
```

### Example 6: Filter and Export by Location

```python
from modules.database import PlanktonDatabase

db = PlanktonDatabase()

# Get samples within Mumbai area (50km radius)
samples = db.get_samples_by_bbox(
    min_lat=18.8,
    max_lat=19.3,
    min_lon=72.6,
    max_lon=73.0
)

print(f"Found {len(samples)} samples in Mumbai area")

# Export to CSV
csv_path = db.export_to_csv(
    output_path='exports/mumbai_samples.csv',
    filters={
        'bbox': {
            'min_lat': 18.8,
            'max_lat': 19.3,
            'min_lon': 72.6,
            'max_lon': 73.0
        }
    }
)

print(f"✅ Exported to {csv_path}")
```

---

## 🎨 Dashboard Integration

### Run Standalone Map Viewer

```bash
streamlit run map_viewer_app.py
```

Features:
- Load samples from local database or Firebase
- Filter by date, location, organism count
- Interactive Folium map with clustering
- Export filtered data to CSV
- Real-time statistics

### Add Map Tab to Existing Dashboard

The map viewer has been integrated into `dashboard/app_comprehensive.py`. To use it:

1. Load the dashboard:
```bash
streamlit run dashboard/app_comprehensive.py
```

2. Navigate to the "🗺️ Map View" tab

3. Features include:
   - All samples plotted on interactive map
   - Click markers to view sample details
   - Filter samples by various criteria
   - Export filtered data

---

## 📊 Database Schema

### Samples Table
```sql
- id: INTEGER PRIMARY KEY
- sample_id: TEXT UNIQUE (e.g., "SAMPLE_20240115_103045")
- timestamp: TEXT (ISO format)
- latitude, longitude: REAL
- location_name: TEXT
- water_body: TEXT
- depth_meters: REAL
- operator_id: TEXT
- session_id: TEXT
- image_path, video_path: TEXT
- firebase_uploaded: INTEGER (0/1)
- firebase_image_url, firebase_video_url: TEXT
- metadata_json: TEXT
```

### Detections Table
```sql
- id: INTEGER PRIMARY KEY
- sample_id: TEXT (foreign key)
- organism_id: INTEGER
- class_name: TEXT
- confidence: REAL
- bbox_x1, bbox_y1, bbox_x2, bbox_y2: REAL
- size_px, size_um: REAL
- centroid_x, centroid_y: REAL
- properties_json: TEXT
```

### Sessions Table
```sql
- id: INTEGER PRIMARY KEY
- session_id: TEXT UNIQUE
- session_type: TEXT ('flow_cell', 'batch', 'realtime')
- start_time, end_time: TEXT
- latitude, longitude: REAL
- total_frames, total_organisms, total_species: INTEGER
- volume_ml, flow_rate_ml_min: REAL
- results_dir: TEXT
- summary_json: TEXT
```

---

## 🔧 Configuration Files

### config/firebase_config.json
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com",
  ...
}
```

### config/preset_locations.json
```json
{
  "Mumbai Harbor": {
    "latitude": 18.9220,
    "longitude": 72.8347,
    "water_body": "Arabian Sea",
    "description": "Mumbai harbor, major port city"
  },
  ...
}
```

---

## 📱 Mobile/Field Usage

For field work with GPS:

1. **Option 1: Manual Entry**
   - Use smartphone GPS app to get coordinates
   - Enter manually in dashboard or code

2. **Option 2: GPS Sensor (Future)**
   - Connect USB GPS to Raspberry Pi
   - Implement GPS module integration
   - Auto-capture coordinates

3. **Option 3: Mobile App (Future)**
   - Build companion mobile app
   - Capture GPS automatically
   - Sync with cloud

---

## 🔒 Security Best Practices

1. **Firebase Credentials**:
   - Never commit `firebase_config.json` to git
   - Use environment variables in production
   - Restrict access with Firebase rules

2. **Database**:
   - Regular backups of SQLite database
   - Validate all input data
   - Use parameterized queries (already implemented)

3. **Cloud Storage**:
   - Set appropriate Firebase Storage rules
   - Monitor usage and costs
   - Use private URLs for sensitive data

---

## 🎓 Training & Documentation

### For Field Researchers

1. **Taking Samples**:
   - Record GPS coordinates (phone app or GPS device)
   - Note location name and water body
   - Measure depth if possible
   - Take clear microscope images

2. **Uploading Data**:
   - Use dashboard or map viewer app
   - Enter location information
   - Process through pipeline
   - Verify upload to cloud

### For Lab Technicians

1. **Processing Samples**:
   - Load images from field
   - Run detection pipeline
   - Review results
   - Associate with field GPS data

2. **Quality Control**:
   - Verify species classifications
   - Check location data accuracy
   - Export reports for analysis

---

## 🚨 Troubleshooting

### Firebase Not Connecting

```
Error: "Firebase config not found"
```

**Solution**:
1. Verify `config/firebase_config.json` exists
2. Check JSON syntax is valid
3. Verify credentials are correct
4. Install firebase-admin: `pip install firebase-admin`

### Map Not Loading

```
Error: "No samples to display"
```

**Solution**:
1. Click "Refresh Data" in sidebar
2. Verify database has samples with lat/lon
3. Check filters aren't too restrictive
4. Verify samples have valid coordinates

### GPS Coordinates Invalid

```
Error: "Invalid latitude: 191.5"
```

**Solution**:
- Latitude must be between -90 and 90
- Longitude must be between -180 and 180
- Check coordinate format (decimal degrees)

---

## 📚 API Reference

### Database Module

```python
from modules.database import PlanktonDatabase

db = PlanktonDatabase(db_path="data/plankton_samples.db")

# Insert sample
sample_id = db.insert_sample(sample_data)

# Insert detection
det_id = db.insert_detection(sample_id, detection_data)

# Query samples
samples = db.get_all_samples_with_location()
samples_bbox = db.get_samples_by_bbox(min_lat, max_lat, min_lon, max_lon)
detections = db.get_sample_detections(sample_id)

# Export
csv_path = db.export_to_csv(output_path, filters)

# Statistics
stats = db.get_statistics()

# Mark uploaded
db.mark_firebase_uploaded(sample_id, image_url, video_url)
```

### Location Module

```python
from modules.location import LocationManager

mgr = LocationManager(preset_locations_path="config/preset_locations.json")

# Manual location
loc = mgr.get_location_manual(lat, lon, location_name, water_body, depth)

# Preset location
loc = mgr.get_location_preset("Mumbai Harbor", depth_meters=5.0)

# Use last location
loc = mgr.use_last_location()

# Calculate distance
dist_km = mgr.calculate_distance(lat1, lon1, lat2, lon2)

# Get bounding box
bbox = mgr.get_location_bounds(center_lat, center_lon, radius_km)
```

### Cloud Storage Module

```python
from modules.cloud_storage import FirebaseStorageManager

firebase = FirebaseStorageManager(config_path="config/firebase_config.json")

# Check if enabled
if firebase.enabled:
    # Upload image
    url = firebase.upload_image(local_path, cloud_path, metadata)

    # Upload video
    url = firebase.upload_video(local_path, cloud_path, metadata)

    # Upload sample data
    success = firebase.upload_sample_data(sample_id, sample_data, detections)

    # Sync complete sample
    result = firebase.sync_sample(sample_id, sample_data, detections,
                                   image_path, video_path)

    # Query from cloud
    samples = firebase.get_samples_by_location(min_lat, max_lat, min_lon, max_lon)

    # Export CSV to cloud
    url = firebase.export_csv_to_cloud(csv_path)

    # Get stats
    stats = firebase.get_storage_stats()
```

### Map Viewer Module

```python
from modules.map_viewer import PlanktonMapViewer

viewer = PlanktonMapViewer(center=(lat, lon), zoom=5)

# Create map with samples
m = viewer.create_map_with_samples(
    samples,
    use_clustering=True,
    add_heatmap=True,
    auto_center=True
)

# Create species distribution map
m = viewer.create_species_distribution_map(samples, species_name)

# Save map
viewer.save_map(m, output_path)

# Filter samples
filtered = viewer.filter_samples_by_bbox(samples, min_lat, max_lat, min_lon, max_lon)
filtered = viewer.filter_samples_by_species(samples, species_names)
```

---

## 🎉 Success!

You now have a complete cloud-integrated plankton detection system with:

✅ GPS/location tracking
✅ Firebase cloud storage
✅ Interactive maps
✅ Local database
✅ CSV exports
✅ Real-time sync

**Next Steps**:
1. Configure Firebase with your credentials
2. Create some test samples with locations
3. Run the map viewer app
4. Explore the interactive map!

For support or questions, refer to the main project README or create an issue.

---

**Happy Plankton Mapping! 🔬🗺️**

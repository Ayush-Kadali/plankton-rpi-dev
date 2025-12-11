#!/usr/bin/env python3
"""
Generate Realistic Demo Data with Diverse Plankton Distributions
Creates samples across Indian lakes, ponds, and water bodies with realistic species abundance
"""

import random
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Import modules
sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location("database", "modules/database.py")
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)

spec = importlib.util.spec_from_file_location("location", "modules/location.py")
location = importlib.util.module_from_spec(spec)
spec.loader.exec_module(location)

spec = importlib.util.spec_from_file_location("data_collector", "modules/data_collector.py")
data_collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(data_collector)

print("=" * 80)
print("GENERATING REALISTIC DEMO DATA - INLAND WATER BODIES")
print("=" * 80)

# Initialize
db = database.PlanktonDatabase("data/judge_demo.db")
loc_mgr = location.LocationManager()
collector = data_collector.PlanktonDataCollector(db, loc_mgr, None)

# Define diverse sampling locations across India's lakes and water bodies
SAMPLING_LOCATIONS = [
    {
        'name': 'Dal Lake',
        'lat': 34.0836,
        'lon': 74.8370,
        'water_body': 'Dal Lake',
        'region': 'Jammu & Kashmir',
        'type': 'freshwater_lake',
        'characteristics': {
            'pollution_level': 'medium',
            'sampling_frequency': 'high',
            'typical_diversity': 'medium',
            'bloom_risk': 'high',
            'dominant_groups': ['Diatom', 'Chlorophyta']
        },
        'samples_count': 18
    },
    {
        'name': 'Wular Lake',
        'lat': 34.3500,
        'lon': 74.6000,
        'water_body': 'Wular Lake',
        'region': 'Jammu & Kashmir',
        'type': 'freshwater_lake',
        'characteristics': {
            'pollution_level': 'low',
            'sampling_frequency': 'medium',
            'typical_diversity': 'high',
            'bloom_risk': 'low',
            'dominant_groups': ['Diatom', 'Copepod']
        },
        'samples_count': 12
    },
    {
        'name': 'Sukhna Lake',
        'lat': 30.7420,
        'lon': 76.8185,
        'water_body': 'Sukhna Lake',
        'region': 'Chandigarh',
        'type': 'freshwater_reservoir',
        'characteristics': {
            'pollution_level': 'medium',
            'sampling_frequency': 'very_high',
            'typical_diversity': 'medium',
            'bloom_risk': 'medium',
            'dominant_groups': ['Diatom', 'Cyanobacteria']
        },
        'samples_count': 25  # High monitoring frequency
    },
    {
        'name': 'Harike Wetland',
        'lat': 31.1650,
        'lon': 74.9697,
        'water_body': 'Harike Wetland',
        'region': 'Punjab',
        'type': 'wetland',
        'characteristics': {
            'pollution_level': 'medium',
            'sampling_frequency': 'high',
            'typical_diversity': 'very_high',
            'bloom_risk': 'high',
            'dominant_groups': ['Diatom', 'Chlorophyta', 'Cyanobacteria']
        },
        'samples_count': 20
    },
    {
        'name': 'Sambhar Lake',
        'lat': 26.9089,
        'lon': 75.0656,
        'water_body': 'Sambhar Salt Lake',
        'region': 'Rajasthan',
        'type': 'saline_lake',
        'characteristics': {
            'pollution_level': 'low',
            'sampling_frequency': 'low',
            'typical_diversity': 'low',  # Saline tolerant species only
            'bloom_risk': 'low',
            'dominant_groups': ['Dunaliella', 'Halobacteria']
        },
        'samples_count': 8
    },
    {
        'name': 'Upper Lake Bhopal',
        'lat': 23.2599,
        'lon': 77.3954,
        'water_body': 'Upper Lake (Bada Talab)',
        'region': 'Madhya Pradesh',
        'type': 'freshwater_lake',
        'characteristics': {
            'pollution_level': 'medium',
            'sampling_frequency': 'high',
            'typical_diversity': 'high',
            'bloom_risk': 'medium',
            'dominant_groups': ['Diatom', 'Chlorophyta', 'Copepod']
        },
        'samples_count': 15
    },
    {
        'name': 'Chilika Lake',
        'lat': 19.7165,
        'lon': 85.3206,
        'water_body': 'Chilika Lake',
        'region': 'Odisha',
        'type': 'brackish_lagoon',
        'characteristics': {
            'pollution_level': 'low',
            'sampling_frequency': 'very_high',  # Biodiversity hotspot
            'typical_diversity': 'very_high',
            'bloom_risk': 'medium',
            'dominant_groups': ['Copepod', 'Diatom', 'Dinoflagellate']
        },
        'samples_count': 28
    },
    {
        'name': 'Loktak Lake',
        'lat': 24.5166,
        'lon': 93.8000,
        'water_body': 'Loktak Lake',
        'region': 'Manipur',
        'type': 'freshwater_lake',
        'characteristics': {
            'pollution_level': 'medium',
            'sampling_frequency': 'medium',
            'typical_diversity': 'very_high',
            'bloom_risk': 'high',
            'dominant_groups': ['Diatom', 'Chlorophyta', 'Cyanobacteria']
        },
        'samples_count': 14
    },
    {
        'name': 'Deepor Beel',
        'lat': 26.1041,
        'lon': 91.6750,
        'water_body': 'Deepor Beel',
        'region': 'Assam',
        'type': 'wetland',
        'characteristics': {
            'pollution_level': 'high',
            'sampling_frequency': 'medium',
            'typical_diversity': 'very_high',
            'bloom_risk': 'very_high',
            'dominant_groups': ['Cyanobacteria', 'Diatom', 'Chlorophyta']
        },
        'samples_count': 16
    },
    {
        'name': 'Vembanad Lake',
        'lat': 9.5916,
        'lon': 76.3946,
        'water_body': 'Vembanad Lake',
        'region': 'Kerala',
        'type': 'brackish_lake',
        'characteristics': {
            'pollution_level': 'medium',
            'sampling_frequency': 'high',
            'typical_diversity': 'very_high',
            'bloom_risk': 'medium',
            'dominant_groups': ['Copepod', 'Diatom', 'Dinoflagellate']
        },
        'samples_count': 20
    },
    {
        'name': 'Pulicat Lake',
        'lat': 13.6631,
        'lon': 80.0447,
        'water_body': 'Pulicat Lake',
        'region': 'Andhra Pradesh',
        'type': 'brackish_lagoon',
        'characteristics': {
            'pollution_level': 'medium',
            'sampling_frequency': 'medium',
            'typical_diversity': 'high',
            'bloom_risk': 'medium',
            'dominant_groups': ['Copepod', 'Diatom', 'Ciliate']
        },
        'samples_count': 14
    },
    {
        'name': 'Kolleru Lake',
        'lat': 16.7000,
        'lon': 81.3000,
        'water_body': 'Kolleru Lake',
        'region': 'Andhra Pradesh',
        'type': 'freshwater_lake',
        'characteristics': {
            'pollution_level': 'high',
            'sampling_frequency': 'high',
            'typical_diversity': 'high',
            'bloom_risk': 'very_high',
            'dominant_groups': ['Cyanobacteria', 'Chlorophyta', 'Diatom']
        },
        'samples_count': 18
    },
    {
        'name': 'Hussain Sagar',
        'lat': 17.4239,
        'lon': 78.4738,
        'water_body': 'Hussain Sagar',
        'region': 'Telangana',
        'type': 'freshwater_lake',
        'characteristics': {
            'pollution_level': 'very_high',
            'sampling_frequency': 'very_high',
            'typical_diversity': 'low',  # Pollution tolerant species
            'bloom_risk': 'very_high',
            'dominant_groups': ['Cyanobacteria', 'Euglenophyta']
        },
        'samples_count': 22
    },
    {
        'name': 'Powai Lake',
        'lat': 19.1250,
        'lon': 72.9053,
        'water_body': 'Powai Lake',
        'region': 'Maharashtra',
        'type': 'freshwater_lake',
        'characteristics': {
            'pollution_level': 'high',
            'sampling_frequency': 'high',
            'typical_diversity': 'medium',
            'bloom_risk': 'high',
            'dominant_groups': ['Cyanobacteria', 'Chlorophyta', 'Diatom']
        },
        'samples_count': 16
    }
]

# Realistic plankton species pools by ecological type
SPECIES_POOLS = {
    'Diatom': ['Navicula', 'Nitzschia', 'Cyclotella', 'Fragilaria', 'Synedra', 'Gomphonema', 'Pinnularia'],
    'Chlorophyta': ['Chlorella', 'Scenedesmus', 'Pediastrum', 'Closterium', 'Spirogyra', 'Volvox'],
    'Cyanobacteria': ['Microcystis', 'Anabaena', 'Oscillatoria', 'Spirulina', 'Aphanizomenon'],
    'Copepod': ['Cyclopoid', 'Calanoid', 'Harpacticoid'],
    'Dinoflagellate': ['Ceratium', 'Peridinium', 'Gonyaulax', 'Noctiluca'],
    'Ciliate': ['Paramecium', 'Vorticella', 'Stentor', 'Coleps'],
    'Euglenophyta': ['Euglena', 'Phacus', 'Trachelomonas'],
    'Dunaliella': ['Dunaliella_salina'],
    'Halobacteria': ['Halobacterium'],
    'Rotifer': ['Brachionus', 'Keratella', 'Asplanchna']
}

def generate_realistic_plankton_community(location_info, time_offset_days):
    """Generate realistic plankton community with natural abundance patterns"""

    chars = location_info['characteristics']
    water_type = location_info['type']

    # Realistic organism counts based on water body type and diversity
    if chars['typical_diversity'] == 'very_high':
        base_count = random.randint(100, 180)
    elif chars['typical_diversity'] == 'high':
        base_count = random.randint(60, 120)
    elif chars['typical_diversity'] == 'medium':
        base_count = random.randint(30, 70)
    else:  # low diversity (saline/polluted)
        base_count = random.randint(5, 30)

    # Seasonal variation
    month = (datetime.now() - timedelta(days=time_offset_days)).month
    if month in [6, 7, 8, 9]:  # Monsoon - higher plankton in freshwater
        if water_type in ['freshwater_lake', 'wetland']:
            base_count = int(base_count * 1.4)
    elif month in [3, 4, 5]:  # Summer - blooms common
        if chars['bloom_risk'] in ['high', 'very_high']:
            base_count = int(base_count * 1.3)

    # Build species community based on dominant groups
    organisms = []
    species_used = []

    # Dominant groups get 60-70% of abundance
    dominant_groups = chars['dominant_groups']
    dominant_count = int(base_count * 0.65)

    # Distribute among dominant groups
    for i, group in enumerate(dominant_groups):
        if group in SPECIES_POOLS:
            group_species = SPECIES_POOLS[group]
            # First dominant group gets more
            if i == 0:
                group_count = int(dominant_count * 0.5)
            else:
                group_count = int(dominant_count * 0.3 / (len(dominant_groups) - 1))

            for _ in range(group_count):
                species = random.choice(group_species)
                species_used.append(species)

    # Add rare species (30-40% abundance, but more diversity)
    remaining_count = base_count - len(species_used)

    # Get all other groups not in dominant
    other_groups = [g for g in SPECIES_POOLS.keys() if g not in dominant_groups]

    # Special handling for water type
    if water_type == 'saline_lake':
        other_groups = ['Dunaliella', 'Halobacteria']
    elif water_type == 'brackish_lagoon':
        other_groups = ['Copepod', 'Dinoflagellate', 'Ciliate', 'Rotifer']

    for _ in range(remaining_count):
        if other_groups:
            group = random.choice(other_groups)
            if group in SPECIES_POOLS:
                species = random.choice(SPECIES_POOLS[group])
                species_used.append(species)

    # Check for bloom event
    bloom_detected = False
    bloom_species = None

    if chars['bloom_risk'] in ['high', 'very_high'] and random.random() < 0.25:
        bloom_detected = True
        # Bloom species from dominant groups
        if 'Cyanobacteria' in dominant_groups:
            bloom_species = random.choice(SPECIES_POOLS['Cyanobacteria'])
        elif 'Chlorophyta' in dominant_groups:
            bloom_species = random.choice(SPECIES_POOLS['Chlorophyta'])
        else:
            bloom_species = random.choice(SPECIES_POOLS[dominant_groups[0]])

        # Add many more of bloom species
        bloom_count = int(base_count * 0.4)
        species_used.extend([bloom_species] * bloom_count)
        base_count += bloom_count

    # Create organism detections
    for i, species in enumerate(species_used[:150]):  # Limit to 150
        organisms.append({
            'id': i + 1,
            'class_name': species,
            'confidence': random.uniform(0.72, 0.97),
            'x1': random.randint(50, 500),
            'y1': random.randint(50, 500),
            'x2': random.randint(100, 600),
            'y2': random.randint(100, 600),
            'size_px': random.uniform(8, 120),
            'centroid_x': random.uniform(100, 500),
            'centroid_y': random.uniform(100, 500)
        })

    # Calculate species richness
    unique_species = len(set(species_used))

    return {
        'summary': {
            'total_organisms': len(organisms),
            'species_richness': unique_species
        },
        'detailed_results': {
            'organisms': organisms,
            'bloom_alerts': [{'species': bloom_species, 'dominance': 70}] if bloom_detected else []
        }
    }

print("\n📍 Generating samples across 14 diverse water bodies...")
print("=" * 80)

total_samples = 0
location_stats = []

for loc in SAMPLING_LOCATIONS:
    print(f"\n📍 {loc['name']} ({loc['region']}) - {loc['type']}")
    print(f"   Generating {loc['samples_count']} samples...")

    samples_created = 0
    bloom_count = 0

    # Generate samples over past 45 days
    days_span = 45
    time_interval = days_span / loc['samples_count']

    for i in range(loc['samples_count']):
        # Calculate timestamp (spread over 45 days)
        time_offset_days = i * time_interval
        sample_time = datetime.now() - timedelta(days=time_offset_days)

        # Add small random variation to coordinates (simulating different sampling points)
        lat_offset = random.uniform(-0.01, 0.01)
        lon_offset = random.uniform(-0.01, 0.01)

        # Generate realistic plankton community
        inference = generate_realistic_plankton_community(loc, time_offset_days)

        # Collect sample
        result = collector.collect_sample(
            latitude=loc['lat'] + lat_offset,
            longitude=loc['lon'] + lon_offset,
            location_name=loc['name'],
            water_body=loc['water_body'],
            depth_meters=random.uniform(0.5, 12.0),
            inference_results=inference,
            operator_id=f"researcher_{loc['region'].lower().replace(' ', '_').replace('&', 'and')}",
            auto_upload=False
        )

        if result['success']:
            samples_created += 1
            if result['bloom_detected']:
                bloom_count += 1

    total_samples += samples_created

    location_stats.append({
        'location': loc['name'],
        'region': loc['region'],
        'type': loc['type'],
        'samples': samples_created,
        'blooms': bloom_count,
        'diversity': loc['characteristics']['typical_diversity']
    })

    print(f"   ✅ Created {samples_created} samples ({bloom_count} with algal blooms)")

print("\n" + "=" * 80)
print("📊 SUMMARY STATISTICS BY LOCATION")
print("=" * 80)

for stat in location_stats:
    print(f"\n{stat['location']} ({stat['region']}):")
    print(f"   Water body type: {stat['type']}")
    print(f"   Samples: {stat['samples']}")
    print(f"   Algal blooms: {stat['blooms']}")
    print(f"   Expected diversity: {stat['diversity']}")

print("\n" + "=" * 80)
print("📈 DATABASE STATISTICS")
print("=" * 80)

db_stats = db.get_statistics()
for key, value in db_stats.items():
    print(f"   {key}: {value}")

# Get species distribution
print("\n" + "=" * 80)
print("🧬 TOP 15 MOST ABUNDANT SPECIES")
print("=" * 80)

species_dist = db.get_species_distribution()
top_species = sorted(species_dist.items(), key=lambda x: x[1], reverse=True)[:15]

for i, (species, count) in enumerate(top_species, 1):
    print(f"   {i}. {species}: {count} detections")

print("\n" + "=" * 80)
print("✅ DEMO DATA GENERATION COMPLETE!")
print("=" * 80)

print(f"\n📊 Generated {total_samples} samples across 14 water bodies")
print(f"📍 Coverage: Kashmir to Kerala, Assam to Rajasthan")
print(f"💧 Water body types: Freshwater lakes, saline lakes, brackish lagoons, wetlands")
print(f"🗄️ Database: data/judge_demo.db")

print("\n🎯 What this demonstrates:")
print("   ✅ Pan-India water quality monitoring")
print("   ✅ Diverse ecosystems (freshwater, brackish, saline)")
print("   ✅ Realistic plankton communities with natural abundance")
print("   ✅ Algal bloom detection in high-risk water bodies")
print("   ✅ Biodiversity hotspots (Chilika, Vembanad)")
print("   ✅ Pollution monitoring (Hussain Sagar, Powai)")
print("   ✅ 45 days of historical monitoring data")
print("   ✅ Species-specific abundance patterns")

print("\n🗺️ Next: View the interactive map")
print("   Run: streamlit run map_viewer_app.py")
print("=" * 80)

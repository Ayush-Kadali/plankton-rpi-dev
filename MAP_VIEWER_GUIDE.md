# 🗺️ Plankton Map Viewer - Quick Start Guide

## Overview
This demo showcases realistic plankton monitoring data across 14 diverse water bodies in India - from Kashmir to Kerala, covering freshwater lakes, brackish lagoons, saline lakes, and wetlands.

## 🚀 Quick Start (2 Steps!)

### Step 1: Generate Demo Data
```bash
python3 generate_demo_data.py
```

This creates ~230 realistic plankton samples across 14 locations:
- **North India**: Dal Lake, Wular Lake, Sukhna Lake, Harike Wetland
- **Central India**: Sambhar Lake, Upper Lake Bhopal
- **East India**: Chilika Lake, Loktak Lake, Deepor Beel, Kolleru Lake
- **South India**: Vembanad Lake, Pulicat Lake, Hussain Sagar, Powai Lake

### Step 2: Launch Interactive Map
```bash
streamlit run map_viewer_app.py
```

Then click "🔄 Refresh Data" in the sidebar!

## 🎨 Understanding the Map

### Marker Colors (Organism Density)
- **🔴 Red** (100+ organisms): Very high density - Potential algal bloom
- **🟠 Orange** (50-99 organisms): High density
- **🔵 Blue** (10-49 organisms): Medium density
- **🟢 Green** (1-9 organisms): Low density
- **⚫ Gray** (0 organisms): No organisms detected

### What Makes This Data Realistic?

1. **Natural Abundance Patterns**
   - Diatoms are most abundant (common in all water bodies)
   - Cyanobacteria dominate in polluted/eutrophic lakes
   - Copepods more common in brackish waters
   - Halophiles only in saline lakes

2. **Varied Plankton Diversity**
   - High diversity: Chilika Lake, Vembanad Lake (100-180 organisms)
   - Medium diversity: Upper Lake Bhopal (30-70 organisms)
   - Low diversity: Sambhar Lake (5-30 organisms, saline tolerant only)

3. **Realistic Bloom Detection**
   - ~25% of samples in high-risk water bodies show blooms
   - Blooms most common in: Hussain Sagar, Deepor Beel, Kolleru Lake
   - Bloom species: Microcystis, Anabaena, Oscillatoria

4. **Geographic & Seasonal Patterns**
   - More samples in research hotspots (Chilika, Sukhna, Hussain Sagar)
   - Fewer samples in remote locations (Sambhar, Wular)
   - 45 days of historical data with seasonal variations

## 📊 Features to Try

### 1. Filter by Location
In the sidebar, expand "📍 Location" and select specific water bodies to compare

### 2. Find Blooms
Set organism count filter:
- Minimum: 100
- Maximum: 1000
- Click "Apply Filters"

All red markers (potential blooms) will be shown!

### 3. Time-based Analysis
Enable date filter to see how plankton populations change over the 45-day period

### 4. Export Data
Click "📥 Export Filtered CSV" to download current filtered data for analysis

## 🌟 Key Highlights

**Biodiversity Hotspots:**
- Chilika Lake: 28 samples, very high diversity
- Vembanad Lake: 20 samples, very high diversity

**Pollution Monitoring:**
- Hussain Sagar: 22 samples, frequent blooms (Hyderabad)
- Powai Lake: 16 samples, high pollution (Mumbai)

**Unique Ecosystems:**
- Sambhar Lake: Saline lake with specialized halophiles
- Harike Wetland: Rich wetland ecosystem
- Loktak Lake: Largest freshwater lake in Northeast India

## 🎯 What This Demonstrates

✅ **Pan-India water quality monitoring** across diverse ecosystems
✅ **Real-time plankton detection** with color-coded density levels
✅ **Bloom early warning system** for harmful algal blooms
✅ **Biodiversity assessment** with species richness metrics
✅ **Interactive visualization** with filters, clustering, heatmaps
✅ **Data export** for further scientific analysis

## 💡 Tips for Judges/Newcomers

1. **Start Simple**: Just click "Refresh Data" and explore the map!
2. **Click Markers**: Each popup shows detailed sample information
3. **Try Filters**: Experiment with different filters to find patterns
4. **Compare Locations**: Notice how diversity varies by water body type
5. **Look for Patterns**: Red clusters indicate potential bloom areas

## 🔧 Customization

Want to add your own locations? Edit `config/preset_locations.json`:

```json
{
  "Your Lake Name": {
    "latitude": 12.3456,
    "longitude": 78.9012,
    "water_body": "Your Lake",
    "description": "Description here"
  }
}
```

Then regenerate demo data!

## 📈 Data Statistics

After running `generate_demo_data.py`, you'll see:
- Total samples generated (~230)
- Distribution across 14 locations
- Top 15 most abundant species
- Number of bloom events detected

---

**Questions?** The map interface has built-in help and color legends. Just load the data and start exploring! 🎉

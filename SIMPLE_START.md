# 🚀 Quick Start - Plankton Detection System

Everything is fixed and working. Use these simple commands:

---

## ✅ **OPTION 1: View the Interactive Map** (Recommended First!)

```bash
# Generate demo data with 7 locations across India
python3 judge_demo.py

# Open the map in your browser
open results/maps/judge_demo_professional.html
```

**What you'll see:**
- 🗺️ Interactive map with 7 coastal locations
- 🔴 Red markers = Algae blooms detected
- 🔵 Blue markers = Research stations / regular monitoring
- 🟢 Green markers = Low frequency sites
- Click any marker for detailed statistics
- 108 realistic samples across 30 days

---

## ✅ **OPTION 2: Launch the Dashboard** (Streamlit App)

```bash
# Simple one-command launch
./run_app.sh

# Or manually:
streamlit run app.py
```

**Dashboard features:**
- 🏠 Home: Overview of all locations
- 🗺️ Map: Embedded interactive map
- 📊 Data: Filter and explore samples
- 📥 Export: Download CSV for any location

---

## ✅ **OPTION 3: Export Location Data**

```bash
# List all locations
python3 export_location_data.py --list

# Export Mumbai data
python3 export_location_data.py --location "Mumbai Harbor"

# Interactive mode
python3 export_location_data.py
```

---

## 📍 **7 Demo Locations**

| Location | Samples | Color | Description |
|----------|---------|-------|-------------|
| Mumbai Harbor | 25 | 🔵 Dark Blue | Research station |
| Chennai Marina | 20 | 🔵 Blue | Regular monitoring |
| Kochi Backwaters | 18 | 🔴 Red | Algae blooms! |
| Sundarbans Delta | 15 | 🟠 Orange | Bloom activity |
| Goa Coast | 12 | 🔵 Light Blue | Moderate sampling |
| Visakhapatnam | 8 | 🟢 Green | Low frequency |
| Gulf of Mannar | 10 | 🔵 Blue | Biodiversity hotspot |

---

## 🎯 **For Judges - Demo Flow**

1. **Open map**: `open results/maps/judge_demo_professional.html`
2. **Show Mumbai** (dark blue) - "Research station with high-frequency monitoring"
3. **Show Kochi** (red) - "Algae bloom detection in backwaters"
4. **Show Gulf of Mannar** - "Biodiversity hotspot with 15+ species"
5. **Export data**: `python3 export_location_data.py --location "Mumbai Harbor"`
6. **Show dashboard**: `streamlit run app.py`

---

**That's it! Start with the map, then try the dashboard.** 🚀

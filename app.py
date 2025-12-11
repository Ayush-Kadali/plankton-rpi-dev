#!/usr/bin/env python3
"""
Marine Plankton Detection System - Scientific Dashboard
Modern, clean, data-focused interface
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import json

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules directly
import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

database = load_module("database", "modules/database.py")
location = load_module("location", "modules/location.py")
map_viewer = load_module("map_viewer", "modules/map_viewer.py")
aqualens_integration = load_module("aqualens_integration", "modules/aqualens_integration.py")

# Page config
st.set_page_config(
    page_title="Marine Plankton Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Scientific Theme CSS
st.markdown("""
<style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
        padding: 2rem;
    }

    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Header styles */
    .scientific-header {
        background: linear-gradient(135deg, #0A2463 0%, #3E92CC 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(10, 36, 99, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .scientific-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }

    .scientific-header p {
        color: rgba(255, 255, 255, 0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        font-weight: 300;
    }

    /* Metric cards - Modern data-focused design */
    .metric-card {
        background: white;
        padding: 1.75rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8eef5;
        transition: all 0.3s ease;
        height: 100%;
    }

    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    }

    .metric-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1;
        margin-bottom: 0.25rem;
    }

    .metric-unit {
        font-size: 0.9rem;
        font-weight: 500;
        color: #94a3b8;
    }

    .metric-trend {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }

    .trend-up { color: #10b981; }
    .trend-down { color: #ef4444; }
    .trend-neutral { color: #64748b; }

    /* Status badges - Scientific color palette */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.3px;
        gap: 0.5rem;
    }

    .badge-critical {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(220, 38, 38, 0.3);
    }

    .badge-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
    }

    .badge-research {
        background: linear-gradient(135deg, #0A2463 0%, #3E92CC 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(10, 36, 99, 0.3);
    }

    .badge-active {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }

    .badge-normal {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }

    /* Data cards */
    .data-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8eef5;
        margin: 1rem 0;
    }

    .data-card h3 {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0 0 1rem 0;
        border-bottom: 2px solid #3E92CC;
        padding-bottom: 0.5rem;
    }

    /* Info boxes - Scientific alerts */
    .info-box {
        background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
    }

    .info-box strong {
        color: #1e40af;
        font-weight: 600;
    }

    .success-box {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
    }

    .success-box strong {
        color: #065f46;
        font-weight: 600;
    }

    .warning-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
    }

    .warning-box strong {
        color: #92400e;
        font-weight: 600;
    }

    .critical-box {
        background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
        border-left: 4px solid #dc2626;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.5rem 0;
    }

    .critical-box strong {
        color: #991b1b;
        font-weight: 600;
    }

    /* Tables - Modern data display */
    .dataframe {
        border: none !important;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .dataframe thead tr th {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        font-size: 0.85rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        border: none !important;
    }

    .dataframe tbody tr td {
        padding: 1rem !important;
        border-bottom: 1px solid #f1f5f9 !important;
        color: #334155 !important;
        font-size: 0.9rem !important;
    }

    .dataframe tbody tr:hover {
        background-color: #f8fafc !important;
    }

    .dataframe tbody tr:last-child td {
        border-bottom: none !important;
    }

    /* Sidebar - Clean scientific style */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid #e2e8f0;
    }

    [data-testid="stSidebar"] h3 {
        color: #0f172a;
        font-weight: 600;
        font-size: 1.1rem;
    }

    /* Buttons - Modern scientific */
    .stButton > button {
        background: linear-gradient(135deg, #0A2463 0%, #3E92CC 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(10, 36, 99, 0.2);
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(10, 36, 99, 0.3);
    }

    /* Tabs - Clean modern style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        color: #64748b;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0A2463 0%, #3E92CC 100%);
        color: white;
        box-shadow: 0 2px 8px rgba(10, 36, 99, 0.2);
    }

    /* Section headers */
    .section-header {
        color: #0f172a;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid #3E92CC;
    }

    /* Legend items */
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.5rem;
        margin: 0.25rem 0;
    }

    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }

    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #3E92CC !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #0f172a;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state"""
    if 'db' not in st.session_state:
        st.session_state.db = database.PlanktonDatabase("data/judge_demo.db")
    if 'samples_loaded' not in st.session_state:
        st.session_state.samples_loaded = False
    if 'all_samples' not in st.session_state:
        st.session_state.all_samples = []
    if 'aqualens_manager' not in st.session_state:
        st.session_state.aqualens_manager = aqualens_integration.get_manager()


def load_samples():
    """Load all samples from database"""
    try:
        samples = st.session_state.db.get_all_samples_with_location()
        for sample in samples:
            if sample.get('metadata_json'):
                try:
                    sample['metadata'] = json.loads(sample['metadata_json'])
                except:
                    sample['metadata'] = {}
        st.session_state.all_samples = samples
        st.session_state.samples_loaded = True
        return samples
    except Exception as e:
        st.error(f"Error loading samples: {e}")
        return []


def render_sidebar():
    """Render modern scientific sidebar"""
    with st.sidebar:
        st.markdown("### 🔬 Marine Plankton Analysis")
        st.markdown("*Real-time monitoring system*")
        st.divider()

        # Load data
        if st.button("🔄 Refresh Data", width="stretch", type="primary"):
            with st.spinner("Loading samples..."):
                samples = load_samples()
                st.success(f"✓ {len(samples)} samples loaded")

        st.divider()

        # Quick stats
        if st.session_state.samples_loaded and st.session_state.all_samples:
            st.markdown("#### 📊 System Status")

            stats = st.session_state.db.get_statistics()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Samples", stats['total_samples'], delta=None)
                st.metric("Species", stats['unique_species'], delta=None)

            with col2:
                st.metric("Locations", stats['samples_with_location'], delta=None)
                st.metric("Detections", stats['total_detections'], delta=None)

        st.divider()

        st.markdown("#### 🎯 Quick Navigation")
        st.markdown("""
        - **Home**: Overview & metrics
        - **Map**: Geographic visualization
        - **Data**: Detailed analysis
        - **Export**: Download reports
        """)

        st.divider()
        st.caption("SIH 2025 | Marine Research Initiative")


def render_home_page():
    """Render modern scientific home page"""

    # Modern header
    st.markdown("""
    <div class="scientific-header">
        <h1>🔬 Marine Plankton Detection System</h1>
        <p>Advanced AI-powered monitoring across Indian coastal regions</p>
    </div>
    """, unsafe_allow_html=True)

    # Check for data
    demo_db_path = Path("data/judge_demo.db")
    if not demo_db_path.exists():
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Initialize System</strong><br>
            Generate demonstration data to begin analysis.
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Generate Demo Data", type="primary"):
            import subprocess
            with st.spinner("Initializing monitoring system..."):
                result = subprocess.run(["python3", "judge_demo.py"], input="y\n",
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    st.success("✓ System initialized successfully")
                    st.rerun()
                else:
                    st.error("✗ Initialization failed")
        return

    # Load data
    if not st.session_state.samples_loaded:
        with st.spinner("Loading monitoring data..."):
            samples = load_samples()
    else:
        samples = st.session_state.all_samples

    if not samples:
        st.warning("No monitoring data available")
        return

    # Key metrics
    st.markdown('<p class="section-header">📊 System Overview</p>', unsafe_allow_html=True)

    # Calculate metrics
    location_groups = defaultdict(list)
    for sample in samples:
        loc_name = sample.get('location_name', 'Unknown')
        location_groups[loc_name].append(sample)

    bloom_count = sum(1 for s in samples
                     if s.get('metadata', {}).get('bloom_detected', False))

    species_dist = st.session_state.db.get_species_distribution()
    total_organisms = sum(species_dist.values())

    # Metric cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Monitoring Sites</div>
            <div class="metric-value">{len(location_groups)}</div>
            <div class="metric-unit">Active locations</div>
            <div class="metric-trend trend-up">▲ Across Indian coast</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Samples</div>
            <div class="metric-value">{len(samples)}</div>
            <div class="metric-unit">Data points</div>
            <div class="metric-trend trend-neutral">● 30-day period</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Species Detected</div>
            <div class="metric-value">{len(species_dist)}</div>
            <div class="metric-unit">Unique taxa</div>
            <div class="metric-trend trend-up">▲ Biodiversity</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        bloom_status = "critical" if bloom_count > 5 else "normal"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Bloom Events</div>
            <div class="metric-value" style="color: {'#dc2626' if bloom_count > 0 else '#10b981'}">{bloom_count}</div>
            <div class="metric-unit">Detected events</div>
            <div class="metric-trend {'trend-down' if bloom_count > 5 else 'trend-neutral'}">
                {'▼ Requires attention' if bloom_count > 5 else '● Monitoring'}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Location summary
    st.markdown('<p class="section-header">📍 Active Monitoring Stations</p>', unsafe_allow_html=True)

    location_data = []
    for loc_name, loc_samples in location_groups.items():
        sample_ids = [s['sample_id'] for s in loc_samples]
        loc_species = st.session_state.db.get_species_distribution(sample_ids)
        loc_blooms = sum(1 for s in loc_samples
                        if s.get('metadata', {}).get('bloom_detected', False))

        # Determine status badge
        if loc_blooms > len(loc_samples) * 0.3:
            status = '🔴 Critical'
            badge_class = 'badge-critical'
        elif loc_blooms > 0:
            status = '🟠 Warning'
            badge_class = 'badge-warning'
        elif len(loc_samples) >= 20:
            status = '🔵 Research'
            badge_class = 'badge-research'
        elif len(loc_samples) >= 10:
            status = '🔵 Active'
            badge_class = 'badge-active'
        else:
            status = '🟢 Normal'
            badge_class = 'badge-normal'

        location_data.append({
            'Location': loc_name,
            'Water Body': loc_samples[0].get('water_body', 'Unknown'),
            'Samples': len(loc_samples),
            'Species': len(loc_species),
            'Organisms': sum(loc_species.values()),
            'Blooms': loc_blooms,
            'Status': status
        })

    df = pd.DataFrame(location_data).sort_values('Samples', ascending=False)

    st.dataframe(df, width="stretch", hide_index=True, height=300)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🗺️ View Geographic Map", width="stretch", type="primary"):
            st.session_state.current_tab = 1
            st.rerun()

    with col2:
        if st.button("📊 Analyze Data", width="stretch"):
            st.session_state.current_tab = 2
            st.rerun()

    with col3:
        if st.button("📥 Export Reports", width="stretch"):
            st.session_state.current_tab = 3
            st.rerun()


def render_map_page():
    """Render interactive map page"""
    st.markdown("""
    <div class="scientific-header">
        <h1>🗺️ Geographic Distribution</h1>
        <p>Interactive monitoring station map</p>
    </div>
    """, unsafe_allow_html=True)

    map_path = Path("results/maps/judge_demo_professional.html")

    if not map_path.exists():
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Map Not Found</strong><br>
            Initialize the system to generate the geographic map.
        </div>
        """, unsafe_allow_html=True)
        return

    # Legend
    st.markdown('<p class="section-header">📌 Status Indicators</p>', unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown('<span class="status-badge badge-critical">🔴 Critical Bloom</span>',
                   unsafe_allow_html=True)
    with col2:
        st.markdown('<span class="status-badge badge-warning">🟠 Moderate Bloom</span>',
                   unsafe_allow_html=True)
    with col3:
        st.markdown('<span class="status-badge badge-research">🔵 Research Station</span>',
                   unsafe_allow_html=True)
    with col4:
        st.markdown('<span class="status-badge badge-active">🔵 Active Monitoring</span>',
                   unsafe_allow_html=True)
    with col5:
        st.markdown('<span class="status-badge badge-normal">🟢 Normal Status</span>',
                   unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Map info
    st.markdown("""
    <div class="info-box">
        <strong>💡 Interactive Features:</strong>
        <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem;">
            <li>Click markers for detailed station statistics</li>
            <li>Circle size indicates sampling coverage area</li>
            <li>Use measurement tools for distance calculations</li>
            <li>Switch base layers for different views</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Display map
    with open(map_path, 'r') as f:
        map_html = f.read()

    components.html(map_html, height=700, scrolling=True)


def render_data_page():
    """Render data analysis page"""
    st.markdown("""
    <div class="scientific-header">
        <h1>📊 Data Analysis</h1>
        <p>Detailed monitoring records and filtering</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.samples_loaded:
        st.warning("Load data first using the sidebar")
        return

    samples = st.session_state.all_samples
    if not samples:
        st.warning("No samples available")
        return

    # Filters
    st.markdown('<p class="section-header">🔍 Data Filters</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        locations = sorted(set(s.get('location_name', 'Unknown') for s in samples))
        selected_locations = st.multiselect("Filter by Location", options=locations,
                                           default=locations)

    with col2:
        filter_blooms = st.selectbox("Bloom Status",
                                     ["All Samples", "Blooms Only", "No Blooms"])

    with col3:
        min_organisms = st.number_input("Min. Organisms", min_value=0, value=0)

    # Apply filters
    filtered_samples = samples

    if selected_locations:
        filtered_samples = [s for s in filtered_samples
                          if s.get('location_name') in selected_locations]

    if filter_blooms == "Blooms Only":
        filtered_samples = [s for s in filtered_samples
                          if s.get('metadata', {}).get('bloom_detected', False)]
    elif filter_blooms == "No Blooms":
        filtered_samples = [s for s in filtered_samples
                          if not s.get('metadata', {}).get('bloom_detected', False)]

    st.markdown(f"<br><p class='section-header'>Displaying {len(filtered_samples)} of {len(samples)} samples</p>",
               unsafe_allow_html=True)

    # Display data
    display_data = []
    for s in filtered_samples[:100]:
        detections = st.session_state.db.get_sample_detections(s['sample_id'])

        display_data.append({
            'Sample ID': s['sample_id'],
            'Location': s.get('location_name', 'Unknown'),
            'Water Body': s.get('water_body', 'Unknown'),
            'Date': s.get('timestamp', 'Unknown')[:10],
            'Latitude': f"{s.get('latitude', 0):.4f}",
            'Longitude': f"{s.get('longitude', 0):.4f}",
            'Organisms': len(detections),
            'Bloom': '⚠️ Yes' if s.get('metadata', {}).get('bloom_detected') else '✓ No'
        })

    df = pd.DataFrame(display_data)
    st.dataframe(df, width="stretch", hide_index=True, height=400)

    if len(filtered_samples) > 100:
        st.info(f"📊 Showing first 100 of {len(filtered_samples)} filtered samples")

    # Download
    if st.button("📥 Download Filtered Data (CSV)", width="stretch"):
        csv = df.to_csv(index=False)
        st.download_button("⬇️ Download", csv,
                          file_name=f"plankton_data_{datetime.now().strftime('%Y%m%d')}.csv",
                          mime="text/csv", width="stretch")


def render_export_page():
    """Render export page"""
    st.markdown("""
    <div class="scientific-header">
        <h1>📥 Data Export</h1>
        <p>Download location-specific reports</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.samples_loaded:
        st.warning("Load data first")
        return

    samples = st.session_state.all_samples

    # Group by location
    location_groups = defaultdict(list)
    for sample in samples:
        loc_name = sample.get('location_name', 'Unknown')
        location_groups[loc_name].append(sample)

    st.markdown(f'<p class="section-header">{len(location_groups)} Locations Available</p>',
               unsafe_allow_html=True)

    # Select location
    selected_location = st.selectbox("Select Monitoring Station",
                                     options=sorted(location_groups.keys()))

    if selected_location:
        loc_samples = location_groups[selected_location]

        st.markdown(f"<br><h3>📍 {selected_location}</h3>", unsafe_allow_html=True)

        # Metrics
        col1, col2, col3, col4 = st.columns(4)

        sample_ids = [s['sample_id'] for s in loc_samples]
        species = st.session_state.db.get_species_distribution(sample_ids)
        total_organisms = sum(species.values())

        with col1:
            st.metric("Total Samples", len(loc_samples))
        with col2:
            st.metric("Species Found", len(species))
        with col3:
            st.metric("Total Organisms", total_organisms)
        with col4:
            blooms = sum(1 for s in loc_samples
                        if s.get('metadata', {}).get('bloom_detected', False))
            st.metric("Bloom Events", blooms)

        st.markdown("<br>", unsafe_allow_html=True)

        # Species distribution
        st.markdown('<p class="section-header">🧬 Species Composition</p>', unsafe_allow_html=True)

        species_data = [
            {'Species': sp, 'Count': cnt,
             'Percentage': f"{(cnt/total_organisms*100):.1f}%"}
            for sp, cnt in sorted(species.items(), key=lambda x: x[1], reverse=True)
        ]

        st.dataframe(pd.DataFrame(species_data), width="stretch",
                    hide_index=True, height=300)

        # Export button
        if st.button(f"📥 Export {selected_location} Data", type="primary", width="stretch"):
            import subprocess

            with st.spinner(f"Generating report for {selected_location}..."):
                result = subprocess.run(
                    ["python3", "export_location_data.py", "--location", selected_location],
                    capture_output=True, text=True
                )

                if result.returncode == 0:
                    st.success("✓ Export completed successfully")

                    safe_name = selected_location.replace(' ', '_').lower()
                    csv_path = Path(f"exports/{safe_name}_data.csv")

                    if csv_path.exists():
                        with open(csv_path, 'r') as f:
                            csv_data = f.read()

                        st.download_button("⬇️ Download CSV Report", csv_data,
                                         file_name=csv_path.name, mime="text/csv",
                                         width="stretch")
                else:
                    st.error("✗ Export failed")


def render_community_detection_page():
    """Render AquaLens Community Detection page"""
    st.markdown("""
    <div class="scientific-header">
        <h1>🧬 Community Detection Analysis</h1>
        <p>Real-time plankton community detection using GML and BigCLAM</p>
    </div>
    """, unsafe_allow_html=True)

    manager = st.session_state.aqualens_manager

    # Info box
    st.markdown("""
    <div class="info-box">
        <strong>📖 About Community Detection:</strong><br>
        This feature uses advanced graph machine learning (GML) algorithms to detect overlapping communities
        in plankton populations. It processes video streams in real-time, extracting embeddings and spatial
        features to identify co-occurring species and community structures using BigCLAM.
    </div>
    """, unsafe_allow_html=True)

    # Server controls
    st.markdown('<p class="section-header">⚙️ Server Controls</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Start Server", type="primary", use_container_width=True):
            with st.spinner("Starting AquaLens server..."):
                if manager.start_server():
                    st.success("✓ Server started successfully")
                    st.rerun()
                else:
                    st.error("✗ Failed to start server")

    with col2:
        if st.button("🛑 Stop Server", use_container_width=True):
            with st.spinner("Stopping server..."):
                if manager.stop_server():
                    st.success("✓ Server stopped")
                    st.rerun()
                else:
                    st.error("✗ Failed to stop server")

    with col3:
        if st.button("🔄 Refresh Status", use_container_width=True):
            st.rerun()

    # Server status
    status = manager.get_status()
    server_running = status.get("running", False)

    if manager.is_server_running():
        st.markdown("""
        <div class="success-box">
            <strong>✓ Server Status:</strong> Running
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Server Status:</strong> Not running - Start the server to use this feature
        </div>
        """, unsafe_allow_html=True)
        return

    # Pipeline controls
    st.markdown('<p class="section-header">🎬 Pipeline Controls</p>', unsafe_allow_html=True)

    # Configuration
    col1, col2 = st.columns(2)

    with col1:
        input_type = st.radio("Input Source", ["Video File", "Camera"], horizontal=True)

        if input_type == "Video File":
            # List available videos
            video_files = []
            for ext in ['*.mp4', '*.avi', '*.mov']:
                video_files.extend(Path('.').glob(ext))
                video_files.extend(Path('aqualens').glob(ext))
                video_files.extend(Path('Real_Time_Vids').glob(ext))

            video_names = [str(v) for v in video_files]
            if video_names:
                selected_video = st.selectbox("Select Video", video_names)
            else:
                st.warning("No video files found")
                selected_video = st.text_input("Enter video path manually:")
        else:
            camera_index = st.number_input("Camera Index", min_value=0, max_value=10, value=0)

    with col2:
        device = st.selectbox("Processing Device", ["cpu", "cuda"])
        fps_target = st.slider("Target FPS", 1.0, 30.0, 6.0, 0.5)
        window_seconds = st.slider("Analysis Window (seconds)", 1.0, 10.0, 3.0, 0.5)
        use_hdbscan = st.checkbox("Use HDBSCAN Clustering", value=False)
        K_init = st.slider("Number of Communities", 2, 12, 6)

    # Start/Stop pipeline
    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Start Analysis", type="primary", use_container_width=True):
            with st.spinner("Starting pipeline..."):
                if input_type == "Video File":
                    result = manager.start_pipeline(
                        video_path=selected_video,
                        device=device,
                        fps_target=fps_target,
                        window_seconds=window_seconds,
                        use_hdbscan=use_hdbscan,
                        K_init=K_init
                    )
                else:
                    result = manager.start_pipeline(
                        camera_index=camera_index,
                        device=device,
                        fps_target=fps_target,
                        window_seconds=window_seconds,
                        use_hdbscan=use_hdbscan,
                        K_init=K_init
                    )

                if "error" in result:
                    st.error(f"✗ {result['error']}")
                else:
                    st.success(f"✓ Pipeline started: {result.get('status', 'unknown')}")
                    st.rerun()

    with col2:
        if st.button("⏹️ Stop Analysis", use_container_width=True):
            with st.spinner("Stopping pipeline..."):
                result = manager.stop_pipeline()
                if "error" in result:
                    st.error(f"✗ {result['error']}")
                else:
                    st.success("✓ Pipeline stopped")
                    st.rerun()

    # Show pipeline status
    if server_running:
        engine_info = status.get("engine", {})
        if engine_info:
            st.markdown("""
            <div class="success-box">
                <strong>✓ Pipeline Status:</strong> Running<br>
                <strong>Source:</strong> {}<br>
                <strong>Output:</strong> {}
            </div>
            """.format(
                engine_info.get('source', 'Unknown'),
                engine_info.get('outdir', 'Unknown')
            ), unsafe_allow_html=True)

            # Display results
            st.markdown('<p class="section-header">📊 Real-Time Analysis</p>', unsafe_allow_html=True)

            # Create two columns for stream and data
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown("### 🎥 Live Stream")
                # Display the stream using an iframe
                stream_url = manager.get_stream_url()
                st.markdown(f"""
                <iframe src="{stream_url}" width="100%" height="500" frameborder="0"></iframe>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("### 📈 Summary")

                # Auto-refresh data
                summary = manager.get_summary()

                if summary and "error" not in summary:
                    st.metric("Total Nodes", summary.get("total_nodes", 0))

                    species_counts = summary.get("species_counts", {})
                    st.metric("Species Detected", len(species_counts))

                    communities = summary.get("communities", [])
                    st.metric("Communities", len(communities))

                    overlapping = summary.get("overlapping", False)
                    overlap_status = "Yes" if overlapping else "No"
                    st.metric("Overlapping Communities", overlap_status)

                    # Species distribution
                    if species_counts:
                        st.markdown("**Species Distribution:**")
                        for species, count in sorted(species_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                            st.write(f"- {species}: {count}")

                    # Community info
                    if communities:
                        st.markdown("**Community Sizes:**")
                        for comm in communities[:5]:
                            st.write(f"- Community {comm.get('community_id', '?')}: {comm.get('count', 0)} members")

                # Refresh button
                if st.button("🔄 Refresh Data", use_container_width=True):
                    st.rerun()
        else:
            st.markdown("""
            <div class="info-box">
                <strong>💡 Ready to start:</strong> Configure and start the pipeline above
            </div>
            """, unsafe_allow_html=True)


def main():
    """Main application"""
    init_session_state()

    # Sidebar
    render_sidebar()

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Overview",
        "🗺️ Geographic Map",
        "📊 Data Analysis",
        "📥 Export Reports",
        "🧬 Community Detection"
    ])

    with tab1:
        render_home_page()

    with tab2:
        render_map_page()

    with tab3:
        render_data_page()

    with tab4:
        render_export_page()

    with tab5:
        render_community_detection_page()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Standalone Plankton Sample Map Viewer Application
Interactive web interface for viewing and filtering plankton samples by location
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime, timedelta
import json

# Add parent to path
parent_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(parent_dir))

# Import modules
from modules.database import PlanktonDatabase
from modules.map_viewer import PlanktonMapViewer
from modules.cloud_storage import FirebaseStorageManager

# Page config
st.set_page_config(
    page_title="Plankton Sample Map Viewer",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, modern UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin: 1rem 0;
    }

    .subtitle {
        font-size: 1.1rem;
        color: #666;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    .info-box {
        background-color: #e7f3ff;
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }

    .info-box h3 {
        color: #1f77b4;
        margin-top: 0;
    }

    .legend-item {
        padding: 0.4rem 0;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state"""
    if 'db' not in st.session_state:
        # Use judge_demo.db for demo data, fallback to default if not found
        import os
        demo_db = "data/judge_demo.db"
        if os.path.exists(demo_db):
            st.session_state.db = PlanktonDatabase(demo_db)
        else:
            st.session_state.db = PlanktonDatabase()

    if 'firebase' not in st.session_state:
        try:
            st.session_state.firebase = FirebaseStorageManager()
        except:
            st.session_state.firebase = None

    if 'all_samples' not in st.session_state:
        st.session_state.all_samples = []

    if 'filtered_samples' not in st.session_state:
        st.session_state.filtered_samples = []


@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_samples(_db):
    """Load samples from database and Firebase"""
    samples = []

    # Load from local database
    db_samples = _db.get_all_samples_with_location()
    samples.extend(db_samples)

    # Remove duplicates by sample_id
    seen_ids = set()
    unique_samples = []

    for sample in samples:
        sample_id = sample.get('sample_id')
        if sample_id and sample_id not in seen_ids:
            seen_ids.add(sample_id)
            unique_samples.append(sample)

    return unique_samples


def render_sidebar():
    """Render sidebar with filters and controls"""
    with st.sidebar:
        st.markdown("### 🗺️ Map Controls")

        st.markdown("---")

        # Data source selection
        st.markdown("#### 📊 Data Source")

        data_source = st.radio(
            "Load samples from:",
            ["Local Database", "Firebase Cloud", "Both"],
            index=2
        )

        if st.button("🔄 Refresh Data", use_container_width=True):
            # Clear cache and reload
            st.cache_data.clear()
            st.session_state.all_samples = load_samples(st.session_state.db)
            st.session_state.filtered_samples = st.session_state.all_samples
            st.success(f"✅ Loaded {len(st.session_state.all_samples)} samples from inland lakes!")
            st.rerun()

        if st.button("🗑️ Clear All Cache", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ Cache cleared! Reloading...")
            st.rerun()

        st.markdown("---")

        # Filters
        st.markdown("#### 🔍 Filters")

        # Date range filter
        with st.expander("📅 Date Range", expanded=False):
            use_date_filter = st.checkbox("Enable date filter")

            if use_date_filter:
                date_start = st.date_input(
                    "Start date",
                    value=datetime.now() - timedelta(days=30)
                )

                date_end = st.date_input(
                    "End date",
                    value=datetime.now()
                )

        # Location filter
        with st.expander("📍 Location", expanded=False):
            location_names = list(set(
                s.get('location_name', 'Unknown')
                for s in st.session_state.all_samples
                if s.get('location_name')
            ))

            if location_names:
                selected_locations = st.multiselect(
                    "Filter by location:",
                    options=location_names
                )

        # Species filter
        with st.expander("🧬 Species", expanded=False):
            species_filter_enabled = st.checkbox("Filter by species")

            if species_filter_enabled:
                species_name = st.text_input("Species name:")

        # Organism count filter
        with st.expander("🦠 Organism Count", expanded=False):
            min_organisms = st.number_input(
                "Minimum organisms:",
                min_value=0,
                value=0,
                step=1
            )

            max_organisms = st.number_input(
                "Maximum organisms:",
                min_value=0,
                value=1000,
                step=10
            )

        # Apply filters button
        if st.button("✨ Apply Filters", type="primary", use_container_width=True):
            filtered = st.session_state.all_samples.copy()

            # Apply date filter
            if use_date_filter:
                filtered = [
                    s for s in filtered
                    if s.get('timestamp')
                    and date_start <= datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00')).date() <= date_end
                ]

            # Apply location filter
            if selected_locations:
                filtered = [
                    s for s in filtered
                    if s.get('location_name') in selected_locations
                ]

            # Apply organism count filter
            filtered = [
                s for s in filtered
                if min_organisms <= s.get('total_organisms', 0) <= max_organisms
            ]

            st.session_state.filtered_samples = filtered
            st.success(f"Filtered to {len(filtered)} samples")

        if st.button("🔄 Reset Filters", use_container_width=True):
            st.session_state.filtered_samples = st.session_state.all_samples

        st.markdown("---")

        # Map options
        st.markdown("#### 🎨 Map Options")

        use_clustering = st.checkbox("Use marker clustering", value=True)
        show_heatmap = st.checkbox("Show heatmap", value=False)

        st.markdown("---")

        # Export options
        st.markdown("#### 💾 Export")

        if st.button("📥 Export Filtered CSV", use_container_width=True):
            if st.session_state.filtered_samples:
                # Create DataFrame
                df = pd.DataFrame(st.session_state.filtered_samples)

                # Convert to CSV
                csv = df.to_csv(index=False)

                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"plankton_samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        st.markdown("---")

        # Stats
        st.markdown("#### 📊 Statistics")

        st.metric("Total Samples", len(st.session_state.all_samples))
        st.metric("Filtered Samples", len(st.session_state.filtered_samples))

        if st.session_state.filtered_samples:
            total_organisms = sum(s.get('total_organisms', 0) for s in st.session_state.filtered_samples)
            st.metric("Total Organisms", total_organisms)

            # Show locations loaded
            with st.expander("📍 Locations", expanded=False):
                locations = sorted(set(s.get('location_name', 'Unknown') for s in st.session_state.all_samples))
                for loc in locations:
                    count = sum(1 for s in st.session_state.all_samples if s.get('location_name') == loc)
                    st.text(f"• {loc} ({count})")


def render_main_content():
    """Render main map content"""
    st.markdown('<div class="main-header">🗺️ Plankton Sample Map Viewer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Real-time Water Quality Monitoring Across India</div>', unsafe_allow_html=True)

    # Show welcome guide if no data loaded yet
    if not st.session_state.all_samples:
        st.info("👋 **Welcome!** Click **🔄 Refresh Data** in the sidebar to load plankton samples from lakes across India.")

        st.markdown("### 📖 Quick Start Guide")
        st.markdown("""
        1. **Load Data:** Click "🔄 Refresh Data" in the sidebar
        2. **Explore Map:** Click colored markers to see sample details
        3. **Filter Data:** Use sidebar filters to narrow down samples
        4. **Export:** Download filtered data as CSV
        """)

        st.markdown("### 🎨 Marker Color Legend")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🔴 **Red:** Very high (100+ organisms) - Bloom")
            st.markdown("🟠 **Orange:** High density (50-99)")
            st.markdown("🔵 **Blue:** Medium density (10-49)")
        with col2:
            st.markdown("🟢 **Green:** Low density (1-9)")
            st.markdown("⚫ **Gray:** No organisms detected")

        return

    st.markdown("---")

    # Summary stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "📍 Samples on Map",
            len(st.session_state.filtered_samples)
        )

    with col2:
        if st.session_state.filtered_samples:
            total_orgs = sum(s.get('total_organisms', 0) for s in st.session_state.filtered_samples)
            st.metric("🦠 Total Organisms", total_orgs)
        else:
            st.metric("🦠 Total Organisms", 0)

    with col3:
        if st.session_state.filtered_samples:
            unique_locations = len(set(
                s.get('location_name')
                for s in st.session_state.filtered_samples
                if s.get('location_name')
            ))
            st.metric("🌍 Unique Locations", unique_locations)
        else:
            st.metric("🌍 Unique Locations", 0)

    with col4:
        if st.session_state.firebase and st.session_state.firebase.enabled:
            st.metric("☁️ Cloud Status", "Connected", delta="Online")
        else:
            st.metric("☁️ Cloud Status", "Local Only", delta="Offline")

    st.markdown("---")

    # Show color legend (compact version for when data is loaded)
    with st.expander("🎨 Marker Color Guide", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("🔴 Red: 100+ (Bloom)")
            st.markdown("🟠 Orange: 50-99")
            st.markdown("🔵 Blue: 10-49")
        with col2:
            st.markdown("🟢 Green: 1-9")
            st.markdown("⚫ Gray: 0")

    # Generate and display map
    if st.session_state.filtered_samples:
        with st.spinner("Generating interactive map..."):
            viewer = PlanktonMapViewer()

            # Get options from sidebar
            use_clustering = st.session_state.get('use_clustering', True)
            show_heatmap = st.session_state.get('show_heatmap', False)

            # Create map
            m = viewer.create_map_with_samples(
                st.session_state.filtered_samples,
                use_clustering=use_clustering,
                add_heatmap=show_heatmap,
                auto_center=True
            )

            # Try to display using folium's built-in method first
            try:
                # Save map HTML and display
                from streamlit_folium import folium_static
                folium_static(m, width=1400, height=600)
            except ImportError:
                # Fallback to components.html if streamlit_folium not available
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html') as f:
                    m.save(f.name)
                    html_path = f.name

                # Read and display HTML
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()

                # Display in iframe with proper dimensions
                st.markdown("### 🗺️ Interactive Map")
                components.html(html_content, height=700, scrolling=False)

                # Clean up temp file
                try:
                    os.unlink(html_path)
                except:
                    pass

        st.success("✅ Map loaded successfully! Click markers to view sample details.")

        # Show sample list below map
        st.markdown("---")
        st.markdown("### 📋 Sample List")

        # Create DataFrame for display
        display_data = []

        for sample in st.session_state.filtered_samples[:100]:  # Limit to 100 for performance
            display_data.append({
                'Sample ID': sample.get('sample_id', 'N/A'),
                'Location': sample.get('location_name', 'Unknown'),
                'Date': sample.get('timestamp', 'N/A')[:10] if sample.get('timestamp') else 'N/A',
                'Lat': f"{sample.get('latitude', 0):.4f}",
                'Lon': f"{sample.get('longitude', 0):.4f}",
                'Organisms': sample.get('total_organisms', 0),
                'Species': sample.get('species_richness', 0)
            })

        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(df, use_container_width=True)

            if len(st.session_state.filtered_samples) > 100:
                st.info(f"Showing first 100 of {len(st.session_state.filtered_samples)} samples")

    else:
        st.warning("⚠️ No samples match your current filters. Try adjusting the filter settings in the sidebar.")


def main():
    """Main application"""
    initialize_session_state()

    # Load initial data if empty
    if not st.session_state.all_samples:
        with st.spinner("Loading samples from inland lakes..."):
            st.session_state.all_samples = load_samples(st.session_state.db)
            st.session_state.filtered_samples = st.session_state.all_samples

    # Render components
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main()

"""Main Streamlit application for SBM Dashboard – Region X."""

import streamlit as st
import random

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="SBM Dashboard – Region X",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── LOAD CUSTOM CSS ───
try:
    with open("assets/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("⚠️ assets/style.css not found. Proceeding without custom styles.")

# ─── IMPORTS ───
from utils.constants import DIMENSION_NAMES
from utils.data_loader import load_sdo_data, load_all_schools, get_schools_by_sdo, compute_dimension_averages
from utils.map_helpers import add_sdo_shield, add_school_dot
from utils.chart_helpers import create_radar_chart, create_trend_chart, create_indicators_table

# ════════════════════════════════════════════════════════════════
# ✅ CACHE DATA LOADING
# ════════════════════════════════════════════════════════════════

@st.cache_data
def load_cached_data():
    """Load SDO data and generate schools. Cached to prevent regeneration on every rerun."""
    sdo_list = load_sdo_data()
    schools = load_all_schools(sdo_list)
    return sdo_list, schools

# Load data (this runs only once)
sdo_list, schools = load_cached_data()

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════

with st.sidebar:
    st.image("https://www.deped.gov.ph/wp-content/uploads/2021/07/DepEd-logo.png", width=180)
    st.markdown("---")
    st.markdown("### 🗺️ Navigation")
    
    sdo_names = [s["name"] for s in sdo_list]
    selected_sdo_name = st.selectbox("Select Division", options=sdo_names, index=0)
    selected_sdo = next(s for s in sdo_list if s["name"] == selected_sdo_name)
    selected_sdo_id = selected_sdo["id"]
    
    st.markdown("---")
    st.markdown("### 📐 Filter by Dimension")
    selected_dimension = st.selectbox(
        "Highlight Dimension",
        options=["Overall"] + DIMENSION_NAMES,
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🔍 Search School")
    search_query = st.text_input("Type school name or ID", placeholder="e.g., Central")
    
    st.markdown("---")
    st.caption("SBM Digital Twin · Prototype v1.0")
    st.caption("DepEd Region X – Northern Mindanao")

# ════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════

st.markdown(f"## 🎓 SBM Dashboard: {selected_sdo['name']}")
st.caption(f"Capital: {selected_sdo['capital']} · {selected_sdo['id']} schools")

# ─── KPI CARDS ───
schools_in_sdo = get_schools_by_sdo(schools, selected_sdo_id)
complete_schools = [s for s in schools_in_sdo if s["data_status"] != "Pending"]
pending_count = len(schools_in_sdo) - len(complete_schools)
dim_avgs = compute_dimension_averages(schools_in_sdo)

if complete_schools:
    overall_avg = round(sum(s["overall_index"] for s in complete_schools) / len(complete_schools), 1)
    max_dim_idx = dim_avgs.index(max(dim_avgs))
    min_dim_idx = dim_avgs.index(min(dim_avgs))
else:
    overall_avg = 0
    max_dim_idx = 0
    min_dim_idx = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        label="🏫 Total Schools",
        value=len(schools_in_sdo),
        delta=f"{pending_count} pending" if pending_count > 0 else None
    )
with col2:
    st.metric(
        label="📊 Overall SBM Index",
        value=f"{overall_avg:.1f} / 3.0" if overall_avg > 0 else "—",
        delta=None
    )
with col3:
    st.metric(
        label="⬆️ Highest Dimension",
        value=DIMENSION_NAMES[max_dim_idx] if overall_avg > 0 else "—",
        delta=f"{dim_avgs[max_dim_idx]:.1f}" if overall_avg > 0 else None
    )
with col4:
    st.metric(
        label="⬇️ Lowest Dimension (Urgent)",
        value=DIMENSION_NAMES[min_dim_idx] if overall_avg > 0 else "—",
        delta=f"{dim_avgs[min_dim_idx]:.1f}" if overall_avg > 0 else None,
        delta_color="inverse"
    )

# ─── MAP ───
st.markdown("---")

try:
    import folium
    from streamlit_folium import st_folium
    
    # Center map on selected SDO
    map_center = [selected_sdo["lat"], selected_sdo["lng"]]
    m = folium.Map(location=map_center, zoom_start=8, tiles="OpenStreetMap")
    
    # Add SDO shields
    for sdo in sdo_list:
        add_sdo_shield(m, sdo)
    
    # Add school dots
    for school in schools_in_sdo:
        add_school_dot(m, school)
    
    # Display map
    st_folium(m, width=None, height=500, key="sbm_map")
    
except ImportError as e:
    st.error(f"Missing import: {e}. Please run: pip install folium streamlit-folium")
except Exception as e:
    st.error(f"Map rendering failed: {e}")

# ─── MAP LEGEND ───
st.markdown("---")
st.markdown("### 🗺️ Map Legend")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("""
    **🏫 SDO Shields** (Color = Lowest Dimension Score)
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:20px;height:20px;background:#0d9488;clip-path:polygon(50% 0%,100% 20%,90% 80%,50% 100%,10% 80%,0% 20%);"></span>
        <span>2.5 – 3.0 (High)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:20px;height:20px;background:#eab308;clip-path:polygon(50% 0%,100% 20%,90% 80%,50% 100%,10% 80%,0% 20%);"></span>
        <span>2.0 – 2.4 (Medium-High)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:20px;height:20px;background:#f97316;clip-path:polygon(50% 0%,100% 20%,90% 80%,50% 100%,10% 80%,0% 20%);"></span>
        <span>1.0 – 1.9 (Medium-Low)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:20px;height:20px;background:#dc2626;clip-path:polygon(50% 0%,100% 20%,90% 80%,50% 100%,10% 80%,0% 20%);"></span>
        <span>0.0 – 0.9 (Low/Critical)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;font-size:12px;color:#6b7280;">
        <span style="display:inline-block;width:20px;height:20px;border:2px dashed #dc2626;border-radius:4px;"></span>
        <span>Urgent (lowest score < 1.0)</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    **📍 School Dots** (Color = Overall SBM Level)
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:16px;height:16px;border-radius:50%;background:#22c55e;"></span>
        <span>Always Manifested (2.5 – 3.0)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:16px;height:16px;border-radius:50%;background:#eab308;"></span>
        <span>Frequently Manifested (2.0 – 2.4)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:16px;height:16px;border-radius:50%;background:#f97316;"></span>
        <span>Rarely Manifested (1.0 – 1.9)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:16px;height:16px;border-radius:50%;background:#9ca3af;"></span>
        <span>Not Yet Manifested (0.0 – 0.9)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:16px;height:16px;border-radius:50%;background:repeating-linear-gradient(45deg, #9ca3af, #9ca3af 3px, #d1d5db 3px, #d1d5db 6px);border:2px solid #6b7280;"></span>
        <span>Data Pending</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    **🔄 Urgency Glow** (Behind SDO Shields)
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:radial-gradient(circle, #dc2626 30%, transparent 70%);"></span>
        <span>Critical (score < 1.0)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;">
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:radial-gradient(circle, #f97316 30%, transparent 70%);"></span>
        <span>Warning (score 1.0 – 1.9)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;font-size:12px;color:#6b7280;">
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:radial-gradient(circle, #eab308 30%, transparent 70%);"></span>
        <span>Monitor (score 2.0 – 2.4)</span>
    </div>
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0;font-size:12px;color:#6b7280;">
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background:transparent;border:1px solid #d1d5db;"></span>
        <span>Stable (score ≥ 2.5)</span>
    </div>
    """, unsafe_allow_html=True)

st.caption("💡 Click on any SDO shield to zoom in and view its schools. Hover over markers for more details.")

# ─── BOTTOM TABS ───
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📋 Indicators", "📊 Radar Chart", "📈 Historical Trend"])

with tab1:
    df = create_indicators_table(schools_in_sdo)
    if not df.empty:
        st.dataframe(
            df[["#", "Indicator", "Dimension", "Score", "Status"]],
            column_config={
                "Score": st.column_config.NumberColumn(format="%.1f"),
            },
            hide_index=True,
            width='stretch'  # ✅ Updated from use_container_width
        )
        st.caption(f"* Average across {len(complete_schools)} complete schools in this division")
    else:
        st.info("No complete SBM data available for this division.")

with tab2:
    all_complete = [s for s in schools if s["data_status"] != "Pending"]
    reg_avgs = compute_dimension_averages(all_complete)
    if any(dim_avgs):
        fig = create_radar_chart(dim_avgs, reg_avgs)
        st.plotly_chart(fig, width='stretch')  # ✅ Updated
    else:
        st.info("No dimension data available for this division.")

with tab3:
    if complete_schools:
        random.seed(42)  # Stable randomization
        current_avg = overall_avg
        years = ["2023-2024", "2022-2023", "2021-2022"]
        values = [
            current_avg,
            round(max(0, min(3, current_avg - 0.2 + (random.random() - 0.5) * 0.4)), 1),
            round(max(0, min(3, current_avg - 0.4 + (random.random() - 0.5) * 0.4)), 1)
        ]
        fig = create_trend_chart(years, values)
        st.plotly_chart(fig, width='stretch')  # ✅ Updated
    else:
        st.info("No historical data available for this division.")

# ─── SEARCH FUNCTIONALITY ───
if search_query:
    st.markdown("---")
    st.markdown(f"### 🔍 Search Results for '{search_query}'")
    
    matches = [s for s in schools if search_query.lower() in s["name"].lower() or search_query in s["id"]]
    
    if matches:
        for match in matches:
            sdo = next(s for s in sdo_list if s["id"] == match["sdo_id"])
            st.write(f"• **{match['name']}** ({match['type']}) – {sdo['name']}")
    else:
        st.info("No schools found matching your search.")

# ─── FOOTER ───
st.markdown("---")
st.caption("© 2024 DepEd Region X – SBM Digital Twin Dashboard · Built with Streamlit")

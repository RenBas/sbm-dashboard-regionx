"""Main Streamlit application for SBM Dashboard – Region X."""

import streamlit as st
import random
import base64

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="SBM Dashboard – Region X",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM THEME ───
if "custom_theme" not in st.session_state:
    st.session_state.custom_theme = "light"

if st.session_state.custom_theme == "dark":
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117 !important; }
        .stApp > header { background-color: #1A1C23 !important; }
        .stApp > header [data-testid="stToolbar"] { background-color: #1A1C23 !important; }
        .stSidebar { background-color: #1A1C23 !important; }
        .stSidebar [data-testid="stSidebarContent"] { background-color: #1A1C23 !important; }
        .stSidebar .stMarkdown, .stSidebar .stSelectbox, .stSidebar .stTextInput { color: #FAFAFA !important; }
        .stSidebar .stSelectbox label, .stSidebar .stTextInput label { color: #FAFAFA !important; }
        .stSidebar .stSelectbox select, .stSidebar .stTextInput input { background-color: #262730 !important; color: #FAFAFA !important; border-color: #4A4A5A !important; }
        .stSidebar .stSelectbox select option { background-color: #262730 !important; color: #FAFAFA !important; }
        .stSidebar .stButton button { background-color: #262730 !important; color: #FAFAFA !important; border-color: #4A4A5A !important; }
        .stSidebar .stButton button:hover { background-color: #3A3A4A !important; }
        .stSidebar .stButton button[data-baseweb="button"][data-theme="primary"] { background-color: #0033A0 !important; color: #FFFFFF !important; }
        .stMarkdown, .stCaption, .stMetric label, .stMetric div { color: #FAFAFA !important; }
        .stMetric { background-color: #1A1C23 !important; border-color: #2A2C33 !important; }
        .stMetric [data-testid="metric-value"] { color: #FAFAFA !important; }
        .stTabs [data-baseweb="tab-list"] { background-color: #1A1C23 !important; border-bottom-color: #2A2C33 !important; }
        .stTabs [data-baseweb="tab"] { color: #9CA3AF !important; }
        .stTabs [data-baseweb="tab"]:hover { color: #FAFAFA !important; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] { color: #FAFAFA !important; border-bottom-color: #0033A0 !important; }
        .stDataFrame { border-color: #2A2C33 !important; }
        .stDataFrame thead tr th { background-color: #1A1C23 !important; color: #FAFAFA !important; }
        .stDataFrame tbody tr td { color: #FAFAFA !important; border-bottom-color: #2A2C33 !important; }
        .stDataFrame tbody tr:hover td { background-color: #262730 !important; }
        .stAlert { background-color: #1A1C23 !important; border-color: #2A2C33 !important; color: #FAFAFA !important; }
        .stAlert .stMarkdown { color: #FAFAFA !important; }
        .stInfo { background-color: #1A1C23 !important; border-color: #0033A0 !important; }
        .stInfo .stMarkdown { color: #FAFAFA !important; }
        .stSelectbox label, .stTextInput label { color: #FAFAFA !important; }
        .stSelectbox select, .stTextInput input { background-color: #262730 !important; color: #FAFAFA !important; border-color: #4A4A5A !important; }
        .stSelectbox select option { background-color: #262730 !important; color: #FAFAFA !important; }
        hr { border-color: #2A2C33 !important; }
        h1, h2, h3, h4, h5, h6 { color: #FAFAFA !important; }
        .custom-footnote { background-color: #1A1C23 !important; border-left: 4px solid #0033A0 !important; color: #FAFAFA !important; }
        .custom-footnote .text-muted { color: #9CA3AF !important; }
        /* HIDE STREAMLIT FOOTER */
        footer { visibility: hidden !important; }
        .stApp > footer { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .custom-footnote { background-color: #F8F9FA !important; border-left: 4px solid #0033A0 !important; color: #1A1A2E !important; }
        .custom-footnote .text-muted { color: #6B7280 !important; }
        footer { visibility: hidden !important; }
        .stApp > footer { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# ─── LOAD CUSTOM CSS ───
try:
    with open("assets/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

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
    sdo_list = load_sdo_data()
    schools = load_all_schools(sdo_list)
    return sdo_list, schools

sdo_list, schools = load_cached_data()

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════

with st.sidebar:
    # ── Logo (using base64 to avoid broken image) ──
    # DepEd logo base64 (small version)
    logo_base64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAABkCAYAAABw4pVUAAAACXBIWXMAAAsTAAALEwEAmpwYAAAFsGlUWHRYTUw6Y29tLmFkb2JlLnhtcAAAAAAAPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNy4wLWNjMDAgNzkuMTY0NzU2LCAyMDIxLzExLzE1LTEw6jI3OjU5ICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iIHhtbG5zOmRjPSJodHRwOi8vcHVybC5vcmcvZGMvZWxlbWVudHMvMS4xLyIgeG1sbnM6cGhvdG9zaG9wPSJodHRwOi8vbnMuYWRvYmUuY29tL3Bob3Rvc2hvcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RFdnQ9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZUV2ZW50IyIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgMjIuNSAoV2luZG93cykiIHhtcDpDcmVhdGVEYXRlPSIyMDIzLTAzLTIwVDA0OjUzOjU5KzA4OjAwIiB4bXA6TW9kaWZ5RGF0ZT0iMjAyMy0wMy0yMFQwNDo1NTozMiswODowMCIgeG1wOk1ldGFkYXRhRGF0ZT0iMjAyMy0wMy0yMFQwNDo1NTozMiswODowMCIgZGM6Zm9ybWF0PSJpbWFnZS9wbmciIHBob3Rvc2hvcDpDb2xvck1vZGU9IjMiIHBob3Rvc2hvcDpJQ0NQcm9maWxlPSJzUkdCIElFQzYxOTY2LTIuMSIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo4Y2U5Y2ZkMC1hNzVhLTQ5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"
    
    st.markdown(f'<img src="{logo_base64}" width="150" style="display:block;margin-left:auto;margin-right:auto;margin-bottom:10px;">', unsafe_allow_html=True)
    
    # ── Appearance ──
    st.markdown("---")
    st.markdown("### 🎨 Appearance")
    col_light, col_dark = st.columns(2)
    with col_light:
        if st.button("☀️ Light", use_container_width=True,
                     type="primary" if st.session_state.custom_theme == "light" else "secondary"):
            st.session_state.custom_theme = "light"
            st.rerun()
    with col_dark:
        if st.button("🌙 Dark", use_container_width=True,
                     type="primary" if st.session_state.custom_theme == "dark" else "secondary"):
            st.session_state.custom_theme = "dark"
            st.rerun()
    
    # ── Navigation ──
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
# MAIN CONTENT (same as before)
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
    st.metric("🏫 Total Schools", len(schools_in_sdo), delta=f"{pending_count} pending" if pending_count > 0 else None)
with col2:
    st.metric("📊 Overall SBM Index", f"{overall_avg:.1f} / 3.0" if overall_avg > 0 else "—")
with col3:
    st.metric("⬆️ Highest Dimension", DIMENSION_NAMES[max_dim_idx] if overall_avg > 0 else "—")
with col4:
    st.metric("⬇️ Lowest Dimension (Urgent)", DIMENSION_NAMES[min_dim_idx] if overall_avg > 0 else "—", delta_color="inverse")

# ─── MAP ───
st.markdown("---")

try:
    import folium
    from streamlit_folium import st_folium
    
    map_center = [selected_sdo["lat"], selected_sdo["lng"]]
    m = folium.Map(location=map_center, zoom_start=8, tiles="OpenStreetMap")
    
    for sdo in sdo_list:
        add_sdo_shield(m, sdo)
    
    for school in schools_in_sdo:
        add_school_dot(m, school)
    
    st_folium(m, width=None, height=500, key="sbm_map")
    
except ImportError as e:
    st.error(f"Missing import: {e}. Please run: pip install folium streamlit-folium")
except Exception as e:
    st.error(f"Map rendering failed: {e}")

# ─── MAP LEGEND WITH FOOTNOTE ───
st.markdown("---")

st.markdown("""
<div class="custom-footnote" style="padding:14px 18px;border-radius:8px;margin-bottom:14px;">
    <b>💡 About the Pulsing Glow:</b> The animated glow behind each SDO shield indicates <b>urgency based on the division's lowest SBM dimension score</b>.
    <br><br>
    <div style="display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:4px;">
        <span style="color:#dc2626;font-weight:600;">🔴 Red glow</span>
        <span>Critical – Score &lt; 1.0</span>
        <span class="text-muted" style="font-size:12px;">(Immediate attention needed)</span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:12px 24px;">
        <span style="color:#f97316;font-weight:600;">🟠 Orange glow</span>
        <span>Warning – Score 1.0 – 1.9</span>
        <span class="text-muted" style="font-size:12px;">(Monitor closely)</span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:12px 24px;">
        <span style="color:#eab308;font-weight:600;">🟡 Yellow glow</span>
        <span>Monitor – Score 2.0 – 2.4</span>
        <span class="text-muted" style="font-size:12px;">(Improvement needed)</span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:12px 24px;">
        <span style="font-weight:600;opacity:0.4;">⚪ No glow</span>
        <span>Stable – Score ≥ 2.5</span>
        <span class="text-muted" style="font-size:12px;">(Performing well)</span>
    </div>
    <div style="margin-top:8px;font-size:12px;opacity:0.6;">
        The glow pulses faster and brighter for more urgent divisions.
    </div>
</div>
""", unsafe_allow_html=True)

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
            column_config={"Score": st.column_config.NumberColumn(format="%.1f")},
            hide_index=True,
            width='stretch'
        )
        st.caption(f"* Average across {len(complete_schools)} complete schools in this division")
    else:
        st.info("No complete SBM data available for this division.")

with tab2:
    all_complete = [s for s in schools if s["data_status"] != "Pending"]
    reg_avgs = compute_dimension_averages(all_complete)
    if any(dim_avgs):
        fig = create_radar_chart(dim_avgs, reg_avgs)
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No dimension data available for this division.")

with tab3:
    if complete_schools:
        random.seed(42)
        current_avg = overall_avg
        years = ["2023-2024", "2022-2023", "2021-2022"]
        values = [
            current_avg,
            round(max(0, min(3, current_avg - 0.2 + (random.random() - 0.5) * 0.4)), 1),
            round(max(0, min(3, current_avg - 0.4 + (random.random() - 0.5) * 0.4)), 1)
        ]
        fig = create_trend_chart(years, values)
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("No historical data available for this division.")

# ─── SEARCH ───
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

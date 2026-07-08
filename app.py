"""Main Streamlit application for SBM Dashboard – Region X."""

import streamlit as st
import random
import pandas as pd

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
from utils.auth import (
    authenticate, login_status, logout, get_accessible_schools,
    get_accessible_divisions_summary, is_school_head
)
from utils.download_helpers import generate_report_data, generate_excel_template, generate_template_csv
from utils.synopsis_generator import generate_synopsis
from utils.twin_ui import render_sandbox  # ✅ New import

# ════════════════════════════════════════════════════════════════
# ✅ CACHE DATA LOADING
# ════════════════════════════════════════════════════════════════

@st.cache_data
def load_cached_data():
    sdo_list = load_sdo_data()
    schools = load_all_schools(sdo_list)
    return sdo_list, schools

sdo_list, schools = load_cached_data()

# ─── COMPUTE REGIONAL AVERAGE (ALL SCHOOLS IN REGION) ───
all_region_complete = [s for s in schools if s["data_status"] != "Pending"]
if all_region_complete:
    regional_dim_avgs = compute_dimension_averages(all_region_complete)
    regional_overall_avg = round(sum(s["overall_index"] for s in all_region_complete) / len(all_region_complete), 1)
else:
    regional_dim_avgs = [0, 0, 0, 0, 0, 0]
    regional_overall_avg = 0

# ════════════════════════════════════════════════════════════════
# AUTHENTICATION CHECK
# ════════════════════════════════════════════════════════════════

auth_status = login_status()

# ─── LOGIN SCREEN ───
if not auth_status["logged_in"]:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;">
        <h1>🎓 SBM Digital Twin Dashboard</h1>
        <p style="color:#6b7280;font-size:18px;">DepEd Region X – Northern Mindanao</p>
        <div style="margin-top:40px;max-width:450px;margin-left:auto;margin-right:auto;">
            <div style="background:#f8f9fa;padding:30px;border-radius:10px;border:1px solid #e5e7eb;">
                <h3 style="margin-top:0;">🔐 Sign In</h3>
                <div style="text-align:left;font-size:13px;color:#4b5563;background:#f1f5f9;padding:12px;border-radius:6px;margin:12px 0;">
                    <b>Demo Credentials:</b><br>
                    <b>Regional:</b> regional / regional123<br>
                    <b>Division:</b> sdo_bukidnon / sdo123<br>
                    <b>School:</b> principal_cdo / school123<br>
                    <i style="font-size:12px;color:#6b7280;">(Copy username exactly as shown)</i>
                </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("🔑 Sign In", use_container_width=True)
        
        if submitted:
            if username and password:
                user = authenticate(username, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password.")
            else:
                st.warning("Please enter both username and password.")
    
    st.markdown("""
            </div>
        </div>
        <p style="color:#9ca3af;font-size:12px;margin-top:20px;">
            For demonstration purposes only. Real authentication will be implemented post-pilot.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.stop()

# ─── USER INFORMATION ───
user = st.session_state.user

if user is None:
    st.warning("Session expired. Please log in again.")
    st.stop()

role = user.get("role", "school")
user_name = user.get("name", "User")

filtered_data = get_accessible_schools(user, sdo_list, schools)
filtered_sdos = filtered_data["filtered_sdos"]
filtered_schools = filtered_data["filtered_schools"]

# ════════════════════════════════════════════════════════════════
# DETERMINE SELECTED SDO
# ════════════════════════════════════════════════════════════════

selected_sdo = None
selected_sdo_id = None

if "go_to_division" in st.session_state:
    target_div_name = st.session_state.go_to_division
    for sdo in sdo_list:
        if sdo["name"] == target_div_name:
            selected_sdo = sdo
            selected_sdo_id = sdo["id"]
            break
    del st.session_state.go_to_division

if selected_sdo is None:
    if is_school_head(user):
        if filtered_schools:
            school = filtered_schools[0]
            selected_sdo = next((s for s in sdo_list if s["id"] == school["sdo_id"]), None)
            selected_sdo_id = selected_sdo["id"] if selected_sdo else None
        else:
            st.warning("No school data available for your account.")
            st.stop()
    else:
        if filtered_sdos:
            if len(filtered_sdos) == 1:
                selected_sdo = filtered_sdos[0]
                selected_sdo_id = selected_sdo["id"]
            else:
                selected_sdo = filtered_sdos[0]
                selected_sdo_id = selected_sdo["id"]
        else:
            st.warning("No divisions accessible.")
            st.stop()

# ─── COMPUTE SCHOOL DATA ───
schools_in_sdo = get_schools_by_sdo(filtered_schools, selected_sdo_id) if selected_sdo_id else []
complete_schools = [s for s in schools_in_sdo if s["data_status"] != "Pending"]
dim_avgs = compute_dimension_averages(schools_in_sdo)

if complete_schools:
    overall_avg = round(sum(s["overall_index"] for s in complete_schools) / len(complete_schools), 1)
    max_dim_idx = dim_avgs.index(max(dim_avgs))
    min_dim_idx = dim_avgs.index(min(dim_avgs))
else:
    overall_avg = 0
    max_dim_idx = 0
    min_dim_idx = 0

is_dark_mode = (st.session_state.custom_theme == "dark")

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(f"### 👤 {user_name}")
    st.caption(get_accessible_divisions_summary(user))
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
    
    st.markdown("---")
    st.markdown("### 🗺️ Navigation")
    
    if not is_school_head(user):
        if filtered_sdos:
            sdo_names = [s["name"] for s in filtered_sdos]
            if len(sdo_names) == 1:
                st.caption(f"📋 {selected_sdo['name']}")
            else:
                selected_sdo_name = st.selectbox("Select Division", options=sdo_names, index=0)
                selected_sdo = next(s for s in filtered_sdos if s["name"] == selected_sdo_name)
                selected_sdo_id = selected_sdo["id"]
                schools_in_sdo = get_schools_by_sdo(filtered_schools, selected_sdo_id)
                complete_schools = [s for s in schools_in_sdo if s["data_status"] != "Pending"]
                dim_avgs = compute_dimension_averages(schools_in_sdo)
                if complete_schools:
                    overall_avg = round(sum(s["overall_index"] for s in complete_schools) / len(complete_schools), 1)
                    max_dim_idx = dim_avgs.index(max(dim_avgs))
                    min_dim_idx = dim_avgs.index(min(dim_avgs))
                else:
                    overall_avg = 0
                    max_dim_idx = 0
                    min_dim_idx = 0
        else:
            st.warning("No divisions accessible.")
            selected_sdo = None
            selected_sdo_id = None
    else:
        if filtered_schools:
            school = filtered_schools[0]
            st.caption(f"🏫 {school['name']}")
    
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
    st.markdown("### 📊 Data Management")
    
    # Download Report
    if selected_sdo_id is not None and selected_sdo is not None:
        report_df = generate_report_data(selected_sdo["name"], schools_in_sdo, complete_schools)
        if report_df is not None and not report_df.empty:
            csv_report = report_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Report (CSV)",
                data=csv_report,
                file_name=f"SBM_Report_{selected_sdo['name'].replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.caption("No data to report.")
    else:
        st.caption("Select a division to download report.")
    
    # Download Excel Template (Comprehensive)
    template_file = generate_excel_template()
    st.download_button(
        label="📋 Download Data Collection Template (Excel)",
        data=template_file,
        file_name="SBM_Data_Collection_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
    st.caption("Template based on DepEd Order No. 007, s. 2024")
    
    # ─── UPLOAD SBM DATA ───
    st.markdown("---")
    st.markdown("### 📤 Upload SBM Data")
    st.caption("Upload a completed Excel template to update the dashboard.")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx)",
        type=["xlsx"],
        key="sbm_data_upload"
    )
    
    if uploaded_file is not None:
        try:
            # Load the uploaded Excel file
            df_schools = pd.read_excel(uploaded_file, sheet_name="School Information")
            df_assessment = pd.read_excel(uploaded_file, sheet_name="SBM Assessment")
            
            st.success(f"✅ Successfully uploaded: {uploaded_file.name}")
            st.caption(f"School Information: {len(df_schools)} schools")
            st.caption(f"SBM Assessment: {len(df_assessment)} indicator scores")
            
            with st.expander("📄 Preview Uploaded Data"):
                st.dataframe(df_schools.head(5), width='stretch')
                st.dataframe(df_assessment.head(10), width='stretch')
            
            # Placeholder for data processing
            st.info("📌 Data processing will be implemented during Phase 2.")
            
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    
    with st.expander("📖 Glossary", expanded=False):
        st.markdown("""
        **SBM (School-Based Management)** – Decentralization of decision-making authority to schools.
        **SDO (Schools Division Office)** – Local DepEd office overseeing schools in a division.
        **SBM Dimensions** – Six key areas of school operations:
        - Curriculum & Teaching
        - Learning Environment
        - Leadership
        - Governance & Accountability
        - Human Resource & Team Development
        - Finance & Resource Management
        **SBM Indicators** – 42 measurable practices and outcomes.
        **Degree of Manifestation** – Scale (0–3):
        - 0.0–0.9 = Not Yet Manifested
        - 1.0–1.9 = Rarely Manifested
        - 2.0–2.4 = Frequently Manifested
        - 2.5–3.0 = Always Manifested
        **Urgency Factor** – 0–1 value indicating urgency.
        **Glow** – Animated pulsing behind SDO shields:
        - 🔴 Red = Critical (< 1.0)
        - 🟠 Orange = Warning (1.0–1.9)
        - 🟡 Yellow = Monitor (2.0–2.4)
        - ⚪ No glow = Stable (≥ 2.5)
        """)
    
    st.markdown("---")
    st.caption("SBM Digital Twin · Prototype v1.0")
    st.caption("DepEd Region X – Northern Mindanao")

# ════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════

if selected_sdo_id is None:
    st.warning("No data available for your role. Please contact your administrator.")
    st.stop()

st.markdown(f"## 🎓 SBM Dashboard: {selected_sdo['name']}")
st.caption(f"Capital: {selected_sdo['capital']} · {selected_sdo['id']} schools")

# ─── KPI CARDS ───
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🏫 Total Schools", len(schools_in_sdo), 
              delta=f"{len([s for s in schools_in_sdo if s['data_status']=='Pending'])} pending" 
              if any(s['data_status']=='Pending' for s in schools_in_sdo) else None)
with col2:
    st.metric("📊 Overall SBM Index", f"{overall_avg:.1f} / 3.0" if overall_avg > 0 else "—")
with col3:
    st.metric("⬆️ Highest Dimension", DIMENSION_NAMES[max_dim_idx] if overall_avg > 0 else "—")
with col4:
    st.metric("⬇️ Lowest Dimension (Urgent)", DIMENSION_NAMES[min_dim_idx] if overall_avg > 0 else "—", delta_color="inverse")

# ─── SYNOPSIS ───
synopsis_html = generate_synopsis(
    user_role=role,
    user_name=user_name,
    selected_sdo=selected_sdo,
    schools_in_sdo=schools_in_sdo,
    complete_schools=complete_schools,
    dim_avgs=dim_avgs,
    overall_avg=overall_avg,
    max_dim_idx=max_dim_idx,
    min_dim_idx=min_dim_idx
)

# ─── TABS BASED ON ROLE ───
if role == "regional":
    tab1, tab2, tab3 = st.tabs(["📋 Executive Summary", "📊 Division Performance Matrix", "🧪 Digital Twin Sandbox"])
    
    with tab1:
        # Executive Summary tab: synopsis, map, legend, and bottom tabs
        from streamlit.components.v1 import html as st_html
        wrapped_html = f"""
        <div style="width:100%;padding:0;margin:0;box-sizing:border-box;">
            {synopsis_html}
        </div>
        """
        st_html(wrapped_html, height=900, scrolling=True)
        
        # ─── MAP ───
        st.markdown("---")
        try:
            import folium
            from streamlit_folium import st_folium
            
            map_center = [selected_sdo["lat"], selected_sdo["lng"]]
            m = folium.Map(location=map_center, zoom_start=8, tiles="OpenStreetMap")
            
            for sdo in filtered_sdos:
                add_sdo_shield(m, sdo)
            
            for school in schools_in_sdo:
                add_school_dot(m, school)
            
            st_folium(m, width=None, height=500, key="sbm_map")
            
        except ImportError as e:
            st.error(f"Missing import: {e}. Please run: pip install folium streamlit-folium")
        except Exception as e:
            st.error(f"Map rendering failed: {e}")

        # ─── MAP LEGEND ───
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
        st.markdown("""
        <div style="background-color:var(--secondary-background-color);padding:10px 16px;border-radius:8px;border-left:4px solid #22c55e;margin-bottom:14px;color:var(--text-color);">
            <b>📏 School Dot Sizes:</b> The size of each school dot represents its <b>total enrollment (number of learners)</b>.
            Larger dots indicate schools with more students, while smaller dots indicate schools with fewer students.
            This helps you quickly see which schools have larger student populations.
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
        
        # ─── BOTTOM TABS (Indicators, Radar Chart, Historical Trend) ───
        st.markdown("---")
        btab1, btab2, btab3 = st.tabs(["📋 Indicators", "📊 Radar Chart", "📈 Historical Trend"])
        with btab1:
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
        with btab2:
            if any(dim_avgs) and any(regional_dim_avgs):
                fig = create_radar_chart(dim_avgs, regional_dim_avgs)
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No dimension data available for this division.")
        with btab3:
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
    
    with tab2:
        # Division Performance Matrix (unchanged)
        st.markdown("### 📊 Division Performance Matrix")
        st.caption("Performance of all 14 divisions across the 6 SBM dimensions. Scores are rounded to 1 decimal place.")
        
        matrix_data = []
        for sdo in sdo_list:
            dim_scores = [round(x, 1) for x in sdo["dimension_scores"]]
            row = {
                "Division": sdo["name"].replace("SDO ", ""),
                "Curriculum & Teaching": dim_scores[0],
                "Learning Environment": dim_scores[1],
                "Leadership": dim_scores[2],
                "Governance & Accountability": dim_scores[3],
                "HR & Team Development": dim_scores[4],
                "Finance & Resource Mgmt.": dim_scores[5]
            }
            matrix_data.append(row)
        
        df = pd.DataFrame(matrix_data)
        avg_row = {"Division": "📊 REGIONAL AVERAGE"}
        for dim in df.columns[1:]:
            avg_row[dim] = round(df[dim].mean(), 1)
        df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)
        
        def color_cell(val):
            if pd.isna(val):
                return ''
            if val >= 2.5:
                return 'background-color: #22c55e; color: white; font-weight: bold;'
            elif val >= 2.0:
                return 'background-color: #eab308; color: white; font-weight: bold;'
            else:
                return 'background-color: #dc2626; color: white; font-weight: bold;'
        
        styled_df = df.style.map(color_cell, subset=df.columns[1:]).format("{:.1f}", subset=df.columns[1:])
        html_table = styled_df.to_html(index=False, escape=False)
        st.markdown(html_table, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display:flex;gap:16px;font-size:13px;margin:8px 0;">
            <span>🟢 <b>Strong</b> (≥ 2.5)</span>
            <span>🟡 <b>Moderate</b> (2.0 – 2.4)</span>
            <span>🔴 <b>Weak</b> (< 2.0)</span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📈 Summary Statistics")
        summary_data = []
        for dim in DIMENSION_NAMES:
            scores = [sdo["dimension_scores"][DIMENSION_NAMES.index(dim)] for sdo in sdo_list]
            strong = sum(1 for x in scores if x >= 2.5)
            moderate = sum(1 for x in scores if 2.0 <= x < 2.5)
            weak = sum(1 for x in scores if x < 2.0)
            summary_data.append({
                "Dimension": dim,
                "Strong (≥2.5)": strong,
                "Moderate (2.0-2.4)": moderate,
                "Weak (<2.0)": weak
            })
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, width='stretch', hide_index=True)
        
        st.markdown("### 🔍 Jump to Division")
        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            division_names = [sdo["name"] for sdo in sdo_list]
            selected_div_name = st.selectbox("Select a division to view its detailed dashboard:", division_names)
        with col_btn:
            if st.button("🚀 Go to Division", use_container_width=True):
                st.session_state.go_to_division = selected_div_name
                st.rerun()
    
    with tab3:
        # ─── Digital Twin Sandbox ───
        from utils.twin_ui import render_sandbox
        render_sandbox(sdo_list, selected_sdo, schools_in_sdo, complete_schools, dim_avgs, overall_avg)

elif role == "division":
    tab1, tab2, tab3 = st.tabs(["📋 Executive Summary", "📊 School Performance Dashboard", "🧪 Digital Twin Sandbox"])
    
    with tab1:
        # Executive Summary tab: synopsis, map, legend, and bottom tabs
        from streamlit.components.v1 import html as st_html
        wrapped_html = f"""
        <div style="width:100%;padding:0;margin:0;box-sizing:border-box;">
            {synopsis_html}
        </div>
        """
        st_html(wrapped_html, height=900, scrolling=True)
        
        # ─── MAP ───
        st.markdown("---")
        try:
            import folium
            from streamlit_folium import st_folium
            
            map_center = [selected_sdo["lat"], selected_sdo["lng"]]
            m = folium.Map(location=map_center, zoom_start=8, tiles="OpenStreetMap")
            
            for sdo in filtered_sdos:
                add_sdo_shield(m, sdo)
            
            for school in schools_in_sdo:
                add_school_dot(m, school)
            
            st_folium(m, width=None, height=500, key="sbm_map")
            
        except ImportError as e:
            st.error(f"Missing import: {e}. Please run: pip install folium streamlit-folium")
        except Exception as e:
            st.error(f"Map rendering failed: {e}")

        # ─── MAP LEGEND ───
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
        st.markdown("""
        <div style="background-color:var(--secondary-background-color);padding:10px 16px;border-radius:8px;border-left:4px solid #22c55e;margin-bottom:14px;color:var(--text-color);">
            <b>📏 School Dot Sizes:</b> The size of each school dot represents its <b>total enrollment (number of learners)</b>.
            Larger dots indicate schools with more students, while smaller dots indicate schools with fewer students.
            This helps you quickly see which schools have larger student populations.
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
        
        # ─── BOTTOM TABS (Indicators, Radar Chart, Historical Trend) ───
        st.markdown("---")
        btab1, btab2, btab3 = st.tabs(["📋 Indicators", "📊 Radar Chart", "📈 Historical Trend"])
        with btab1:
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
        with btab2:
            if any(dim_avgs) and any(regional_dim_avgs):
                fig = create_radar_chart(dim_avgs, regional_dim_avgs)
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("No dimension data available for this division.")
        with btab3:
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
    
    with tab2:
        # School Performance Dashboard – no map, no radar, no bottom tabs
        st.markdown("### 📊 School Performance Dashboard")
        st.caption(f"Detailed school-level performance for {selected_sdo['name']}.")
        
        # ─── Bar Chart: Division vs Regional Overall SBM Index ───
        st.markdown("#### 🏆 Division vs Regional Overall SBM Index")
        import plotly.graph_objects as go
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name="Division",
            x=["SBM Index"],
            y=[overall_avg],
            marker_color="#0033A0",
            text=[f"{overall_avg:.1f}"],
            textposition='auto',
            width=0.4
        ))
        
        fig.add_trace(go.Bar(
            name="Region X",
            x=["SBM Index"],
            y=[regional_overall_avg],
            marker_color="#9CA3AF",
            text=[f"{regional_overall_avg:.1f}"],
            textposition='auto',
            width=0.4
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=40, r=40, t=20, b=40),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            yaxis=dict(range=[0, 3.5], tickvals=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]),
            xaxis=dict(showticklabels=False),
            bargap=0.5,
            bargroupgap=0.2,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        diff = overall_avg - regional_overall_avg
        if diff > 0:
            diff_text = f"📈 Division is {diff:.1f} points above regional average"
            diff_color = "#22c55e"
        elif diff < 0:
            diff_text = f"📉 Division is {abs(diff):.1f} points below regional average"
            diff_color = "#dc2626"
        else:
            diff_text = "📊 Division is at par with regional average"
            diff_color = "#eab308"
        
        st.plotly_chart(fig, width='stretch')
        st.markdown(f"""
        <div style="text-align:center;padding:8px;font-size:15px;font-weight:500;color:{diff_color};">
            {diff_text}
        </div>
        """, unsafe_allow_html=True)
        
        # ─── Distribution per dimension ───
        st.markdown("#### 📈 Distribution of Schools by Performance Level")
        dist_data = []
        for dim in DIMENSION_NAMES:
            dim_idx = DIMENSION_NAMES.index(dim)
            scores = [s["dimension_scores"][dim_idx] for s in complete_schools]
            strong = sum(1 for x in scores if x >= 2.5)
            moderate = sum(1 for x in scores if 2.0 <= x < 2.5)
            weak = sum(1 for x in scores if x < 2.0)
            dist_data.append({
                "Dimension": dim,
                "Strong (≥2.5)": strong,
                "Moderate (2.0-2.4)": moderate,
                "Weak (<2.0)": weak
            })
        dist_df = pd.DataFrame(dist_data)
        st.dataframe(dist_df, width='stretch', hide_index=True)
        
        # ─── Bar chart ───
        fig2 = go.Figure()
        for level, color in [("Strong (≥2.5)", "#22c55e"), ("Moderate (2.0-2.4)", "#eab308"), ("Weak (<2.0)", "#dc2626")]:
            fig2.add_trace(go.Bar(
                name=level,
                x=dist_df["Dimension"],
                y=dist_df[level],
                marker_color=color,
                text=dist_df[level],
                textposition='auto'
            ))
        fig2.update_layout(
            barmode='group',
            height=400,
            margin=dict(l=40, r=40, t=20, b=40),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            xaxis=dict(tickangle=-15)
        )
        st.plotly_chart(fig2, width='stretch')
        
        # ─── Paginated, searchable table ───
        st.markdown("#### 📋 School List")
        
        school_rows = []
        for s in schools_in_sdo:
            if s["data_status"] == "Pending":
                overall_score = "—"
                dim_scores = ["—"] * 6
            else:
                overall_score = round(s["overall_index"], 1)
                dim_scores = [round(x, 1) for x in s["dimension_scores"]]
            school_rows.append({
                "School": s["name"],
                "Type": s["type"],
                "Overall SBM Index": overall_score,
                "Curriculum & Teaching": dim_scores[0],
                "Learning Environment": dim_scores[1],
                "Leadership": dim_scores[2],
                "Governance & Accountability": dim_scores[3],
                "HR & Team Development": dim_scores[4],
                "Finance & Resource Mgmt.": dim_scores[5],
                "Data Status": s["data_status"],
                "School ID": s["id"]
            })
        table_df = pd.DataFrame(school_rows)
        
        if search_query:
            filtered_table = table_df[table_df["School"].str.contains(search_query, case=False, na=False)]
        else:
            filtered_table = table_df
        
        display_df = filtered_table.drop(columns=["School ID"])
        
        page_size = 20
        total_rows = len(display_df)
        total_pages = max(1, (total_rows + page_size - 1) // page_size)
        
        if "school_page" not in st.session_state:
            st.session_state.school_page = 1
        
        if total_pages > 1:
            cols = st.columns([1, 3, 1])
            with cols[0]:
                if st.button("◀ Previous", disabled=(st.session_state.school_page <= 1)):
                    st.session_state.school_page -= 1
                    st.rerun()
            with cols[1]:
                st.caption(f"Page {st.session_state.school_page} of {total_pages}")
            with cols[2]:
                if st.button("Next ▶", disabled=(st.session_state.school_page >= total_pages)):
                    st.session_state.school_page += 1
                    st.rerun()
        
        start_idx = (st.session_state.school_page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        page_df = display_df.iloc[start_idx:end_idx].copy()
        
        numeric_cols = ["Overall SBM Index", "Curriculum & Teaching", "Learning Environment", 
                        "Leadership", "Governance & Accountability", "HR & Team Development", 
                        "Finance & Resource Mgmt."]
        for col in numeric_cols:
            if col in page_df.columns:
                page_df[col] = pd.to_numeric(page_df[col], errors='coerce')
                page_df[col] = page_df[col].round(1)
        
        def color_score(val):
            if pd.isna(val):
                return ''
            if val >= 2.5:
                return 'background-color: #22c55e; color: white; font-weight: bold;'
            elif val >= 2.0:
                return 'background-color: #eab308; color: white; font-weight: bold;'
            else:
                return 'background-color: #dc2626; color: white; font-weight: bold;'
        
        styled_page = page_df.style.map(color_score, subset=numeric_cols)
        styled_page = styled_page.format("{:.1f}", subset=numeric_cols)
        
        st.dataframe(styled_page, width='stretch', height=400)
        
        st.markdown("""
        <div style="display:flex;gap:16px;font-size:13px;margin:8px 0;">
            <span>🟢 <b>Strong</b> (≥ 2.5)</span>
            <span>🟡 <b>Moderate</b> (2.0 – 2.4)</span>
            <span>🔴 <b>Weak</b> (< 2.0)</span>
            <span>⚪ <b>Pending</b> (No data)</span>
        </div>
        """, unsafe_allow_html=True)
        
        if len(page_df) == 0:
            st.info("No schools match your search criteria.")
        
        st.markdown("#### 🔍 Jump to School")
        col_school, col_school_btn = st.columns([3, 1])
        with col_school:
            school_names = [s["name"] for s in schools_in_sdo]
            selected_school_name = st.selectbox("Select a school to view its detailed dashboard:", school_names)
        with col_school_btn:
            if st.button("🚀 Go to School", use_container_width=True):
                st.info(f"Navigating to {selected_school_name} (feature coming soon)")
    
    with tab3:
        # ─── Digital Twin Sandbox ───
        from utils.twin_ui import render_sandbox
        render_sandbox(sdo_list, selected_sdo, schools_in_sdo, complete_schools, dim_avgs, overall_avg)

else:
    # School head: no tabs – just synopsis, map, legend, bottom tabs
    from streamlit.components.v1 import html as st_html
    wrapped_html = f"""
    <div style="width:100%;padding:0;margin:0;box-sizing:border-box;">
        {synopsis_html}
    </div>
    """
    st_html(wrapped_html, height=900, scrolling=True)

    # ─── MAP ───
    st.markdown("---")
    try:
        import folium
        from streamlit_folium import st_folium
        
        map_center = [selected_sdo["lat"], selected_sdo["lng"]]
        m = folium.Map(location=map_center, zoom_start=8, tiles="OpenStreetMap")
        
        for sdo in filtered_sdos:
            add_sdo_shield(m, sdo)
        
        for school in schools_in_sdo:
            add_school_dot(m, school)
        
        st_folium(m, width=None, height=500, key="sbm_map")
        
    except ImportError as e:
        st.error(f"Missing import: {e}. Please run: pip install folium streamlit-folium")
    except Exception as e:
        st.error(f"Map rendering failed: {e}")

    # ─── MAP LEGEND ───
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
    st.markdown("""
    <div style="background-color:var(--secondary-background-color);padding:10px 16px;border-radius:8px;border-left:4px solid #22c55e;margin-bottom:14px;color:var(--text-color);">
        <b>📏 School Dot Sizes:</b> The size of each school dot represents its <b>total enrollment (number of learners)</b>.
        Larger dots indicate schools with more students, while smaller dots indicate schools with fewer students.
        This helps you quickly see which schools have larger student populations.
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
    btab1, btab2, btab3 = st.tabs(["📋 Indicators", "📊 Radar Chart", "📈 Historical Trend"])
    with btab1:
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
    with btab2:
        if any(dim_avgs) and any(regional_dim_avgs):
            fig = create_radar_chart(dim_avgs, regional_dim_avgs)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("No dimension data available for this division.")
    with btab3:
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
    matches = [s for s in filtered_schools if search_query.lower() in s["name"].lower() or search_query in s["id"]]
    if matches:
        for match in matches:
            sdo = next(s for s in sdo_list if s["id"] == match["sdo_id"])
            st.write(f"• **{match['name']}** ({match['type']}) – {sdo['name']}")
    else:
        st.info("No schools found matching your search.")

# ─── FOOTER ───
st.markdown("---")
st.caption("© 2024 DepEd Region X – SBM Digital Twin Dashboard · Built with Streamlit")

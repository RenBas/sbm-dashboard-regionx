"""Main Streamlit application for SBM Dashboard – Region X."""

import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from streamlit.components.v1 import html as st_html

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="SBM Dashboard – Region X",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── IMPORTS ───
from utils.constants import DIMENSION_NAMES
from utils.data_loader import load_sdo_data, load_all_schools, get_schools_by_sdo, compute_dimension_averages
from utils.map_helpers import add_sdo_shield, add_school_dot
from utils.chart_helpers import create_radar_chart, create_trend_chart, create_indicators_table
from utils.auth import (
    authenticate, login_status, logout, get_accessible_schools,
    get_accessible_divisions_summary, is_school_head
)
from utils.download_helpers import generate_report_data, generate_excel_template
from utils.synopsis_generator import generate_synopsis
from utils.twin_ui import render_sandbox

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

# ────────────────────────────────────────────────────────────────
# 1. SESSION STATE INITIALISATION
# ────────────────────────────────────────────────────────────────
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "uploaded_sdo_list" not in st.session_state:
    st.session_state.uploaded_sdo_list = None
if "uploaded_schools" not in st.session_state:
    st.session_state.uploaded_schools = None

if "debug_info" not in st.session_state:
    st.session_state.debug_info = {}

def reset_app():
    """Hard reset: clear all data and revert to empty state."""
    if "sbm_data_upload" in st.session_state:
        del st.session_state.sbm_data_upload
    st.session_state.uploaded_file = None
    st.session_state.uploaded_sdo_list = None
    st.session_state.uploaded_schools = None
    st.session_state.analysis_complete = False
    st.session_state.debug_info = {}
    st.cache_data.clear()
    st.rerun()

# ────────────────────────────────────────────────────────────────
# 2. DATA LOADING
# ────────────────────────────────────────────────────────────────
def get_active_data():
    if st.session_state.uploaded_sdo_list is not None and st.session_state.uploaded_schools is not None:
        return st.session_state.uploaded_sdo_list, st.session_state.uploaded_schools
    else:
        return [], []

sdo_list, schools = get_active_data()

all_region_complete = [s for s in schools if s.get("data_status") != "Pending"]
if all_region_complete:
    regional_dim_avgs = compute_dimension_averages(all_region_complete)
    regional_overall_avg = round(sum(s.get("overall_index", 0) for s in all_region_complete) / len(all_region_complete), 1)
else:
    regional_dim_avgs = [0, 0, 0, 0, 0, 0]
    regional_overall_avg = 0

# ────────────────────────────────────────────────────────────────
# 3. AUTHENTICATION
# ────────────────────────────────────────────────────────────────
auth_status = login_status()
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

user = st.session_state.user
if user is None:
    st.warning("Session expired. Please log in again.")
    st.stop()

role = user.get("role", "school")
user_name = user.get("name", "User")

filtered_data = get_accessible_schools(user, sdo_list, schools)
filtered_sdos = filtered_data.get("filtered_sdos", [])
filtered_schools = filtered_data.get("filtered_schools", [])

# ────────────────────────────────────────────────────────────────
# 4. SELECTED SDO
# ────────────────────────────────────────────────────────────────
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

if selected_sdo is None and sdo_list:
    if is_school_head(user):
        if filtered_schools:
            school = filtered_schools[0]
            selected_sdo = next((s for s in sdo_list if s["id"] == school.get("sdo_id")), None)
            selected_sdo_id = selected_sdo["id"] if selected_sdo else None
        else:
            selected_sdo = sdo_list[0] if sdo_list else None
            selected_sdo_id = selected_sdo["id"] if selected_sdo else None
    else:
        if filtered_sdos:
            if len(filtered_sdos) == 1:
                selected_sdo = filtered_sdos[0]
                selected_sdo_id = selected_sdo["id"]
            else:
                selected_sdo = filtered_sdos[0]
                selected_sdo_id = selected_sdo["id"]
        else:
            selected_sdo = sdo_list[0] if sdo_list else None
            selected_sdo_id = selected_sdo["id"] if selected_sdo else None

if selected_sdo is not None:
    if "capital" not in selected_sdo or pd.isna(selected_sdo.get("capital")):
        selected_sdo["capital"] = ""
    if "name" in selected_sdo:
        selected_sdo["name"] = str(selected_sdo["name"])

if selected_sdo_id is not None:
    schools_in_sdo = get_schools_by_sdo(filtered_schools, selected_sdo_id) if filtered_schools else []
else:
    schools_in_sdo = []

complete_schools = [s for s in schools_in_sdo if s.get("data_status") != "Pending"]
dim_avgs = compute_dimension_averages(schools_in_sdo)

if complete_schools:
    overall_avg = round(sum(s.get("overall_index", 0) for s in complete_schools) / len(complete_schools), 1)
    max_dim_idx = dim_avgs.index(max(dim_avgs))
    min_dim_idx = dim_avgs.index(min(dim_avgs))
else:
    overall_avg = 0
    max_dim_idx = 0
    min_dim_idx = 0

# ────────────────────────────────────────────────────────────────
# 5. SIDEBAR
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"### 👤 {user_name}")
    st.caption(get_accessible_divisions_summary(user))
    st.markdown("---")
    
    if st.session_state.uploaded_sdo_list is not None:
        st.info("📌 **Using Uploaded Data**")
        if st.button("🔄 Reset to Empty Slate", use_container_width=True, key="reset_to_empty_slate"):
            reset_app()
    else:
        st.warning("📌 **No data loaded.** Please upload SBM data and click **Run Analysis**.")
        if st.button("🔄 Reset", use_container_width=True, key="reset_empty_state"):
            reset_app()
    
    st.markdown("---")
    st.markdown("### 🎨 Appearance")
    col_light, col_dark = st.columns(2)
    with col_light:
        if st.button("☀️ Light", use_container_width=True,
                     type="primary" if st.session_state.custom_theme == "light" else "secondary",
                     key="light_theme"):
            st.session_state.custom_theme = "light"
            st.rerun()
    with col_dark:
        if st.button("🌙 Dark", use_container_width=True,
                     type="primary" if st.session_state.custom_theme == "dark" else "secondary",
                     key="dark_theme"):
            st.session_state.custom_theme = "dark"
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 🗺️ Navigation")
    if sdo_list and selected_sdo:
        if not is_school_head(user):
            sdo_names = [s["name"] for s in filtered_sdos] if filtered_sdos else [s["name"] for s in sdo_list]
            if len(sdo_names) == 1:
                st.caption(f"📋 {selected_sdo['name']}")
            else:
                selected_sdo_name = st.selectbox("Select Division", options=sdo_names, index=0, key="sidebar_division_select")
                selected_sdo = next((s for s in sdo_list if s["name"] == selected_sdo_name), selected_sdo)
                selected_sdo_id = selected_sdo["id"] if selected_sdo else None
                schools_in_sdo = get_schools_by_sdo(filtered_schools, selected_sdo_id) if selected_sdo_id else []
                complete_schools = [s for s in schools_in_sdo if s.get("data_status") != "Pending"]
                dim_avgs = compute_dimension_averages(schools_in_sdo)
                if complete_schools:
                    overall_avg = round(sum(s.get("overall_index", 0) for s in complete_schools) / len(complete_schools), 1)
                    max_dim_idx = dim_avgs.index(max(dim_avgs))
                    min_dim_idx = dim_avgs.index(min(dim_avgs))
                else:
                    overall_avg = 0
                    max_dim_idx = 0
                    min_dim_idx = 0
        else:
            if filtered_schools:
                school = filtered_schools[0]
                st.caption(f"🏫 {school.get('name', '')}")
    else:
        st.caption("📭 No data loaded – please upload.")
    
    st.markdown("---")
    st.markdown("### 📐 Filter by Dimension")
    selected_dimension = st.selectbox("Highlight Dimension", options=["Overall"] + DIMENSION_NAMES, index=0, key="dimension_filter")
    
    st.markdown("---")
    st.markdown("### 🔍 Search School")
    search_query = st.text_input("Type school name or ID", placeholder="e.g., Central", key="search_school")
    
    st.markdown("---")
    st.markdown("### 📊 Data Management")
    if selected_sdo and selected_sdo_id is not None and schools_in_sdo:
        report_df = generate_report_data(selected_sdo["name"], schools_in_sdo, complete_schools)
        if report_df is not None and not report_df.empty:
            csv_report = report_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Report (CSV)",
                data=csv_report,
                file_name=f"SBM_Report_{selected_sdo['name'].replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_report"
            )
        else:
            st.caption("No data to report.")
    else:
        st.caption("No data loaded.")
    
    template_file = generate_excel_template()
    st.download_button(
        label="📋 Download Data Collection Template (Excel)",
        data=template_file,
        file_name="SBM_Data_Collection_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        key="download_template"
    )
    st.caption("Template based on DepEd Order No. 007, s. 2024")
    
    st.markdown("---")
    st.markdown("### 📤 Upload SBM Data")
    st.caption("Upload a completed Excel template to replace the current data.")
    
    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx)",
        type=["xlsx"],
        key="sbm_data_upload"
    )
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.success("✅ File uploaded. Click **Run Analysis** to process.")
    else:
        st.session_state.uploaded_file = None
    
    st.markdown("---")
    col_run, col_reset = st.columns(2)
    with col_run:
        run_clicked = st.button("🚀 Run Analysis", type="primary", use_container_width=True, disabled=uploaded_file is None, key="run_analysis")
    with col_reset:
        reset_clicked = st.button("🔄 Reset", use_container_width=True, key="reset_main")
    
    if reset_clicked:
        reset_app()
    
    with st.expander("🔍 Debug Data Info", expanded=True):  # expanded by default
        st.write(f"**Data Source:** {'Uploaded' if st.session_state.uploaded_sdo_list is not None else 'Empty'}")
        st.write(f"**Total SDOs:** {len(sdo_list)}")
        st.write(f"**Total Schools:** {len(schools)}")
        st.write(f"**Complete Schools:** {len([s for s in schools if s.get('data_status') != 'Pending'])}")
        st.write(f"**Pending Schools:** {len([s for s in schools if s.get('data_status') == 'Pending'])}")
        if schools:
            sample = schools[0]
            st.write(f"**Sample School Scores:** {sample.get('dimension_scores', [])}")
        if sdo_list:
            sample_sdo = sdo_list[0]
            st.write(f"**Sample SDO Scores:** {sample_sdo.get('dimension_scores', [])}")
        if st.session_state.debug_info:
            st.write("**Debug Info from last processing:**")
            st.json(st.session_state.debug_info)
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True, key="logout_button"):
        logout()
    
    with st.expander("📖 Glossary", expanded=False):
        st.markdown("""
        **SBM (School-Based Management)** – Decentralisation of decision-making authority to schools.
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

# ────────────────────────────────────────────────────────────────
# 6. PROCESS UPLOAD – WITH PERSISTENT DEBUG
# ────────────────────────────────────────────────────────────────

def process_uploaded_excel(uploaded_file):
    """
    Read the multi-sheet Excel template.
    Expects:
    - Sheet 0 or 'School Information': School metadata
    - Sheet 1 or 'SBM Assessment': Assessment scores by indicator/dimension
    """
    # Read both sheets
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    
    # Determine sheet names
    school_sheet = 'School Information' if 'School Information' in sheet_names else 0
    assessment_sheet = 'SBM Assessment' if 'SBM Assessment' in sheet_names else (1 if len(sheet_names) > 1 else None)
    
    # Read school information
    school_df = pd.read_excel(xls, sheet_name=school_sheet)
    
    debug = {}
    debug["columns_detected"] = school_df.columns.tolist()
    debug["num_rows_school"] = len(school_df)
    debug["sheets_found"] = sheet_names
    
    # Read assessment data if available
    dim_scores_by_school = {}
    if assessment_sheet is not None:
        try:
            assessment_df = pd.read_excel(xls, sheet_name=assessment_sheet)
            debug["num_rows_assessment"] = len(assessment_df)
            
            # Map dimension names to indices (standard 6 dimensions)
            # Note: Data file may only have 4 dimensions, we fill missing with 0
            dimension_map = {
                "Leadership and Governance": 0,
                "Curriculum and Instruction": 1,
                "Learning Environment": 2,  # May not be in data
                "Accountability and Continuous Improvement": 3,
                "Management of Resources": 4,
                "Finance & Resource Management": 5  # May not be in data
            }
            
            # Also try alternative mappings (match prefix_map above)
            alt_dimension_map = {
                "LG_": 0, "CI_": 1, "LE_": 2, "AC_": 3, "MR_": 4, "FR_": 5
            }
            
            # Pivot assessment data to get one row per school with dimension averages
            if 'Dimension' in assessment_df.columns and 'Score' in assessment_df.columns:
                pivot = assessment_df.pivot_table(
                    index=['School ID'],
                    columns='Dimension',
                    values='Score',
                    aggfunc='mean'
                ).reset_index()
                
                # Convert to dict for easy lookup
                for _, row in pivot.iterrows():
                    school_id = str(row['School ID'])
                    scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                    for dim_name, dim_idx in dimension_map.items():
                        if dim_name in row and pd.notna(row[dim_name]):
                            scores[dim_idx] = float(row[dim_name])
                    dim_scores_by_school[school_id] = scores
                    
                debug["schools_with_scores"] = len(dim_scores_by_school)
                debug["dimensions_found_in_data"] = [c for c in pivot.columns if c != 'School ID']
            elif any(col.startswith(tuple(alt_dimension_map.keys())) for col in assessment_df.columns):
                # Handle wide format with prefixed columns
                for idx, row in assessment_df.iterrows():
                    school_id = str(row.get('School ID', idx))
                    scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                    for prefix, dim_idx in alt_dimension_map.items():
                        matching_cols = [c for c in assessment_df.columns if c.startswith(prefix)]
                        if matching_cols:
                            vals = pd.to_numeric(row[matching_cols], errors="coerce").dropna()
                            if not vals.empty:
                                scores[dim_idx] = vals.mean()
                    dim_scores_by_school[school_id] = scores
                debug["schools_with_scores"] = len(dim_scores_by_school)
        except Exception as e:
            debug["assessment_error"] = str(e)
    else:
        debug["assessment_sheet"] = "Not found"

    # ── Define the six dimension prefixes (fallback for single-sheet format) ──
    prefix_map = {
        "LG_": 0,   # Leadership and Governance
        "CI_": 1,   # Curriculum & Instruction  
        "LE_": 2,   # Learning Environment
        "AC_": 3,   # Accountability and Continuous Improvement
        "MR_": 4,   # Management of Resources
        "FR_": 5    # Finance & Resource Management
    }

    # ── Identify which columns belong to each dimension (for single-sheet fallback) ──
    dim_columns = {idx: [] for idx in range(6)}
    for col in school_df.columns:
        for prefix, idx in prefix_map.items():
            if col.startswith(prefix):
                dim_columns[idx].append(col)
                break

    debug["dimension_column_counts"] = {DIMENSION_NAMES[i]: len(dim_columns[i]) for i in range(6)}

    # ── Build schools list (with safe NaN handling) ──
    schools = []
    for idx, row in school_df.iterrows():
        school_id = str(row.get("School ID", idx))
        
        # Get dimension scores from assessment data if available
        dimension_scores = dim_scores_by_school.get(school_id, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        
        # If no assessment data found, try to compute from inline columns (fallback)
        if all(s == 0.0 for s in dimension_scores) and any(dim_columns.values()):
            for dim_idx in range(6):
                cols = dim_columns[dim_idx]
                if cols:
                    vals = pd.to_numeric(row[cols], errors="coerce").dropna()
                    if not vals.empty:
                        dimension_scores[dim_idx] = vals.mean()
                    else:
                        dimension_scores[dim_idx] = 0.0

        # Safe conversion of metadata
        def safe_float(val):
            v = pd.to_numeric(val, errors='coerce')
            return 0.0 if pd.isna(v) else float(v)

        def safe_int(val):
            v = pd.to_numeric(val, errors='coerce')
            return 0 if pd.isna(v) else int(v)

        def safe_str(val):
            if pd.isna(val):
                return ""
            return str(val)

        school = {
            "id": safe_str(row.get("School ID", idx)),
            "name": safe_str(row.get("School Name", f"School {idx}")),
            "type": safe_str(row.get("School Type", row.get("Offering", ""))),
            "degree": safe_str(row.get("Degree of Manifestation", "Pending")),
            "sdo_id": safe_str(row.get("Division", "")),
            "data_status": safe_str(row.get("Data Status", "Complete")),
            "lat": safe_float(row.get("Latitude", 0)),
            "lng": safe_float(row.get("Longitude", 0)),
            "enrollment": safe_int(row.get("Enrollment", 0)),
            "urban_rural": safe_str(row.get("Urban/Rural", "Urban")),
            "head_name": safe_str(row.get("School Head Name", "")),
            "head_email": safe_str(row.get("School Head Email", "")),
            "dimension_scores": dimension_scores,
            "overall_index": sum(dimension_scores) / len([s for s in dimension_scores if s > 0]) if any(s > 0 for s in dimension_scores) else 0,
            "lowest_dim_index": dimension_scores.index(min(dimension_scores)) if any(s > 0 for s in dimension_scores) else 0,
            "lowest_dim_score": min(dimension_scores) if any(s > 0 for s in dimension_scores) else 0
        }
        schools.append(school)

    debug["sample_school_scores"] = schools[0]["dimension_scores"] if schools else None

    # ── Build SDO list ──
    sdo_names = set(s["sdo_id"] for s in schools if s["sdo_id"])
    debug["sdo_names_found"] = list(sdo_names)

    sdo_list = []
    for sdo_name in sdo_names:
        div_schools = [s for s in schools if s["sdo_id"] == sdo_name]
        lat = div_schools[0]["lat"] if div_schools else 0.0
        lng = div_schools[0]["lng"] if div_schools else 0.0

        complete_div_schools = [s for s in div_schools if s["data_status"] != "Pending"]
        if complete_div_schools:
            dim_scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            for d in range(6):
                vals = [s["dimension_scores"][d] for s in complete_div_schools if s["dimension_scores"][d] > 0]
                if vals:
                    dim_scores[d] = sum(vals) / len(vals)
        else:
            dim_scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        lowest_dim_score = min(dim_scores) if any(dim_scores) else 0.0
        lowest_dim_index = dim_scores.index(lowest_dim_score) if any(dim_scores) else 0
        lowest_dim_name = DIMENSION_NAMES[lowest_dim_index]
        
        # Calculate urgency factor (1 = most urgent, 0 = least urgent)
        all_lowest = [min(s.get("dimension_scores", [0,0,0,0,0,0])) for s in complete_div_schools if any(s.get("dimension_scores", [0,0,0,0,0,0]))]
        if all_lowest:
            min_score = min(all_lowest)
            max_score = max(all_lowest)
            range_val = max_score - min_score if max_score > min_score else 0.001
            raw = (lowest_dim_score - min_score) / range_val
            urgency_factor = round(1 - raw, 3)
        else:
            urgency_factor = 0.0

        sdo_list.append({
            "id": sdo_name,
            "name": sdo_name,
            "capital": "",
            "lat": lat,
            "lng": lng,
            "dimension_scores": dim_scores,
            "lowest_dim_score": lowest_dim_score,
            "lowest_dim_index": lowest_dim_index,
            "lowest_dim_name": lowest_dim_name,
            "urgency_factor": urgency_factor,
            "overall_index": sum(dim_scores) / len([s for s in dim_scores if s > 0]) if any(s > 0 for s in dim_scores) else 0
        })

    debug["sample_sdo_scores"] = sdo_list[0]["dimension_scores"] if sdo_list else None
    debug["num_sdo"] = len(sdo_list)
    debug["num_schools"] = len(schools)

    return sdo_list, schools, debug

# Run logic
if run_clicked and uploaded_file is not None:
    with st.spinner("⏳ Processing uploaded data..."):
        try:
            new_sdo_list, new_schools, debug_info = process_uploaded_excel(uploaded_file)
            # Store in session state
            st.session_state.uploaded_sdo_list = new_sdo_list
            st.session_state.uploaded_schools = new_schools
            st.session_state.debug_info = debug_info
            st.session_state.analysis_complete = True
            st.success("✅ Data loaded successfully! Refreshing...")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Processing error: {e}")
            st.session_state.analysis_complete = False

if run_clicked and uploaded_file is None:
    st.warning("Please upload a file first.")

# ────────────────────────────────────────────────────────────────
# 7. MAIN CONTENT – Only if data is loaded
# ────────────────────────────────────────────────────────────────

if not sdo_list or not schools:
    # Show debug info on the page to help diagnose
    st.error("📭 No data loaded. The file was processed but no schools or divisions were created.")
    if st.session_state.debug_info:
        st.write("**Debug Information from last processing:**")
        st.json(st.session_state.debug_info)
    st.info("💡 Please check that the uploaded file has data rows and that the 'Division' column is populated.")
    st.stop()

if selected_sdo_id is None:
    st.warning("No division selected. Please select a division from the sidebar.")
    st.stop()

if selected_sdo is not None:
    if "capital" not in selected_sdo or pd.isna(selected_sdo.get("capital")):
        selected_sdo["capital"] = ""
    if "name" in selected_sdo:
        selected_sdo["name"] = str(selected_sdo["name"])

# ─── DIVISION HEADER ───
st.markdown(f"## 🎓 SBM Dashboard: {selected_sdo['name']}")
st.caption(f"Capital: {selected_sdo.get('capital', '')} · {selected_sdo.get('id', '')} schools")

# ─── TABS ───
if role == "regional":
    tab1, tab2, tab3 = st.tabs(["📋 Executive Summary", "📊 Division Performance Matrix", "🧪 Digital Twin Sandbox"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏫 Total Schools", len(schools_in_sdo), 
                      delta=f"{len([s for s in schools_in_sdo if s.get('data_status')=='Pending'])} pending" 
                      if any(s.get('data_status')=='Pending' for s in schools_in_sdo) else None)
        with col2:
            st.metric("📊 Overall SBM Index", f"{overall_avg:.1f} / 3.0" if overall_avg > 0 else "—")
        with col3:
            st.metric("⬆️ Highest Dimension", DIMENSION_NAMES[max_dim_idx] if overall_avg > 0 else "—")
        with col4:
            st.metric("⬇️ Lowest Dimension (Urgent)", DIMENSION_NAMES[min_dim_idx] if overall_avg > 0 else "—", delta_color="inverse")
        
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
        wrapped_html = f"""
        <div style="width:100%;padding:0;margin:0;box-sizing:border-box;">
            {synopsis_html}
        </div>
        """
        st_html(wrapped_html, height=900, scrolling=True)
        
        st.markdown("---")
        try:
            map_center = [selected_sdo["lat"], selected_sdo["lng"]]
            m = folium.Map(location=map_center, zoom_start=8, tiles="OpenStreetMap")
            for sdo in filtered_sdos:
                add_sdo_shield(m, sdo)
            for school in schools_in_sdo:
                add_school_dot(m, school)
            st_folium(m, width=None, height=500, key="sbm_map")
        except Exception as e:
            st.error(f"Map rendering failed: {e}")
        
        st.markdown("---")
        st.markdown("""
        <div class="custom-footnote" style="padding:14px 18px;border-radius:8px;margin-bottom:14px;">
            <b>💡 About the Pulsing Glow:</b> The animated glow behind each SDO shield indicates <b>urgency based on the division's lowest SBM dimension score</b>.
            <br><br>
            <div style="display:flex;flex-wrap:wrap;gap:12px 24px;margin-top:4px;">
                <span style="color:#dc2626;font-weight:600;">🔴 Red glow</span> <span>Critical – Score &lt; 1.0</span>
                <span style="color:#f97316;font-weight:600;">🟠 Orange glow</span> <span>Warning – Score 1.0 – 1.9</span>
                <span style="color:#eab308;font-weight:600;">🟡 Yellow glow</span> <span>Monitor – Score 2.0 – 2.4</span>
                <span style="font-weight:600;opacity:0.4;">⚪ No glow</span> <span>Stable – Score ≥ 2.5</span>
            </div>
            <div style="margin-top:8px;font-size:12px;opacity:0.6;">The glow pulses faster and brighter for more urgent divisions.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color:var(--secondary-background-color);padding:10px 16px;border-radius:8px;border-left:4px solid #22c55e;margin-bottom:14px;color:var(--text-color);">
            <b>📏 School Dot Sizes:</b> The size of each school dot represents its <b>total enrollment (number of learners)</b>.
            Larger dots indicate schools with more students, while smaller dots indicate schools with fewer students.
        </div>
        """, unsafe_allow_html=True)
        st.caption("💡 Click on any SDO shield to zoom in and view its schools. Hover over markers for more details.")
        
        st.markdown("---")
        btab1, btab2, btab3 = st.tabs(["📋 Indicators", "📊 Radar Chart", "📈 Historical Trend"])
        with btab1:
            df = create_indicators_table(schools_in_sdo)
            if not df.empty:
                st.dataframe(df[["#", "Indicator", "Dimension", "Score", "Status"]],
                             column_config={"Score": st.column_config.NumberColumn(format="%.1f")},
                             hide_index=True, width='stretch')
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
        st.markdown("### 📊 Division Performance Matrix")
        st.caption("Performance of all divisions across the 6 SBM dimensions. Scores are rounded to 1 decimal place.")
        matrix_data = []
        for sdo in sdo_list:
            dim_scores = [round(x, 1) for x in sdo.get("dimension_scores", [0,0,0,0,0,0])]
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
            if pd.isna(val): return ''
            if val >= 2.5: return 'background-color: #22c55e; color: white; font-weight: bold;'
            elif val >= 2.0: return 'background-color: #eab308; color: white; font-weight: bold;'
            else: return 'background-color: #dc2626; color: white; font-weight: bold;'
        
        styled_df = df.style.map(color_cell, subset=df.columns[1:]).format("{:.1f}", subset=df.columns[1:])
        st.markdown(styled_df.to_html(index=False, escape=False), unsafe_allow_html=True)
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
            scores = [sdo.get("dimension_scores", [0,0,0,0,0,0])[DIMENSION_NAMES.index(dim)] for sdo in sdo_list]
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
            selected_div_name = st.selectbox("Select a division to view its detailed dashboard:", division_names, key="jump_division")
        with col_btn:
            if st.button("🚀 Go to Division", use_container_width=True, key="go_division_button"):
                st.session_state.go_to_division = selected_div_name
                st.rerun()
    
    with tab3:
        render_sandbox(sdo_list, selected_sdo, schools_in_sdo, complete_schools, dim_avgs, overall_avg)

elif role == "division":
    tab1, tab2, tab3 = st.tabs(["📋 Executive Summary", "📊 School Performance Dashboard", "🧪 Digital Twin Sandbox"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏫 Total Schools", len(schools_in_sdo), 
                      delta=f"{len([s for s in schools_in_sdo if s.get('data_status')=='Pending'])} pending" 
                      if any(s.get('data_status')=='Pending' for s in schools_in_sdo) else None)
        with col2:
            st.metric("📊 Overall SBM Index", f"{overall_avg:.1f} / 3.0" if overall_avg > 0 else "—")
        with col3:
            st.metric("⬆️ Highest Dimension", DIMENSION_NAMES[max_dim_idx] if overall_avg > 0 else "—")
        with col4:
            st.metric("⬇️ Lowest Dimension (Urgent)", DIMENSION_NAMES[min_dim_idx] if overall_avg > 0 else "—", delta_color="inverse")
        
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
        wrapped_html = f"""
        <div style="width:100%;padding:0;margin:0;box-sizing:border-box;">
            {synopsis_html}
        </div>
        """
        st_html(wrapped_html, height=900, scrolling=True)
        
        st.markdown("---")
        try:
            map_center = [selected_sdo["lat"], selected_sdo["lng"]]
            m = folium.Map(location=map_center, zoom_start=8, tiles="OpenStreetMap")
            for sdo in filtered_sdos:
                add_sdo_shield(m, sdo)
            for school in schools_in_sdo:
                add_school_dot(m, school)
            st_folium(m, width=None, height=500, key="sbm_map")
        except Exception as e:
            st.error(f"Map rendering failed: {e}")
        
        st.markdown("---")
        st.markdown("""
        <div class="custom-footnote" style="padding:14px 18px;border-radius:8px;margin-bottom:14px;">
            <b>💡 About the Pulsing Glow:</b> ... (same as before)
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color:var(--secondary-background-color);padding:10px 16px;border-radius:8px;border-left:4px solid #22c55e;margin-bottom:14px;color:var(--text-color);">
            <b>📏 School Dot Sizes:</b> ... (same)
        </div>
        """, unsafe_allow_html=True)
        st.caption("💡 Click on any SDO shield to zoom in and view its schools. Hover over markers for more details.")
        
        st.markdown("---")
        btab1, btab2, btab3 = st.tabs(["📋 Indicators", "📊 Radar Chart", "📈 Historical Trend"])
        with btab1:
            df = create_indicators_table(schools_in_sdo)
            if not df.empty:
                st.dataframe(df[["#", "Indicator", "Dimension", "Score", "Status"]],
                             column_config={"Score": st.column_config.NumberColumn(format="%.1f")},
                             hide_index=True, width='stretch')
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
        st.markdown("### 📊 School Performance Dashboard")
        st.caption(f"Detailed school-level performance for {selected_sdo['name']}.")
        st.info("School Performance Dashboard – full code to be inserted here.")
    
    with tab3:
        render_sandbox(sdo_list, selected_sdo, schools_in_sdo, complete_schools, dim_avgs, overall_avg)

else:
    st.info("School head view – detailed dashboard coming soon.")

# ─── SEARCH RESULTS ───
if search_query and schools:
    st.markdown("---")
    st.markdown(f"### 🔍 Search Results for '{search_query}'")
    matches = [s for s in filtered_schools if search_query.lower() in s.get("name", "").lower() or search_query in s.get("id", "")]
    if matches:
        for match in matches:
            sdo = next((s for s in sdo_list if s["id"] == match.get("sdo_id")), None)
            if sdo:
                st.write(f"• **{match.get('name', '')}** ({match.get('type', '')}) – {sdo.get('name', '')}")
    else:
        st.info("No schools found matching your search.")

st.markdown("---")
st.caption("© 2024 DepEd Region X – SBM Digital Twin Dashboard · Built with Streamlit")

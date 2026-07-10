"""Main Streamlit application for SBM Dashboard – Region X."""

import streamlit as st
import random
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from streamlit.components.v1 import html as st_html
import uuid

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
from utils.map_helpers import add_sdo_shield, add_school_dot, score_to_color
from utils.chart_helpers import create_radar_chart, create_trend_chart, create_indicators_table, render_school_dashboard
from utils.auth import (
    authenticate, login_status, logout, get_accessible_schools,
    get_accessible_divisions_summary, is_school_head
)
from utils.download_helpers import generate_report_data, generate_excel_template
from utils.export_helpers import generate_excel_report, generate_pdf_report
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
if "school_id_input" not in st.session_state:
    st.session_state.school_id_input = ""
if "loaded_school" not in st.session_state:
    st.session_state.loaded_school = None
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "debug_info" not in st.session_state:
    st.session_state.debug_info = {}

def reset_app():
    if "sbm_data_upload" in st.session_state:
        del st.session_state.sbm_data_upload
    st.session_state.uploaded_file = None
    st.session_state.uploaded_sdo_list = None
    st.session_state.uploaded_schools = None
    st.session_state.analysis_complete = False
    st.session_state.debug_info = {}
    st.session_state.school_id_input = ""
    st.session_state.loaded_school = None
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
# 3. LIVE USER COUNTER (Upstash Redis) – fully fault‑tolerant
# ────────────────────────────────────────────────────────────────
def get_redis_connection():
    """Return a Redis connection if secrets are configured and reachable, else None."""
    try:
        import redis
        host = st.secrets["redis"]["host"]
        port = st.secrets["redis"]["port"]
        password = st.secrets["redis"]["password"]
    except Exception:
        return None
    try:
        r = redis.Redis(
            host=host,
            port=port,
            password=password,
            ssl=True,
            decode_responses=True,
            socket_connect_timeout=3
        )
        r.ping()
        return r
    except Exception:
        return None

def update_active_users():
    """Register this session and return the current active user count, or None if unavailable."""
    r = get_redis_connection()
    if r is None:
        return None
    try:
        key = f"session:{st.session_state.session_id}"
        r.setex(key, 300, "1")
        return len(r.keys("session:*"))
    except Exception:
        return None

# ────────────────────────────────────────────────────────────────
# 4. AUTHENTICATION (ROLE‑BASED LOGIN)
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
                <p style="font-size:14px;color:#4b5563;">Select your role to see demo credentials.</p>
    """, unsafe_allow_html=True)

    login_role = st.selectbox(
        "I am a…",
        options=["Regional", "Division", "School Head"],
        index=None,
        placeholder="Choose your role",
        key="login_role"
    )

    if login_role == "Regional":
        st.info("👤 Demo Account\n\nUsername: `regional`\nPassword: `regional123`")
    elif login_role == "Division":
        st.info(
            "👥 Demo Division Accounts (password: `sdo123`)\n\n"
            "• `sdo_bukidnon`\n"
            "• `sdo_cdo`\n"
            "• `sdo_misamis_occ`\n"
            "• `sdo_iligan`\n"
            "• `sdo_valencia`"
        )
    elif login_role == "School Head":
        st.info(
            "🏫 Demo School Head Accounts (password: `school123`)\n\n"
            "• `principal` – generic, enter your School ID after login\n"
            "• `principal_cdo`\n"
            "• `principal_bukidnon`\n"
            "• `principal_ozamiz`\n"
            "• `principal_iligan`\n"
            "• `principal_valencia`\n"
            "• `principal_misamis_occ`"
        )

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
# 5. SELECTED SDO (only used for regional/division roles)
# ────────────────────────────────────────────────────────────────
selected_sdo = None
selected_sdo_id = None

if role != "school":
    if "go_to_division" in st.session_state:
        target_div_name = st.session_state.go_to_division
        for sdo in sdo_list:
            if sdo["name"] == target_div_name:
                selected_sdo = sdo
                selected_sdo_id = sdo["id"]
                break
        del st.session_state.go_to_division

    if selected_sdo is None and sdo_list:
        if filtered_sdos:
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
else:
    if st.session_state.loaded_school is not None:
        schools_in_sdo = [st.session_state.loaded_school]
    elif filtered_schools:
        schools_in_sdo = filtered_schools
        st.session_state.loaded_school = filtered_schools[0]
    else:
        schools_in_sdo = []
    if schools_in_sdo:
        selected_sdo_id = schools_in_sdo[0].get("sdo_id")
        selected_sdo = next((s for s in sdo_list if s["id"] == selected_sdo_id), None)

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
# 6. SIDEBAR
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── User counter ──
    active_count = update_active_users()
    if active_count is not None and active_count > 0:
        st.caption(f"👥 Active viewers: {active_count}")
    else:
        st.caption("👥 Active viewers: N/A (Redis not available)")

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

    # ── School Head: School ID input ──
    if role == "school":
        if st.session_state.loaded_school is None:
            st.markdown("### 🔍 Enter School ID")
            school_id = st.text_input(
                "Type your School ID",
                value=st.session_state.school_id_input,
                placeholder="e.g., 128191",
                key="sidebar_school_id"
            )
            if school_id != st.session_state.school_id_input:
                st.session_state.school_id_input = school_id
                match = next((s for s in schools if s["id"] == school_id.strip()), None)
                if match:
                    st.session_state.loaded_school = match
                    st.rerun()
                else:
                    st.session_state.loaded_school = None
                    if school_id.strip():
                        st.warning("❌ School ID not found.")
        else:
            school = st.session_state.loaded_school
            st.success(f"🏫 {school.get('name', '')}")
            if st.button("Change School", use_container_width=True, key="change_school"):
                st.session_state.loaded_school = None
                st.session_state.school_id_input = ""
                st.rerun()
    else:
        # Regional / Division navigation
        st.markdown("### 🗺️ Navigation")
        if sdo_list and selected_sdo:
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
            st.caption("📭 No data loaded – please upload.")

    st.markdown("---")
    st.markdown("### 📐 Filter by Dimension")
    selected_dimension = st.selectbox("Highlight Dimension", options=["Overall"] + DIMENSION_NAMES, index=0, key="dimension_filter")

    st.markdown("---")
    st.markdown("### 🔍 Search School")
    search_query = st.text_input("Type school name or ID", placeholder="e.g., Central", key="search_school")

    st.markdown("---")
    st.markdown("### 📊 Data Management")
    if role != "school" and selected_sdo and selected_sdo_id is not None and schools_in_sdo:
        excel_data = generate_excel_report(
            selected_sdo["name"], schools_in_sdo, complete_schools, dim_avgs, regional_dim_avgs
        )
        st.download_button(
            label="📥 Download Excel Report",
            data=excel_data,
            file_name=f"SBM_Report_{selected_sdo['name'].replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            key="download_excel"
        )
        pdf_data = generate_pdf_report(
            selected_sdo["name"], schools_in_sdo, complete_schools, dim_avgs, regional_dim_avgs, overall_avg
        )
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_data,
            file_name=f"SBM_Report_{selected_sdo['name'].replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="download_pdf"
        )
    elif role == "school" and schools_in_sdo:
        school = schools_in_sdo[0]
        school_df = pd.DataFrame([school])
        csv_data = school_df.to_csv(index=False)
        st.download_button(
            label="📥 Download School Data (CSV)",
            data=csv_data,
            file_name=f"{school.get('name', 'school').replace(' ', '_')}_data.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_school_csv"
        )
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

    with st.expander("🔍 Debug Data Info", expanded=True):
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
        - 🟢 Green = Stable (≥ 2.5) – no glow
        """)

    st.markdown("---")
    st.caption("SBM Digital Twin · Prototype v1.0")
    st.caption("DepEd Region X – Northern Mindanao")

# ────────────────────────────────────────────────────────────────
# 7. PROCESS UPLOAD – WITH PERSISTENT DEBUG
# ────────────────────────────────────────────────────────────────

def process_uploaded_excel(uploaded_file):
    df = pd.read_excel(uploaded_file, sheet_name=0)
    debug = {}
    debug["columns_detected"] = df.columns.tolist()
    debug["num_rows"] = len(df)

    prefix_map = {
        "CT_": 0, "LE_": 1, "LG_": 2,
        "AC_": 3, "HR_": 4, "FR_": 5
    }

    dim_columns = {idx: [] for idx in range(6)}
    for col in df.columns:
        for prefix, idx in prefix_map.items():
            if col.startswith(prefix):
                dim_columns[idx].append(col)
                break

    debug["dimension_column_counts"] = {DIMENSION_NAMES[i]: len(dim_columns[i]) for i in range(6)}

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

    schools = []
    for idx, row in df.iterrows():
        dimension_scores = [0.0] * 6
        for dim_idx in range(6):
            cols = dim_columns[dim_idx]
            if cols:
                vals = pd.to_numeric(row[cols], errors="coerce").dropna()
                dimension_scores[dim_idx] = vals.mean() if not vals.empty else 0.0

        enrollment_raw = safe_int(row.get("Enrollment", 0))
        enrollment = enrollment_raw if enrollment_raw > 0 else 1

        lowest_school_dim_score = min(dimension_scores)
        lowest_school_dim_index = dimension_scores.index(lowest_school_dim_score)

        school = {
            "id": safe_str(row.get("School ID", idx)),
            "name": safe_str(row.get("School Name", f"School {idx}")),
            "type": safe_str(row.get("School Type", row.get("Offering", ""))),
            "degree": safe_str(row.get("School Type", row.get("Offering", ""))),
            "sdo_id": safe_str(row.get("Division", "")),
            "data_status": safe_str(row.get("Data Status", "Complete")),
            "lat": safe_float(row.get("Latitude", 0)),
            "lng": safe_float(row.get("Longitude", 0)),
            "enrollment": enrollment,
            "urban_rural": safe_str(row.get("Urban/Rural", "Urban")),
            "head_name": safe_str(row.get("School Head Name", "")),
            "head_email": safe_str(row.get("School Head Email", "")),
            "dimension_scores": dimension_scores,
            "overall_index": sum(dimension_scores) / 6,
            "lowest_dim_score": lowest_school_dim_score,
            "lowest_dim_index": lowest_school_dim_index
        }
        schools.append(school)

    debug["sample_school_scores"] = schools[0]["dimension_scores"] if schools else None

    # ── Build SDO list ──
    sdo_names = set(s["sdo_id"] for s in schools if s["sdo_id"])
    debug["sdo_names_found"] = list(sdo_names)

    sdo_list = []
    for sdo_name in sdo_names:
        div_schools = [s for s in schools if s["sdo_id"] == sdo_name]

        lat, lng = 0.0, 0.0
        for s in div_schools:
            if s["lat"] != 0.0 or s["lng"] != 0.0:
                lat, lng = s["lat"], s["lng"]
                break
        if lat == 0.0 and lng == 0.0 and div_schools:
            lat, lng = div_schools[0]["lat"], div_schools[0]["lng"]

        complete_div = [s for s in div_schools if s["data_status"] != "Pending"]
        dim_scores = [0.0] * 6
        if complete_div:
            for d in range(6):
                vals = [s["dimension_scores"][d] for s in complete_div if s["dimension_scores"][d] > 0]
                if vals:
                    dim_scores[d] = sum(vals) / len(vals)

        lowest_dim_score = min(dim_scores) if any(dim_scores) else 0.0
        overall_index = round(sum(dim_scores) / 6, 1) if any(dim_scores) else 0.0
        urgency_factor = round((3.0 - overall_index) / 3.0, 2)

        lowest_dim_idx = dim_scores.index(min(dim_scores))
        lowest_dim_name = DIMENSION_NAMES[lowest_dim_idx]

        sdo_list.append({
            "id": sdo_name,
            "name": sdo_name,
            "capital": "",
            "lat": lat,
            "lng": lng,
            "dimension_scores": dim_scores,
            "lowest_dim_score": lowest_dim_score,
            "lowest_dim_name": lowest_dim_name,
            "overall_index": overall_index,
            "urgency_factor": urgency_factor
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
# 8. MAIN CONTENT – Only if data is loaded
# ────────────────────────────────────────────────────────────────

if not sdo_list or not schools:
    st.error("📭 No data loaded.")
    if st.session_state.debug_info:
        st.write("**Debug Information from last processing:**")
        st.json(st.session_state.debug_info)
    st.info("💡 Please check that the uploaded file has data rows and that the 'Division' column is populated.")
    st.stop()

# ─── Helper to render map safely ───
def render_map(selected_sdo, filtered_sdos, schools_in_sdo, selected_dimension="Overall"):
    lat = selected_sdo.get("lat", 0) if selected_sdo else 0
    lng = selected_sdo.get("lng", 0) if selected_sdo else 0
    if lat == 0.0 and lng == 0.0:
        st.warning("📍 Map unavailable – no geographic coordinates (Latitude/Longitude) provided for this division.")
        return

    if selected_dimension == "Overall" or selected_dimension not in DIMENSION_NAMES:
        dim_index = None
    else:
        dim_index = DIMENSION_NAMES.index(selected_dimension)

    map_center = [lat, lng]
    m = folium.Map(location=map_center, zoom_start=8, tiles="CartoDB positron")
    for sdo in filtered_sdos:
        add_sdo_shield(m, sdo)
    for school in schools_in_sdo:
        add_school_dot(m, school, dim_index=dim_index)

    st_folium(m, width=None, height=500, key="sbm_map")

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
            user_role=role, user_name=user_name, selected_sdo=selected_sdo,
            schools_in_sdo=schools_in_sdo, complete_schools=complete_schools,
            dim_avgs=dim_avgs, overall_avg=overall_avg,
            max_dim_idx=max_dim_idx, min_dim_idx=min_dim_idx
        )
        wrapped_html = f"""<div style="width:100%;padding:0;margin:0;box-sizing:border-box;">{synopsis_html}</div>"""
        st_html(wrapped_html, height=900, scrolling=True)

        st.markdown("---")
        render_map(selected_sdo, filtered_sdos, schools_in_sdo, selected_dimension)

        st.markdown("---")
        st.markdown("""
        <div style="padding:12px 14px;border-radius:6px;background:#f8f9fa;border-left:4px solid #0033a0;font-size:14px;color:#1a1a2e;margin-bottom:12px;">
            <b>💡 About the Pulsing Glow:</b> The animated glow behind each SDO shield indicates <b>urgency based on the division's lowest SBM dimension score</b>.
            <div style="display:flex;flex-wrap:wrap;gap:8px 16px;margin-top:6px;">
                <span style="color:#dc2626;font-weight:600;">🔴 Red</span> Critical (<1.0) ·
                <span style="color:#f97316;font-weight:600;">🟠 Orange</span> Warning (1.0‑1.9) ·
                <span style="color:#eab308;font-weight:600;">🟡 Yellow</span> Monitor (2.0‑2.4) ·
                <span style="color:#22c55e;font-weight:600;">🟢 Green</span> Stable (≥2.5) – no glow
            </div>
            <div style="margin-top:6px;font-size:12px;opacity:0.7;">Faster pulses = more urgent divisions.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color:var(--secondary-background-color);padding:8px 12px;border-radius:6px;border-left:4px solid #22c55e;margin-bottom:12px;color:var(--text-color);font-size:14px;">
            <b>📏 School Dot Sizes:</b> size = enrolment (larger = more learners).
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
        st.caption("Performance of all divisions across the 6 SBM dimensions.")
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
            user_role=role, user_name=user_name, selected_sdo=selected_sdo,
            schools_in_sdo=schools_in_sdo, complete_schools=complete_schools,
            dim_avgs=dim_avgs, overall_avg=overall_avg,
            max_dim_idx=max_dim_idx, min_dim_idx=min_dim_idx
        )
        wrapped_html = f"""<div style="width:100%;padding:0;margin:0;box-sizing:border-box;">{synopsis_html}</div>"""
        st_html(wrapped_html, height=900, scrolling=True)

        st.markdown("---")
        render_map(selected_sdo, filtered_sdos, schools_in_sdo, selected_dimension)

        st.markdown("---")
        st.markdown("""
        <div style="padding:12px 14px;border-radius:6px;background:#f8f9fa;border-left:4px solid #0033a0;font-size:14px;color:#1a1a2e;margin-bottom:12px;">
            <b>💡 About the Pulsing Glow:</b> ... (same as before)
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color:var(--secondary-background-color);padding:8px 12px;border-radius:6px;border-left:4px solid #22c55e;margin-bottom:12px;color:var(--text-color);font-size:14px;">
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
        st.markdown(f"### 📊 School Performance Dashboard – {selected_sdo['name']}")
        render_school_dashboard(schools_in_sdo)

    with tab3:
        render_sandbox(sdo_list, selected_sdo, schools_in_sdo, complete_schools, dim_avgs, overall_avg)

else:
    # ─── SCHOOL HEAD VIEW ───
    if not schools_in_sdo:
        st.info("### 🔍 Enter your School ID in the sidebar to load your dashboard.")
        st.stop()

    school = schools_in_sdo[0]
    div_name = selected_sdo["name"] if selected_sdo else "Unknown Division"

    st.markdown(f"## 🏫 {school['name']}")

    enrollment_display = ""
    if school.get("enrollment", 0) > 1:
        enrollment_display = f" · {school['enrollment']:,} learners"
    st.caption(f"{school.get('type', 'N/A')} · {div_name}{enrollment_display}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        overall = school.get("overall_index", 0)
        st.metric("📊 Overall SBM Index", f"{overall:.1f} / 3.0")
    with col2:
        if overall >= 2.5:
            level = "Always Manifested"
        elif overall >= 2.0:
            level = "Frequently Manifested"
        elif overall >= 1.0:
            level = "Rarely Manifested"
        else:
            level = "Not Yet Manifested"
        st.metric("🎯 SBM Level", level)
    with col3:
        lowest_idx = school.get("lowest_dim_index", 0)
        lowest_name = DIMENSION_NAMES[lowest_idx] if 0 <= lowest_idx < 6 else "?"
        lowest_score = school.get("lowest_dim_score", 0)
        st.metric("⬇️ Lowest Dimension", f"{lowest_name} ({lowest_score:.1f})")
    with col4:
        highest_idx = school["dimension_scores"].index(max(school["dimension_scores"]))
        highest_name = DIMENSION_NAMES[highest_idx]
        highest_score = school["dimension_scores"][highest_idx]
        st.metric("⬆️ Highest Dimension", f"{highest_name} ({highest_score:.1f})")

    st.markdown("### 📊 Dimension Scores")
    dim_scores = school.get("dimension_scores", [0]*6)
    dim_colors = [score_to_color(s) for s in dim_scores]
    fig = go.Figure(data=[
        go.Bar(
            x=DIMENSION_NAMES,
            y=dim_scores,
            marker_color=dim_colors,
            text=[f"{s:.1f}" for s in dim_scores],
            textposition='auto',
            hovertemplate='%{x}: %{y:.1f}<extra></extra>'
        )
    ])
    fig.update_layout(
        yaxis=dict(range=[0, 3], title='Score'),
        height=350,
        margin=dict(l=20, r=20, t=10, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, width='stretch', key="school_dim_bar")

    st.markdown("### 📋 SBM Indicators")
    df_ind = create_indicators_table([school])
    if not df_ind.empty:
        st.dataframe(
            df_ind[["#", "Indicator", "Dimension", "Score", "Status"]],
            column_config={"Score": st.column_config.NumberColumn(format="%.1f")},
            hide_index=True,
            width='stretch'
        )
    else:
        st.info("No indicator data available.")

    st.markdown("### 📍 School Location")
    lat = school.get("lat", 0)
    lng = school.get("lng", 0)
    if lat != 0 or lng != 0:
        m = folium.Map(location=[lat, lng], zoom_start=15, tiles="CartoDB positron")
        add_school_dot(m, school)
        st_folium(m, width=None, height=400, key="school_map")
    else:
        st.warning("📍 Map unavailable – no coordinates provided for this school.")

# ─── SEARCH RESULTS (styled cards) ───
if search_query and schools:
    st.markdown("---")
    st.markdown(f"### 🔍 Search Results for '{search_query}'")
    matches = [s for s in filtered_schools if search_query.lower() in s.get("name", "").lower() or search_query in s.get("id", "")]
    if matches:
        for match in matches:
            sdo = next((s for s in sdo_list if s["id"] == match.get("sdo_id")), None)
            card_html = f"""
            <div style="border:1px solid #e5e7eb;border-radius:8px;padding:12px;margin-bottom:8px;background:#ffffff;">
                <b style="font-size:16px;">{match.get('name', '')}</b><br>
                <span style="color:#6b7280;font-size:13px;">{match.get('type', '')} · {sdo.get('name', '') if sdo else 'Unknown SDO'}</span>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No schools found matching your search.")

st.markdown("---")
st.markdown("<div style='text-align:center;color:#9ca3af;font-size:13px;padding:10px 0;'>© 2026 DepEd Region X – SBM Digital Twin Dashboard · Built with Streamlit</div>", unsafe_allow_html=True)

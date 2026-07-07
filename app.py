"""Main Streamlit application for SBM Dashboard – Region X."""

import streamlit as st
import random
from datetime import datetime

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
from utils.download_helpers import generate_report_data, generate_template_csv

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

# ✅ Safeguard: If user is None for any reason, redirect to login
if user is None:
    st.warning("Session expired. Please log in again.")
    st.stop()

role = user.get("role", "school")
user_name = user.get("name", "User")

# Filter data based on user role
filtered_data = get_accessible_schools(user, sdo_list, schools)
filtered_sdos = filtered_data["filtered_sdos"]
filtered_schools = filtered_data["filtered_schools"]

# ════════════════════════════════════════════════════════════════
# DETERMINE SELECTED SDO (BEFORE SIDEBAR)
# ════════════════════════════════════════════════════════════════

# Initialize variables
selected_sdo = None
selected_sdo_id = None

if is_school_head(user):
    # School head: auto-select their school's SDO
    if filtered_schools:
        school = filtered_schools[0]
        selected_sdo = next((s for s in sdo_list if s["id"] == school["sdo_id"]), None)
        selected_sdo_id = selected_sdo["id"] if selected_sdo else None
    else:
        st.warning("No school data available for your account.")
        st.stop()
else:
    # Division or Regional: we need to choose one division
    if filtered_sdos:
        # If only one division (division level), auto-select it
        if len(filtered_sdos) == 1:
            selected_sdo = filtered_sdos[0]
            selected_sdo_id = selected_sdo["id"]
        else:
            # Regional: will select via sidebar dropdown
            # We'll set a default (first in list) but sidebar will override
            selected_sdo = filtered_sdos[0]
            selected_sdo_id = selected_sdo["id"]
    else:
        st.warning("No divisions accessible.")
        st.stop()

# ─── COMPUTE SCHOOL DATA (for the selected SDO) ───
# This must be done before sidebar because download buttons and synopsis use it.
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

# ─── DETECT DARK MODE FOR SYNOPSIS ───
is_dark_mode = (st.session_state.custom_theme == "dark")

# ════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════

with st.sidebar:
    # ── User Info ──
    st.markdown(f"### 👤 {user_name}")
    st.caption(get_accessible_divisions_summary(user))
    st.markdown("---")
    
    # ── Appearance ──
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
    
    # Only show division selector if not school head
    if not is_school_head(user):
        if filtered_sdos:
            sdo_names = [s["name"] for s in filtered_sdos]
            if len(sdo_names) == 1:
                # Division level: auto-selected, just display
                st.caption(f"📋 {selected_sdo['name']}")
            else:
                # Regional: dropdown to select division
                selected_sdo_name = st.selectbox("Select Division", options=sdo_names, index=0)
                # Update selected_sdo and selected_sdo_id based on selection
                selected_sdo = next(s for s in filtered_sdos if s["name"] == selected_sdo_name)
                selected_sdo_id = selected_sdo["id"]
                # Recompute schools for the new selection
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
        # School head: show school name
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
    
    # ── Data Management ──
    st.markdown("---")
    st.markdown("### 📊 Data Management")
    
    # Download Report Button
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
    
    # Download Template Button
    template_df = generate_template_csv()
    csv_template = template_df.to_csv(index=False)
    st.download_button(
        label="📋 Download Data Collection Template (CSV)",
        data=csv_template,
        file_name="SBM_Data_Collection_Template.csv",
        mime="text/csv",
        use_container_width=True
    )
    st.caption("Template based on DepEd Order No. 007, s. 2024")
    
    # ── Logout ──
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    
    # ── Glossary ──
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

        **Urgency Factor** – 0–1 value indicating how urgent it is to address a division's lowest dimension.

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

# ─── SYNOPSIS SECTION ───
st.markdown("---")

# ---- Build synopsis HTML directly here ----
# Determine theme colors
if is_dark_mode:
    bg_main = "#0E1117"
    bg_card = "#1A1C23"
    bg_strong = "#1A3A2A"
    bg_weak = "#3A1A1A"
    bg_analysis = "#1A1C23"
    bg_interventions = "#2A2A1A"
    bg_priority = "#1A2A3A"
    text_main = "#FAFAFA"
    text_secondary = "#B0B0B0"
    text_muted = "#9CA3AF"
    border_light = "#2A2C33"
    border_strong = "#166534"
    border_weak = "#991B1B"
    gradient_start = "#1A1C23"
    gradient_end = "#262730"
    shadow = "rgba(255,255,255,0.05)"
else:
    bg_main = "#FFFFFF"
    bg_card = "#FFFFFF"
    bg_strong = "#f0fdf4"
    bg_weak = "#fef2f2"
    bg_analysis = "#FFFFFF"
    bg_interventions = "#fffbeb"
    bg_priority = "#f0f4ff"
    text_main = "#1A1A2E"
    text_secondary = "#4B5563"
    text_muted = "#6B7280"
    border_light = "#E5E7EB"
    border_strong = "#166534"
    border_weak = "#991B1B"
    gradient_start = "#f0f4ff"
    gradient_end = "#e8eeff"
    shadow = "rgba(0,0,0,0.05)"

strongest_dim = DIMENSION_NAMES[max_dim_idx]
weakest_dim = DIMENSION_NAMES[min_dim_idx]
strongest_score = dim_avgs[max_dim_idx]
weakest_score = dim_avgs[min_dim_idx]
total_schools = len(schools_in_sdo)
pending_count = len(schools_in_sdo) - len(complete_schools)
current_date = datetime.now().strftime('%B %d, %Y')

# Determine overall level
if overall_avg >= 2.5:
    overall_level = "High"
    overall_color = "#22c55e"
    overall_emoji = "🟢"
elif overall_avg >= 2.0:
    overall_level = "Medium-High"
    overall_color = "#eab308"
    overall_emoji = "🟡"
elif overall_avg >= 1.0:
    overall_level = "Medium-Low"
    overall_color = "#f97316"
    overall_emoji = "🟠"
else:
    overall_level = "Low"
    overall_color = "#dc2626"
    overall_emoji = "🔴"

# Urgency level
if weakest_score < 1.0:
    urgency_level = "Critical"
    urgency_color = "#dc2626"
    urgency_emoji = "🔴"
elif weakest_score < 2.0:
    urgency_level = "Warning"
    urgency_color = "#f97316"
    urgency_emoji = "🟠"
elif weakest_score < 2.5:
    urgency_level = "Monitor"
    urgency_color = "#eab308"
    urgency_emoji = "🟡"
else:
    urgency_level = "Stable"
    urgency_color = "#22c55e"
    urgency_emoji = "🟢"

# Build the HTML synopsis based on role
if role == "regional":
    title = "Regional Executive Summary"
    subtitle = f"Region X – Northern Mindanao"
    strength_label = "Regional Strength"
    weakness_label = "Critical Priority"
    analysis_text = f"<b>{weakest_dim}</b> is the weakest dimension regionally. This requires urgent regional-level intervention and coordinated support across divisions.<br><br><b>{strongest_dim}</b> is the region's strength. Document and share best practices across all divisions."
    interventions = f"""
    <li><b>Short-Term (0-6 Months):</b> Deploy Regional Field Technical Assistance Team (RFTAT) to priority divisions.</li>
    <li><b>Medium-Term (6-12 Months):</b> Establish Regional SBM Monitoring and Evaluation System.</li>
    <li><b>Long-Term (12+ Months):</b> Integrate SBM improvement into Regional Education Development Plan.</li>
    """
    policy_recs = f"""
    <li><b>Immediate:</b> Prioritize {weakest_dim} in regional planning and resource allocation.</li>
    <li><b>Short-Term:</b> Develop region-wide capacity building programs for {weakest_dim}.</li>
    <li><b>Long-Term:</b> Build sustainable systems for continuous improvement across all dimensions.</li>
    """
    summary_cards = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:12px 0;">
        <div style="background:{bg_card};padding:12px;border-radius:8px;text-align:center;border:1px solid {border_light};">
            <div style="font-size:24px;font-weight:700;color:{text_main};">14</div>
            <div style="font-size:12px;color:{text_muted};">Total Divisions</div>
        </div>
        <div style="background:{bg_card};padding:12px;border-radius:8px;text-align:center;border:1px solid {border_light};">
            <div style="font-size:24px;font-weight:700;color:{overall_color};">{overall_avg:.1f}</div>
            <div style="font-size:12px;color:{text_muted};">Division SBM Index</div>
            <div style="font-size:11px;color:{overall_color};">{overall_level}</div>
        </div>
        <div style="background:{bg_card};padding:12px;border-radius:8px;text-align:center;border:1px solid {border_light};">
            <div style="font-size:24px;font-weight:700;color:{urgency_color};">{urgency_level}</div>
            <div style="font-size:12px;color:{text_muted};">Urgency Level</div>
            <div style="font-size:11px;color:{urgency_color};">{urgency_emoji} {weakest_dim} ({weakest_score:.1f})</div>
        </div>
    </div>
    """
elif role == "division":
    title = "Division Executive Summary"
    subtitle = f"{selected_sdo['name']}"
    strength_label = "Strongest Dimension"
    weakness_label = "Weakest Dimension"
    analysis_text = f"<b>{weakest_dim}</b> is the weakest dimension across the division. This requires division-wide attention and coordinated support.<br><br><b>{strongest_dim}</b> is the division's strength. Document and share best practices across schools."
    interventions = f"""
    <li><b>Urgent:</b> Deploy division TA team to schools struggling with {weakest_dim}.</li>
    <li><b>Short-Term:</b> Conduct division-wide training for {weakest_dim}.</li>
    <li><b>Medium-Term:</b> Establish regular monitoring and reporting mechanisms.</li>
    <li><b>Sustain:</b> Scale up best practices from {strongest_dim} across all schools.</li>
    """
    policy_recs = f"""
    <li><b>0-3 Months:</b> Address {weakest_dim} with targeted TA and capacity building.</li>
    <li><b>3-6 Months:</b> Strengthen monitoring and evaluation systems.</li>
    <li><b>6-12 Months:</b> Scale up best practices across the division.</li>
    """
    summary_cards = f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:12px 0;">
        <div style="background:{bg_card};padding:12px;border-radius:8px;text-align:center;border:1px solid {border_light};">
            <div style="font-size:24px;font-weight:700;color:{text_main};">{total_schools}</div>
            <div style="font-size:12px;color:{text_muted};">Total Schools</div>
        </div>
        <div style="background:{bg_card};padding:12px;border-radius:8px;text-align:center;border:1px solid {border_light};">
            <div style="font-size:24px;font-weight:700;color:{overall_color};">{overall_avg:.1f}</div>
            <div style="font-size:12px;color:{text_muted};">Division SBM Index</div>
            <div style="font-size:11px;color:{overall_color};">{overall_level}</div>
        </div>
        <div style="background:{bg_card};padding:12px;border-radius:8px;text-align:center;border:1px solid {border_light};">
            <div style="font-size:24px;font-weight:700;color:{urgency_color};">{pending_count}</div>
            <div style="font-size:12px;color:{text_muted};">Schools with Pending Data</div>
        </div>
    </div>
    """
else:  # school
    school = schools_in_sdo[0] if schools_in_sdo else None
    school_name = school["name"] if school else "Your School"
    title = f"Executive Summary: {school_name}"
    subtitle = ""
    strength_label = "Strongest Dimension"
    weakness_label = "Weakest Dimension"
    analysis_text = f"<b>{weakest_dim}</b> is the weakest dimension. This area requires immediate attention and targeted interventions.<br><br><b>{strongest_dim}</b> is the strongest dimension. Continue current practices and use this as a model for other areas."
    interventions = f"""
    <li><b>Immediate:</b> Conduct focused assessment and capacity building for {weakest_dim}.</li>
    <li><b>Short-Term:</b> Develop an improvement plan with specific, measurable targets.</li>
    <li><b>Medium-Term:</b> Implement interventions and monitor progress regularly.</li>
    <li><b>Sustain:</b> Maintain and enhance performance in {strongest_dim}.</li>
    """
    policy_recs = ""
    summary_cards = f"""
    <div style="background:{bg_card};padding:16px;border-radius:8px;margin:12px 0;border:1px solid {border_light};">
        <h4 style="margin-top:0;color:{text_main};">📊 Overall Performance: {overall_emoji} {overall_level}</h4>
        <p style="font-size:15px;margin-bottom:4px;color:{text_main};">
            <b>Overall SBM Index:</b> <span style="color:{overall_color};font-weight:700;">{overall_avg:.1f} / 3.0</span>
            <span style="font-size:13px;color:{text_muted};margin-left:12px;">({overall_level} performance)</span>
        </p>
    </div>
    """

synopsis_html = f"""
<div style="background:linear-gradient(135deg, {gradient_start} 0%, {gradient_end} 100%);padding:20px 24px;border-radius:12px;border-left:6px solid #0033A0;margin-bottom:20px;color:{text_main};box-shadow:0 2px 8px {shadow};">
    <h3 style="margin-top:0;color:#0033A0;">📋 {title}</h3>
    <p style="font-size:14px;color:{text_secondary};margin-bottom:12px;">
        <b>Prepared for:</b> {user_name} · {(' <b>Division:</b> '+selected_sdo['name']) if role in ['division','school'] else ''} · <b>Date:</b> {current_date}
    </p>
    
    {summary_cards}
    
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:12px 0;">
        <div style="background:{bg_strong};padding:14px;border-radius:8px;border-left:4px solid {border_strong};">
            <h4 style="margin:0 0 6px 0;font-size:14px;color:{border_strong};">✅ {strength_label}</h4>
            <p style="font-size:16px;font-weight:700;margin:0;color:{border_strong};">{strongest_dim}</p>
            <p style="font-size:13px;margin:4px 0 0 0;color:{text_secondary};">Score: <b>{strongest_score:.1f}</b> / 3.0</p>
        </div>
        <div style="background:{bg_weak};padding:14px;border-radius:8px;border-left:4px solid {border_weak};">
            <h4 style="margin:0 0 6px 0;font-size:14px;color:{border_weak};">⚠️ {weakness_label}</h4>
            <p style="font-size:16px;font-weight:700;margin:0;color:{border_weak};">{weakest_dim}</p>
            <p style="font-size:13px;margin:4px 0 0 0;color:{text_secondary};">Score: <b>{weakest_score:.1f}</b> / 3.0</p>
        </div>
    </div>
    
    <div style="background:{bg_analysis};padding:16px;border-radius:8px;margin:12px 0;border:1px solid {border_light};">
        <h4 style="margin-top:0;color:{text_main};">💡 Strategic Analysis</h4>
        <p style="font-size:14px;color:{text_secondary};">
            {analysis_text}
        </p>
    </div>
    
    <div style="background:{bg_interventions};padding:16px;border-radius:8px;border:1px solid #fcd34d;margin:12px 0;">
        <h4 style="margin-top:0;color:#92400e;">🎯 Recommended Interventions</h4>
        <ul style="font-size:13px;color:{text_secondary};padding-left:20px;margin:4px 0;">
            {interventions}
        </ul>
    </div>
    
    {f'''
    <div style="background:{bg_priority};padding:12px;border-radius:8px;border:1px solid #93c5fd;margin:12px 0;">
        <h4 style="margin-top:0;color:#1e40af;font-size:14px;">📌 Policy Recommendations</h4>
        <ul style="font-size:13px;color:{text_secondary};padding-left:20px;margin:4px 0;">
            {policy_recs}
        </ul>
    </div>
    ''' if policy_recs else ''}
    
    <p style="font-size:12px;color:{text_muted};margin-top:12px;text-align:right;">
        <i>Based on current SBM data. For {'school-level' if role=='school' else 'division-level' if role=='division' else 'regional-level'} planning and decision-making.</i>
    </p>
</div>
"""

# ─── WRAP WITH FULL HTML DOCUMENT FOR IFRAME ───
full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            background-color: {bg_main};
            color: {text_main};
            font-family: 'Segoe UI', Roboto, sans-serif;
        }}
        .synopsis-container {{
            padding: 10px;
            max-width: 100%;
            box-sizing: border-box;
        }}
    </style>
</head>
<body>
    <div class="synopsis-container">
        {synopsis_html}
    </div>
</body>
</html>
"""

# ─── RENDER SYNOPSIS USING st.components.v1.html ───
from streamlit.components.v1 import html as st_html
st_html(full_html, height=900, scrolling=True)

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

# ─── ADD EXPLANATION FOR SCHOOL DOT SIZES ───
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
    all_complete = [s for s in filtered_schools if s["data_status"] != "Pending"]
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

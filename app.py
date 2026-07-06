"""Main Streamlit application for SBM Dashboard – Region X."""

import streamlit as st
import folium
from streamlit_folium import folium_static, st_folium

# ─── PAGE CONFIG ───
st.set_page_config(
    page_title="SBM Dashboard – Region X",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── LOAD CUSTOM CSS ───
with open("assets/style.css", "r") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── INJECT PULSE CSS (from map_helpers) ───
from utils.map_helpers import get_pulse_css
st.markdown(get_pulse_css(), unsafe_allow_html=True)

# ... rest of your app code ...

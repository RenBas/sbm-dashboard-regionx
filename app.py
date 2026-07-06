 import streamlit as st

# 1. Set the exact Page Configuration and Heading
st.set_page_config(page_title="The SBM Intelligence Engine", layout="wide", page_icon="🏫")

st.title("The SBM Intelligence Engine")
st.markdown("### *Actualizing DepEd Order No. 007, s. 2024 through Dynamic Monitoring and Digital Twin Simulation*")
st.divider()

st.write("""
**Welcome to the Unified SBM Engine for Northern Mindanao (Region X).**
This system is built in modular layers to support the Schools Division Offices (SDOs) and Schools:
1. **🗺️ Interactive Geospatial Map:** Visualize SBM status across Region X, drill down by Division, and inspect individual schools.
2. **📊 Dynamic Dashboard:** Track the 42 SBM Indicators and the Self-Assessment Calendar.
3. **🧠 Digital Twin:** Run contextualized 'What-If' simulations for Technical Assistance.

👈 **Use the sidebar to navigate between the modules.**
""")

st.success("✅ The SBM Intelligence Engine is successfully connected and running!")  

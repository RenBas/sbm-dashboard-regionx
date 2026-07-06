import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Set up the Page Configuration
st.set_page_config(page_title="SBM Intelligence Engine", layout="wide", page_icon="🏫")

# 2. Create the Header
st.title("🏫 SBM Intelligence Engine")
st.markdown("### *Dynamic Monitoring & Digital Twin for DO 007, s. 2024*")
st.divider()

# 3. Create a Sidebar for School Selection (The SDO View)
st.sidebar.header("📍 School Context & Selection")
selected_school = st.sidebar.selectbox(
    "Select School:",
    ["Mabini National High School (Urban)", "Rizal Elementary (Rural)", "San Jose IPSF (GIDA/IP)"]
)

# Contextual Adjustment Slider (The Digital Twin feature)
context_weight = st.sidebar.slider("Contextual Adjustment Factor", 0.8, 1.2, 1.0, 0.1, 
                                   help="Adjusts baseline expectations based on school context (e.g., GIDA)")

# 4. Simulate the "Brain" (Data for the 6 Dimensions)
# In the real app, this will be pulled from our Pandas DataFrame
dimensions = ["Curriculum & Teaching", "Learning Environment", "Leadership", 
              "Governance & Accountability", "Human Resource", "Finance & Resource"]

# Dummy scores (1 to 4 scale based on DO 007)
scores = [3, 2, 4, 3, 2, 1] 

# 5. Create the Main Dashboard Layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 Overall SBM Health")
    avg_score = sum(scores) / len(scores)
    
    # Display the main metric
    st.metric(label="Average Degree of Manifestation", value=f"{avg_score:.2f}", delta=f"{context_weight}x Context")
    
    # Map the score to the DO 007 terminology
    if avg_score >= 3.5:
        status = "Always Manifested 🟢"
    elif avg_score >= 2.5:
        status = "Frequently Manifested 🟡"
    elif avg_score >= 1.5:
        status = "Rarely Manifested 🟠"
    else:
        status = "Not Yet Manifested 🔴"
        
    st.success(status) if "Always" in status else st.warning(status)

with col2:
    st.subheader("🕸️ The 6 SBM Dimensions (Radar Chart)")
    
    # Create a Plotly Radar Chart
    fig = px.line_polar(
        r=scores + [scores[0]], # Close the loop
        theta=dimensions + [dimensions[0]], 
        line_close=True,
        range_r=[0, 4],
        title="SBM Practice Manifestation"
    )
    fig.update_traces(fill='toself')
    st.plotly_chart(fig, use_container_width=True)

# 6. The "No MOV" Data Input Section (Section V.E compliance)
st.divider()
st.subheader("📝 Self-Assessment & Technical Assistance (TA) Log")
st.caption("Per DO 007, s. 2024: Attaching MOVs is no longer necessary. Log agreements here.")

ta_remarks = st.text_area("SDO & School Agreement / Remarks:", height=100, 
                          placeholder="e.g., School to submit adjusted SIP by Friday. SDO to deploy SGOD focal person for Mental Health TA...")

if st.button("💾 Save to SBM Record"):
    st.toast("Assessment logged successfully! DFTAT notified.", icon="✅")

import streamlit as st
import pandas as pd
import plotly.express as px  # optional, but good for visualisation

# ------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# ------------------------------------------------------------------
st.set_page_config(
    page_title="SBM Dashboard & Digital Twin",
    page_icon="📊",
    layout="wide"
)

# ------------------------------------------------------------------
# 2. SESSION STATE INITIALISATION (The "Zero" State)
# ------------------------------------------------------------------
def reset_app():
    """Hard reset: clear all processed data, twin state, and flags."""
    keys_to_clear = [
        "uploaded_file",
        "raw_school_info",
        "raw_sbm_assessment",
        "processed_school_data",
        "processed_sbm_scores",
        "dimension_averages",
        "twin_results",
        "dashboard_rendered"
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

    # Always set these flags to False
    st.session_state.analysis_complete = False
    st.session_state.dashboard_rendered = False

# Initialise control flags if they don't exist
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "dashboard_rendered" not in st.session_state:
    st.session_state.dashboard_rendered = False

# ------------------------------------------------------------------
# 3. UI LAYOUT: Upload, Run, and Reset
# ------------------------------------------------------------------
st.title("📊 SBM Dashboard & Digital Twin")
st.markdown("Upload your SBM Excel file, then click **Run Analysis** to process the data.")

# ---- File Uploader ----
uploaded_file = st.file_uploader(
    "📂 Upload Excel file (mock_sbm_data.xlsx)",
    type=["xlsx"],
    key="sbm_file_uploader"
)

if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    st.success("✅ File uploaded successfully. Press **'Run Analysis'** to begin processing.")
else:
    # If uploader is cleared, reset analysis flag
    st.session_state.analysis_complete = False
    st.session_state.dashboard_rendered = False

# ---- Action Buttons ----
col1, col2 = st.columns(2)

with col1:
    run_clicked = st.button(
        "🚀 Run Analysis",
        type="primary",
        use_container_width=True,
        disabled=uploaded_file is None
    )

with col2:
    reset_clicked = st.button(
        "🔄 Reset Dashboard & Twin",
        type="secondary",
        use_container_width=True
    )

# ------------------------------------------------------------------
# 4. HANDLE BUTTON LOGIC
# ------------------------------------------------------------------

# ---- Reset ----
if reset_clicked:
    reset_app()
    st.rerun()

# ---- Run Analysis (Heavy processing only here) ----
if run_clicked:
    if uploaded_file is None:
        st.warning("Please upload a file first.")
    else:
        with st.spinner("⏳ Processing SBM data and initialising Twin... Please wait."):
            try:
                # -------------------------------------------------------------
                # 4a. READ THE EXCEL FILE (Two sheets)
                # -------------------------------------------------------------
                school_info = pd.read_excel(uploaded_file, sheet_name="School Information")
                sbm_assessment = pd.read_excel(uploaded_file, sheet_name="SBM Assessment")

                # Store raw data in session_state (for debugging / optional display)
                st.session_state.raw_school_info = school_info
                st.session_state.raw_sbm_assessment = sbm_assessment

                # -------------------------------------------------------------
                # 4b. PROCESSING PIPELINE (Replace with your actual logic)
                # -------------------------------------------------------------
                # Clean School Info: drop rows with all NaN
                clean_schools = school_info.dropna(how='all')

                # Clean SBM Assessment: drop rows where Score is empty (Pending schools)
                clean_scores = sbm_assessment.dropna(subset=['Score'], how='any')

                # Compute dimension averages (this is a minimal but useful summary)
                dimension_avg = clean_scores.groupby('Dimension')['Score'].mean().reset_index()

                # (Optional) Merge to get school-level dimension scores
                # school_dimension_scores = clean_scores.merge(clean_schools, on='School ID', how='left')

                # Store processed results
                st.session_state.processed_school_data = clean_schools
                st.session_state.processed_sbm_scores = clean_scores
                st.session_state.dimension_averages = dimension_avg

                # -------------------------------------------------------------
                # 4c. CALL YOUR DIGITAL TWIN SIMULATION (Optional)
                # -------------------------------------------------------------
                # Safely attempt to import and run the twin.
                # If the import fails, we simply skip it and show a placeholder.
                twin_results = None
                try:
                    # Attempt to import your twin UI (if it exists)
                    # Adjust the import path to match your project structure.
                    from utils.twin_ui import render_twin  # example function name
                    # twin_results = render_twin(clean_scores, clean_schools)
                    st.session_state.twin_results = "Twin executed successfully (placeholder)."
                except ImportError as e:
                    # If the import fails, we don't crash the whole app.
                    st.session_state.twin_results = f"Twin module not loaded: {e}"
                except Exception as e:
                    st.session_state.twin_results = f"Twin execution error: {e}"

                # Mark analysis as complete so the dashboard renders
                st.session_state.analysis_complete = True
                st.session_state.dashboard_rendered = False  # force fresh render

                st.success("✅ Analysis complete! Loading dashboard...")
                st.rerun()  # Rerun to display results in a clean state

            except Exception as e:
                # If any error occurs, we display it but DO NOT re-run automatically.
                st.error(f"❌ Processing failed: {str(e)}")
                st.session_state.analysis_complete = False
                # The app remains stable; user can fix the file or reset.

# ------------------------------------------------------------------
# 5. RENDER THE DASHBOARD (Only when analysis is complete)
# ------------------------------------------------------------------
if st.session_state.get("analysis_complete", False):
    st.divider()
    st.subheader("📊 Dashboard & Twin Output")

    # Display dimension averages
    if "dimension_averages" in st.session_state:
        df_dim = st.session_state.dimension_averages
        st.dataframe(df_dim, use_container_width=True)

        # Plot with Plotly for a nicer view
        fig = px.bar(
            df_dim,
            x="Dimension",
            y="Score",
            title="Average Score per SBM Dimension",
            color="Dimension",
            text="Score"
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig, use_container_width=True)

    # Display a sample of the processed SBM scores
    with st.expander("🔍 View Processed SBM Assessment Data"):
        if "processed_sbm_scores" in st.session_state:
            st.dataframe(st.session_state.processed_sbm_scores.head(50))

    with st.expander("🏫 View School Information"):
        if "processed_school_data" in st.session_state:
            st.dataframe(st.session_state.processed_school_data)

    # Display Twin results (if any)
    if "twin_results" in st.session_state:
        with st.expander("🤖 Digital Twin Output"):
            st.write(st.session_state.twin_results)

    st.session_state.dashboard_rendered = True

elif uploaded_file is not None and not st.session_state.analysis_complete:
    # File uploaded but not analysed yet
    st.info("📌 File ready. Click **'Run Analysis'** to process.")

else:
    # Default state – nothing uploaded
    st.info("🔄 Ready. Please upload an Excel file and click **'Run Analysis'**.")

# ------------------------------------------------------------------
# 6. FOOTER / NOTES
# ------------------------------------------------------------------
st.caption("SBM Dashboard v2.0 – Manual control mode. Upload → Run → Reset.")

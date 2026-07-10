"""Chart creation utilities for Streamlit."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from .constants import DIMENSION_NAMES

def create_radar_chart(division_avgs, regional_avgs):
    """
    Create a Plotly radar chart comparing division vs regional averages.
    Increased size and added hover tooltips showing both values.
    """
    fig = go.Figure()
    
    # ── Division trace (with hover showing both) ──
    fig.add_trace(go.Scatterpolar(
        r=division_avgs,
        theta=DIMENSION_NAMES,
        fill='toself',
        name='This Division',
        line_color='#0033a0',
        fillcolor='rgba(0, 51, 160, 0.25)',
        marker=dict(color='#0033a0', size=8),
        hovertemplate='<b>%{theta}</b><br>Division: %{r:.1f}<br>Region X: %{customdata:.1f}<extra></extra>',
        customdata=regional_avgs
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=regional_avgs,
        theta=DIMENSION_NAMES,
        fill='toself',
        name='Region X Average',
        line_color='#ce1126',
        line_dash='dash',
        fillcolor='rgba(206, 17, 38, 0.10)',
        marker=dict(color='#ce1126', size=7),
        hovertemplate='<b>%{theta}</b><br>Region X: %{r:.1f}<br>Division: %{customdata:.1f}<extra></extra>',
        customdata=division_avgs
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 3],
                tickvals=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                tickfont=dict(size=11)
            ),
            angularaxis=dict(tickfont=dict(size=13))
        ),
        legend=dict(orientation='h', yanchor='bottom', y=1.1, xanchor='center', x=0.5, font=dict(size=13)),
        margin=dict(l=60, r=60, t=60, b=60),
        height=500,
        width=700,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )
    return fig


def create_trend_chart(years, values):
    """Create a bar chart showing historical trend."""
    fig = go.Figure()
    colors = ['#0033a0' if i == 0 else '#93a3c7' for i in range(len(years))]
    fig.add_trace(go.Bar(
        x=years,
        y=values,
        marker_color=colors,
        text=[f'{v:.1f}' for v in values],
        textposition='outside',
        textfont=dict(size=11, color='#1a1a2e'),
        hovertemplate='%{x}: %{y:.1f}<extra></extra>'
    ))
    fig.update_layout(
        yaxis=dict(title='SBM Index', range=[0, 3.5], tickvals=[0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0], tickfont=dict(size=10)),
        xaxis=dict(tickfont=dict(size=11)),
        margin=dict(l=50, r=20, t=10, b=30),
        height=180,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def create_indicators_table(schools):
    """
    Create a DataFrame of indicator averages for the selected division.
    For the prototype, we use sample indicators (14 of the 42).
    """
    sample_indicators = [
        {"id": 1, "desc": "Grade 3 proficiency – early literacy", "dim": 0},
        {"id": 2, "desc": "Grade 6/10/12 NAT proficiency", "dim": 0},
        {"id": 4, "desc": "Teachers prepare contextualized materials", "dim": 0},
        {"id": 9, "desc": "Zero bullying incidence", "dim": 1},
        {"id": 11, "desc": "Reduced drop-out incidence", "dim": 1},
        {"id": 16, "desc": "Functional DRRM plan", "dim": 1},
        {"id": 19, "desc": "School develops strategic plan", "dim": 2},
        {"id": 22, "desc": "Innovates in frontline services", "dim": 2},
        {"id": 23, "desc": "Strategic plan operationalized", "dim": 3},
        {"id": 25, "desc": "Functional PTA", "dim": 3},
        {"id": 28, "desc": "Teachers complete professional development", "dim": 4},
        {"id": 33, "desc": "Recognizes personnel performance", "dim": 4},
        {"id": 36, "desc": "Inspects infrastructure & facilities", "dim": 5},
        {"id": 41, "desc": "75–100% MOOE utilization", "dim": 5},
    ]
    complete_schools = [s for s in schools if s["data_status"] != "Pending"]
    if not complete_schools:
        return pd.DataFrame()
    data = []
    for ind in sample_indicators:
        dim_idx = ind["dim"]
        avg_score = round(sum(s["dimension_scores"][dim_idx] for s in complete_schools) / len(complete_schools), 1)
        if avg_score >= 2.5:
            status = "Always"
            color = "#22c55e"
        elif avg_score >= 2.0:
            status = "Frequently"
            color = "#eab308"
        elif avg_score >= 1.0:
            status = "Rarely"
            color = "#f97316"
        else:
            status = "Not Yet"
            color = "#9ca3af"
        data.append({
            "#": ind["id"],
            "Indicator": ind["desc"],
            "Dimension": DIMENSION_NAMES[ind["dim"]],
            "Score": avg_score,
            "Status": status,
            "Color": color
        })
    return pd.DataFrame(data)


def render_school_dashboard(schools_in_sdo):
    """
    Display a comprehensive school performance dashboard for a division.
    Shows summary metrics and a searchable, colour-coded data table.
    """
    if not schools_in_sdo:
        st.info("No school data available for this division.")
        return

    total = len(schools_in_sdo)
    complete = [s for s in schools_in_sdo if s.get("data_status") != "Pending"]
    overall_avg = sum(s.get("overall_index", 0) for s in complete) / len(complete) if complete else 0.0

    levels = {"Always Manifested": 0, "Frequently Manifested": 0, "Rarely Manifested": 0, "Not Yet Manifested": 0}
    for s in complete:
        score = s.get("overall_index", 0)
        if score >= 2.5:
            levels["Always Manifested"] += 1
        elif score >= 2.0:
            levels["Frequently Manifested"] += 1
        elif score >= 1.0:
            levels["Rarely Manifested"] += 1
        else:
            levels["Not Yet Manifested"] += 1

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("🏫 Total Schools", total)
    with col2:
        st.metric("📊 Avg SBM Index", f"{overall_avg:.1f}" if complete else "—")
    with col3:
        st.metric("🟢 Always Manifested", levels["Always Manifested"])
    with col4:
        st.metric("🟡 Frequently Manifested", levels["Frequently Manifested"])
    with col5:
        st.metric("🟠 Rarely Manifested", levels["Rarely Manifested"])

    st.markdown("### 📋 School‑Level Data")

    rows = []
    for school in schools_in_sdo:
        dim_scores = school.get("dimension_scores", [0]*6)
        overall = school.get("overall_index", 0)
        if school.get("data_status") == "Pending":
            sbm_level = "Pending"
        elif overall >= 2.5:
            sbm_level = "Always Manifested"
        elif overall >= 2.0:
            sbm_level = "Frequently Manifested"
        elif overall >= 1.0:
            sbm_level = "Rarely Manifested"
        else:
            sbm_level = "Not Yet Manifested"

        lowest_idx = school.get("lowest_dim_index", 0)
        lowest_dim = DIMENSION_NAMES[lowest_idx] if 0 <= lowest_idx < 6 else "?"

        rows.append({
            "School": school.get("name", ""),
            "Type": school.get("type", ""),
            "Enrollment": school.get("enrollment", 0),
            "Overall": overall,
            "Curriculum & Teaching": dim_scores[0],
            "Learning Environment": dim_scores[1],
            "Leadership": dim_scores[2],
            "Governance & Accountability": dim_scores[3],
            "HR & Team Dev.": dim_scores[4],
            "Finance & Resource": dim_scores[5],
            "Lowest Dim.": f"{lowest_dim} ({school.get('lowest_dim_score', 0):.1f})",
            "SBM Level": sbm_level
        })

    df = pd.DataFrame(rows)

    def color_dim(val):
        if pd.isna(val): return ''
        if val >= 2.5: return 'background-color: #22c55e; color: white'
        elif val >= 2.0: return 'background-color: #eab308; color: white'
        elif val >= 1.0: return 'background-color: #f97316; color: white'
        else: return 'background-color: #dc2626; color: white'

    dim_cols = df.columns[3:9]  # Overall, CT, LE, LD, GA, HR, FR
    styled_df = df.style.map(color_dim, subset=dim_cols).format("{:.1f}", subset=dim_cols)

    st.dataframe(
        styled_df,
        column_config={
            "Overall": st.column_config.NumberColumn(format="%.1f"),
            "Curriculum & Teaching": st.column_config.NumberColumn(format="%.1f"),
            "Learning Environment": st.column_config.NumberColumn(format="%.1f"),
            "Leadership": st.column_config.NumberColumn(format="%.1f"),
            "Governance & Accountability": st.column_config.NumberColumn(format="%.1f"),
            "HR & Team Dev.": st.column_config.NumberColumn(format="%.1f"),
            "Finance & Resource": st.column_config.NumberColumn(format="%.1f"),
        },
        hide_index=True,
        use_container_width=True,
        height=500
    )

    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download School Data (CSV)",
        data=csv,
        file_name="school_performance.csv",
        mime="text/csv",
        key="download_school_dashboard"
    )

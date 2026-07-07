"""Synopsis generator for SBM Dashboard – creates narrative reports for decision-makers."""

import streamlit as st
from datetime import datetime
from utils.constants import DIMENSION_NAMES


def generate_synopsis(user_role, user_name, selected_sdo, schools_in_sdo, complete_schools, dim_avgs, overall_avg, max_dim_idx, min_dim_idx):
    """
    Generate a narrative synopsis based on the user's role and the data.
    Returns a formatted HTML string.
    """
    if not complete_schools:
        return _no_data_message()
    
    # Get dimension names
    strongest_dim = DIMENSION_NAMES[max_dim_idx]
    weakest_dim = DIMENSION_NAMES[min_dim_idx]
    strongest_score = dim_avgs[max_dim_idx]
    weakest_score = dim_avgs[min_dim_idx]
    total_schools = len(schools_in_sdo)
    pending_count = len(schools_in_sdo) - len(complete_schools)
    
    # Determine overall performance level
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
    
    # Determine urgency level for weakest dimension
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
    
    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Generate role-specific content
    if user_role == "school":
        return _school_synopsis(
            user_name, selected_sdo, schools_in_sdo, complete_schools,
            strongest_dim, weakest_dim, strongest_score, weakest_score,
            overall_avg, overall_level, overall_color, overall_emoji,
            urgency_level, urgency_color, urgency_emoji, current_date
        )
    elif user_role == "division":
        return _division_synopsis(
            user_name, selected_sdo, schools_in_sdo, complete_schools,
            strongest_dim, weakest_dim, strongest_score, weakest_score,
            overall_avg, overall_level, overall_color, overall_emoji,
            urgency_level, urgency_color, urgency_emoji, total_schools, pending_count, current_date
        )
    elif user_role == "regional":
        return _regional_synopsis(
            user_name, selected_sdo, schools_in_sdo, complete_schools,
            strongest_dim, weakest_dim, strongest_score, weakest_score,
            overall_avg, overall_level, overall_color, overall_emoji,
            urgency_level, urgency_color, urgency_emoji, total_schools, pending_count, current_date
        )
    else:
        return _no_data_message()


def _school_synopsis(user_name, selected_sdo, schools_in_sdo, complete_schools,
                     strongest_dim, weakest_dim, strongest_score, weakest_score,
                     overall_avg, overall_level, overall_color, overall_emoji,
                     urgency_level, urgency_color, urgency_emoji, current_date):
    """Synopsis for School Head level."""
    school = schools_in_sdo[0] if schools_in_sdo else None
    school_name = school["name"] if school else "Your School"
    
    html = f"""
    <div style="background:linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);padding:20px 24px;border-radius:12px;border-left:6px solid #0033A0;margin-bottom:20px;color:#1a1a2e;">
        <h3 style="margin-top:0;color:#0033A0;">📋 Executive Summary: {school_name}</h3>
        <p style="font-size:14px;color:#4b5563;margin-bottom:12px;">
            <b>Prepared for:</b> {user_name} · <b>Date:</b> {current_date}
        </p>
        
        <div style="background:white;padding:16px;border-radius:8px;margin:12px 0;">
            <h4 style="margin-top:0;">📊 Overall Performance: {overall_emoji} {overall_level}</h4>
            <p style="font-size:15px;margin-bottom:4px;">
                <b>Overall SBM Index:</b> <span style="color:{overall_color};font-weight:700;">{overall_avg:.1f} / 3.0</span>
                <span style="font-size:13px;color:#6b7280;margin-left:12px;">({overall_level} performance)</span>
            </p>
        </div>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:12px 0;">
            <div style="background:#f0fdf4;padding:14px;border-radius:8px;border-left:4px solid #22c55e;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#166534;">✅ Strongest Dimension</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#166534;">{strongest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Score: <b>{strongest_score:.1f}</b> / 3.0</p>
            </div>
            <div style="background:#fef2f2;padding:14px;border-radius:8px;border-left:4px solid #dc2626;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#991b1b;">⚠️ Weakest Dimension</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#991b1b;">{weakest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Score: <b>{weakest_score:.1f}</b> / 3.0</p>
            </div>
        </div>
        
        <div style="background:white;padding:16px;border-radius:8px;margin:12px 0;">
            <h4 style="margin-top:0;">💡 Analysis</h4>
            <p style="font-size:14px;color:#4b5563;">
                <b>{weakest_dim}</b> is the weakest dimension. This area requires immediate attention and targeted interventions.
                <br><br>
                <b>{strongest_dim}</b> is the strongest dimension. Continue current practices and use this as a model for other areas.
            </p>
        </div>
        
        <div style="background:#fffbeb;padding:16px;border-radius:8px;border:1px solid #fcd34d;margin:12px 0;">
            <h4 style="margin-top:0;color:#92400e;">🎯 Recommended Interventions</h4>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                <li><b>Immediate:</b> Conduct focused assessment and capacity building for {weakest_dim}.</li>
                <li><b>Short-Term:</b> Develop an improvement plan with specific, measurable targets.</li>
                <li><b>Medium-Term:</b> Implement interventions and monitor progress regularly.</li>
                <li><b>Sustain:</b> Maintain and enhance performance in {strongest_dim}.</li>
            </ul>
        </div>
        
        <p style="font-size:12px;color:#6b7280;margin-top:12px;text-align:right;">
            <i>Based on current SBM self-assessment data. For school-level planning and decision-making.</i>
        </p>
    </div>
    """
    return html


def _division_synopsis(user_name, selected_sdo, schools_in_sdo, complete_schools,
                       strongest_dim, weakest_dim, strongest_score, weakest_score,
                       overall_avg, overall_level, overall_color, overall_emoji,
                       urgency_level, urgency_color, urgency_emoji, total_schools, pending_count, current_date):
    """Synopsis for Division level."""
    html = f"""
    <div style="background:linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);padding:20px 24px;border-radius:12px;border-left:6px solid #0033A0;margin-bottom:20px;color:#1a1a2e;">
        <h3 style="margin-top:0;color:#0033A0;">📋 Division Executive Summary</h3>
        <p style="font-size:14px;color:#4b5563;margin-bottom:12px;">
            <b>Prepared for:</b> {user_name} · <b>Division:</b> {selected_sdo['name']} · <b>Date:</b> {current_date}
        </p>
        
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:12px 0;">
            <div style="background:white;padding:12px;border-radius:8px;text-align:center;">
                <div style="font-size:24px;font-weight:700;">{total_schools}</div>
                <div style="font-size:12px;color:#6b7280;">Total Schools</div>
            </div>
            <div style="background:white;padding:12px;border-radius:8px;text-align:center;">
                <div style="font-size:24px;font-weight:700;color:{overall_color};">{overall_avg:.1f}</div>
                <div style="font-size:12px;color:#6b7280;">Division SBM Index</div>
                <div style="font-size:11px;color:{overall_color};">{overall_level}</div>
            </div>
            <div style="background:white;padding:12px;border-radius:8px;text-align:center;">
                <div style="font-size:24px;font-weight:700;color:{urgency_color};">{pending_count}</div>
                <div style="font-size:12px;color:#6b7280;">Schools with Pending Data</div>
            </div>
        </div>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:12px 0;">
            <div style="background:#f0fdf4;padding:14px;border-radius:8px;border-left:4px solid #22c55e;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#166534;">✅ Strongest Dimension</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#166534;">{strongest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Division Average: <b>{strongest_score:.1f}</b> / 3.0</p>
            </div>
            <div style="background:#fef2f2;padding:14px;border-radius:8px;border-left:4px solid #dc2626;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#991b1b;">⚠️ Weakest Dimension</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#991b1b;">{weakest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Division Average: <b>{weakest_score:.1f}</b> / 3.0</p>
            </div>
        </div>
        
        <div style="background:white;padding:16px;border-radius:8px;margin:12px 0;">
            <h4 style="margin-top:0;">💡 Analysis</h4>
            <p style="font-size:14px;color:#4b5563;">
                <b>{weakest_dim}</b> is the weakest dimension across the division. This requires division-wide attention and coordinated support.
                <br><br>
                <b>{strongest_dim}</b> is the division's strength. Document and share best practices across schools.
            </p>
        </div>
        
        <div style="background:#fffbeb;padding:16px;border-radius:8px;border:1px solid #fcd34d;margin:12px 0;">
            <h4 style="margin-top:0;color:#92400e;">🎯 Recommended Interventions</h4>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                <li><b>Urgent:</b> Deploy division TA team to schools struggling with {weakest_dim}.</li>
                <li><b>Short-Term:</b> Conduct division-wide training for {weakest_dim}.</li>
                <li><b>Medium-Term:</b> Establish regular monitoring and reporting mechanisms.</li>
                <li><b>Sustain:</b> Scale up best practices from {strongest_dim} across all schools.</li>
            </ul>
        </div>
        
        <div style="background:#f0f4ff;padding:12px;border-radius:8px;border:1px solid #93c5fd;margin:12px 0;">
            <h4 style="margin-top:0;color:#1e40af;font-size:14px;">📌 Priority Action Items</h4>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                <li><b>0-3 Months:</b> Address {weakest_dim} with targeted TA and capacity building.</li>
                <li><b>3-6 Months:</b> Strengthen monitoring and evaluation systems.</li>
                <li><b>6-12 Months:</b> Scale up best practices across the division.</li>
            </ul>
        </div>
        
        <p style="font-size:12px;color:#6b7280;margin-top:12px;text-align:right;">
            <i>Based on current SBM data. For division-level planning and decision-making.</i>
        </p>
    </div>
    """
    return html


def _regional_synopsis(user_name, selected_sdo, schools_in_sdo, complete_schools,
                       strongest_dim, weakest_dim, strongest_score, weakest_score,
                       overall_avg, overall_level, overall_color, overall_emoji,
                       urgency_level, urgency_color, urgency_emoji, total_schools, pending_count, current_date):
    """Synopsis for Regional level."""
    html = f"""
    <div style="background:linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);padding:20px 24px;border-radius:12px;border-left:6px solid #0033A0;margin-bottom:20px;color:#1a1a2e;">
        <h3 style="margin-top:0;color:#0033A0;">📋 Regional Executive Summary</h3>
        <p style="font-size:14px;color:#4b5563;margin-bottom:12px;">
            <b>Prepared for:</b> {user_name} · <b>Region:</b> X – Northern Mindanao · <b>Date:</b> {current_date}
        </p>
        
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:12px 0;">
            <div style="background:white;padding:12px;border-radius:8px;text-align:center;">
                <div style="font-size:24px;font-weight:700;">14</div>
                <div style="font-size:12px;color:#6b7280;">Total Divisions</div>
            </div>
            <div style="background:white;padding:12px;border-radius:8px;text-align:center;">
                <div style="font-size:24px;font-weight:700;color:{overall_color};">{overall_avg:.1f}</div>
                <div style="font-size:12px;color:#6b7280;">Division SBM Index</div>
                <div style="font-size:11px;color:{overall_color};">{overall_level}</div>
            </div>
            <div style="background:white;padding:12px;border-radius:8px;text-align:center;">
                <div style="font-size:24px;font-weight:700;color:{urgency_color};">{urgency_level}</div>
                <div style="font-size:12px;color:#6b7280;">Urgency Level</div>
                <div style="font-size:11px;color:{urgency_color};">{urgency_emoji} {weakest_dim} ({weakest_score:.1f})</div>
            </div>
        </div>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:12px 0;">
            <div style="background:#f0fdf4;padding:14px;border-radius:8px;border-left:4px solid #22c55e;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#166534;">✅ Regional Strength</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#166534;">{strongest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Regional Average: <b>{strongest_score:.1f}</b> / 3.0</p>
            </div>
            <div style="background:#fef2f2;padding:14px;border-radius:8px;border-left:4px solid #dc2626;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#991b1b;">⚠️ Critical Priority</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#991b1b;">{weakest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Regional Average: <b>{weakest_score:.1f}</b> / 3.0</p>
            </div>
        </div>
        
        <div style="background:white;padding:16px;border-radius:8px;margin:12px 0;">
            <h4 style="margin-top:0;">💡 Strategic Analysis</h4>
            <p style="font-size:14px;color:#4b5563;">
                <b>{weakest_dim}</b> is the weakest dimension regionally. This requires urgent regional-level intervention and coordinated support across divisions.
                <br><br>
                <b>{strongest_dim}</b> is the region's strength. Document and share best practices across all divisions.
            </p>
        </div>
        
        <div style="background:#fffbeb;padding:16px;border-radius:8px;border:1px solid #fcd34d;margin:12px 0;">
            <h4 style="margin-top:0;color:#92400e;">🎯 Regional Strategic Interventions</h4>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                <li><b>Short-Term (0-6 Months):</b> Deploy Regional Field Technical Assistance Team (RFTAT) to priority divisions.</li>
                <li><b>Medium-Term (6-12 Months):</b> Establish Regional SBM Monitoring and Evaluation System.</li>
                <li><b>Long-Term (12+ Months):</b> Integrate SBM improvement into Regional Education Development Plan.</li>
            </ul>
        </div>
        
        <div style="background:#f0f4ff;padding:12px;border-radius:8px;border:1px solid #93c5fd;margin:12px 0;">
            <h4 style="margin-top:0;color:#1e40af;font-size:14px;">📌 Policy Recommendations</h4>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                <li><b>Immediate:</b> Prioritize {weakest_dim} in regional planning and resource allocation.</li>
                <li><b>Short-Term:</b> Develop region-wide capacity building programs for {weakest_dim}.</li>
                <li><b>Long-Term:</b> Build sustainable systems for continuous improvement across all dimensions.</li>
            </ul>
        </div>
        
        <p style="font-size:12px;color:#6b7280;margin-top:12px;text-align:right;">
            <i>Based on current SBM data. For regional-level strategic planning and decision-making.</i>
        </p>
    </div>
    """
    return html


def _no_data_message():
    """Return message when no data is available."""
    return """
    <div style="background:#fef3c7;padding:20px;border-radius:12px;border-left:6px solid #f59e0b;margin-bottom:20px;">
        <h4 style="margin-top:0;color:#92400e;">ℹ️ No Data Available</h4>
        <p style="color:#4b5563;font-size:14px;">
            There is currently no complete SBM data available for your role or selected division. 
            Please ensure that schools have submitted their SBM self-assessment data.
        </p>
    </div>
    """

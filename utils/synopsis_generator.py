"""Synopsis generator for SBM Dashboard – creates narrative reports for decision-makers."""

import streamlit as st
from .constants import DIMENSION_NAMES

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
    
    # Generate role-specific content
    if user_role == "school":
        return _school_synopsis(
            user_name, selected_sdo, schools_in_sdo, complete_schools,
            strongest_dim, weakest_dim, strongest_score, weakest_score,
            overall_avg, overall_level, overall_color, overall_emoji,
            urgency_level, urgency_color, urgency_emoji
        )
    elif user_role == "division":
        return _division_synopsis(
            user_name, selected_sdo, schools_in_sdo, complete_schools,
            strongest_dim, weakest_dim, strongest_score, weakest_score,
            overall_avg, overall_level, overall_color, overall_emoji,
            urgency_level, urgency_color, urgency_emoji, total_schools, pending_count
        )
    elif user_role == "regional":
        return _regional_synopsis(
            user_name, selected_sdo, schools_in_sdo, complete_schools,
            strongest_dim, weakest_dim, strongest_score, weakest_score,
            overall_avg, overall_level, overall_color, overall_emoji,
            urgency_level, urgency_color, urgency_emoji, total_schools, pending_count
        )
    else:
        return _no_data_message()


def _school_synopsis(user_name, selected_sdo, schools_in_sdo, complete_schools,
                     strongest_dim, weakest_dim, strongest_score, weakest_score,
                     overall_avg, overall_level, overall_color, overall_emoji,
                     urgency_level, urgency_color, urgency_emoji):
    """Synopsis for School Head level."""
    school = schools_in_sdo[0] if schools_in_sdo else None
    school_name = school["name"] if school else "Your School"
    
    return f"""
    <div style="background:linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);padding:20px 24px;border-radius:12px;border-left:6px solid #0033A0;margin-bottom:20px;color:#1a1a2e;">
        <h3 style="margin-top:0;color:#0033A0;">📋 Executive Summary: {school_name}</h3>
        <p style="font-size:14px;color:#4b5563;margin-bottom:12px;">
            <b>Prepared for:</b> {user_name} · <b>Date:</b> {__import__('datetime').datetime.now().strftime('%B %d, %Y')}
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
                <p style="font-size:12px;color:#6b7280;margin:6px 0 0 0;">
                    <i>This dimension is performing well. The school has effectively implemented practices in this area, contributing positively to overall SBM implementation.</i>
                </p>
            </div>
            <div style="background:#fef2f2;padding:14px;border-radius:8px;border-left:4px solid #dc2626;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#991b1b;">⚠️ Weakest Dimension</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#991b1b;">{weakest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Score: <b>{weakest_score:.1f}</b> / 3.0</p>
                <p style="font-size:12px;color:#6b7280;margin:6px 0 0 0;">
                    <i>This dimension requires immediate attention. The school's performance in this area is below expected standards.</i>
                </p>
            </div>
        </div>
        
        <div style="background:white;padding:16px;border-radius:8px;margin:12px 0;">
            <h4 style="margin-top:0;">💡 Why This Matters</h4>
            <p style="font-size:14px;color:#4b5563;margin-bottom:8px;">
                <b>Why is {weakest_dim} underperforming?</b>
            </p>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin-top:4px;">
                <li>Limited resources allocated to this dimension may be insufficient to meet requirements.</li>
                <li>Lack of targeted capacity-building initiatives for school personnel in this area.</li>
                <li>Inconsistent monitoring and evaluation of practices related to this dimension.</li>
                <li>Stakeholder engagement and participation in this area may be limited.</li>
            </ul>
            
            <p style="font-size:14px;color:#4b5563;margin-top:12px;">
                <b>Why is {strongest_dim} performing well?</b>
            </p>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin-top:4px;">
                <li>Strong leadership and commitment from school personnel in this area.</li>
                <li>Consistent implementation of best practices and regular monitoring.</li>
                <li>Effective stakeholder engagement and community support.</li>
                <li>Adequate resources allocated to support this dimension.</li>
            </ul>
        </div>
        
        <div style="background:#fffbeb;padding:16px;border-radius:8px;border:1px solid #fcd34d;margin:12px 0;">
            <h4 style="margin-top:0;color:#92400e;">🎯 Recommended Interventions</h4>
            
            <div style="margin:8px 0;">
                <p style="font-weight:600;font-size:14px;margin:0 0 4px 0;color:#92400e;">For {weakest_dim} (Weakest Dimension):</p>
                <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                    <li><b>Immediate Action:</b> Conduct a focused assessment to identify specific gaps in {weakest_dim}.</li>
                    <li><b>Capacity Building:</b> Provide targeted training and professional development for school personnel.</li>
                    <li><b>Resource Allocation:</b> Prioritize budget and resources to support improvements in this dimension.</li>
                    <li><b>Monitoring:</b> Establish regular monitoring and progress tracking mechanisms.</li>
                    <li><b>Stakeholder Engagement:</b> Increase participation of parents, teachers, and community members.</li>
                </ul>
            </div>
            
            <div style="margin:8px 0;">
                <p style="font-weight:600;font-size:14px;margin:0 0 4px 0;color:#92400e;">For {strongest_dim} (Strongest Dimension):</p>
                <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                    <li><b>Sustain:</b> Continue current practices and maintain consistent monitoring.</li>
                    <li><b>Share:</b> Document best practices and share with other schools/divisions.</li>
                    <li><b>Replicate:</b> Apply successful strategies from this dimension to other areas.</li>
                    <li><b>Innovate:</b> Explore opportunities to further enhance performance.</li>
                </ul>
            </div>
        </div>
        
        <p style="font-size:12px;color:#6b7280;margin-top:12px;text-align:right;">
            <i>This synopsis is generated based on current SBM data and provides actionable insights for school improvement.</i>
        </p>
    </div>
    """


def _division_synopsis(user_name, selected_sdo, schools_in_sdo, complete_schools,
                       strongest_dim, weakest_dim, strongest_score, weakest_score,
                       overall_avg, overall_level, overall_color, overall_emoji,
                       urgency_level, urgency_color, urgency_emoji, total_schools, pending_count):
    """Synopsis for Division level."""
    return f"""
    <div style="background:linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);padding:20px 24px;border-radius:12px;border-left:6px solid #0033A0;margin-bottom:20px;color:#1a1a2e;">
        <h3 style="margin-top:0;color:#0033A0;">📋 Division-Level Executive Summary</h3>
        <p style="font-size:14px;color:#4b5563;margin-bottom:12px;">
            <b>Prepared for:</b> {user_name} · <b>Division:</b> {selected_sdo['name']} · 
            <b>Date:</b> {__import__('datetime').datetime.now().strftime('%B %d, %Y')}
        </p>
        
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:12px 0;">
            <div style="background:white;padding:12px;border-radius:8px;text-align:center;">
                <div style="font-size:24px;font-weight:700;">{total_schools}</div>
                <div style="font-size:12px;color:#6b7280;">Total Schools</div>
            </div>
            <div style="background:white;padding:12px;border-radius:8px;text-align:center;">
                <div style="font-size:24px;font-weight:700;color:{overall_color};">{overall_avg:.1f}</div>
                <div style="font-size:12px;color:#6b7280;">Overall SBM Index</div>
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
                <p style="font-size:12px;color:#6b7280;margin:6px 0 0 0;">
                    <i>This dimension is the division's area of strength. Schools under this division have effectively implemented practices in this area.</i>
                </p>
            </div>
            <div style="background:#fef2f2;padding:14px;border-radius:8px;border-left:4px solid #dc2626;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#991b1b;">⚠️ Weakest Dimension</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#991b1b;">{weakest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Division Average: <b>{weakest_score:.1f}</b> / 3.0</p>
                <p style="font-size:12px;color:#6b7280;margin:6px 0 0 0;">
                    <i>This dimension requires division-wide attention. Most schools in the division are struggling in this area.</i>
                </p>
            </div>
        </div>
        
        <div style="background:white;padding:16px;border-radius:8px;margin:12px 0;">
            <h4 style="margin-top:0;">💡 Root Cause Analysis</h4>
            <p style="font-size:14px;color:#4b5563;margin-bottom:8px;">
                <b>Why is {weakest_dim} underperforming across the division?</b>
            </p>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin-top:4px;">
                <li>Insufficient technical assistance provided to schools on this dimension.</li>
                <li>Limited resources and funding allocated to support improvement efforts.</li>
                <li>Gaps in capacity-building programs for school heads and teachers.</li>
                <li>Inconsistent monitoring and evaluation of SBM implementation.</li>
                <li>Challenges in stakeholder engagement and community participation.</li>
            </ul>
            
            <p style="font-size:14px;color:#4b5563;margin-top:12px;">
                <b>Why is {strongest_dim} performing well?</b>
            </p>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin-top:4px;">
                <li>Strong leadership support and commitment from schools.</li>
                <li>Effective implementation of DepEd programs and initiatives.</li>
                <li>Regular monitoring and feedback mechanisms in place.</li>
                <li>Active stakeholder engagement and community partnerships.</li>
            </ul>
        </div>
        
        <div style="background:#fffbeb;padding:16px;border-radius:8px;border:1px solid #fcd34d;margin:12px 0;">
            <h4 style="margin-top:0;color:#92400e;">🎯 Recommended Division-Level Interventions</h4>
            
            <div style="margin:8px 0;">
                <p style="font-weight:600;font-size:14px;margin:0 0 4px 0;color:#92400e;">For {weakest_dim} (Division-Wide Weakness):</p>
                <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                    <li><b>Technical Assistance Plan:</b> Develop a targeted TA plan to support schools struggling in this dimension.</li>
                    <li><b>Capacity Building:</b> Conduct division-wide training and professional development.</li>
                    <li><b>Resource Mobilization:</b> Allocate SDO funds and resources to support improvement.</li>
                    <li><b>Monitoring Framework:</b> Establish regular progress monitoring and reporting mechanisms.</li>
                    <li><b>Peer Learning:</b> Facilitate sharing of best practices among schools.</li>
                </ul>
            </div>
            
            <div style="margin:8px 0;">
                <p style="font-weight:600;font-size:14px;margin:0 0 4px 0;color:#92400e;">For {strongest_dim} (Division Strength):</p>
                <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                    <li><b>Scale Up:</b> Promote successful practices across all schools in the division.</li>
                    <li><b>Documentation:</b> Create a repository of best practices for reference.</li>
                    <li><b>Recognition:</b> Acknowledge and reward schools performing well in this dimension.</li>
                    <li><b>Innovation:</b> Encourage continuous improvement and innovation.</li>
                </ul>
            </div>
        </div>
        
        <div style="background:#f0f4ff;padding:12px;border-radius:8px;border:1px solid #93c5fd;margin:12px 0;">
            <h4 style="margin-top:0;color:#1e40af;font-size:14px;">📌 Priority Action Items</h4>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                <li><b>Urgent (0-3 Months):</b> Address {weakest_dim} through targeted TA and capacity building.</li>
                <li><b>Short-Term (3-6 Months):</b> Strengthen monitoring and evaluation systems.</li>
                <li><b>Medium-Term (6-12 Months):</b> Scale up best practices across the division.</li>
                <li><b>Long-Term (12+ Months):</b> Build sustainable systems for continuous improvement.</li>
            </ul>
        </div>
        
        <p style="font-size:12px;color:#6b7280;margin-top:12px;text-align:right;">
            <i>This synopsis is based on current SBM data and provides actionable insights for division-level decision-making.</i>
        </p>
    </div>
    """


def _regional_synopsis(user_name, selected_sdo, schools_in_sdo, complete_schools,
                       strongest_dim, weakest_dim, strongest_score, weakest_score,
                       overall_avg, overall_level, overall_color, overall_emoji,
                       urgency_level, urgency_color, urgency_emoji, total_schools, pending_count):
    """Synopsis for Regional level."""
    return f"""
    <div style="background:linear-gradient(135deg, #f0f4ff 0%, #e8eeff 100%);padding:20px 24px;border-radius:12px;border-left:6px solid #0033A0;margin-bottom:20px;color:#1a1a2e;">
        <h3 style="margin-top:0;color:#0033A0;">📋 Regional-Level Executive Summary</h3>
        <p style="font-size:14px;color:#4b5563;margin-bottom:12px;">
            <b>Prepared for:</b> {user_name} · <b>Region:</b> X – Northern Mindanao · 
            <b>Date:</b> {__import__('datetime').datetime.now().strftime('%B %d, %Y')}
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
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#166534;">✅ Division Strength</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#166534;">{strongest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Regional Average: <b>{strongest_score:.1f}</b> / 3.0</p>
                <p style="font-size:12px;color:#6b7280;margin:6px 0 0 0;">
                    <i>This dimension represents the region's area of strength relative to others.</i>
                </p>
            </div>
            <div style="background:#fef2f2;padding:14px;border-radius:8px;border-left:4px solid #dc2626;">
                <h4 style="margin:0 0 6px 0;font-size:14px;color:#991b1b;">⚠️ Critical Priority</h4>
                <p style="font-size:16px;font-weight:700;margin:0;color:#991b1b;">{weakest_dim}</p>
                <p style="font-size:13px;margin:4px 0 0 0;color:#4b5563;">Regional Average: <b>{weakest_score:.1f}</b> / 3.0</p>
                <p style="font-size:12px;color:#6b7280;margin:6px 0 0 0;">
                    <i>This dimension requires immediate regional-level intervention across multiple divisions.</i>
                </p>
            </div>
        </div>
        
        <div style="background:white;padding:16px;border-radius:8px;margin:12px 0;">
            <h4 style="margin-top:0;">💡 Strategic Analysis</h4>
            <p style="font-size:14px;color:#4b5563;margin-bottom:8px;">
                <b>Why is {weakest_dim} a regional priority?</b>
            </p>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin-top:4px;">
                <li>Consistently low performance across multiple divisions in this dimension.</li>
                <li>Systemic challenges requiring regional-level policy and program interventions.</li>
                <li>Resource constraints and competing priorities at the division level.</li>
                <li>Need for coordinated technical assistance and capacity-building programs.</li>
                <li>Alignment with national education priorities and directives.</li>
            </ul>
            
            <p style="font-size:14px;color:#4b5563;margin-top:12px;">
                <b>Why is {strongest_dim} a regional strength?</b>
            </p>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin-top:4px;">
                <li>Successful implementation of region-wide programs in this area.</li>
                <li>Strong leadership and commitment from division offices.</li>
                <li>Effective collaboration and sharing of best practices.</li>
                <li>Favorable policy environment and resource allocation.</li>
            </ul>
        </div>
        
        <div style="background:#fffbeb;padding:16px;border-radius:8px;border:1px solid #fcd34d;margin:12px 0;">
            <h4 style="margin-top:0;color:#92400e;">🎯 Regional-Level Strategic Interventions</h4>
            
            <div style="margin:8px 0;">
                <p style="font-weight:600;font-size:14px;margin:0 0 4px 0;color:#92400e;">For {weakest_dim} (Regional Priority):</p>
                <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                    <li><b>Regional Policy:</b> Develop and implement a Regional Technical Assistance Framework.</li>
                    <li><b>Capacity Building:</b> Design and deliver region-wide training programs.</li>
                    <li><b>Resource Mobilization:</b> Advocate for increased budget allocation to support improvement.</li>
                    <li><b>Monitoring & Evaluation:</b> Establish regional SBM monitoring and reporting systems.</li>
                    <li><b>Partnerships:</b> Forge partnerships with stakeholders for support and resources.</li>
                </ul>
            </div>
            
            <div style="margin:8px 0;">
                <p style="font-weight:600;font-size:14px;margin:0 0 4px 0;color:#92400e;">For {strongest_dim} (Regional Strength):</p>
                <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                    <li><b>Scale Across Region:</b> Replicate successful practices across all divisions.</li>
                    <li><b>Knowledge Management:</b> Document and disseminate best practices region-wide.</li>
                    <li><b>Recognition:</b> Celebrate and reward high-performing divisions and schools.</li>
                    <li><b>Innovation:</b> Encourage pilot programs and innovative approaches.</li>
                </ul>
            </div>
        </div>
        
        <div style="background:#f0f4ff;padding:12px;border-radius:8px;border:1px solid #93c5fd;margin:12px 0;">
            <h4 style="margin-top:0;color:#1e40af;font-size:14px;">📌 Regional Policy Recommendations</h4>
            <ul style="font-size:13px;color:#4b5563;padding-left:20px;margin:4px 0;">
                <li><b>Short-Term (0-6 Months):</b> Deploy Regional Field Technical Assistance Team (RFTAT) to priority divisions.</li>
                <li><b>Medium-Term (6-12 Months):</b> Establish Regional SBM Monitoring and Evaluation System.</li>
                <li><b>Long-Term (12+ Months):</b> Integrate SBM improvement into Regional Education Development Plan.</li>
            </ul>
        </div>
        
        <p style="font-size:12px;color:#6b7280;margin-top:12px;text-align:right;">
            <i>This synopsis is based on current SBM data and provides strategic insights for regional-level decision-making.</i>
        </p>
    </div>
    """


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

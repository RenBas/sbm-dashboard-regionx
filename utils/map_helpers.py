"""Helper functions for creating Folium map elements – WITH ANIMATED GLOW.
   Uses DivIcon only for the glow (lightweight), CustomIcon for shield.
"""

import folium
import base64
from .constants import DIMENSION_NAMES, SHIELD_COLORS, DEGREE_COLORS

# ─── COLOR HELPERS ───

def score_to_color(score):
    """Return hex colour based on SBM index (red/orange/yellow/green)."""
    if score < 1.0:
        return '#dc2626'
    elif score < 2.0:
        return '#f97316'
    elif score < 2.5:
        return '#eab308'
    else:
        return '#22c55e'

def get_shield_color(score):
    return score_to_color(score)

def get_school_dot_size(enrollment):
    if enrollment == 0:
        return 6
    elif enrollment < 500:
        return 8
    elif enrollment < 1500:
        return 12
    else:
        return 16

# ─── SHIELD SVG GENERATOR ───

def create_shield_svg(color, size=32, label=""):
    hex_color = color if color.startswith('#') else color
    svg = f'''
    <svg width="{size}" height="{size}" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{hex_color};stop-opacity:1" />
                <stop offset="100%" style="stop-color:{hex_color};stop-opacity:0.8" />
            </linearGradient>
            <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="1" stdDeviation="2" flood-opacity="0.3"/>
            </filter>
        </defs>
        <polygon points="16,2 28,6 26,22 16,30 6,22 4,6" 
                 fill="url(#shieldGrad)" 
                 stroke="rgba(255,255,255,0.6)" 
                 stroke-width="1.5"
                 filter="url(#shadow)"/>
        <text x="16" y="18" text-anchor="middle" 
              font-size="7" fill="white" font-weight="bold" 
              font-family="sans-serif">
            {label[:3]}
        </text>
    </svg>
    '''
    svg_bytes = svg.encode('utf-8')
    b64 = base64.b64encode(svg_bytes).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"

# ─── ANIMATED GLOW ───

def create_glow_html(urgency):
    if urgency <= 0.1:
        return None
    if urgency > 0.7:
        glow_color = "#dc2626"
        glow_opacity = 0.55
        pulse_duration = 1.2
    elif urgency > 0.4:
        glow_color = "#f97316"
        glow_opacity = 0.45
        pulse_duration = 1.8
    else:
        glow_color = "#eab308"
        glow_opacity = 0.35
        pulse_duration = 2.4
    size = 50 + urgency * 50
    css = '''
    <style>
        @keyframes pulseGlow {
            0% { transform: translate(-50%,-50%) scale(0.9); opacity: 0.5; }
            100% { transform: translate(-50%,-50%) scale(1.4); opacity: 1; }
        }
    </style>
    '''
    html = f'''
    {css}
    <div style="position:relative;width:{size}px;height:{size}px;pointer-events:none;">
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                    width:{size}px;height:{size}px;border-radius:50%;
                    background:radial-gradient(circle, {glow_color} 0%, {glow_color}99 15%, {glow_color}55 40%, {glow_color}22 65%, transparent 85%);
                    opacity:{glow_opacity};
                    animation: pulseGlow {pulse_duration}s ease-in-out infinite alternate;
                    pointer-events:none;">
        </div>
    </div>
    '''
    return html

# ─── MARKER FUNCTIONS ───

def add_sdo_shield(map_obj, sdo):
    score = sdo.get("lowest_dim_score", 0)
    color = get_shield_color(score)
    label = sdo.get("name", "SDO").replace("SDO ", "").split(" ")[0][:3]
    urgency = sdo.get("urgency_factor", 0)

    # Glow
    glow_html = create_glow_html(urgency)
    if glow_html:
        glow_icon = folium.DivIcon(
            html=glow_html,
            icon_size=(100, 100),
            icon_anchor=(50, 50),
            popup_anchor=(0, -50)
        )
        folium.Marker(
            location=[sdo.get("lat", 0), sdo.get("lng", 0)],
            icon=glow_icon,
            opacity=1
        ).add_to(map_obj)

    # Shield
    icon_url = create_shield_svg(color, size=32, label=label)
    icon = folium.CustomIcon(
        icon_url,
        icon_size=(32, 32),
        icon_anchor=(16, 16),
        popup_anchor=(0, -16)
    )

    # Tooltip
    name = sdo.get("name", "Division")
    overall = sdo.get("overall_index", 0)
    low_dim = sdo.get("lowest_dim_name", "N/A")
    low_score = sdo.get("lowest_dim_score", 0)
    tooltip = f"{name} | SBM Index: {overall:.1f} | Lowest: {low_dim} ({low_score:.1f}) | Urgency: {urgency:.2f}"

    folium.Marker(
        location=[sdo.get("lat", 0), sdo.get("lng", 0)],
        popup=folium.Popup(get_sdo_popup_html(sdo), max_width=250),
        icon=icon,
        tooltip=tooltip
    ).add_to(map_obj)


def add_school_dot(map_obj, school, dim_index=None):
    """
    Add a colour‑coded school dot.
    - If dim_index is None, colour by overall_index.
    - If dim_index is provided (0-5), colour by that dimension's score.
    """
    is_pending = school.get("data_status") == "Pending"
    
    if is_pending:
        fill_color = "#9ca3af"
        border_color = "#6b7280"
        weight = 3
        dash_array = "5,5"
        fill_opacity = 0.4
        tooltip = f"{school.get('name', 'School')} (Data Pending)"
    else:
        if dim_index is not None and 0 <= dim_index < 6:
            # Use specific dimension score
            score = school.get("dimension_scores", [0]*6)[dim_index]
            dim_name = DIMENSION_NAMES[dim_index]
            tooltip = (
                f"{school.get('name', 'School')} | "
                f"{dim_name}: {score:.1f}"
            )
        else:
            # Use overall index
            score = school.get("overall_index", 0)
            low_dim_idx = school.get("lowest_dim_index", 0)
            low_dim_name = DIMENSION_NAMES[low_dim_idx] if 0 <= low_dim_idx < len(DIMENSION_NAMES) else "?"
            tooltip = (
                f"{school.get('name', 'School')} | SBM Index: {score:.1f} | "
                f"Lowest: {low_dim_name} ({school.get('lowest_dim_score', 0):.1f})"
            )
        
        fill_color = score_to_color(score)
        border_color = "rgba(255,255,255,0.9)"
        weight = 2
        dash_array = None
        fill_opacity = 0.9

    size = get_school_dot_size(school.get("enrollment", 0))
    folium.CircleMarker(
        location=[school.get("lat", 0), school.get("lng", 0)],
        radius=size,
        color=border_color,
        weight=weight,
        fill=True,
        fill_color=fill_color,
        fill_opacity=fill_opacity,
        dash_array=dash_array,
        popup=folium.Popup(get_school_popup_html(school), max_width=250),
        tooltip=tooltip
    ).add_to(map_obj)


# ─── POPUP HTML HELPERS ───

def get_sdo_popup_html(sdo):
    name = sdo.get("name", "SDO")
    capital = sdo.get("capital", "")
    overall = sdo.get("overall_index", 0)
    low_name = sdo.get("lowest_dim_name", "N/A")
    low_score = sdo.get("lowest_dim_score", 0)
    urgency = sdo.get("urgency_factor", 0)
    return f'''
    <div style="font-weight:600;font-size:15px;color:#0033a0;">{name}</div>
    <div style="font-size:12px;color:#4b5563;">{capital}</div>
    <hr style="margin:4px 0;">
    <div style="font-size:13px;">
        <b>Overall Index:</b> {overall:.1f} / 3.0<br>
        <b>Lowest Dimension:</b> {low_name} ({low_score:.1f})<br>
        <b>Urgency Factor:</b> {urgency:.2f}<br>
        <span style="color:#6b7280;font-size:11px;">Click to zoom in</span>
    </div>
    '''

def get_school_popup_html(school):
    if school.get("data_status") == "Pending":
        return f'''
        <div style="font-weight:600;font-size:14px;color:#0033a0;">{school.get('name', '')}</div>
        <div style="font-size:12px;color:#4b5563;">{school.get('type', '')} · ⏳ Data Pending</div>
        <hr style="margin:4px 0;">
        <div style="color:#6b7280;font-size:13px;">No SBM assessment submitted yet.</div>
        '''
    name = school.get("name", "")
    stype = school.get("type", "")
    enrollment = school.get("enrollment", 0)
    degree = school.get("degree", "")
    overall = school.get("overall_index", 0)
    low_idx = school.get("lowest_dim_index", 0)
    low_name = DIMENSION_NAMES[low_idx] if 0 <= low_idx < len(DIMENSION_NAMES) else "?"
    low_score = school.get("lowest_dim_score", 0)
    return f'''
    <div style="font-weight:600;font-size:14px;color:#0033a0;">{name}</div>
    <div style="font-size:12px;color:#4b5563;">{stype} · {enrollment:,} learners</div>
    <hr style="margin:4px 0;">
    <div style="font-size:13px;">
        <b>SBM Level:</b> {degree}<br>
        <b>Overall Index:</b> {overall:.1f} / 3.0<br>
        <b>Lowest Dim:</b> {low_name} ({low_score:.1f})
    </div>
    '''

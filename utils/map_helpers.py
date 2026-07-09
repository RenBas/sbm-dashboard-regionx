"""Helper functions for creating Folium map elements – WITH ANIMATED GLOW.
   Uses DivIcon only for the glow (lightweight), CustomIcon for shield.
"""

import folium
import base64
from .constants import DIMENSION_NAMES, SHIELD_COLORS, DEGREE_COLORS

# ─── COLOR HELPERS ───

def get_shield_color(score):
    if score >= 2.5:
        return SHIELD_COLORS["high"]
    elif score >= 2.0:
        return SHIELD_COLORS["medium_high"]
    elif score >= 1.0:
        return SHIELD_COLORS["medium_low"]
    else:
        return SHIELD_COLORS["low"]

def get_school_dot_color(degree):
    return DEGREE_COLORS.get(degree, "#9ca3af")

def get_school_dot_size(enrollment):
    if enrollment == 0:
        return 6
    elif enrollment < 500:
        return 8
    elif enrollment < 1500:
        return 12
    else:
        return 16

def score_to_color(score):
    """Return a hex colour based on SBM index (same urgency scale as shields)."""
    if score < 1.0:
        return '#dc2626'   # red – critical
    elif score < 2.0:
        return '#f97316'   # orange – warning
    elif score < 2.5:
        return '#eab308'   # yellow – monitor
    else:
        return '#22c55e'   # green – stable

# ─── SHIELD SVG GENERATOR ───

def create_shield_svg(color, size=32, label=""):
    if color.startswith('#'):
        hex_color = color
    else:
        hex_color = color
    
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

# ─── ANIMATED GLOW (DivIcon) ───

def create_glow_html(urgency):
    """
    Create an animated glow effect using HTML/CSS with radial gradient.
    Returns HTML string for DivIcon.
    """
    if urgency <= 0.1:
        return None
    
    # Glow parameters based on urgency
    if urgency > 0.7:
        glow_color = "#dc2626"  # Red
        glow_opacity = 0.55
        pulse_duration = 1.2  # Fast pulse
    elif urgency > 0.4:
        glow_color = "#f97316"  # Orange
        glow_opacity = 0.45
        pulse_duration = 1.8
    else:
        glow_color = "#eab308"  # Yellow
        glow_opacity = 0.35
        pulse_duration = 2.4
    
    # Size based on urgency (larger = more urgent)
    size = 50 + urgency * 50  # 50px to 100px
    
    # CSS keyframes for pulsing animation
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
    """
    Add an SDO marker with:
    - Shield: CustomIcon (SVG)
    - Glow: DivIcon (HTML/CSS) - ANIMATED
    """
    color = get_shield_color(sdo["lowest_dim_score"])
    label = sdo["name"].replace("SDO ", "").split(" ")[0][:3]
    urgency = sdo.get("urgency_factor", 0)
    
    # ── ANIMATED GLOW (DivIcon) ──
    glow_html = create_glow_html(urgency)
    if glow_html:
        glow_icon = folium.DivIcon(
            html=glow_html,
            icon_size=(100, 100),
            icon_anchor=(50, 50),
            popup_anchor=(0, -50)
        )
        
        folium.Marker(
            location=[sdo["lat"], sdo["lng"]],
            icon=glow_icon,
            tooltip="Glow",
            opacity=1
        ).add_to(map_obj)
    
    # ── SHIELD (CustomIcon) ──
    icon_url = create_shield_svg(color, size=32, label=label)
    icon = folium.CustomIcon(
        icon_url,
        icon_size=(32, 32),
        icon_anchor=(16, 16),
        popup_anchor=(0, -16)
    )
    
    folium.Marker(
        location=[sdo["lat"], sdo["lng"]],
        popup=folium.Popup(get_sdo_popup_html(sdo), max_width=250),
        icon=icon,
        tooltip=sdo["name"]
    ).add_to(map_obj)


def add_school_dot(map_obj, school):
    """
    Add a colour‑coded school marker to the folium map.
    - Colour is based on the school's overall SBM index (red/orange/yellow/green).
    - Size is based on enrollment.
    - Pending schools are shown in grey with a dashed border.
    """
    is_pending = school["data_status"] == "Pending"
    
    if is_pending:
        fill_color = "#9ca3af"
        border_color = "#6b7280"
        weight = 3
        dash_array = "5,5"
        fill_opacity = 0.4
    else:
        # Use the overall SBM index to determine colour
        score = school.get("overall_index", 0)
        fill_color = score_to_color(score)
        border_color = "rgba(255,255,255,0.9)"
        weight = 2
        dash_array = None
        fill_opacity = 0.9
    
    size = get_school_dot_size(school["enrollment"])
    
    folium.CircleMarker(
        location=[school["lat"], school["lng"]],
        radius=size,
        color=border_color,
        weight=weight,
        fill=True,
        fill_color=fill_color,
        fill_opacity=fill_opacity,
        dash_array=dash_array,
        popup=folium.Popup(get_school_popup_html(school), max_width=250),
        tooltip=school["name"]
    ).add_to(map_obj)


# ─── POPUP HTML HELPERS ───

def get_sdo_popup_html(sdo):
    return f'''
    <div style="font-weight:600;font-size:15px;color:#0033a0;">{sdo["name"]}</div>
    <div style="font-size:12px;color:#4b5563;">{sdo["capital"]}</div>
    <hr style="margin:4px 0;">
    <div style="font-size:13px;">
        <b>Overall Index:</b> {sdo["overall_index"]:.1f} / 3.0<br>
        <b>Lowest Dimension:</b> {sdo["lowest_dim_name"]} ({sdo["lowest_dim_score"]:.1f})<br>
        <b>Urgency Factor:</b> {sdo.get("urgency_factor", 0):.2f}<br>
        <span style="color:#6b7280;font-size:11px;">Click to zoom in</span>
    </div>
    '''

def get_school_popup_html(school):
    if school["data_status"] == "Pending":
        return f'''
        <div style="font-weight:600;font-size:14px;color:#0033a0;">{school["name"]}</div>
        <div style="font-size:12px;color:#4b5563;">{school["type"]} · ⏳ Data Pending</div>
        <hr style="margin:4px 0;">
        <div style="color:#6b7280;font-size:13px;">No SBM assessment submitted yet.</div>
        '''
    
    return f'''
    <div style="font-weight:600;font-size:14px;color:#0033a0;">{school["name"]}</div>
    <div style="font-size:12px;color:#4b5563;">{school["type"]} · {school["enrollment"]:,} learners</div>
    <hr style="margin:4px 0;">
    <div style="font-size:13px;">
        <b>SBM Level:</b> {school["degree"]}<br>
        <b>Overall Index:</b> {school["overall_index"]:.1f} / 3.0<br>
        <b>Lowest Dim:</b> {DIMENSION_NAMES[school["lowest_dim_index"]]} ({school["lowest_dim_score"]:.1f})
    </div>
    '''

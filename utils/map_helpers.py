"""Helper functions for creating Folium map elements – FINAL VERSION.
   Uses CircleMarker with layered circles for glow effect.
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

# ─── GLOW HELPER ───

def add_glow(map_obj, lat, lng, urgency, color):
    """
    Add a layered glow effect using multiple circles.
    Higher urgency = larger, brighter glow.
    """
    # Only add glow if urgency is above threshold
    if urgency <= 0.1:
        return
    
    # Determine glow intensity (0.1 to 1.0)
    intensity = urgency
    
    # Define glow colors (red for critical, orange for moderate)
    if urgency > 0.7:
        glow_color = "#dc2626"  # Red (critical)
        base_opacity = 0.4
    elif urgency > 0.4:
        glow_color = "#f97316"  # Orange (warning)
        base_opacity = 0.3
    else:
        glow_color = "#eab308"  # Yellow (monitor)
        base_opacity = 0.2
    
    # Base radius (larger for higher urgency)
    base_radius = 15 + intensity * 25  # 15px to 40px
    
    # ── LAYER 1: Inner core (small, bright) ──
    folium.CircleMarker(
        location=[lat, lng],
        radius=base_radius * 0.3,
        color=glow_color,
        fill=True,
        fill_color=glow_color,
        fill_opacity=base_opacity * 1.0,
        weight=0,
    ).add_to(map_obj)
    
    # ── LAYER 2: Middle glow (medium, semi-transparent) ──
    folium.CircleMarker(
        location=[lat, lng],
        radius=base_radius * 0.6,
        color=glow_color,
        fill=True,
        fill_color=glow_color,
        fill_opacity=base_opacity * 0.5,
        weight=0,
    ).add_to(map_obj)
    
    # ── LAYER 3: Outer halo (large, very transparent) ──
    folium.CircleMarker(
        location=[lat, lng],
        radius=base_radius * 1.0,
        color=glow_color,
        fill=True,
        fill_color=glow_color,
        fill_opacity=base_opacity * 0.2,
        weight=0,
    ).add_to(map_obj)

# ─── MARKER FUNCTIONS ───

def add_sdo_shield(map_obj, sdo):
    """
    Add an SDO marker with custom SVG shield and layered glow.
    """
    color = get_shield_color(sdo["lowest_dim_score"])
    label = sdo["name"].replace("SDO ", "").split(" ")[0][:3]
    urgency = sdo.get("urgency_factor", 0)
    
    # ── LAYERED GLOW (added before shield so it sits behind) ──
    add_glow(map_obj, sdo["lat"], sdo["lng"], urgency, color)
    
    # ── SHIELD ──
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
    """Add a school dot using standard folium CircleMarker."""
    is_pending = school["data_status"] == "Pending"
    color = get_school_dot_color(school["degree"]) if not is_pending else "#9ca3af"
    size = get_school_dot_size(school["enrollment"])
    
    fill_opacity = 0.9 if not is_pending else 0.4
    border_color = "#6b7280" if is_pending else "rgba(255,255,255,0.9)"
    border_weight = 2 if not is_pending else 3
    dash_array = "5,5" if is_pending else None
    
    folium.CircleMarker(
        location=[school["lat"], school["lng"]],
        radius=size,
        color=border_color,
        weight=border_weight,
        fill=True,
        fill_color=color,
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

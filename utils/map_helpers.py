"""Helper functions for creating Folium map elements – SIMPLIFIED VERSION.
   Uses standard CircleMarker and Icon (no custom HTML/CSS in markers).
"""

import folium
from .constants import DIMENSION_NAMES, SHIELD_COLORS, DEGREE_COLORS

# ─── COLOR HELPERS ───

def get_shield_color(score):
    """Return shield color based on lowest dimension score."""
    if score >= 2.5:
        return SHIELD_COLORS["high"]       # "#0d9488" (Teal)
    elif score >= 2.0:
        return SHIELD_COLORS["medium_high"] # "#eab308" (Yellow)
    elif score >= 1.0:
        return SHIELD_COLORS["medium_low"]  # "#f97316" (Orange)
    else:
        return SHIELD_COLORS["low"]         # "#dc2626" (Red)


def get_school_dot_color(degree):
    """Return dot color based on SBM degree."""
    return DEGREE_COLORS.get(degree, "#9ca3af")


def get_school_dot_size(enrollment):
    """Return dot size based on enrollment."""
    if enrollment == 0:
        return 6
    elif enrollment < 500:
        return 8
    elif enrollment < 1500:
        return 12
    else:
        return 16


# ─── MARKER FUNCTIONS ───

def add_sdo_shield(map_obj, sdo):
    """
    Add an SDO marker using standard folium Icon (FontAwesome shield).
    Also adds a pulsing glow circle behind urgent SDOs (urgency > 0.5).
    """
    color = get_shield_color(sdo["lowest_dim_score"])
    
    # Map our color to FontAwesome icon color names
    if color == "#0d9488":
        icon_color = "blue"
    elif color == "#eab308":
        icon_color = "orange"
    elif color == "#f97316":
        icon_color = "darkorange"
    else:
        icon_color = "red"
    
    # Create the shield icon
    icon = folium.Icon(color=icon_color, icon="shield", prefix="fa")
    
    # Add the marker
    folium.Marker(
        location=[sdo["lat"], sdo["lng"]],
        popup=folium.Popup(get_sdo_popup_html(sdo), max_width=250),
        icon=icon,
        tooltip=sdo["name"]
    ).add_to(map_obj)
    
    # ── Urgency Glow (visual alternative to CSS pulse) ──
    urgency = sdo.get("urgency_factor", 0)
    if urgency > 0.5:
        glow_color = "#dc2626" if urgency > 0.8 else "#f97316"
        glow_radius = 20 + urgency * 30  # 35px to 50px
        folium.Circle(
            location=[sdo["lat"], sdo["lng"]],
            radius=glow_radius,
            color=glow_color,
            fill=True,
            fill_color=glow_color,
            fill_opacity=0.1 + urgency * 0.25,  # 0.15 to 0.30
            weight=1.5,
            popup=f"⚠️ Urgency Level: {urgency:.0%}"
        ).add_to(map_obj)


def add_school_dot(map_obj, school):
    """
    Add a school dot using standard folium CircleMarker.
    Pending schools appear with a dashed border and lower opacity.
    """
    is_pending = school["data_status"] == "Pending"
    color = get_school_dot_color(school["degree"]) if not is_pending else "#9ca3af"
    size = get_school_dot_size(school["enrollment"])
    
    # Pending schools: lower opacity, dashed border
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
    """Generate HTML popup content for an SDO shield."""
    return f'''
    <div style="font-weight:600;font-size:15px;color:#0033a0;">{sdo["name"]}</div>
    <div style="font-size:12px;color:#4b5563;">{sdo["capital"]}</div>
    <hr style="margin:4px 0;">
    <div style="font-size:13px;">
        <b>Overall Index:</b> {sdo["overall_index"]:.1f} / 3.0<br>
        <b>Lowest Dimension:</b> {sdo["lowest_dim_name"]} ({sdo["lowest_dim_score"]:.1f})<br>
        <span style="color:#6b7280;font-size:11px;">Click to zoom in</span>
    </div>
    '''


def get_school_popup_html(school):
    """Generate HTML popup content for a school dot."""
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

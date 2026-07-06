"""
Utility package for the SBM Dashboard.
Exports helper functions for data loading, map rendering, and chart creation.
"""

from .constants import DIMENSION_NAMES, DEGREE_COLORS, SHIELD_COLORS, INDICATOR_MAPPING
from .data_loader import load_sdo_data, load_all_schools, get_schools_by_sdo, compute_dimension_averages
from .map_helpers import (
    create_shield_html, create_school_dot_html, get_pulse_css,
    get_shield_color, get_sdo_popup_html, get_school_popup_html
)
from .chart_helpers import (
    create_radar_chart, create_trend_chart, create_indicators_table
)

__all__ = [
    # Constants
    "DIMENSION_NAMES",
    "DEGREE_COLORS",
    "SHIELD_COLORS",
    "INDICATOR_MAPPING",
    # Data Loaders
    "load_sdo_data",
    "load_all_schools",
    "get_schools_by_sdo",
    "compute_dimension_averages",
    # Map Helpers
    "create_shield_html",
    "create_school_dot_html",
    "get_pulse_css",
    "get_shield_color",
    "get_sdo_popup_html",
    "get_school_popup_html",
    # Chart Helpers
    "create_radar_chart",
    "create_trend_chart",
    "create_indicators_table",
]

"""
Utility package for the SBM Dashboard.
"""

from .constants import DIMENSION_NAMES, DEGREE_COLORS, SHIELD_COLORS, INDICATORS
from .data_loader import load_sdo_data, load_all_schools, get_schools_by_sdo, compute_dimension_averages
from .map_helpers import add_sdo_shield, add_school_dot
from .chart_helpers import create_radar_chart, create_trend_chart, create_indicators_table
from .auth import authenticate, login_status, logout, get_accessible_schools, get_accessible_divisions_summary, is_school_head
from .download_helpers import generate_report_data, generate_template_csv
from .synopsis_generator import generate_synopsis

__all__ = [
    "DIMENSION_NAMES",
    "DEGREE_COLORS",
    "SHIELD_COLORS",
    "INDICATORS",
    "load_sdo_data",
    "load_all_schools",
    "get_schools_by_sdo",
    "compute_dimension_averages",
    "add_sdo_shield",
    "add_school_dot",
    "create_radar_chart",
    "create_trend_chart",
    "create_indicators_table",
    "authenticate",
    "login_status",
    "logout",
    "get_accessible_schools",
    "get_accessible_divisions_summary",
    "is_school_head",
    "generate_report_data",
    "generate_template_csv",
    "generate_synopsis",
]

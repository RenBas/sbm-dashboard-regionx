"""Constant definitions for the SBM Dashboard."""

DIMENSION_NAMES = [
    "Curriculum & Teaching",
    "Learning Environment",
    "Leadership",
    "Governance & Accountability",
    "Human Resource & Team Dev.",
    "Finance & Resource Mgmt."
]

DEGREE_COLORS = {
    "Always Manifested": "#22c55e",
    "Frequently Manifested": "#eab308",
    "Rarely Manifested": "#f97316",
    "Not Yet Manifested": "#9ca3af",
    "Pending": "#9ca3af"
}

SHIELD_COLORS = {
    "high": "#0d9488",      # >= 2.5
    "medium_high": "#eab308",  # 2.0 - 2.4
    "medium_low": "#f97316",   # 1.0 - 1.9
    "low": "#dc2626"        # < 1.0
}

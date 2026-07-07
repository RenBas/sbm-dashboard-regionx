"""Authentication and authorization utilities for SBM Dashboard."""

import streamlit as st
from typing import Dict, List, Optional

# ─── ROLES ───
ROLES = {
    "regional": {
        "name": "Regional Office",
        "level": 3,
        "icon": "🏛️",
        "description": "View all schools across Region X"
    },
    "division": {
        "name": "Division Office",
        "level": 2,
        "icon": "📋",
        "description": "View all schools in your division"
    },
    "school": {
        "name": "School Head",
        "level": 1,
        "icon": "🏫",
        "description": "View only your school's data"
    }
}

# ─── MOCK USER DATA ───
MOCK_USERS = {
    # ── Regional ──
    "regional": {
        "username": "regional",
        "password": "regional123",
        "role": "regional",
        "name": "Regional Director",
        "division": None,
        "school_id": None
    },
    # ── Division ──
    "sdo_bukidnon": {
        "username": "sdo_bukidnon",
        "password": "sdo123",
        "role": "division",
        "name": "SDO Bukidnon Superintendent",
        "division": "SDO Bukidnon",
        "school_id": None
    },
    "sdo_cdo": {
        "username": "sdo_cdo",
        "password": "sdo123",
        "role": "division",
        "name": "SDO Cagayan de Oro Superintendent",
        "division": "SDO Cagayan de Oro City",
        "school_id": None
    },
    "sdo_misamis_occ": {
        "username": "sdo_misamis_occ",
        "password": "sdo123",
        "role": "division",
        "name": "SDO Misamis Occidental Superintendent",
        "division": "SDO Misamis Occidental",
        "school_id": None
    },
    "sdo_iligan": {
        "username": "sdo_iligan",
        "password": "sdo123",
        "role": "division",
        "name": "SDO Iligan City Superintendent",
        "division": "SDO Iligan City",
        "school_id": None
    },
    "sdo_valencia": {
        "username": "sdo_valencia",
        "password": "sdo123",
        "role": "division",
        "name": "SDO Valencia City Superintendent",
        "division": "SDO Valencia City",
        "school_id": None
    },
    # ── School Heads ──
    "principal_cdo": {
        "username": "principal_cdo",
        "password": "school123",
        "role": "school",
        "name": "Principal, CDO National High School",
        "division": None,
        "school_id": "12001"
    },
    "principal_bukidnon": {
        "username": "principal_bukidnon",
        "password": "school123",
        "role": "school",
        "name": "Principal, Bukidnon Central ES",
        "division": None,
        "school_id": "11001"
    },
    "principal_ozamiz": {
        "username": "principal_ozamiz",
        "password": "school123",
        "role": "school",
        "name": "Principal, Ozamiz City NHS",
        "division": None,
        "school_id": "13001"
    },
    "principal_iligan": {
        "username": "principal_iligan",
        "password": "school123",
        "role": "school",
        "name": "Principal, Iligan City NHS",
        "division": None,
        "school_id": "14001"
    },
    "principal_valencia": {
        "username": "principal_valencia",
        "password": "school123",
        "role": "school",
        "name": "Principal, Valencia Central ES",
        "division": None,
        "school_id": "15001"
    },
    "principal_misamis_occ": {
        "username": "principal_misamis_occ",
        "password": "school123",
        "role": "school",
        "name": "Principal, Misamis Occidental NHS",
        "division": None,
        "school_id": "16001"
    }
}

# ─── AUTHENTICATION FUNCTIONS ───

def authenticate(username: str, password: str) -> Optional[Dict]:
    """Authenticate a user against mock user data."""
    # Trim whitespace and handle case-insensitive if needed
    username = username.strip()
    user = MOCK_USERS.get(username)
    if user and user["password"] == password:
        # Return user dict without the password
        return {k: v for k, v in user.items() if k != "password"}
    return None

def get_user_role(user: Dict) -> str:
    return user.get("role", "school")

def get_user_division(user: Dict) -> Optional[str]:
    return user.get("division")

def get_user_school_id(user: Dict) -> Optional[str]:
    return user.get("school_id")

def is_regional(user: Dict) -> bool:
    return get_user_role(user) == "regional"

def is_division(user: Dict) -> bool:
    return get_user_role(user) in ["regional", "division"]

def is_school_head(user: Dict) -> bool:
    return get_user_role(user) == "school"

def get_accessible_schools(user: Dict, sdo_list: List, all_schools: List) -> Dict:
    role = get_user_role(user)
    if role == "regional":
        return {"filtered_sdos": sdo_list, "filtered_schools": all_schools}
    elif role == "division":
        division_name = get_user_division(user)
        filtered_sdos = [s for s in sdo_list if s["name"] == division_name]
        filtered_schools = [s for s in all_schools if s["sdo_id"] in [sdo["id"] for sdo in filtered_sdos]]
        return {"filtered_sdos": filtered_sdos, "filtered_schools": filtered_schools}
    elif role == "school":
        school_id = get_user_school_id(user)
        filtered_schools = [s for s in all_schools if s["id"] == school_id]
        if filtered_schools:
            school = filtered_schools[0]
            filtered_sdos = [s for s in sdo_list if s["id"] == school["sdo_id"]]
        else:
            filtered_sdos = []
        return {"filtered_sdos": filtered_sdos, "filtered_schools": filtered_schools}
    return {"filtered_sdos": [], "filtered_schools": []}

def get_accessible_divisions_summary(user: Dict) -> str:
    role = get_user_role(user)
    if role == "regional":
        return "🌐 **Access Level: Regional** – You can view all divisions and schools."
    elif role == "division":
        div = get_user_division(user) or "your division"
        return f"📋 **Access Level: Division** – You can view all schools in {div}."
    elif role == "school":
        return "🏫 **Access Level: School Head** – You can view only your school's data."
    return "🔒 Access level unknown."

def login_status() -> Dict:
    if "user" not in st.session_state:
        return {"logged_in": False, "user": None}
    return {"logged_in": True, "user": st.session_state.user}

def logout():
    st.session_state.user = None
    st.rerun()

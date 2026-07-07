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

# ─── MOCK USER DATA (Replace with real authentication later) ───
MOCK_USERS = {
    # ── Regional Level ──
    "regional": {
        "username": "regional",
        "password": "regional123",
        "role": "regional",
        "name": "Regional Director",
        "division": None,
        "school_id": None
    },
    
    # ── Division Level ──
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
    
    # ── School Head Level ──
    "principal_cdo_nhs": {
        "username": "principal_cdo_nhs",
        "password": "school123",
        "role": "school",
        "name": "Principal, CDO National High School",
        "division": None,
        "school_id": "12001"  # Mock school ID
    },
    "principal_bukidnon_es": {
        "username": "principal_bukidnon_es",
        "password": "school123",
        "role": "school",
        "name": "Principal, Bukidnon Central ES",
        "division": None,
        "school_id": "11001"
    },
    "principal_ozamiz_nhs": {
        "username": "principal_ozamiz_nhs",
        "password": "school123",
        "role": "school",
        "name": "Principal, Ozamiz City NHS",
        "division": None,
        "school_id": "13001"
    },
    "principal_iligan_nhs": {
        "username": "principal_iligan_nhs",
        "password": "school123",
        "role": "school",
        "name": "Principal, Iligan City NHS",
        "division": None,
        "school_id": "14001"
    },
    "principal_valencia_es": {
        "username": "principal_valencia_es",
        "password": "school123",
        "role": "school",
        "name": "Principal, Valencia Central ES",
        "division": None,
        "school_id": "15001"
    },
    "principal_misamis_occ_nhs": {
        "username": "principal_misamis_occ_nhs",
        "password": "school123",
        "role": "school",
        "name": "Principal, Misamis Occidental NHS",
        "division": None,
        "school_id": "16001"
    }
}

# ─── AUTHENTICATION FUNCTIONS ───

def authenticate(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user against mock user data.
    Returns user dict if valid, None otherwise.
    """
    # Debug: print attempted login
    print(f"🔐 Login attempt: username='{username}', password='{password}'")
    
    user = MOCK_USERS.get(username)
    if user and user["password"] == password:
        print(f"✅ Login successful: {username}")
        return {k: v for k, v in user.items() if k != "password"}
    
    # Check for exact matches (case-insensitive fallback)
    for key, value in MOCK_USERS.items():
        if value["username"].lower() == username.lower() and value["password"] == password:
            print(f"✅ Login successful (case-insensitive): {username}")
            return {k: v for k, v in value.items() if k != "password"}
    
    print(f"❌ Login failed: {username}")
    return None

def get_user_role(user: Dict) -> str:
    """Get the role of a user."""
    return user.get("role", "school")

def get_user_division(user: Dict) -> Optional[str]:
    """Get the division of a user (if they have one)."""
    return user.get("division")

def get_user_school_id(user: Dict) -> Optional[str]:
    """Get the school ID of a user (if they have one)."""
    return user.get("school_id")

def is_regional(user: Dict) -> bool:
    """Check if user has regional access."""
    return get_user_role(user) == "regional"

def is_division(user: Dict) -> bool:
    """Check if user has division access."""
    return get_user_role(user) in ["regional", "division"]

def is_school_head(user: Dict) -> bool:
    """Check if user is a school head."""
    return get_user_role(user) == "school"

def get_accessible_schools(user: Dict, sdo_list: List, all_schools: List) -> Dict:
    """
    Filter schools and SDOs based on user role.
    Returns:
        - filtered_sdos: list of SDOs the user can see
        - filtered_schools: list of schools the user can see
    """
    role = get_user_role(user)
    
    if role == "regional":
        # Regional: see everything
        return {
            "filtered_sdos": sdo_list,
            "filtered_schools": all_schools
        }
    
    elif role == "division":
        # Division: see only their division
        division_name = get_user_division(user)
        filtered_sdos = [s for s in sdo_list if s["name"] == division_name]
        filtered_schools = [s for s in all_schools if s["sdo_id"] in [sdo["id"] for sdo in filtered_sdos]]
        return {
            "filtered_sdos": filtered_sdos,
            "filtered_schools": filtered_schools
        }
    
    elif role == "school":
        # School Head: see only their school
        school_id = get_user_school_id(user)
        filtered_schools = [s for s in all_schools if s["id"] == school_id]
        # Find the SDO that contains this school
        if filtered_schools:
            school = filtered_schools[0]
            filtered_sdos = [s for s in sdo_list if s["id"] == school["sdo_id"]]
        else:
            filtered_sdos = []
        return {
            "filtered_sdos": filtered_sdos,
            "filtered_schools": filtered_schools
        }
    
    # Fallback: return empty
    return {
        "filtered_sdos": [],
        "filtered_schools": []
    }

def get_accessible_sdo_names(user: Dict, sdo_list: List) -> List[str]:
    """Get list of SDO names accessible to the user."""
    role = get_user_role(user)
    
    if role == "regional":
        return [s["name"] for s in sdo_list]
    elif role == "division":
        division = get_user_division(user)
        return [division] if division else []
    elif role == "school":
        return []
    return []

def get_accessible_divisions_summary(user: Dict) -> str:
    """Get a human-readable summary of what the user can see."""
    role = get_user_role(user)
    
    if role == "regional":
        return "🌐 **Access Level: Regional** – You can view all divisions and schools in Region X."
    elif role == "division":
        div = get_user_division(user) or "your division"
        return f"📋 **Access Level: Division** – You can view all schools in {div}."
    elif role == "school":
        return "🏫 **Access Level: School Head** – You can view only your school's data."
    return "🔒 Access level unknown."

def login_status() -> Dict:
    """Get current login status from session state."""
    if "user" not in st.session_state:
        return {"logged_in": False, "user": None}
    return {"logged_in": True, "user": st.session_state.user}

def logout():
    """Log out the current user."""
    st.session_state.user = None
    st.rerun()

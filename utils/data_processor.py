"""
Data processor for uploaded SBM data.
Transforms uploaded Excel files into the data structures used by the dashboard.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from .constants import DIMENSION_NAMES, INDICATORS

def process_uploaded_data(school_df: pd.DataFrame, assessment_df: pd.DataFrame) -> Dict:
    """
    Process uploaded Excel data and return structured data for the dashboard.
    """
    # 1. Validate required columns
    required_school_cols = ["School ID", "School Name", "Division", "Latitude", "Longitude", "Enrollment", "Data Status"]
    missing = [c for c in required_school_cols if c not in school_df.columns]
    if missing:
        raise ValueError(f"Missing columns in School Information: {missing}")
    
    required_assessment_cols = ["School ID", "Indicator ID", "Score"]
    missing = [c for c in required_assessment_cols if c not in assessment_df.columns]
    if missing:
        raise ValueError(f"Missing columns in SBM Assessment: {missing}")
    
    # 2. Clean data
    school_df = school_df.copy()
    assessment_df = assessment_df.copy()
    
    # Convert School ID to string
    school_df["School ID"] = school_df["School ID"].astype(str)
    assessment_df["School ID"] = assessment_df["School ID"].astype(str)
    
    # Convert numeric columns
    school_df["Latitude"] = pd.to_numeric(school_df["Latitude"], errors='coerce').fillna(0.0)
    school_df["Longitude"] = pd.to_numeric(school_df["Longitude"], errors='coerce').fillna(0.0)
    school_df["Enrollment"] = pd.to_numeric(school_df["Enrollment"], errors='coerce').fillna(0).astype(int)
    
    # Convert scores to numeric, clamp to 0-3
    assessment_df["Score"] = pd.to_numeric(assessment_df["Score"], errors='coerce')
    assessment_df["Score"] = assessment_df["Score"].clip(0, 3).fillna(0)
    
    # 3. Build dimension scores
    indicator_to_dimension = {}
    for ind in INDICATORS:
        indicator_to_dimension[ind["id"]] = ind["dimension"]
    
    # Build SDO list
    sdo_names = school_df["Division"].unique()
    sdo_list = []
    for idx, sdo_name in enumerate(sdo_names):
        sdo_entry = {
            "id": idx + 1,
            "name": sdo_name,
            "capital": sdo_name,
            "lat": school_df[school_df["Division"] == sdo_name]["Latitude"].mean() or 0.0,
            "lng": school_df[school_df["Division"] == sdo_name]["Longitude"].mean() or 0.0,
        }
        sdo_list.append(sdo_entry)
    
    # Build school list
    schools_list = []
    for _, school_row in school_df.iterrows():
        school_id = school_row["School ID"]
        school_name = school_row["School Name"]
        division = school_row["Division"]
        data_status = school_row["Data Status"]
        enrollment = school_row["Enrollment"]
        lat = school_row["Latitude"]
        lng = school_row["Longitude"]
        school_type = school_row.get("School Type", "Elementary")
        
        # Find SDO ID
        sdo_match = next((s for s in sdo_list if s["name"] == division), None)
        sdo_id = sdo_match["id"] if sdo_match else None
        
        # Get scores for this school
        scores_df = assessment_df[assessment_df["School ID"] == school_id]
        
        if scores_df.empty or data_status == "Pending":
            dim_scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            overall_index = 0.0
            degree = "Pending"
        else:
            dim_scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            dim_counts = [0, 0, 0, 0, 0, 0]
            
            for _, row in scores_df.iterrows():
                indicator_id = row["Indicator ID"]
                score = row["Score"]
                dim_name = indicator_to_dimension.get(indicator_id)
                if dim_name and dim_name in DIMENSION_NAMES:
                    dim_idx = DIMENSION_NAMES.index(dim_name)
                    if not pd.isna(score) and score > 0:
                        dim_scores[dim_idx] += score
                        dim_counts[dim_idx] += 1
            
            for i in range(6):
                if dim_counts[i] > 0:
                    dim_scores[i] = round(dim_scores[i] / dim_counts[i], 1)
                else:
                    dim_scores[i] = 0.0
            
            overall_index = round(sum(dim_scores) / 6, 1) if any(dim_scores) else 0.0
            
            if overall_index >= 2.5:
                degree = "Always Manifested"
            elif overall_index >= 2.0:
                degree = "Frequently Manifested"
            elif overall_index >= 1.0:
                degree = "Rarely Manifested"
            else:
                degree = "Not Yet Manifested"
        
        # Find lowest dimension
        if any(dim_scores):
            lowest_idx = dim_scores.index(min(dim_scores))
            lowest_score = min(dim_scores)
        else:
            lowest_idx = 0
            lowest_score = 0.0
        
        school_entry = {
            "id": school_id,
            "name": school_name,
            "type": school_type,
            "sdo_id": sdo_id,
            "lat": lat,
            "lng": lng,
            "enrollment": enrollment,
            "overall_index": overall_index,
            "degree": degree,
            "dimension_scores": dim_scores,
            "data_status": data_status,
            "lowest_dim_index": lowest_idx,
            "lowest_dim_score": lowest_score,
            "division": division
        }
        schools_list.append(school_entry)
    
    # Compute SDO-level dimension averages and urgency factors
    for sdo in sdo_list:
        sdo_id = sdo["id"]
        sdo_schools = [s for s in schools_list if s["sdo_id"] == sdo_id and s["data_status"] != "Pending"]
        
        if sdo_schools:
            dim_avgs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            for s in sdo_schools:
                for i in range(6):
                    dim_avgs[i] += s["dimension_scores"][i]
            dim_avgs = [round(v / len(sdo_schools), 1) for v in dim_avgs]
            sdo["dimension_scores"] = dim_avgs
            sdo["overall_index"] = round(sum(dim_avgs) / 6, 1)
            sdo["lowest_dim_index"] = dim_avgs.index(min(dim_avgs))
            sdo["lowest_dim_score"] = min(dim_avgs)
            sdo["lowest_dim_name"] = DIMENSION_NAMES[sdo["lowest_dim_index"]]
        else:
            sdo["dimension_scores"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            sdo["overall_index"] = 0.0
            sdo["lowest_dim_index"] = 0
            sdo["lowest_dim_score"] = 0.0
            sdo["lowest_dim_name"] = DIMENSION_NAMES[0]
    
    # Compute urgency factors (relative to min/max)
    all_lowest = [s["lowest_dim_score"] for s in sdo_list]
    min_score = min(all_lowest) if all_lowest else 0
    max_score = max(all_lowest) if all_lowest else 1
    range_val = max_score - min_score or 0.001
    
    for sdo in sdo_list:
        raw = (sdo["lowest_dim_score"] - min_score) / range_val
        sdo["urgency_factor"] = round(1 - raw, 3)
    
    return {
        "sdo_list": sdo_list,
        "schools": schools_list
    }

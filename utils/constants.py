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

# Full 42 SBM Indicators (from DO No. 007, s. 2024) - Updated to match actual data file dimensions
INDICATORS = [
    # CT_1 to CT_8: Curriculum & Teaching
    {"id": "CT_1", "dimension": "Curriculum & Teaching", "description": "Grade 3 learners achieve the proficiency level for each cluster of early language, literacy, and numeracy skills"},
    {"id": "CT_2", "dimension": "Curriculum & Teaching", "description": "Grade 6, 10, and 12 learners achieve the proficiency level in all 21st century skills and core learning areas in the National Achievement Test (NAT)"},
    {"id": "CT_3", "dimension": "Curriculum & Teaching", "description": "School-based ALS learners attain certification as elementary and junior high school completers"},
    {"id": "CT_4", "dimension": "Curriculum & Teaching", "description": "Teachers prepare contextualized learning materials responsive to the needs of learners"},
    {"id": "CT_5", "dimension": "Curriculum & Teaching", "description": "Teachers conduct remediation activities to address learning gaps in reading and comprehension, science and technology, and mathematics"},
    {"id": "CT_6", "dimension": "Curriculum & Teaching", "description": "Teachers integrate topics promoting peace and DepEd core values"},
    {"id": "CT_7", "dimension": "Curriculum & Teaching", "description": "The school conducts test item analysis to inform its teaching and learning process"},
    {"id": "CT_8", "dimension": "Curriculum & Teaching", "description": "The school engages local industries to strengthen its TLE-TVL course offerings"},
    # LE_9 to LE_18: Learning Environment
    {"id": "LE_9", "dimension": "Learning Environment", "description": "The school has zero bullying incidence"},
    {"id": "LE_10", "dimension": "Learning Environment", "description": "The school has zero child abuse incidence"},
    {"id": "LE_11", "dimension": "Learning Environment", "description": "The school has reduced its drop-out incidence"},
    {"id": "LE_12", "dimension": "Learning Environment", "description": "The school conducts culture-sensitive activities"},
    {"id": "LE_13", "dimension": "Learning Environment", "description": "The school provides access to learning experiences for the disadvantaged, OSYs, and adult learners"},
    {"id": "LE_14", "dimension": "Learning Environment", "description": "The school has a functional school-based ALS program"},
    {"id": "LE_15", "dimension": "Learning Environment", "description": "The school has a functional child-protection committee"},
    {"id": "LE_16", "dimension": "Learning Environment", "description": "The school has a functional DRRM plan"},
    {"id": "LE_17", "dimension": "Learning Environment", "description": "The school has a functional support mechanism for mental wellness"},
    {"id": "LE_18", "dimension": "Learning Environment", "description": "The school has special education- and FWD-friendly facilities"},
    # LG_19 to LG_22: Leadership
    {"id": "LG_19", "dimension": "Leadership", "description": "The school develops a strategic plan"},
    {"id": "LG_20", "dimension": "Leadership", "description": "The school has a functional school-community planning team"},
    {"id": "LG_21", "dimension": "Leadership", "description": "The school has a functional Supreme Student Government/ Supreme Pupil Government"},
    {"id": "LG_22", "dimension": "Leadership", "description": "The school innovates in its provision of frontline services to stakeholders"},
    # AC_23 to AC_28: Governance & Accountability
    {"id": "AC_23", "dimension": "Governance & Accountability", "description": "The school's strategic plan is operationalized through an implementation plan"},
    {"id": "AC_24", "dimension": "Governance & Accountability", "description": "The school has a functional School Governance Council (SGC)"},
    {"id": "AC_25", "dimension": "Governance & Accountability", "description": "The school has a functional Parent-Teacher Association (PTA)"},
    {"id": "AC_26", "dimension": "Governance & Accountability", "description": "The school collaborates with stakeholders and other schools in strengthening partnerships"},
    {"id": "AC_27", "dimension": "Governance & Accountability", "description": "The school monitors and evaluates its programs, projects, and activities"},
    {"id": "AC_28", "dimension": "Governance & Accountability", "description": "The school maintains an average rating of satisfactory from its internal and external stakeholders"},
    # HR_29 to HR_35: Human Resource & Team Dev.
    {"id": "HR_29", "dimension": "Human Resource & Team Dev.", "description": "School personnel achieve an average rating of very satisfactory in the individual performance commitment and review"},
    {"id": "HR_30", "dimension": "Human Resource & Team Dev.", "description": "The school achieves an average rating of very satisfactory in the office performance commitment and review"},
    {"id": "HR_31", "dimension": "Human Resource & Team Dev.", "description": "The school conducts needs-based Learning Action Cells and Learning & Development activities"},
    {"id": "HR_32", "dimension": "Human Resource & Team Dev.", "description": "The school facilitates the promotion and continuous professional development of its personnel"},
    {"id": "HR_33", "dimension": "Human Resource & Team Dev.", "description": "The school recognizes and rewards milestone achievements of its personnel"},
    {"id": "HR_34", "dimension": "Human Resource & Team Dev.", "description": "The school facilitates receipt of correct salaries, allowances, and other additional compensation in a timely manner"},
    {"id": "HR_35", "dimension": "Human Resource & Team Dev.", "description": "Teacher workload is distributed fairly and equitably"},
    # FR_36 to FR_42: Finance & Resource Mgmt.
    {"id": "FR_36", "dimension": "Finance & Resource Mgmt.", "description": "The school inspects its infrastructure and facilities"},
    {"id": "FR_37", "dimension": "Finance & Resource Mgmt.", "description": "The school initiates improvement of its infrastructure and facilities"},
    {"id": "FR_38", "dimension": "Finance & Resource Mgmt.", "description": "The school has a functional library"},
    {"id": "FR_39", "dimension": "Finance & Resource Mgmt.", "description": "The school has functional water, electric, and internet facilities"},
    {"id": "FR_40", "dimension": "Finance & Resource Mgmt.", "description": "The school has a functional computer laboratory/ classroom"},
    {"id": "FR_41", "dimension": "Finance & Resource Mgmt.", "description": "The school achieves a 75-100% utilization rate of its Maintenance and Other Operating Expenses (MOOE)"},
    {"id": "FR_42", "dimension": "Finance & Resource Mgmt.", "description": "The school liquidates 100% of its utilized MOOE"}
]

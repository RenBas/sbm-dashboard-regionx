"""
Risk Analyzer – Identifies at-risk schools and divisions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .twin_helpers import compute_dimension_averages_from_scores, get_degree_value


@dataclass
class RiskProfile:
    """Risk profile for a school or division."""
    entity_id: str
    entity_name: str
    entity_type: str  # "school" or "division"
    overall_risk_score: float  # 0.0 to 1.0
    risk_category: str  # "High", "Moderate", "Low"
    risk_factors: List[Dict]
    recommended_interventions: List[str]
    confidence: float


class RiskAnalyzer:
    """
    Analyzes SBM data to identify at-risk schools and divisions.
    """
    
    def __init__(self):
        self.risk_thresholds = {
            "high": 0.6,
            "moderate": 0.3
        }
        self.dimension_weights = {
            "Finance & Resource Mgmt.": 1.2,  # Higher weight (more critical)
            "Governance & Accountability": 1.1,
            "Curriculum & Teaching": 1.0,
            "Learning Environment": 1.0,
            "Leadership": 0.9,
            "Human Resource & Team Dev.": 0.9
        }
    
    def analyze_school(self, school_data: Dict, 
                       historical_trend: List[float] = None) -> RiskProfile:
        """
        Analyze risk for a single school.
        
        Args:
            school_data: Dict with school information and dimension_scores
            historical_trend: List of historical overall scores (optional)
            
        Returns:
            RiskProfile object
        """
        school_id = school_data.get("id", "unknown")
        school_name = school_data.get("name", "Unknown School")
        scores = school_data.get("dimension_scores", [0, 0, 0, 0, 0, 0])
        
        risk_factors = []
        risk_score = 0.0
        total_weight = 0.0
        
        # 1. Analyze each dimension
        for i, score in enumerate(scores):
            weight = self.dimension_weights.get(DIMENSION_NAMES[i] if i < len(DIMENSION_NAMES) else "", 1.0)
            total_weight += weight
            
            if score < 1.0:
                risk_score += weight * 1.0  # High risk
                risk_factors.append({
                    "dimension": DIMENSION_NAMES[i] if i < len(DIMENSION_NAMES) else f"Dim {i+1}",
                    "score": score,
                    "risk_level": "High",
                    "weight": weight,
                    "description": f"Score is critically low ({score:.1f}). Immediate intervention required."
                })
            elif score < 2.0:
                risk_score += weight * 0.6
                risk_factors.append({
                    "dimension": DIMENSION_NAMES[i] if i < len(DIMENSION_NAMES) else f"Dim {i+1}",
                    "score": score,
                    "risk_level": "Moderate",
                    "weight": weight,
                    "description": f"Score is below expected ({score:.1f}). Monitoring and targeted support needed."
                })
            elif score < 2.5:
                risk_score += weight * 0.2
                risk_factors.append({
                    "dimension": DIMENSION_NAMES[i] if i < len(DIMENSION_NAMES) else f"Dim {i+1}",
                    "score": score,
                    "risk_level": "Low",
                    "weight": weight,
                    "description": f"Score is acceptable ({score:.1f}). Continue current practices."
                })
            else:
                risk_factors.append({
                    "dimension": DIMENSION_NAMES[i] if i < len(DIMENSION_NAMES) else f"Dim {i+1}",
                    "score": score,
                    "risk_level": "Minimal",
                    "weight": weight,
                    "description": f"Score is strong ({score:.1f}). Maintain and share best practices."
                })
        
        # Normalize risk score
        overall_risk = risk_score / total_weight if total_weight > 0 else 0.0
        
        # 2. Analyze trend (if available)
        if historical_trend and len(historical_trend) > 1:
            # Check if trend is declining
            if historical_trend[-1] < historical_trend[0]:
                overall_risk *= 1.2
                risk_factors.append({
                    "dimension": "Trend",
                    "score": historical_trend[-1],
                    "risk_level": "High" if overall_risk > 0.6 else "Moderate",
                    "weight": 0.5,
                    "description": f"Declining trend detected: {historical_trend[0]:.1f} → {historical_trend[-1]:.1f}"
                })
        
        # Determine risk category
        if overall_risk >= self.risk_thresholds["high"]:
            category = "High"
        elif overall_risk >= self.risk_thresholds["moderate"]:
            category = "Moderate"
        else:
            category = "Low"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(risk_factors, category)
        
        return RiskProfile(
            entity_id=school_id,
            entity_name=school_name,
            entity_type="school",
            overall_risk_score=round(overall_risk, 2),
            risk_category=category,
            risk_factors=risk_factors,
            recommended_interventions=recommendations,
            confidence=0.85  # Placeholder confidence score
        )
    
    def analyze_division(self, division_name: str, schools_data: List[Dict]) -> RiskProfile:
        """
        Analyze risk for a whole division.
        
        Args:
            division_name: Division name
            schools_data: List of school data dictionaries
            
        Returns:
            RiskProfile object
        """
        # Compute division-level averages
        if not schools_data:
            return RiskProfile(
                entity_id="unknown",
                entity_name=division_name,
                entity_type="division",
                overall_risk_score=0.0,
                risk_category="Unknown",
                risk_factors=[],
                recommended_interventions=["No data available for this division."],
                confidence=0.0
            )
        
        # Aggregate scores
        total_scores = np.zeros(6)
        at_risk_count = 0
        
        for school in schools_data:
            scores = school.get("dimension_scores", [0, 0, 0, 0, 0, 0])
            total_scores += np.array(scores)
            if school.get("risk_score", 0) > 0.5:
                at_risk_count += 1
        
        avg_scores = total_scores / len(schools_data)
        
        # Use the same analysis logic as school, but with aggregated data
        aggregated_data = {
            "id": division_name,
            "name": division_name,
            "dimension_scores": avg_scores.tolist()
        }
        
        profile = self.analyze_school(aggregated_data)
        profile.entity_type = "division"
        profile.entity_name = division_name
        profile.risk_factors.append({
            "dimension": "At-Risk Schools",
            "score": at_risk_count,
            "risk_level": "High" if at_risk_count / len(schools_data) > 0.3 else "Moderate",
            "weight": 0.5,
            "description": f"{at_risk_count} out of {len(schools_data)} schools are at risk ({at_risk_count/len(schools_data)*100:.1f}%)"
        })
        
        return profile
    
    def _generate_recommendations(self, risk_factors: List[Dict], risk_category: str) -> List[str]:
        """Generate intervention recommendations based on risk factors."""
        recommendations = []
        
        high_risk_dimensions = [f for f in risk_factors if f.get("risk_level") == "High"]
        moderate_risk_dimensions = [f for f in risk_factors if f.get("risk_level") == "Moderate"]
        
        if risk_category == "High":
            recommendations.append("🚨 Immediate action required. Schedule urgent technical assistance visit.")
            recommendations.append("📋 Conduct comprehensive SBM assessment to identify root causes.")
            recommendations.append("🤝 Engage stakeholders (PTA, LGU, community) for support.")
            recommendations.append("📊 Establish weekly progress monitoring.")
        elif risk_category == "Moderate":
            recommendations.append("📅 Schedule regular technical assistance and coaching sessions.")
            recommendations.append("📈 Develop a 3-month improvement plan with specific targets.")
            recommendations.append("🔄 Implement peer learning with high-performing schools.")
            recommendations.append("📊 Monitor progress monthly.")
        else:
            recommendations.append("✅ Continue current practices and maintain momentum.")
            recommendations.append("📚 Document best practices for sharing with other schools.")
            recommendations.append("🎯 Set ambitious targets for further improvement.")
            recommendations.append("🤝 Explore opportunities for innovation and scaling.")
        
        # Add dimension-specific recommendations
        for factor in high_risk_dimensions[:2]:
            dim_name = factor.get("dimension")
            if dim_name:
                recommendations.append(f"🎯 Focus on {dim_name}: Develop targeted intervention plan.")
        
        return recommendations
    
    def get_division_risk_summary(self, division_name: str, schools_data: List[Dict]) -> Dict:
        """
        Get a summary of risk analysis for a division.
        
        Args:
            division_name: Division name
            schools_data: List of school data dictionaries
            
        Returns:
            Dict with summary statistics
        """
        # Analyze each school
        school_profiles = []
        risk_counts = {"High": 0, "Moderate": 0, "Low": 0}
        
        for school in schools_data:
            profile = self.analyze_school(school)
            school_profiles.append(profile)
            risk_counts[profile.risk_category] = risk_counts.get(profile.risk_category, 0) + 1
        
        # Compute average risk score
        avg_risk = round(sum(p.overall_risk_score for p in school_profiles) / len(school_profiles), 2) if school_profiles else 0
        
        return {
            "division": division_name,
            "total_schools": len(schools_data),
            "avg_risk_score": avg_risk,
            "risk_distribution": risk_counts,
            "high_risk_percentage": round(risk_counts.get("High", 0) / len(schools_data) * 100, 1) if schools_data else 0,
            "high_risk_schools": [p.entity_name for p in school_profiles if p.risk_category == "High"][:10],
            "recommendations": self._generate_division_recommendations(risk_counts, avg_risk)
        }
    
    def _generate_division_recommendations(self, risk_counts: Dict, avg_risk: float) -> List[str]:
        """Generate division-level recommendations."""
        recommendations = []
        
        high_percentage = risk_counts.get("High", 0) / (sum(risk_counts.values()) or 1) * 100
        
        if high_percentage > 30:
            recommendations.append("🚨 Critical alert: More than 30% of schools are at high risk.")
            recommendations.append("📋 Deploy Regional Field Technical Assistance Team (RFTAT) immediately.")
            recommendations.append("💰 Reallocate resources to support high-risk schools.")
        elif high_percentage > 15:
            recommendations.append("⚠️ Moderate risk: 15-30% of schools need urgent support.")
            recommendations.append("📅 Schedule division-wide SBM capacity building.")
            recommendations.append("🤝 Establish peer mentoring program with high-performing schools.")
        else:
            recommendations.append("✅ Division is generally stable. Continue monitoring and support.")
            recommendations.append("📚 Share best practices across all schools.")
            recommendations.append("🎯 Set division-wide improvement targets.")
        
        return recommendations

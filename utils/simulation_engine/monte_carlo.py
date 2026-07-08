"""
Monte Carlo Simulation for Probabilistic Forecasting.

Runs thousands of simulations to generate probabilistic forecasts
with confidence intervals.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from .twin_helpers import get_degree_value, calculate_degree_of_manifestation


@dataclass
class SimulationResult:
    """Results from a single Monte Carlo simulation."""
    forecast_values: List[float]
    confidence_intervals: Dict[str, List[float]]
    distribution: Dict[str, float]
    summary: Dict[str, float]


class MonteCarloSimulation:
    """
    Monte Carlo simulation engine for SBM forecasting.
    """
    
    def __init__(self, n_simulations: int = 1000):
        self.n_simulations = n_simulations
        self.results = []
        self.seed = 42
        np.random.seed(self.seed)
    
    def simulate_school_progression(self, current_scores: List[float], 
                                     intervention_effects: Dict[str, float],
                                     time_steps: int = 3,
                                     volatility: float = 0.2) -> SimulationResult:
        """
        Simulate school progression with random variations.
        """
        # Guard: if all scores are zero, return a flat forecast
        if not current_scores or all(s == 0 for s in current_scores):
            return SimulationResult(
                forecast_values=[0.0] * time_steps,
                confidence_intervals={"50%": [0.0]*time_steps, "75%": [0.0]*time_steps, "90%": [0.0]*time_steps},
                distribution={"Not Yet Manifested": 100.0, "Rarely Manifested": 0.0, 
                              "Frequently Manifested": 0.0, "Always Manifested": 0.0},
                summary={"mean": 0.0, "median": 0.0, "std": 0.0, "min": 0.0, "max": 0.0}
            )
        
        # Cap volatility to avoid wild swings
        volatility = min(volatility, 0.3)
        
        # Run multiple simulations
        all_paths = []
        final_values = []
        
        # Reduce simulations for speed if needed (but keep at least 100)
        n_sim = min(self.n_simulations, 500)  # Cap for performance
        
        for sim in range(n_sim):
            path = self._run_single_simulation(current_scores, intervention_effects, time_steps, volatility)
            all_paths.append(path)
            final_values.append(path[-1])
        
        # Compute results
        paths_array = np.array(all_paths)
        summary = {
            "mean": np.mean(final_values),
            "median": np.median(final_values),
            "std": np.std(final_values),
            "min": np.min(final_values),
            "max": np.max(final_values),
        }
        
        # Compute confidence intervals (using percentiles)
        confidence_intervals = {
            "50%": [np.percentile(paths_array[:, t], 25) for t in range(time_steps)],
            "75%": [np.percentile(paths_array[:, t], 12.5) for t in range(time_steps)],
            "90%": [np.percentile(paths_array[:, t], 5) for t in range(time_steps)],
            "95%": [np.percentile(paths_array[:, t], 2.5) for t in range(time_steps)],
        }
        
        # Distribution of final values
        degree_counts = {
            "Not Yet Manifested": 0,
            "Rarely Manifested": 0,
            "Frequently Manifested": 0,
            "Always Manifested": 0
        }
        for val in final_values:
            degree = calculate_degree_of_manifestation(val)
            if degree in degree_counts:
                degree_counts[degree] += 1
        
        distribution = {k: v / n_sim * 100 for k, v in degree_counts.items()}
        
        mean_path = np.mean(paths_array, axis=0)
        
        return SimulationResult(
            forecast_values=mean_path.tolist(),
            confidence_intervals=confidence_intervals,
            distribution=distribution,
            summary=summary
        )
    
    def _run_single_simulation(self, current_scores: List[float],
                               intervention_effects: Dict[str, float],
                               time_steps: int,
                               volatility: float) -> List[float]:
        """
        Run a single simulation path.
        """
        path = []
        scores = current_scores.copy()
        overall = sum(scores) / len(scores) if scores else 0
        path.append(overall)
        
        for t in range(time_steps):
            # Apply intervention effects
            for i in range(len(scores)):
                effect_key = f"dim_{i}"
                if effect_key in intervention_effects:
                    # Intervention adds to the score
                    scores[i] += intervention_effects[effect_key] * (0.5 + 0.5 * np.random.random())
                else:
                    # Default: small improvement with random variation
                    scores[i] += 0.05 * np.random.random()
                
                # Add random shock, but ensure it doesn't blow up
                shock = np.random.normal(0, volatility / 2)
                scores[i] += shock
                # Clamp to 0-3
                scores[i] = max(0.0, min(3.0, scores[i]))
            
            # Recompute overall
            overall = sum(scores) / len(scores) if scores else 0
            path.append(round(overall, 2))
        
        return path
    
    def simulate_division(self, schools_data: List[Dict],
                          intervention_effects: Dict[str, float],
                          time_steps: int = 3) -> Dict:
        """Simulate a whole division."""
        # Skip if no schools
        if not schools_data:
            return {
                "division": "Unknown",
                "n_schools": 0,
                "time_steps": time_steps,
                "mean_forecast": [0.0]*time_steps,
                "current_index": 0,
                "predicted_index": 0,
                "improvement": 0,
                "improvement_percent": 0
            }
        
        all_results = []
        for school in schools_data:
            scores = school.get("dimension_scores", [0, 0, 0, 0, 0, 0])
            # Skip schools with no data
            if all(s == 0 for s in scores):
                continue
            result = self.simulate_school_progression(scores, intervention_effects, time_steps)
            all_results.append(result)
        
        if not all_results:
            return {
                "division": "Unknown",
                "n_schools": 0,
                "time_steps": time_steps,
                "mean_forecast": [0.0]*time_steps,
                "current_index": 0,
                "predicted_index": 0,
                "improvement": 0,
                "improvement_percent": 0
            }
        
        mean_forecasts = np.mean([r.forecast_values for r in all_results], axis=0)
        
        summary = {
            "division": "Aggregated",
            "n_schools": len(all_results),
            "time_steps": time_steps,
            "mean_forecast": mean_forecasts.tolist(),
            "current_index": mean_forecasts[0],
            "predicted_index": mean_forecasts[-1],
            "improvement": mean_forecasts[-1] - mean_forecasts[0],
            "improvement_percent": ((mean_forecasts[-1] - mean_forecasts[0]) / (mean_forecasts[0] or 0.01)) * 100
        }
        
        return summary
    
    def get_risk_analysis(self, current_scores: List[float], 
                          predicted_scores: List[float],
                          threshold: float = 1.5) -> Dict:
        """Analyze risk based on predicted scores."""
        if not current_scores or not predicted_scores:
            return {
                "current_avg": 0,
                "predicted_avg": 0,
                "change": 0,
                "overall_risk": "Low",
                "risk_indicators": [],
                "at_risk_dimensions": 0
            }
        
        current_avg = sum(current_scores) / len(current_scores)
        predicted_avg = sum(predicted_scores) / len(predicted_scores)
        
        risk_indicators = []
        for i, (current, predicted) in enumerate(zip(current_scores, predicted_scores)):
            if predicted < threshold:
                risk_indicators.append({
                    "dimension": f"Dimension {i+1}",
                    "current": current,
                    "predicted": predicted,
                    "status": "At Risk" if predicted < threshold else "Stable"
                })
        
        overall_risk = "High" if predicted_avg < threshold else "Moderate" if predicted_avg < 2.0 else "Low"
        
        return {
            "current_avg": current_avg,
            "predicted_avg": predicted_avg,
            "change": predicted_avg - current_avg,
            "overall_risk": overall_risk,
            "risk_indicators": risk_indicators,
            "at_risk_dimensions": len([r for r in risk_indicators if r["status"] == "At Risk"])
        }

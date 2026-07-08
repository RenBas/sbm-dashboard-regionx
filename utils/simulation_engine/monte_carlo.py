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
        
        Args:
            current_scores: List of 6 dimension scores (0.0–3.0)
            intervention_effects: Dict of intervention effects on each dimension
            time_steps: Number of time steps to simulate
            volatility: Standard deviation of random shocks
            
        Returns:
            SimulationResult with probabilistic forecasts
        """
        # Run multiple simulations
        all_paths = []
        final_values = []
        
        for sim in range(self.n_simulations):
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
        
        # Compute confidence intervals
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
        
        distribution = {k: v / self.n_simulations * 100 for k, v in degree_counts.items()}
        
        # Create result object
        # For each time step, compute the mean forecast
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
        overall = sum(scores) / len(scores)
        path.append(overall)
        
        for t in range(time_steps):
            # Apply intervention effects
            for i in range(len(scores)):
                # Each dimension can be affected differently
                effect_key = f"dim_{i}"
                if effect_key in intervention_effects:
                    # Intervention adds to the score
                    scores[i] += intervention_effects[effect_key] * (0.5 + 0.5 * np.random.random())
                else:
                    # Default: small improvement with random variation
                    scores[i] += 0.05 * np.random.random()
                
                # Add random shock
                scores[i] += np.random.normal(0, volatility / 2)
                scores[i] = max(0.0, min(3.0, scores[i]))
            
            # Recompute overall
            overall = sum(scores) / len(scores)
            path.append(round(overall, 2))
        
        return path
    
    def simulate_division(self, schools_data: List[Dict],
                          intervention_effects: Dict[str, float],
                          time_steps: int = 3) -> Dict:
        """
        Simulate a whole division.
        
        Args:
            schools_data: List of school data dictionaries with dimension_scores
            intervention_effects: Dict of intervention effects
            time_steps: Number of time steps
            
        Returns:
            Dict with division-level simulation results
        """
        all_results = []
        for school in schools_data:
            scores = school.get("dimension_scores", [0, 0, 0, 0, 0, 0])
            result = self.simulate_school_progression(scores, intervention_effects, time_steps)
            all_results.append(result)
        
        # Aggregate division results
        mean_forecasts = np.mean([r.forecast_values for r in all_results], axis=0)
        
        summary = {
            "division": "Aggregated",
            "n_schools": len(schools_data),
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
        """
        Analyze risk based on predicted scores.
        
        Args:
            current_scores: Current SBM scores
            predicted_scores: Predicted SBM scores
            threshold: Score below which is considered "at risk"
            
        Returns:
            Dict with risk analysis
        """
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

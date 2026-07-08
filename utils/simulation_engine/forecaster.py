"""
Forecaster – Time-series forecasting for SBM indices.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline


class Forecaster:
    """
    Time-series forecaster for SBM indices.
    """
    
    def __init__(self, degree: int = 2):
        self.degree = degree
        self.models = {}
        self.history = {}
    
    def fit_historical_data(self, school_id: str, historical_scores: List[float]) -> None:
        """
        Fit a trend model to historical SBM scores.
        
        Args:
            school_id: School identifier
            historical_scores: List of historical overall scores (chronological)
        """
        if len(historical_scores) < 3:
            # Not enough data for fitting
            self.history[school_id] = historical_scores
            self.models[school_id] = None
            return
        
        # Create time points
        X = np.arange(len(historical_scores)).reshape(-1, 1)
        y = np.array(historical_scores)
        
        # Fit polynomial regression
        model = Pipeline([
            ('poly', PolynomialFeatures(degree=self.degree)),
            ('linear', LinearRegression())
        ])
        model.fit(X, y)
        
        self.models[school_id] = model
        self.history[school_id] = historical_scores
    
    def predict_future(self, school_id: str, steps: int = 3) -> Dict:
        """
        Predict future SBM scores.
        
        Args:
            school_id: School identifier
            steps: Number of steps to predict
            
        Returns:
            Dict with predictions and confidence intervals
        """
        if school_id not in self.models or self.models[school_id] is None:
            return self._default_prediction(steps)
        
        model = self.models[school_id]
        history = self.history.get(school_id, [])
        
        # Determine start point for prediction
        start_idx = len(history)
        X_future = np.arange(start_idx, start_idx + steps).reshape(-1, 1)
        
        # Predict
        predictions = model.predict(X_future)
        
        # Clamp to 0-3 range
        predictions = np.clip(predictions, 0, 3)
        
        # Compute confidence intervals based on historical residuals
        if len(history) > 1:
            X_hist = np.arange(len(history)).reshape(-1, 1)
            y_hist = np.array(history)
            y_pred_hist = model.predict(X_hist)
            residuals = y_hist - y_pred_hist
            std_error = np.std(residuals)
        else:
            std_error = 0.15  # Default error
        
        confidence_intervals = {
            "50%": (predictions - 0.67 * std_error, predictions + 0.67 * std_error),
            "75%": (predictions - 1.15 * std_error, predictions + 1.15 * std_error),
            "90%": (predictions - 1.64 * std_error, predictions + 1.64 * std_error),
        }
        
        return {
            "school_id": school_id,
            "predictions": predictions.tolist(),
            "confidence_intervals": {
                k: [round(float(ci[0][i]), 2), round(float(ci[1][i]), 2)]
                for k, ci in confidence_intervals.items() for i in range(len(predictions))
            } if isinstance(confidence_intervals, dict) else confidence_intervals,
            "trend_direction": "Upward" if predictions[-1] > predictions[0] else "Downward" if predictions[-1] < predictions[0] else "Stable",
            "predicted_change": round(predictions[-1] - predictions[0], 2)
        }
    
    def _default_prediction(self, steps: int) -> Dict:
        """Return default predictions when no historical data is available."""
        return {
            "school_id": "unknown",
            "predictions": [1.5] * steps,
            "confidence_intervals": {"50%": (1.0, 2.0), "75%": (0.8, 2.2), "90%": (0.5, 2.5)},
            "trend_direction": "Unknown",
            "predicted_change": 0.0
        }
    
    def batch_predict(self, schools_data: List[Dict], steps: int = 3) -> List[Dict]:
        """
        Predict future SBM scores for multiple schools.
        
        Args:
            schools_data: List of school data dictionaries
            steps: Number of steps to predict
            
        Returns:
            List of prediction results
        """
        results = []
        for school in schools_data:
            school_id = school.get("id")
            historical = school.get("historical_scores", [])
            
            if historical:
                self.fit_historical_data(school_id, historical)
            else:
                # Use current scores as a baseline
                scores = school.get("dimension_scores", [0, 0, 0, 0, 0, 0])
                current_avg = sum(scores) / len(scores) if scores else 0
                historical = [current_avg] * 2  # Short history
                self.fit_historical_data(school_id, historical)
            
            pred = self.predict_future(school_id, steps)
            pred["school_name"] = school.get("name", "Unknown")
            results.append(pred)
        
        return results

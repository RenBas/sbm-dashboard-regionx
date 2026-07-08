def predict_school_transition(self, school_id: str, current_scores: List[float],
                               interventions: Dict[str, float] = None,
                               steps: int = 3) -> Dict:
    """
    Predict a school's state transitions over multiple time periods.
    """
    # Guard: if all scores are zero, return a flat prediction
    if not current_scores or all(s == 0 for s in current_scores):
        return {
            "school_id": school_id,
            "current_state": "Not Yet Manifested",
            "current_index": 0,
            "steps": [{"step": i+1, "state": "Not Yet Manifested", "score": 0.0, "confidence": 1.0, "time_period": f"Year {i+1}"} for i in range(steps)],
            "predicted_states": ["Not Yet Manifested"] * steps,
            "confidence_scores": [1.0] * steps
        }
    
    # ... rest of the function remains the same

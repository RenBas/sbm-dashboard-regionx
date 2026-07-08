"""
Test script for Digital Twin Simulation Engine.
"""

import sys
sys.path.append('.')

from utils.simulation_engine import (
    MarkovModel, CausalModel, MonteCarloSimulation, RiskAnalyzer, Forecaster
)

def test_markov_model():
    print("Testing Markov Model...")
    model = MarkovModel()
    
    current_scores = [2.0, 1.8, 2.5, 1.2, 2.0, 1.5]  # Dimension scores
    interventions = {"technical_assistance": 0.7, "capacity_building": 0.5}
    
    result = model.predict_school_transition(
        school_id="TEST001",
        current_scores=current_scores,
        interventions=interventions,
        steps=3
    )
    
    print(f"Current State: {result['current_state']}")
    print(f"Predicted States: {result['predicted_states']}")
    print(f"Confidence: {result['confidence_scores']}")
    print("\n")

def test_monte_carlo():
    print("Testing Monte Carlo Simulation...")
    mc = MonteCarloSimulation(n_simulations=100)
    
    current_scores = [2.0, 1.8, 2.5, 1.2, 2.0, 1.5]
    interventions = {"dim_0": 0.3, "dim_1": 0.2, "dim_3": 0.5}
    
    result = mc.simulate_school_progression(
        current_scores=current_scores,
        intervention_effects=interventions,
        time_steps=3,
        volatility=0.15
    )
    
    print(f"Forecast: {result.forecast_values}")
    print(f"Summary: {result.summary}")
    print(f"Distribution: {result.distribution}")
    print("\n")

def test_risk_analyzer():
    print("Testing Risk Analyzer...")
    analyzer = RiskAnalyzer()
    
    school_data = {
        "id": "TEST001",
        "name": "Test School",
        "dimension_scores": [2.0, 1.8, 2.5, 1.2, 2.0, 1.5]
    }
    
    profile = analyzer.analyze_school(school_data)
    print(f"Risk Score: {profile.overall_risk_score}")
    print(f"Risk Category: {profile.risk_category}")
    print(f"Recommendations: {profile.recommended_interventions[:2]}")
    print("\n")

def test_forecaster():
    print("Testing Forecaster...")
    forecaster = Forecaster()
    
    historical = [1.5, 1.7, 1.9, 2.1, 2.0, 2.2]
    forecaster.fit_historical_data("TEST001", historical)
    
    result = forecaster.predict_future("TEST001", steps=3)
    print(f"Predictions: {result['predictions']}")
    print(f"Trend: {result['trend_direction']}")
    print(f"Change: {result['predicted_change']}")
    print("\n")

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Digital Twin Simulation Engine")
    print("=" * 50)
    print()
    
    test_markov_model()
    test_monte_carlo()
    test_risk_analyzer()
    test_forecaster()
    
    print("✅ All tests completed!")

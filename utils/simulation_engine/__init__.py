"""
Simulation Engine for SBM Digital Twin – Phase 2.

This package contains all core simulation and prediction modules:
- markov_model: Markov Chain for state transitions
- causal_model: Causal impact analysis for interventions
- monte_carlo: Monte Carlo simulation for probabilistic forecasts
- risk_analyzer: At-risk school detection
- forecaster: Time-series forecasting
- twin_helpers: Shared utility functions
"""

from .markov_model import MarkovModel, StateTransition
from .causal_model import CausalModel, InterventionImpact
from .monte_carlo import MonteCarloSimulation
from .risk_analyzer import RiskAnalyzer
from .forecaster import Forecaster
from .twin_helpers import (
    calculate_degree_of_manifestation,
    get_dimension_index,
    normalize_scores,
    validate_sbm_data,
    compute_dimension_averages_from_scores
)

__all__ = [
    "MarkovModel",
    "StateTransition",
    "CausalModel",
    "InterventionImpact",
    "MonteCarloSimulation",
    "RiskAnalyzer",
    "Forecaster",
    "calculate_degree_of_manifestation",
    "get_dimension_index",
    "normalize_scores",
    "validate_sbm_data",
    "compute_dimension_averages_from_scores",
]

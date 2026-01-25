"""
Touch Dependency Model (TDM)
============================

A production-ready ML system for evaluating player touch dependency.

Usage:
    from tdm import TouchDependencyModel

    tdm = TouchDependencyModel()
    tdm.load_models()

    report = tdm.evaluate_player({
        'FG': 373, 'FGA': 1024, 'FT': 285, 'FTA': 374,
        '3P': 0, '3PA': 0, 'AST': 247, 'MP': 2800,
        'PTS': 1031, 'TOV': 150
    })

    print(report['tds_score'])
    print(report['scouting_summary'])
"""

from .predictor import TouchDependencyModel
from .features import FeatureEngineer
from .scoring import TDSCalculator
from .archetypes import ArchetypeClusterer
from .data_loader import DataLoader

__version__ = "1.0.0"
__all__ = [
    "TouchDependencyModel",
    "FeatureEngineer",
    "TDSCalculator",
    "ArchetypeClusterer",
    "DataLoader"
]

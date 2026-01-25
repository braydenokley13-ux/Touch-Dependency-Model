"""
Main Touch Dependency Model predictor engine.
"""

import numpy as np
from pathlib import Path
from typing import Dict, Optional, Union, List
import warnings

from .features import FeatureEngineer
from .scoring import TDSCalculator
from .archetypes import ArchetypeClusterer
from .models import LinearTSModel, XGBoostTSModel, EnsembleTSModel
from .scouting import ScoutingSummaryGenerator, GMRecommendationEngine


class TouchDependencyModel:
    """
    Main interface for the Touch Dependency Model.

    Combines all components to evaluate player touch dependency
    and generate scouting reports.

    Usage:
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

    def __init__(self, model_dir: str = "models"):
        """
        Initialize TouchDependencyModel.

        Args:
            model_dir: Directory containing saved model files
        """
        self.model_dir = Path(model_dir)

        # Core components
        self.feature_engineer = FeatureEngineer()
        self.linear_model = LinearTSModel()
        self.xgb_model = XGBoostTSModel()
        self.ensemble_model = EnsembleTSModel()
        self.tds_calculator = TDSCalculator()
        self.clusterer = ArchetypeClusterer()

        # Scouting components
        self.summary_generator = ScoutingSummaryGenerator()
        self.gm_engine = GMRecommendationEngine()

        self._is_loaded = False

    def load_models(self, model_dir: Optional[str] = None) -> 'TouchDependencyModel':
        """
        Load all trained models from disk.

        Args:
            model_dir: Optional override for model directory

        Returns:
            self
        """
        if model_dir:
            self.model_dir = Path(model_dir)

        try:
            # Load feature engineer
            self.feature_engineer.load(self.model_dir / 'feature_engineer.pkl')

            # Load models
            self.linear_model.load(self.model_dir / 'linear_model.pkl')
            self.xgb_model.load(self.model_dir / 'xgboost_model.pkl')
            self.ensemble_model.load(self.model_dir / 'ensemble_weights.pkl')

            # Connect ensemble to loaded models
            self.ensemble_model.linear_model = self.linear_model
            self.ensemble_model.xgb_model = self.xgb_model

            # Load TDS calculator
            self.tds_calculator.load(self.model_dir / 'tds_calculator.pkl')

            # Load clusterer
            self.clusterer.load(self.model_dir / 'clusterer.pkl')

            self._is_loaded = True

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Model files not found in {self.model_dir}. "
                "Run train_model.py first to generate models."
            ) from e

        return self

    def evaluate_player(self, stats: Dict) -> Dict:
        """
        Evaluate a single player and generate full report.

        Args:
            stats: Dictionary of player statistics. Required keys:
                - FG: Field goals made
                - FGA: Field goal attempts
                - FT: Free throws made
                - FTA: Free throw attempts
                - PTS: Total points
                - MP: Minutes played

                Optional keys:
                - 3P, 3PA: Three-point makes/attempts
                - 2P, 2PA: Two-point makes/attempts (computed if missing)
                - AST: Assists
                - TOV: Turnovers
                - Age: Player age
                - Pos: Position
                - Player: Player name
                - USG%, AST%, TOV%: Pre-computed advanced stats

        Returns:
            Dictionary containing:
                - tds_score: Touch Dependency Score (0-100)
                - tds_category: TDS interpretation category
                - archetype: Player archetype classification
                - predicted_ts: Model predicted TS%
                - actual_ts: Actual TS%
                - residual: Performance vs expectation
                - scouting_summary: Natural language assessment
                - short_summary: Brief 1-2 sentence summary
                - gm_recommendations: Actionable GM guidance
                - feature_values: Computed feature values
        """
        if not self._is_loaded:
            raise ValueError("Models not loaded. Call load_models() first.")

        # Validate and prepare input
        stats = self._validate_input(stats)

        # Compute actual TS%
        actual_ts = self._compute_ts(stats)

        # Transform to feature vector
        X = self.feature_engineer.transform_single_player(stats)

        # Get model prediction
        predicted_ts = float(self.ensemble_model.predict(X)[0])

        # Calculate residual and TDS
        residual = actual_ts - predicted_ts
        tds_score = self.tds_calculator.compute_tds(residual)
        tds_category, tds_desc = self.tds_calculator.interpret_tds(tds_score)

        # Get computed feature values for clustering and reporting
        feature_values = self._extract_feature_values(stats, X)
        feature_values['TS%'] = actual_ts
        feature_values['TDS'] = tds_score

        # Predict archetype
        clustering_features = self._prepare_clustering_features(feature_values)
        archetype, cluster_id = self.clusterer.predict_archetype(clustering_features)

        # Build profile for scouting
        profile = {
            'player_name': stats.get('Player', 'Player'),
            'usg_pct': feature_values.get('USG%', 20),
            'ast_pct': feature_values.get('AST%', 15),
            'ts_pct': actual_ts,
            'predicted_ts': predicted_ts,
            'tds_score': tds_score,
            'archetype': archetype,
            'three_pa_rate': feature_values.get('3PA_rate', 0.30),
            'fta_rate': feature_values.get('FTA_rate', 0.25),
            'age': stats.get('Age'),
            'ft_pct': stats.get('FT', 0) / max(stats.get('FTA', 1), 1)
        }

        # Generate scouting language
        scouting_summary = self.summary_generator.generate_summary(profile)
        short_summary = self.summary_generator.generate_short_summary(profile)
        gm_recommendations = self.gm_engine.generate_recommendations(profile)

        return {
            'tds_score': round(tds_score, 1),
            'tds_category': tds_category,
            'tds_description': tds_desc,
            'archetype': archetype,
            'archetype_description': self.clusterer.get_archetype_description(archetype),
            'predicted_ts': round(predicted_ts, 4),
            'actual_ts': round(actual_ts, 4),
            'residual': round(residual, 4),
            'scouting_summary': scouting_summary,
            'short_summary': short_summary,
            'gm_recommendations': gm_recommendations,
            'feature_values': {k: round(v, 3) if isinstance(v, float) else v
                             for k, v in feature_values.items()}
        }

    def evaluate_batch(self, players: List[Dict]) -> List[Dict]:
        """
        Evaluate multiple players.

        Args:
            players: List of player stat dictionaries

        Returns:
            List of evaluation reports
        """
        return [self.evaluate_player(p) for p in players]

    def quick_score(self, stats: Dict) -> float:
        """
        Get just the TDS score without full report.

        Args:
            stats: Player statistics

        Returns:
            TDS score (0-100)
        """
        if not self._is_loaded:
            raise ValueError("Models not loaded. Call load_models() first.")

        stats = self._validate_input(stats)
        actual_ts = self._compute_ts(stats)
        X = self.feature_engineer.transform_single_player(stats)
        predicted_ts = float(self.ensemble_model.predict(X)[0])
        residual = actual_ts - predicted_ts

        return self.tds_calculator.compute_tds(residual)

    def _validate_input(self, stats: Dict) -> Dict:
        """Validate and fill in missing stats."""
        required = ['FG', 'FGA', 'FT', 'FTA', 'PTS', 'MP']
        missing = [k for k in required if k not in stats or stats[k] is None]

        if missing:
            raise ValueError(f"Missing required stats: {missing}")

        # Make a copy
        stats = dict(stats)

        # Fill in computed values
        if '3P' not in stats:
            stats['3P'] = 0
        if '3PA' not in stats:
            stats['3PA'] = 0
        if '2P' not in stats:
            stats['2P'] = stats['FG'] - stats['3P']
        if '2PA' not in stats:
            stats['2PA'] = stats['FGA'] - stats['3PA']
        if 'TOV' not in stats:
            stats['TOV'] = 0
        if 'AST' not in stats:
            stats['AST'] = 0

        # Validate values
        if stats['FGA'] == 0:
            raise ValueError("FGA cannot be zero")
        if stats['MP'] == 0:
            raise ValueError("MP cannot be zero")

        return stats

    def _compute_ts(self, stats: Dict) -> float:
        """Compute True Shooting Percentage."""
        pts = stats['PTS']
        fga = stats['FGA']
        fta = stats['FTA']

        denominator = 2 * (fga + 0.44 * fta)
        if denominator == 0:
            return 0.0

        return pts / denominator

    def _extract_feature_values(self, stats: Dict, X: np.ndarray) -> Dict:
        """Extract readable feature values."""
        fga = stats['FGA']
        fta = stats['FTA']
        mp = stats['MP']

        values = {}

        # Use precomputed if available, otherwise estimate
        if 'USG%' in stats:
            values['USG%'] = stats['USG%']
        else:
            # Rough estimate
            possessions = fga + 0.44 * fta + stats.get('TOV', 0)
            values['USG%'] = (possessions / mp) * 48 * 5 if mp > 0 else 20

        if 'AST%' in stats:
            values['AST%'] = stats['AST%']
        else:
            ast = stats.get('AST', 0)
            values['AST%'] = (ast / mp) * 48 * 2.5 if mp > 0 else 15

        if 'TOV%' in stats:
            values['TOV%'] = stats['TOV%']
        else:
            tov = stats.get('TOV', 0)
            possessions = fga + 0.44 * fta + tov
            values['TOV%'] = (tov / possessions * 100) if possessions > 0 else 10

        values['3PA_rate'] = stats.get('3PA', 0) / fga if fga > 0 else 0
        values['2PA_rate'] = stats.get('2PA', fga) / fga if fga > 0 else 1
        values['FTA_rate'] = fta / fga if fga > 0 else 0.25

        return values

    def _prepare_clustering_features(self, feature_values: Dict) -> np.ndarray:
        """Prepare feature vector for clustering."""
        features = [
            feature_values.get('USG%', 20),
            feature_values.get('AST%', 15),
            feature_values.get('TS%', 0.54),
            feature_values.get('TDS', 50),
            feature_values.get('3PA_rate', 0.30),
            feature_values.get('FTA_rate', 0.25)
        ]
        return np.array(features)

    def get_model_info(self) -> Dict:
        """Get information about loaded models."""
        if not self._is_loaded:
            return {'status': 'not_loaded'}

        return {
            'status': 'loaded',
            'model_dir': str(self.model_dir),
            'feature_names': self.feature_engineer.feature_names,
            'linear_model_coefficients': self.linear_model.get_coefficients()
                if self.linear_model.is_fitted else None,
            'xgb_feature_importance': self.xgb_model.get_feature_importance()
                if self.xgb_model.is_fitted else None,
            'ensemble_weights': self.ensemble_model.weights,
            'tds_distribution': self.tds_calculator.get_distribution_stats()
                if self.tds_calculator.is_calibrated else None,
            'archetypes': list(self.clusterer.cluster_labels_.values())
                if self.clusterer.is_fitted else None
        }

    @property
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self._is_loaded

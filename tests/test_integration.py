"""Integration tests for Touch Dependency Model."""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import os


VALID_ARCHETYPES = [
    "Star Playmaker", "Volume Scorer", "Floor General", "Sharpshooter",
    "Reliable Starter", "Energy Scorer", "Rim Runner", "Stretch Big",
    "Role Player", "Defensive Specialist", "Developing Player", "Bench Scorer"
]


class TestTDSCalculator:
    """Test TDS Calculator integration."""

    def test_calibrate_and_compute(self):
        """Test calibration and TDS computation."""
        from tdm.scoring import TDSCalculator

        # Generate synthetic residuals
        np.random.seed(42)
        residuals = np.random.normal(0, 0.03, 1000)

        calc = TDSCalculator()
        calc.calibrate(residuals)

        # Test TDS computation
        tds_median = calc.compute_tds(0)  # Median residual
        tds_high = calc.compute_tds(0.05)  # High residual
        tds_low = calc.compute_tds(-0.05)  # Low residual

        # Median should be ~50
        assert 40 < tds_median < 60

        # Higher residual = higher TDS
        assert tds_high > tds_median
        assert tds_low < tds_median

        # All in valid range
        assert 0 <= tds_low <= 100
        assert 0 <= tds_high <= 100

    def test_interpret_tds(self):
        """Test TDS interpretation."""
        from tdm.scoring import TDSCalculator

        calc = TDSCalculator()
        calc.calibrate(np.random.normal(0, 0.03, 100))

        category, desc = calc.interpret_tds(85)
        assert category == "Highly Scalable"

        category, desc = calc.interpret_tds(25)
        assert category == "Highly Touch Dependent"

        category, desc = calc.interpret_tds(55)
        assert category == "Neutral"


class TestArchetypeClusterer:
    """Test Archetype Clusterer integration."""

    def test_fit_and_predict(self):
        """Test fitting and prediction."""
        from tdm.archetypes import ArchetypeClusterer

        # Generate synthetic feature data
        np.random.seed(42)
        n_samples = 200
        features = np.column_stack([
            np.random.uniform(15, 35, n_samples),  # USG%
            np.random.uniform(5, 40, n_samples),   # AST%
            np.random.uniform(0.45, 0.65, n_samples),  # TS%
            np.random.uniform(20, 80, n_samples),  # TDS
            np.random.uniform(0.1, 0.6, n_samples),  # 3PA_rate
            np.random.uniform(0.15, 0.45, n_samples)  # FTA_rate
        ])

        clusterer = ArchetypeClusterer(n_clusters=12)
        clusterer.fit(features)

        # Test prediction
        test_features = features[0]
        archetype, cluster_id = clusterer.predict_archetype(test_features)

        assert archetype in VALID_ARCHETYPES
        assert 0 <= cluster_id < 12

    def test_get_archetype_profiles(self):
        """Test archetype profile retrieval."""
        from tdm.archetypes import ArchetypeClusterer

        np.random.seed(42)
        features = np.random.rand(100, 6)

        clusterer = ArchetypeClusterer(n_clusters=12)
        clusterer.fit(features)

        profiles = clusterer.get_archetype_profiles()

        assert len(profiles) == 12
        for archetype, profile in profiles.items():
            assert archetype in VALID_ARCHETYPES
            assert isinstance(profile, dict)


class TestScoutingSummaryGenerator:
    """Test scouting summary generation."""

    def test_generate_summary(self):
        """Test summary generation."""
        from tdm.scouting import ScoutingSummaryGenerator

        generator = ScoutingSummaryGenerator()

        profile = {
            'player_name': 'Test Player',
            'usg_pct': 25,
            'ast_pct': 18,
            'ts_pct': 0.58,
            'predicted_ts': 0.55,
            'tds_score': 65,
            'archetype': 'Star Playmaker',
            'three_pa_rate': 0.35,
            'fta_rate': 0.28,
            'age': 26
        }

        summary = generator.generate_summary(profile)

        assert len(summary) > 100
        assert isinstance(summary, str)
        # Should mention key metrics
        assert 'usage' in summary.lower() or 'usg' in summary.lower()

    def test_generate_short_summary(self):
        """Test short summary generation."""
        from tdm.scouting import ScoutingSummaryGenerator

        generator = ScoutingSummaryGenerator()

        profile = {
            'archetype': 'Sharpshooter',
            'tds_score': 70,
            'ts_pct': 0.60
        }

        short = generator.generate_short_summary(profile)

        assert len(short) < 200
        assert 'Sharpshooter' in short


class TestGMRecommendationEngine:
    """Test GM recommendation generation."""

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        from tdm.scouting import GMRecommendationEngine

        engine = GMRecommendationEngine()

        profile = {
            'archetype': 'Sharpshooter',
            'tds_score': 65,
            'usg_pct': 18,
            'ast_pct': 12,
            'ts_pct': 0.59,
            'three_pa_rate': 0.50,
            'fta_rate': 0.20,
            'age': 28
        }

        recommendations = engine.generate_recommendations(profile)

        assert 'deployment' in recommendations
        assert 'acquisition' in recommendations
        assert 'market_value' in recommendations
        assert 'development' in recommendations

        for key, value in recommendations.items():
            assert isinstance(value, str)
            assert len(value) > 10


class TestDataLoader:
    """Test data loading functionality."""

    def test_load_and_filter(self):
        """Test data loading with filtering."""
        from tdm.data_loader import DataLoader

        # Check if data file exists
        data_path = Path("data/Seasons_Stats.csv")
        if not data_path.exists():
            pytest.skip("Data file not found")

        loader = DataLoader()
        df = loader.load_training_data()

        # Check filtering worked
        assert df['MP'].min() >= loader.MIN_MINUTES_THRESHOLD
        assert df['FGA'].min() >= loader.MIN_FGA_THRESHOLD

        # Check required columns exist
        for col in loader.REQUIRED_COLUMNS:
            assert col in df.columns


class TestEndToEndPipeline:
    """Test complete end-to-end evaluation pipeline."""

    @pytest.fixture
    def trained_model(self, tmp_path):
        """Create a trained model for testing."""
        from tdm.data_loader import DataLoader
        from tdm.features import FeatureEngineer
        from tdm.models import EnsembleTSModel
        from tdm.scoring import TDSCalculator
        from tdm.archetypes import ArchetypeClusterer

        # Check if data exists
        if not Path("data/Seasons_Stats.csv").exists():
            pytest.skip("Data file not found")

        # Load data
        loader = DataLoader()
        df = loader.load_training_data()

        # Engineer features
        engineer = FeatureEngineer()
        X, y, feature_names = engineer.create_feature_matrix(df)

        # Train ensemble
        ensemble = EnsembleTSModel()
        ensemble.fit(X, y, feature_names)

        # Get residuals and calibrate TDS
        residuals = ensemble.compute_final_residuals(X, y)
        tds_calc = TDSCalculator()
        tds_calc.calibrate(residuals)

        # Prepare clustering features
        tds_scores = tds_calc.compute_tds_batch(residuals)
        clustering_df = pd.DataFrame({
            'USG%': df['USG%'].values[:len(residuals)],
            'AST%': df['AST%'].values[:len(residuals)],
            'TS%': y,
            'TDS': tds_scores,
            '3PA_rate': (df['3PA'] / df['FGA'].replace(0, 1)).values[:len(residuals)],
            'FTA_rate': (df['FTA'] / df['FGA'].replace(0, 1)).values[:len(residuals)]
        }).fillna(0)

        clusterer = ArchetypeClusterer(n_clusters=12)
        clusterer.fit(clustering_df.values)

        # Save models
        model_dir = tmp_path / "models"
        model_dir.mkdir()

        engineer.save(model_dir / 'feature_engineer.pkl')
        ensemble.linear_model.save(model_dir / 'linear_model.pkl')
        ensemble.xgb_model.save(model_dir / 'xgboost_model.pkl')
        ensemble.save(model_dir / 'ensemble_weights.pkl')
        tds_calc.save(model_dir / 'tds_calculator.pkl')
        clusterer.save(model_dir / 'clusterer.pkl')

        return str(model_dir)

    def test_full_evaluation(self, trained_model):
        """Test complete player evaluation."""
        from tdm import TouchDependencyModel

        tdm = TouchDependencyModel(model_dir=trained_model)
        tdm.load_models()

        # Create test player stats
        test_player = {
            'Player': 'Test Player',
            'FG': 200,
            'FGA': 450,
            'FT': 100,
            'FTA': 120,
            'PTS': 550,
            'MP': 2000,
            '3P': 50,
            '3PA': 150,
            'AST': 100,
            'TOV': 60,
            'Age': 26,
            'Pos': 'G'
        }

        report = tdm.evaluate_player(test_player)

        # Validate report structure
        assert 'tds_score' in report
        assert 'archetype' in report
        assert 'predicted_ts' in report
        assert 'actual_ts' in report
        assert 'scouting_summary' in report
        assert 'gm_recommendations' in report

        # Validate values
        assert 0 <= report['tds_score'] <= 100
        assert report['archetype'] in VALID_ARCHETYPES
        assert 0 < report['actual_ts'] < 1
        assert 0 < report['predicted_ts'] < 1
        assert len(report['scouting_summary']) > 50


class TestInputValidation:
    """Test input validation."""

    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        from tdm.predictor import TouchDependencyModel

        # Create minimal mock
        tdm = TouchDependencyModel()
        tdm._is_loaded = True

        incomplete_stats = {
            'FG': 100,
            'FGA': 250
            # Missing FT, FTA, PTS, MP
        }

        with pytest.raises(ValueError, match="Missing required"):
            tdm._validate_input(incomplete_stats)

    def test_zero_fga(self):
        """Test handling of zero FGA."""
        from tdm.predictor import TouchDependencyModel

        tdm = TouchDependencyModel()
        tdm._is_loaded = True

        stats = {
            'FG': 0, 'FGA': 0, 'FT': 0, 'FTA': 0,
            'PTS': 0, 'MP': 100
        }

        with pytest.raises(ValueError, match="FGA cannot be zero"):
            tdm._validate_input(stats)

    def test_zero_mp(self):
        """Test handling of zero minutes."""
        from tdm.predictor import TouchDependencyModel

        tdm = TouchDependencyModel()
        tdm._is_loaded = True

        stats = {
            'FG': 10, 'FGA': 20, 'FT': 5, 'FTA': 6,
            'PTS': 25, 'MP': 0
        }

        with pytest.raises(ValueError, match="MP cannot be zero"):
            tdm._validate_input(stats)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

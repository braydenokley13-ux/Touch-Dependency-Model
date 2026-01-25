"""Tests for feature engineering."""

import pytest
import numpy as np
import pandas as pd
from tdm.features import FeatureEngineer


class TestFeatureEngineer:
    """Test suite for FeatureEngineer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.engineer = FeatureEngineer()

    def test_compute_ts_percent_basic(self):
        """Test basic TS% calculation."""
        # 100 points on 50 FGA and 20 FTA
        # TS% = 100 / (2 * (50 + 0.44 * 20)) = 100 / 117.6 = 0.850
        ts = self.engineer.compute_ts_percent(
            fg=40, fga=50, ft=20, fta=20, pts=100
        )
        assert abs(ts - 0.850) < 0.01

    def test_compute_ts_percent_zero_attempts(self):
        """Test TS% with zero attempts."""
        ts = self.engineer.compute_ts_percent(
            fg=0, fga=0, ft=0, fta=0, pts=0
        )
        assert ts == 0.0

    def test_compute_ts_percent_no_free_throws(self):
        """Test TS% without free throws."""
        # 100 points on 100 FGA, no FT
        # TS% = 100 / (2 * 100) = 0.500
        ts = self.engineer.compute_ts_percent(
            fg=50, fga=100, ft=0, fta=0, pts=100
        )
        assert abs(ts - 0.500) < 0.001

    def test_compute_usg_percent(self):
        """Test usage percentage calculation."""
        # Player with 500 FGA, 200 FTA, 100 TOV in 2000 MP
        # Team with 5000 FGA, 2000 FTA, 1000 TOV in 20000 MP
        usg = self.engineer.compute_usg_percent(
            fga=500, fta=200, tov=100, mp=2000,
            team_fga=5000, team_fta=2000, team_tov=1000, team_mp=20000
        )
        # Should be around 20% (1/5 of team possessions in 1/10 of time = 50%)
        assert 10 < usg < 100

    def test_compute_usg_percent_zero_mp(self):
        """Test usage with zero minutes."""
        usg = self.engineer.compute_usg_percent(
            fga=100, fta=50, tov=20, mp=0,
            team_fga=1000, team_fta=500, team_tov=200, team_mp=2000
        )
        assert usg == 0.0

    def test_compute_ast_percent(self):
        """Test assist percentage calculation."""
        ast_pct = self.engineer.compute_ast_percent(
            ast=200, mp=2000, team_fg=3000, fg=300, team_mp=20000
        )
        # Should produce a reasonable assist rate
        assert 0 <= ast_pct <= 100

    def test_compute_tov_percent(self):
        """Test turnover percentage calculation."""
        tov_pct = self.engineer.compute_tov_percent(
            tov=50, fga=400, fta=100
        )
        # TOV% = 100 * 50 / (400 + 44 + 50) = 10.1%
        expected = 100 * 50 / (400 + 0.44 * 100 + 50)
        assert abs(tov_pct - expected) < 0.1

    def test_compute_shot_diet_rates(self):
        """Test shot distribution rates."""
        three_rate, two_rate, fta_rate = self.engineer.compute_shot_diet_rates(
            fga=100, three_pa=30, two_pa=70, fta=25
        )
        assert abs(three_rate - 0.30) < 0.001
        assert abs(two_rate - 0.70) < 0.001
        assert abs(fta_rate - 0.25) < 0.001

    def test_compute_shot_diet_rates_zero_fga(self):
        """Test shot diet with zero FGA."""
        three_rate, two_rate, fta_rate = self.engineer.compute_shot_diet_rates(
            fga=0, three_pa=0, two_pa=0, fta=0
        )
        assert three_rate == 0.0
        assert two_rate == 0.0
        assert fta_rate == 0.0

    def test_normalize_position(self):
        """Test position normalization."""
        assert self.engineer._normalize_position('PG') == 'Guard'
        assert self.engineer._normalize_position('SG') == 'Guard'
        assert self.engineer._normalize_position('SF') == 'Forward'
        assert self.engineer._normalize_position('PF') == 'Forward'
        assert self.engineer._normalize_position('C') == 'Center'
        assert self.engineer._normalize_position('G-F') == 'Guard-Forward'

    def test_normalize_position_unknown(self):
        """Test unknown position handling."""
        assert self.engineer._normalize_position('X') == 'Unknown'
        assert self.engineer._normalize_position('') == 'Unknown'
        assert self.engineer._normalize_position(None) == 'Unknown'


class TestFeatureMatrixCreation:
    """Test feature matrix creation."""

    def test_create_feature_matrix_basic(self):
        """Test basic feature matrix creation."""
        # Create sample data
        data = pd.DataFrame({
            'Player': ['Player A', 'Player B'],
            'FG': [200, 300],
            'FGA': [400, 600],
            'FT': [100, 150],
            'FTA': [120, 180],
            'PTS': [550, 800],
            'MP': [2000, 2500],
            '3P': [50, 80],
            '3PA': [130, 200],
            '2P': [150, 220],
            '2PA': [270, 400],
            'AST': [100, 200],
            'TOV': [50, 80],
            'Age': [25, 28],
            'Pos': ['G', 'F'],
            'TS%': [0.55, 0.56],
            'USG%': [22, 26],
            'AST%': [15, 20],
            'TOV%': [10, 11]
        })

        engineer = FeatureEngineer()
        X, y, feature_names = engineer.create_feature_matrix(data)

        assert X.shape[0] == 2  # 2 players
        assert len(feature_names) > 5  # Multiple features
        assert len(y) == 2
        assert all(0 < yi < 1 for yi in y)  # TS% should be between 0 and 1


class TestTransformSinglePlayer:
    """Test single player transformation."""

    def test_transform_requires_fitting(self):
        """Test that transform requires fitted scaler."""
        engineer = FeatureEngineer()

        stats = {
            'FG': 100, 'FGA': 250,
            'FT': 50, 'FTA': 60,
            'MP': 1000
        }

        with pytest.raises(ValueError, match="not fitted"):
            engineer.transform_single_player(stats)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

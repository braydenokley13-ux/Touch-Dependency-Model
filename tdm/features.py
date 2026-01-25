"""
Feature engineering for Touch Dependency Model.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import joblib


class FeatureEngineer:
    """Handles feature computation and transformation for TDM."""

    POSITION_CATEGORIES = ['G', 'F', 'C', 'G-F', 'F-C', 'F-G', 'C-F', 'PG', 'SG', 'SF', 'PF']

    def __init__(self):
        """Initialize FeatureEngineer."""
        self.scaler = StandardScaler()
        self.position_encoder = None
        self.feature_names = []
        self._is_fitted = False

    def compute_ts_percent(self, fg: float, fga: float, ft: float,
                           fta: float, pts: float) -> float:
        """
        Compute True Shooting Percentage.

        TS% = PTS / (2 * (FGA + 0.44 * FTA))

        Args:
            fg: Field goals made
            fga: Field goal attempts
            ft: Free throws made
            fta: Free throw attempts
            pts: Points scored

        Returns:
            True Shooting Percentage (0-1 scale)
        """
        denominator = 2 * (fga + 0.44 * fta)
        if denominator == 0:
            return 0.0
        return pts / denominator

    def compute_usg_percent(self, fga: float, fta: float, tov: float,
                            mp: float, team_fga: float, team_fta: float,
                            team_tov: float, team_mp: float) -> float:
        """
        Compute Usage Percentage.

        USG% = 100 * ((FGA + 0.44 * FTA + TOV) * (Team MP / 5)) /
               (MP * (Team FGA + 0.44 * Team FTA + Team TOV))

        Args:
            fga: Player field goal attempts
            fta: Player free throw attempts
            tov: Player turnovers
            mp: Player minutes played
            team_fga: Team field goal attempts
            team_fta: Team free throw attempts
            team_tov: Team turnovers
            team_mp: Team minutes played

        Returns:
            Usage Percentage (0-100 scale)
        """
        if mp == 0 or team_mp == 0:
            return 0.0

        player_possessions = fga + 0.44 * fta + tov
        team_possessions = team_fga + 0.44 * team_fta + team_tov

        if team_possessions == 0:
            return 0.0

        usg = 100 * (player_possessions * (team_mp / 5)) / (mp * team_possessions)
        return min(usg, 100.0)

    def compute_ast_percent(self, ast: float, mp: float, team_fg: float,
                           fg: float, team_mp: float) -> float:
        """
        Compute Assist Percentage.

        AST% = 100 * AST / (((MP / (Team MP / 5)) * Team FG) - FG)

        Args:
            ast: Player assists
            mp: Player minutes played
            team_fg: Team field goals
            fg: Player field goals
            team_mp: Team minutes played

        Returns:
            Assist Percentage (0-100 scale)
        """
        if mp == 0 or team_mp == 0:
            return 0.0

        teammate_fg = ((mp / (team_mp / 5)) * team_fg) - fg
        if teammate_fg <= 0:
            return 0.0

        ast_pct = 100 * ast / teammate_fg
        return min(ast_pct, 100.0)

    def compute_tov_percent(self, tov: float, fga: float, fta: float) -> float:
        """
        Compute Turnover Percentage (simplified).

        TOV% = 100 * TOV / (FGA + 0.44 * FTA + TOV)

        Args:
            tov: Turnovers
            fga: Field goal attempts
            fta: Free throw attempts

        Returns:
            Turnover Percentage (0-100 scale)
        """
        possessions = fga + 0.44 * fta + tov
        if possessions == 0:
            return 0.0
        return 100 * tov / possessions

    def compute_shot_diet_rates(self, fga: float, three_pa: float,
                                 two_pa: float, fta: float) -> Tuple[float, float, float]:
        """
        Compute shot distribution rates.

        Args:
            fga: Total field goal attempts
            three_pa: Three-point attempts
            two_pa: Two-point attempts
            fta: Free throw attempts

        Returns:
            Tuple of (3PA_rate, 2PA_rate, FTA_rate)
        """
        if fga == 0:
            return 0.0, 0.0, 0.0

        three_pa_rate = three_pa / fga
        two_pa_rate = two_pa / fga
        fta_rate = fta / fga

        return three_pa_rate, two_pa_rate, fta_rate

    def _normalize_position(self, pos: str) -> str:
        """Normalize position string to standard category."""
        if pd.isna(pos) or pos == '':
            return 'Unknown'

        pos = str(pos).upper().strip()

        # Map specific positions to general categories
        pos_map = {
            'PG': 'Guard',
            'SG': 'Guard',
            'G': 'Guard',
            'SF': 'Forward',
            'PF': 'Forward',
            'F': 'Forward',
            'C': 'Center',
            'G-F': 'Guard-Forward',
            'F-G': 'Guard-Forward',
            'F-C': 'Forward-Center',
            'C-F': 'Forward-Center'
        }

        return pos_map.get(pos, 'Unknown')

    def create_feature_matrix(self, df: pd.DataFrame,
                              use_precomputed: bool = True,
                              fit_scaler: bool = True) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Create feature matrix from raw data.

        Args:
            df: DataFrame with player statistics
            use_precomputed: Use precomputed advanced stats if available
            fit_scaler: Whether to fit the scaler (True for training, False for inference)

        Returns:
            Tuple of (X features, y target, feature_names)
        """
        features = pd.DataFrame()

        # Compute or use precomputed TS% (target)
        if use_precomputed and 'TS%' in df.columns:
            y = df['TS%'].values
        else:
            y = df.apply(lambda row: self.compute_ts_percent(
                row['FG'], row['FGA'], row['FT'], row['FTA'], row['PTS']
            ), axis=1).values

        # Usage Rate
        if use_precomputed and 'USG%' in df.columns:
            features['USG%'] = df['USG%'].fillna(df['USG%'].median())
        else:
            features['USG%'] = df.apply(lambda row: self.compute_usg_percent(
                row['FGA'], row['FTA'], row.get('TOV', 0), row['MP'],
                row.get('team_FGA', row['FGA'] * 5),
                row.get('team_FTA', row['FTA'] * 5),
                row.get('team_TOV', row.get('TOV', 0) * 5),
                row.get('team_MP', row['MP'] * 5)
            ), axis=1)

        # Assist Rate
        if use_precomputed and 'AST%' in df.columns:
            features['AST%'] = df['AST%'].fillna(df['AST%'].median())
        else:
            features['AST%'] = df.apply(lambda row: self.compute_ast_percent(
                row['AST'], row['MP'],
                row.get('team_FG', row['FG'] * 5),
                row['FG'],
                row.get('team_MP', row['MP'] * 5)
            ), axis=1)

        # Turnover Rate
        if use_precomputed and 'TOV%' in df.columns:
            features['TOV%'] = df['TOV%'].fillna(df['TOV%'].median())
        elif 'TOV' in df.columns:
            features['TOV%'] = df.apply(lambda row: self.compute_tov_percent(
                row.get('TOV', 0), row['FGA'], row['FTA']
            ), axis=1)
        else:
            features['TOV%'] = 10.0  # Default average

        # Shot diet rates
        features['3PA_rate'] = df['3PA'] / df['FGA'].replace(0, 1)
        features['2PA_rate'] = df['2PA'] / df['FGA'].replace(0, 1)
        features['FTA_rate'] = df['FTA'] / df['FGA'].replace(0, 1)

        # Age
        if 'Age' in df.columns:
            features['Age'] = df['Age'].fillna(df['Age'].median())
        else:
            features['Age'] = 27  # Default

        # Per-game stats (normalized by minutes)
        features['FGA_per_36'] = (df['FGA'] / df['MP'].replace(0, 1)) * 36
        features['AST_per_36'] = (df['AST'] / df['MP'].replace(0, 1)) * 36
        features['PTS_per_36'] = (df['PTS'] / df['MP'].replace(0, 1)) * 36

        # Position encoding
        if 'Pos' in df.columns:
            positions = df['Pos'].apply(self._normalize_position)
            pos_dummies = pd.get_dummies(positions, prefix='Pos')
            features = pd.concat([features, pos_dummies], axis=1)

        # Store feature names
        self.feature_names = features.columns.tolist()

        # Handle missing values
        features = features.fillna(features.median())

        # Remove invalid rows
        valid_mask = ~(np.isnan(y) | np.isinf(y) | (y <= 0) | (y >= 1))
        X = features.values[valid_mask]
        y = y[valid_mask]

        # Scale features
        if fit_scaler:
            X = self.scaler.fit_transform(X)
            self._is_fitted = True
        else:
            if not self._is_fitted:
                raise ValueError("Scaler not fitted. Call with fit_scaler=True first.")
            X = self.scaler.transform(X)

        return X, y, self.feature_names

    def transform_single_player(self, stats: dict) -> np.ndarray:
        """
        Transform single player stats to feature vector.

        Args:
            stats: Dictionary of player statistics

        Returns:
            Scaled feature vector
        """
        if not self._is_fitted:
            raise ValueError("FeatureEngineer not fitted. Load models or train first.")

        features = {}

        # Compute advanced stats
        fga = stats.get('FGA', 0)
        fta = stats.get('FTA', 0)
        tov = stats.get('TOV', 0)
        mp = stats.get('MP', 1)

        # USG%
        if 'USG%' in stats:
            features['USG%'] = stats['USG%']
        else:
            possessions = fga + 0.44 * fta + tov
            # Estimate ~20% as default
            features['USG%'] = min(100, max(0, (possessions / mp) * 48 * 5)) if mp > 0 else 20

        # AST%
        if 'AST%' in stats:
            features['AST%'] = stats['AST%']
        else:
            ast = stats.get('AST', 0)
            features['AST%'] = min(50, max(0, (ast / mp) * 48 * 2.5)) if mp > 0 else 15

        # TOV%
        if 'TOV%' in stats:
            features['TOV%'] = stats['TOV%']
        else:
            possessions = fga + 0.44 * fta + tov
            features['TOV%'] = (tov / possessions * 100) if possessions > 0 else 10

        # Shot diet
        three_pa = stats.get('3PA', 0)
        two_pa = stats.get('2PA', fga - three_pa)
        features['3PA_rate'] = three_pa / fga if fga > 0 else 0
        features['2PA_rate'] = two_pa / fga if fga > 0 else 1
        features['FTA_rate'] = fta / fga if fga > 0 else 0.3

        # Age
        features['Age'] = stats.get('Age', 27)

        # Per-36 stats
        features['FGA_per_36'] = (fga / mp) * 36 if mp > 0 else 10
        features['AST_per_36'] = (stats.get('AST', 0) / mp) * 36 if mp > 0 else 3
        features['PTS_per_36'] = (stats.get('PTS', 0) / mp) * 36 if mp > 0 else 15

        # Position - create all position columns with 0s, set 1 for matching
        pos = stats.get('Pos', 'Unknown')
        norm_pos = self._normalize_position(pos)

        for feat in self.feature_names:
            if feat.startswith('Pos_'):
                pos_cat = feat.replace('Pos_', '')
                features[feat] = 1 if pos_cat == norm_pos else 0

        # Build feature vector in correct order
        feature_vector = []
        for feat_name in self.feature_names:
            if feat_name in features:
                feature_vector.append(features[feat_name])
            else:
                feature_vector.append(0)

        X = np.array(feature_vector).reshape(1, -1)
        return self.scaler.transform(X)

    def save(self, filepath: str) -> None:
        """Save feature engineer state."""
        state = {
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_fitted': self._is_fitted
        }
        joblib.dump(state, filepath)

    def load(self, filepath: str) -> None:
        """Load feature engineer state."""
        state = joblib.load(filepath)
        self.scaler = state['scaler']
        self.feature_names = state['feature_names']
        self._is_fitted = state['is_fitted']

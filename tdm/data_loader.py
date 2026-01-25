"""
Data loading and validation utilities for Touch Dependency Model.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Tuple


class DataLoader:
    """Handles loading, validation, and preprocessing of basketball statistics data."""

    REQUIRED_COLUMNS = [
        'Year', 'Player', 'Pos', 'Age', 'Tm', 'G', 'MP',
        'FG', 'FGA', 'FT', 'FTA', '3P', '3PA', '2P', '2PA',
        'AST', 'TOV', 'PTS'
    ]

    ADVANCED_COLUMNS = ['TS%', 'USG%', 'AST%', 'TOV%', 'PER']

    MIN_MINUTES_THRESHOLD = 500
    MIN_FGA_THRESHOLD = 100

    def __init__(self, data_dir: str = "data"):
        """Initialize DataLoader with data directory path."""
        self.data_dir = Path(data_dir)

    def load_training_data(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """
        Load and preprocess training data from CSV.

        Args:
            filepath: Path to CSV file. If None, uses default Seasons_Stats.csv

        Returns:
            Preprocessed DataFrame ready for feature engineering
        """
        if filepath is None:
            filepath = self.data_dir / "Seasons_Stats.csv"
        else:
            filepath = Path(filepath)

        df = pd.read_csv(filepath, index_col=0)
        df = self._clean_data(df)
        df = self.validate_required_columns(df)
        df = self.filter_valid_seasons(df)
        df = self.compute_team_aggregates(df)

        return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean raw data: handle missing values, fix types."""
        # Drop rows with critical missing values
        critical_cols = ['Player', 'FG', 'FGA', 'FT', 'FTA', 'MP', 'PTS']
        existing_critical = [c for c in critical_cols if c in df.columns]
        df = df.dropna(subset=existing_critical)

        # Fill missing optional columns with 0
        optional_zero_cols = ['3P', '3PA', 'TOV', 'AST', 'GS']
        for col in optional_zero_cols:
            if col in df.columns:
                df[col] = df[col].fillna(0)

        # Convert numeric columns
        numeric_cols = ['FG', 'FGA', 'FT', 'FTA', '3P', '3PA', '2P', '2PA',
                       'MP', 'G', 'AST', 'TOV', 'PTS', 'Age']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Remove duplicate rows (player traded mid-season appears multiple times)
        # Keep TOT row if exists, otherwise keep first entry
        df = df.sort_values(['Year', 'Player', 'Tm'])
        df['is_tot'] = df['Tm'] == 'TOT'
        df = df.sort_values(['Year', 'Player', 'is_tot'], ascending=[True, True, False])
        df = df.drop_duplicates(subset=['Year', 'Player'], keep='first')
        df = df.drop(columns=['is_tot'])

        return df.reset_index(drop=True)

    def validate_required_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate that required columns exist."""
        missing = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return df

    def filter_valid_seasons(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter to valid seasons based on minutes and shot attempts.

        Filters:
        - Minimum minutes played (default 500)
        - Minimum field goal attempts (default 100)
        - Valid age (18-45)
        """
        df = df[df['MP'] >= self.MIN_MINUTES_THRESHOLD].copy()
        df = df[df['FGA'] >= self.MIN_FGA_THRESHOLD].copy()

        if 'Age' in df.columns:
            df = df[(df['Age'] >= 18) & (df['Age'] <= 45)]

        return df.reset_index(drop=True)

    def compute_team_aggregates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute team-level aggregates needed for certain advanced stats.

        Adds columns:
        - team_FG: Team field goals
        - team_FGA: Team field goal attempts
        - team_MP: Team minutes played
        - team_AST: Team assists
        """
        # Group by year and team to get team totals
        team_stats = df.groupby(['Year', 'Tm']).agg({
            'FG': 'sum',
            'FGA': 'sum',
            'MP': 'sum',
            'AST': 'sum',
            'FT': 'sum',
            'FTA': 'sum',
            'TOV': 'sum',
            'PTS': 'sum'
        }).reset_index()

        team_stats.columns = ['Year', 'Tm', 'team_FG', 'team_FGA', 'team_MP',
                             'team_AST', 'team_FT', 'team_FTA', 'team_TOV', 'team_PTS']

        # Merge back to original dataframe
        df = df.merge(team_stats, on=['Year', 'Tm'], how='left')

        # Fill missing team stats (for players on multiple teams)
        for col in ['team_FG', 'team_FGA', 'team_MP', 'team_AST']:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mean())

        return df

    def load_player_info(self, filepath: Optional[str] = None) -> pd.DataFrame:
        """Load player biographical information."""
        if filepath is None:
            filepath = self.data_dir / "Players.csv"
        return pd.read_csv(filepath)

    def get_player_seasons(self, player_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Get all seasons for a specific player."""
        return df[df['Player'].str.contains(player_name, case=False, na=False)]

    def split_train_test(self, df: pd.DataFrame, test_years: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split data into train/test by year.

        Args:
            df: Full dataset
            test_years: Number of most recent years to use for testing

        Returns:
            Tuple of (train_df, test_df)
        """
        max_year = df['Year'].max()
        test_cutoff = max_year - test_years

        train_df = df[df['Year'] <= test_cutoff].copy()
        test_df = df[df['Year'] > test_cutoff].copy()

        return train_df, test_df

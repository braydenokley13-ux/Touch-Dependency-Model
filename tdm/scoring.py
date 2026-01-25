"""
Touch Dependency Score (TDS) calculation engine.
"""

import numpy as np
from scipy import stats
from typing import Optional, Tuple, List
import joblib


class TDSCalculator:
    """
    Calculates Touch Dependency Score from model residuals.

    TDS measures how well a player maintains efficiency relative to
    expected performance based on their touch load. Higher TDS indicates
    the player can scale to different roles without efficiency loss.

    Scale: 0-100
    - 0-30: Highly Touch Dependent (needs specific role)
    - 30-40: Touch Dependent
    - 40-50: Slightly Dependent
    - 50-60: Neutral
    - 60-70: Slightly Scalable
    - 70-80: Touch Independent
    - 80-100: Highly Scalable (plug-and-play value)
    """

    INTERPRETATION = {
        (0, 30): ("Highly Touch Dependent", "Needs specific role and high usage to be effective"),
        (30, 40): ("Touch Dependent", "Performs best with consistent offensive role"),
        (40, 50): ("Slightly Dependent", "Minor efficiency drop in reduced roles"),
        (50, 60): ("Neutral", "Efficiency relatively stable across roles"),
        (60, 70): ("Slightly Scalable", "Maintains or improves efficiency in varied roles"),
        (70, 80): ("Touch Independent", "Efficient regardless of role or usage"),
        (80, 100): ("Highly Scalable", "Elite role flexibility, plug-and-play value")
    }

    def __init__(self):
        """Initialize TDSCalculator."""
        self.calibration_residuals: Optional[np.ndarray] = None
        self.residual_mean: float = 0.0
        self.residual_std: float = 1.0
        self._is_calibrated = False

    def calibrate(self, training_residuals: np.ndarray) -> 'TDSCalculator':
        """
        Calibrate the TDS calculator using training data residuals.

        Args:
            training_residuals: Array of residuals from training data

        Returns:
            self
        """
        # Remove outliers (beyond 3 std)
        residuals = training_residuals.copy()
        mean = np.mean(residuals)
        std = np.std(residuals)

        mask = np.abs(residuals - mean) <= 3 * std
        self.calibration_residuals = residuals[mask]

        self.residual_mean = np.mean(self.calibration_residuals)
        self.residual_std = np.std(self.calibration_residuals)

        self._is_calibrated = True
        return self

    def compute_tds(self, residual: float) -> float:
        """
        Compute Touch Dependency Score from a single residual.

        Args:
            residual: Player's residual (actual_TS - predicted_TS)

        Returns:
            TDS score (0-100 scale)
        """
        if not self._is_calibrated:
            raise ValueError("Calculator not calibrated. Call calibrate() first.")

        # Use empirical percentile from calibration data
        percentile = stats.percentileofscore(
            self.calibration_residuals, residual, kind='mean'
        )

        # Clamp to 0-100
        tds = np.clip(percentile, 0, 100)

        return float(tds)

    def compute_tds_batch(self, residuals: np.ndarray) -> np.ndarray:
        """
        Compute TDS for multiple players.

        Args:
            residuals: Array of residuals

        Returns:
            Array of TDS scores
        """
        return np.array([self.compute_tds(r) for r in residuals])

    def interpret_tds(self, score: float) -> Tuple[str, str]:
        """
        Get interpretation of TDS score.

        Args:
            score: TDS score (0-100)

        Returns:
            Tuple of (category_name, description)
        """
        for (low, high), (name, desc) in self.INTERPRETATION.items():
            if low <= score < high:
                return name, desc

        # Handle edge case of score = 100
        if score >= 100:
            return "Highly Scalable", "Elite role flexibility, plug-and-play value"

        return "Unknown", "Score out of expected range"

    def get_percentile_thresholds(self) -> dict:
        """
        Get residual values at key percentile thresholds.

        Useful for understanding the calibration distribution.

        Returns:
            Dictionary of percentile -> residual value
        """
        if not self._is_calibrated:
            raise ValueError("Calculator not calibrated.")

        percentiles = [10, 25, 50, 75, 90, 95, 99]
        return {
            p: np.percentile(self.calibration_residuals, p)
            for p in percentiles
        }

    def get_distribution_stats(self) -> dict:
        """
        Get statistics about the calibration distribution.

        Returns:
            Dictionary with distribution statistics
        """
        if not self._is_calibrated:
            raise ValueError("Calculator not calibrated.")

        return {
            'mean': self.residual_mean,
            'std': self.residual_std,
            'min': np.min(self.calibration_residuals),
            'max': np.max(self.calibration_residuals),
            'median': np.median(self.calibration_residuals),
            'n_samples': len(self.calibration_residuals),
            'skewness': stats.skew(self.calibration_residuals),
            'kurtosis': stats.kurtosis(self.calibration_residuals)
        }

    def z_score_method(self, residual: float) -> float:
        """
        Alternative TDS calculation using z-score normalization.

        Converts residual to z-score, then maps to 0-100 scale
        using cumulative normal distribution.

        Args:
            residual: Player's residual

        Returns:
            TDS score (0-100)
        """
        if self.residual_std == 0:
            return 50.0

        z_score = (residual - self.residual_mean) / self.residual_std
        percentile = stats.norm.cdf(z_score) * 100

        return float(np.clip(percentile, 0, 100))

    def compare_to_population(self, residual: float) -> dict:
        """
        Compare a residual to the calibration population.

        Args:
            residual: Player's residual

        Returns:
            Comparison statistics
        """
        if not self._is_calibrated:
            raise ValueError("Calculator not calibrated.")

        tds = self.compute_tds(residual)
        z_score = (residual - self.residual_mean) / self.residual_std

        better_than = np.sum(self.calibration_residuals < residual)
        total = len(self.calibration_residuals)

        return {
            'tds': tds,
            'z_score': z_score,
            'better_than_pct': (better_than / total) * 100,
            'residual': residual,
            'vs_mean': residual - self.residual_mean
        }

    def save(self, filepath: str) -> None:
        """Save calculator state."""
        state = {
            'calibration_residuals': self.calibration_residuals,
            'residual_mean': self.residual_mean,
            'residual_std': self.residual_std,
            'is_calibrated': self._is_calibrated
        }
        joblib.dump(state, filepath)

    def load(self, filepath: str) -> None:
        """Load calculator state."""
        state = joblib.load(filepath)
        self.calibration_residuals = state['calibration_residuals']
        self.residual_mean = state['residual_mean']
        self.residual_std = state['residual_std']
        self._is_calibrated = state['is_calibrated']

    @property
    def is_calibrated(self) -> bool:
        """Check if calculator is calibrated."""
        return self._is_calibrated

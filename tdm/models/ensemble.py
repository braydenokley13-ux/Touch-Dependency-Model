"""
Ensemble model combining linear and XGBoost predictions.
"""

import numpy as np
from typing import Optional, Dict, Tuple, List
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_predict
import joblib

from .linear_model import LinearTSModel
from .xgboost_model import XGBoostTSModel


class EnsembleTSModel:
    """
    Ensemble model combining linear regression and XGBoost.

    Uses weighted averaging or learned stacking to combine predictions
    from both models for optimal performance.
    """

    def __init__(self, linear_model: Optional[LinearTSModel] = None,
                 xgb_model: Optional[XGBoostTSModel] = None,
                 weights: Optional[Tuple[float, float]] = None):
        """
        Initialize EnsembleTSModel.

        Args:
            linear_model: Pre-trained LinearTSModel
            xgb_model: Pre-trained XGBoostTSModel
            weights: Tuple of (linear_weight, xgb_weight). Default (0.3, 0.7)
        """
        self.linear_model = linear_model or LinearTSModel()
        self.xgb_model = xgb_model or XGBoostTSModel()
        self.weights = weights or (0.3, 0.7)
        self.stacker = LinearRegression()
        self._use_stacking = False
        self._is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray,
            feature_names: Optional[List[str]] = None,
            use_stacking: bool = False,
            tune_xgb: bool = False) -> 'EnsembleTSModel':
        """
        Fit both models and optionally learn stacking weights.

        Args:
            X: Feature matrix
            y: Target values
            feature_names: Names of features
            use_stacking: If True, learn optimal weights via stacking
            tune_xgb: If True, tune XGBoost hyperparameters

        Returns:
            self
        """
        # Fit individual models
        self.linear_model.fit(X, y, feature_names)
        self.xgb_model.fit(X, y, feature_names, tune_hyperparams=tune_xgb)

        if use_stacking:
            self._fit_stacker(X, y)
            self._use_stacking = True

        self._is_fitted = True
        return self

    def _fit_stacker(self, X: np.ndarray, y: np.ndarray) -> None:
        """Fit stacking meta-model using out-of-fold predictions."""
        # Get OOF predictions from both models
        linear_oof = self.linear_model.get_cv_predictions(X, y, cv=5)
        xgb_oof = self.xgb_model.get_cv_predictions(X, y, cv=5)

        # Stack predictions
        stacked_features = np.column_stack([linear_oof, xgb_oof])

        # Fit meta-model
        self.stacker.fit(stacked_features, y)

        # Update weights from stacker coefficients
        total = sum(abs(c) for c in self.stacker.coef_)
        if total > 0:
            self.weights = tuple(abs(c) / total for c in self.stacker.coef_)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Generate ensemble predictions.

        Args:
            X: Feature matrix

        Returns:
            Ensemble predicted TS% values
        """
        if not self._is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        linear_pred = self.linear_model.predict(X)
        xgb_pred = self.xgb_model.predict(X)

        if self._use_stacking:
            stacked = np.column_stack([linear_pred, xgb_pred])
            return self.stacker.predict(stacked)
        else:
            return self.combine_predictions(linear_pred, xgb_pred)

    def combine_predictions(self, linear_pred: np.ndarray,
                           xgb_pred: np.ndarray) -> np.ndarray:
        """
        Combine predictions using weighted average.

        Args:
            linear_pred: Linear model predictions
            xgb_pred: XGBoost predictions

        Returns:
            Weighted average predictions
        """
        w_linear, w_xgb = self.weights
        return w_linear * linear_pred + w_xgb * xgb_pred

    def compute_final_residuals(self, X: np.ndarray, y: np.ndarray) -> np.ndarray:
        """
        Compute residuals from ensemble predictions.

        Args:
            X: Feature matrix
            y: Actual TS% values

        Returns:
            Residuals (actual - predicted)
        """
        predictions = self.predict(X)
        return y - predictions

    def get_model_contributions(self, X: np.ndarray) -> Dict[str, np.ndarray]:
        """
        Get individual model predictions for analysis.

        Args:
            X: Feature matrix

        Returns:
            Dictionary with predictions from each model and ensemble
        """
        return {
            'linear': self.linear_model.predict(X),
            'xgboost': self.xgb_model.predict(X),
            'ensemble': self.predict(X)
        }

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Dict[str, float]]:
        """
        Evaluate all models.

        Args:
            X: Feature matrix
            y: True values

        Returns:
            Dictionary with metrics for each model
        """
        from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

        predictions = self.get_model_contributions(X)
        results = {}

        for name, preds in predictions.items():
            rmse = np.sqrt(mean_squared_error(y, preds))
            r2 = r2_score(y, preds)
            mae = mean_absolute_error(y, preds)

            results[name] = {
                'rmse': rmse,
                'r2': r2,
                'mae': mae
            }

        return results

    def save(self, filepath: str) -> None:
        """Save ensemble model."""
        state = {
            'weights': self.weights,
            'stacker': self.stacker,
            'use_stacking': self._use_stacking,
            'is_fitted': self._is_fitted
        }
        joblib.dump(state, filepath)

    def load(self, filepath: str) -> None:
        """Load ensemble weights."""
        state = joblib.load(filepath)
        self.weights = state['weights']
        self.stacker = state['stacker']
        self._use_stacking = state['use_stacking']
        self._is_fitted = state['is_fitted']

    def save_all(self, model_dir: str) -> None:
        """Save all models to directory."""
        from pathlib import Path
        model_path = Path(model_dir)
        model_path.mkdir(parents=True, exist_ok=True)

        self.linear_model.save(model_path / 'linear_model.pkl')
        self.xgb_model.save(model_path / 'xgboost_model.pkl')
        self.save(model_path / 'ensemble_weights.pkl')

    def load_all(self, model_dir: str) -> None:
        """Load all models from directory."""
        from pathlib import Path
        model_path = Path(model_dir)

        self.linear_model.load(model_path / 'linear_model.pkl')
        self.xgb_model.load(model_path / 'xgboost_model.pkl')
        self.load(model_path / 'ensemble_weights.pkl')
        self._is_fitted = True

    @property
    def is_fitted(self) -> bool:
        """Check if model is fitted."""
        return self._is_fitted

"""
Linear regression model for True Shooting prediction.
"""

import numpy as np
from typing import Optional, Dict, List
from sklearn.linear_model import RidgeCV
from sklearn.model_selection import cross_val_score, cross_val_predict
import joblib


class LinearTSModel:
    """
    Linear regression model for predicting True Shooting Percentage.

    Uses Ridge regression with cross-validation for regularization tuning.
    Provides interpretable coefficients showing touch dependency drivers.
    """

    def __init__(self, alphas: Optional[List[float]] = None):
        """
        Initialize LinearTSModel.

        Args:
            alphas: List of regularization strengths to try. Default uses
                   logspace from 0.001 to 100.
        """
        if alphas is None:
            alphas = np.logspace(-3, 2, 50).tolist()

        self.model = RidgeCV(alphas=alphas, cv=5, scoring='neg_mean_squared_error')
        self.feature_names: List[str] = []
        self._is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray,
            feature_names: Optional[List[str]] = None) -> 'LinearTSModel':
        """
        Fit the linear model.

        Args:
            X: Feature matrix (n_samples, n_features)
            y: Target values (True Shooting %)
            feature_names: Names of features for interpretability

        Returns:
            self
        """
        self.model.fit(X, y)
        self._is_fitted = True

        if feature_names is not None:
            self.feature_names = feature_names
        else:
            self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]

        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict True Shooting Percentage.

        Args:
            X: Feature matrix

        Returns:
            Predicted TS% values
        """
        if not self._is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")
        return self.model.predict(X)

    def get_coefficients(self) -> Dict[str, float]:
        """
        Get model coefficients with feature names.

        Returns:
            Dictionary mapping feature names to coefficients
        """
        if not self._is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        coefficients = dict(zip(self.feature_names, self.model.coef_))
        coefficients['intercept'] = self.model.intercept_

        # Sort by absolute coefficient value
        sorted_coefs = dict(sorted(
            coefficients.items(),
            key=lambda x: abs(x[1]) if x[0] != 'intercept' else 0,
            reverse=True
        ))

        return sorted_coefs

    def calculate_residuals(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """
        Calculate residuals (actual - predicted).

        Positive residuals = player outperforming expected TS%
        Negative residuals = player underperforming expected TS%

        Args:
            y_true: Actual TS% values
            y_pred: Predicted TS% values

        Returns:
            Array of residuals
        """
        return y_true - y_pred

    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv: int = 5) -> Dict[str, float]:
        """
        Perform cross-validation and return metrics.

        Args:
            X: Feature matrix
            y: Target values
            cv: Number of cross-validation folds

        Returns:
            Dictionary with CV metrics (mean and std of RMSE, R2)
        """
        # RMSE
        mse_scores = -cross_val_score(
            self.model, X, y, cv=cv, scoring='neg_mean_squared_error'
        )
        rmse_scores = np.sqrt(mse_scores)

        # R2
        r2_scores = cross_val_score(self.model, X, y, cv=cv, scoring='r2')

        return {
            'rmse_mean': rmse_scores.mean(),
            'rmse_std': rmse_scores.std(),
            'r2_mean': r2_scores.mean(),
            'r2_std': r2_scores.std(),
            'best_alpha': self.model.alpha_ if self._is_fitted else None
        }

    def get_cv_predictions(self, X: np.ndarray, y: np.ndarray, cv: int = 5) -> np.ndarray:
        """
        Get cross-validated predictions (out-of-fold).

        Args:
            X: Feature matrix
            y: Target values
            cv: Number of folds

        Returns:
            Out-of-fold predictions
        """
        return cross_val_predict(self.model, X, y, cv=cv)

    def save(self, filepath: str) -> None:
        """Save model to disk."""
        state = {
            'model': self.model,
            'feature_names': self.feature_names,
            'is_fitted': self._is_fitted
        }
        joblib.dump(state, filepath)

    def load(self, filepath: str) -> None:
        """Load model from disk."""
        state = joblib.load(filepath)
        self.model = state['model']
        self.feature_names = state['feature_names']
        self._is_fitted = state['is_fitted']

    @property
    def is_fitted(self) -> bool:
        """Check if model is fitted."""
        return self._is_fitted

"""
XGBoost model for True Shooting prediction.
"""

import numpy as np
from typing import Optional, Dict, List, Tuple
from sklearn.model_selection import cross_val_score, cross_val_predict, GridSearchCV
import joblib

try:
    import xgboost as xgb
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False


class XGBoostTSModel:
    """
    XGBoost gradient boosting model for predicting True Shooting Percentage.

    Captures nonlinear relationships between features and efficiency.
    """

    DEFAULT_PARAMS = {
        'objective': 'reg:squarederror',
        'max_depth': 4,
        'learning_rate': 0.05,
        'n_estimators': 200,
        'min_child_weight': 5,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'random_state': 42,
        'n_jobs': -1
    }

    TUNING_GRID = {
        'max_depth': [3, 4, 5, 6],
        'learning_rate': [0.01, 0.05, 0.1],
        'n_estimators': [100, 200, 300],
        'min_child_weight': [3, 5, 7],
        'subsample': [0.7, 0.8, 0.9]
    }

    def __init__(self, params: Optional[Dict] = None):
        """
        Initialize XGBoostTSModel.

        Args:
            params: XGBoost parameters. Uses defaults if not specified.
        """
        if not HAS_XGBOOST:
            raise ImportError("xgboost not installed. Run: pip install xgboost")

        self.params = {**self.DEFAULT_PARAMS, **(params or {})}
        self.model = xgb.XGBRegressor(**self.params)
        self.feature_names: List[str] = []
        self._is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray,
            feature_names: Optional[List[str]] = None,
            tune_hyperparams: bool = False,
            eval_set: Optional[Tuple[np.ndarray, np.ndarray]] = None) -> 'XGBoostTSModel':
        """
        Fit the XGBoost model.

        Args:
            X: Feature matrix
            y: Target values
            feature_names: Names of features
            tune_hyperparams: Whether to perform hyperparameter tuning
            eval_set: Optional (X_val, y_val) for early stopping

        Returns:
            self
        """
        if feature_names is not None:
            self.feature_names = feature_names
        else:
            self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]

        if tune_hyperparams:
            self._tune_hyperparameters(X, y)

        if eval_set is not None:
            self.model.fit(
                X, y,
                eval_set=[eval_set],
                verbose=False
            )
        else:
            self.model.fit(X, y)

        self._is_fitted = True
        return self

    def _tune_hyperparameters(self, X: np.ndarray, y: np.ndarray) -> None:
        """Tune hyperparameters using grid search."""
        # Use smaller grid for faster tuning
        small_grid = {
            'max_depth': [3, 5],
            'learning_rate': [0.05, 0.1],
            'n_estimators': [100, 200],
            'min_child_weight': [3, 5]
        }

        base_model = xgb.XGBRegressor(
            objective='reg:squarederror',
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1
        )

        grid_search = GridSearchCV(
            base_model,
            small_grid,
            cv=3,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )

        grid_search.fit(X, y)

        # Update model with best parameters
        self.params.update(grid_search.best_params_)
        self.model = xgb.XGBRegressor(**self.params)

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

    def get_feature_importance(self, importance_type: str = 'gain') -> Dict[str, float]:
        """
        Get feature importance scores.

        Args:
            importance_type: Type of importance ('gain', 'weight', 'cover')

        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self._is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        importance = self.model.feature_importances_
        importance_dict = dict(zip(self.feature_names, importance))

        # Sort by importance
        sorted_importance = dict(sorted(
            importance_dict.items(),
            key=lambda x: x[1],
            reverse=True
        ))

        return sorted_importance

    def cross_validate(self, X: np.ndarray, y: np.ndarray, cv: int = 5) -> Dict[str, float]:
        """
        Perform cross-validation.

        Args:
            X: Feature matrix
            y: Target values
            cv: Number of folds

        Returns:
            Dictionary with CV metrics
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
            'r2_std': r2_scores.std()
        }

    def get_cv_predictions(self, X: np.ndarray, y: np.ndarray, cv: int = 5) -> np.ndarray:
        """Get cross-validated predictions."""
        return cross_val_predict(self.model, X, y, cv=cv)

    def save(self, filepath: str) -> None:
        """Save model to disk."""
        state = {
            'model': self.model,
            'params': self.params,
            'feature_names': self.feature_names,
            'is_fitted': self._is_fitted
        }
        joblib.dump(state, filepath)

    def load(self, filepath: str) -> None:
        """Load model from disk."""
        state = joblib.load(filepath)
        self.model = state['model']
        self.params = state['params']
        self.feature_names = state['feature_names']
        self._is_fitted = state['is_fitted']

    @property
    def is_fitted(self) -> bool:
        """Check if model is fitted."""
        return self._is_fitted

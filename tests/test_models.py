"""Tests for model classes."""

import pytest
import numpy as np
from tdm.models import LinearTSModel, XGBoostTSModel, EnsembleTSModel


class TestLinearTSModel:
    """Test suite for LinearTSModel."""

    def setup_method(self):
        """Set up test fixtures."""
        np.random.seed(42)
        self.X = np.random.randn(100, 5)
        self.y = 0.5 + 0.1 * self.X[:, 0] + 0.05 * self.X[:, 1] + np.random.randn(100) * 0.02

    def test_fit_predict(self):
        """Test basic fit and predict."""
        model = LinearTSModel()
        model.fit(self.X, self.y)

        predictions = model.predict(self.X)

        assert len(predictions) == len(self.y)
        assert model.is_fitted

    def test_get_coefficients(self):
        """Test coefficient extraction."""
        model = LinearTSModel()
        model.fit(self.X, self.y, feature_names=['f1', 'f2', 'f3', 'f4', 'f5'])

        coefs = model.get_coefficients()

        assert 'f1' in coefs
        assert 'intercept' in coefs
        assert len(coefs) == 6  # 5 features + intercept

    def test_calculate_residuals(self):
        """Test residual calculation."""
        model = LinearTSModel()
        model.fit(self.X, self.y)

        predictions = model.predict(self.X)
        residuals = model.calculate_residuals(self.y, predictions)

        assert len(residuals) == len(self.y)
        # Mean residual should be close to 0 for training data
        assert abs(np.mean(residuals)) < 0.1

    def test_cross_validate(self):
        """Test cross-validation."""
        model = LinearTSModel()
        model.fit(self.X, self.y)

        cv_results = model.cross_validate(self.X, self.y, cv=3)

        assert 'rmse_mean' in cv_results
        assert 'r2_mean' in cv_results
        assert cv_results['rmse_mean'] >= 0
        assert cv_results['r2_mean'] <= 1

    def test_predict_before_fit_raises(self):
        """Test that predict before fit raises error."""
        model = LinearTSModel()

        with pytest.raises(ValueError, match="not fitted"):
            model.predict(self.X)


class TestXGBoostTSModel:
    """Test suite for XGBoostTSModel."""

    def setup_method(self):
        """Set up test fixtures."""
        np.random.seed(42)
        self.X = np.random.randn(100, 5)
        self.y = 0.5 + 0.1 * self.X[:, 0] ** 2 + np.random.randn(100) * 0.02

    def test_fit_predict(self):
        """Test basic fit and predict."""
        model = XGBoostTSModel()
        model.fit(self.X, self.y)

        predictions = model.predict(self.X)

        assert len(predictions) == len(self.y)
        assert model.is_fitted

    def test_get_feature_importance(self):
        """Test feature importance extraction."""
        model = XGBoostTSModel()
        model.fit(self.X, self.y, feature_names=['f1', 'f2', 'f3', 'f4', 'f5'])

        importance = model.get_feature_importance()

        assert len(importance) == 5
        assert all(v >= 0 for v in importance.values())

    def test_cross_validate(self):
        """Test cross-validation."""
        model = XGBoostTSModel()
        model.fit(self.X, self.y)

        cv_results = model.cross_validate(self.X, self.y, cv=3)

        assert 'rmse_mean' in cv_results
        assert 'r2_mean' in cv_results


class TestEnsembleTSModel:
    """Test suite for EnsembleTSModel."""

    def setup_method(self):
        """Set up test fixtures."""
        np.random.seed(42)
        self.X = np.random.randn(100, 5)
        self.y = 0.5 + 0.1 * self.X[:, 0] + np.random.randn(100) * 0.02

    def test_fit_predict(self):
        """Test basic ensemble fit and predict."""
        ensemble = EnsembleTSModel()
        ensemble.fit(self.X, self.y)

        predictions = ensemble.predict(self.X)

        assert len(predictions) == len(self.y)
        assert ensemble.is_fitted

    def test_combine_predictions(self):
        """Test prediction combination."""
        ensemble = EnsembleTSModel(weights=(0.3, 0.7))

        linear_pred = np.array([0.50, 0.55, 0.60])
        xgb_pred = np.array([0.52, 0.53, 0.58])

        combined = ensemble.combine_predictions(linear_pred, xgb_pred)

        # Expected: 0.3 * linear + 0.7 * xgb
        expected = 0.3 * linear_pred + 0.7 * xgb_pred
        np.testing.assert_array_almost_equal(combined, expected)

    def test_compute_residuals(self):
        """Test residual computation."""
        ensemble = EnsembleTSModel()
        ensemble.fit(self.X, self.y)

        residuals = ensemble.compute_final_residuals(self.X, self.y)

        assert len(residuals) == len(self.y)
        # Mean should be close to 0
        assert abs(np.mean(residuals)) < 0.1

    def test_get_model_contributions(self):
        """Test getting individual model predictions."""
        ensemble = EnsembleTSModel()
        ensemble.fit(self.X, self.y)

        contributions = ensemble.get_model_contributions(self.X)

        assert 'linear' in contributions
        assert 'xgboost' in contributions
        assert 'ensemble' in contributions
        assert len(contributions['linear']) == len(self.y)

    def test_evaluate(self):
        """Test model evaluation."""
        ensemble = EnsembleTSModel()
        ensemble.fit(self.X, self.y)

        metrics = ensemble.evaluate(self.X, self.y)

        assert 'linear' in metrics
        assert 'xgboost' in metrics
        assert 'ensemble' in metrics

        for model_metrics in metrics.values():
            assert 'rmse' in model_metrics
            assert 'r2' in model_metrics
            assert 'mae' in model_metrics


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

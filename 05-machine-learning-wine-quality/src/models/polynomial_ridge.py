"""Polynomial Ridge regression submitted with the linear-model work."""

from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

from src.feature_engineering import SelectiveLog1p


ALPHAS = [0.0001, 0.001, 0.01, 0.1, 1, 10, 100]


def build_model():
    """Build the submitted degree-two setup as a leakage-safe pipeline."""
    return Pipeline([
        ("log", SelectiveLog1p(enabled=True)),
        ("poly", PolynomialFeatures(degree=2, include_bias=False)),
        ("scaler", StandardScaler()),
        ("model", Ridge(alpha=1)),
    ])


def parameter_grid():
    """Compare the submitted degrees/alphas and optional log transform."""
    return {
        "log__enabled": [False, True],
        "poly__degree": [1, 2, 3, 4],
        "model__alpha": ALPHAS,
    }

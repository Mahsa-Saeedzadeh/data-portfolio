"""Bayesian ridge regression model."""

from sklearn.linear_model import BayesianRidge

from src.preprocessing import make_scaled_pipeline


def build_model():
    """Scale all inputs before fitting Bayesian ridge regression."""
    return make_scaled_pipeline(BayesianRidge())


def parameter_grid():
    """Try a few coherent Bayesian prior-strength combinations."""
    return [
        {
            "model__alpha_1": [1e-7],
            "model__alpha_2": [1e-7],
            "model__lambda_1": [1e-7],
            "model__lambda_2": [1e-7],
        },
        {
            "model__alpha_1": [1e-6],
            "model__alpha_2": [1e-6],
            "model__lambda_1": [1e-6],
            "model__lambda_2": [1e-6],
        },
        {
            "model__alpha_1": [1e-5],
            "model__alpha_2": [1e-5],
            "model__lambda_1": [1e-5],
            "model__lambda_2": [1e-5],
        },
        {
            "model__alpha_1": [1e-5],
            "model__alpha_2": [1e-5],
            "model__lambda_1": [1e-6],
            "model__lambda_2": [1e-6],
        },
        {
            "model__alpha_1": [1e-6],
            "model__alpha_2": [1e-6],
            "model__lambda_1": [1e-5],
            "model__lambda_2": [1e-5],
        },
    ]

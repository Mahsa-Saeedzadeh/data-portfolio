"""Simple reference model used before comparing real algorithms."""

from sklearn.dummy import DummyRegressor


def build_model():
    """Always predict the average quality of the current training fold."""
    return DummyRegressor(strategy="mean")


def parameter_grid():
    """Compare the two useful constant-prediction references."""
    return {"strategy": ["mean", "median"]}

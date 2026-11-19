"""Ridge regression model submitted by the linear-model group."""

from sklearn.linear_model import Ridge

from src.preprocessing import make_scaled_pipeline


def build_model():
    """Scale the inputs and use the latest submitted Ridge alpha."""
    return make_scaled_pipeline(Ridge(alpha=0.001))


def parameter_grid():
    """Return the complete alpha series submitted by the linear group."""
    return {"model__alpha": [0.0001, 0.001, 0.01, 0.1, 1, 10, 100]}

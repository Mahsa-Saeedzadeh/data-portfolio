"""Linear regression model."""

from sklearn.linear_model import LinearRegression

from src.preprocessing import make_scaled_pipeline


def build_model():
    """Scale all inputs before fitting ordinary linear regression."""
    return make_scaled_pipeline(LinearRegression())


def parameter_grid():
    """Check the few meaningful built-in linear-regression switches."""
    return {
        "model__fit_intercept": [True, False],
        "model__positive": [False, True],
    }

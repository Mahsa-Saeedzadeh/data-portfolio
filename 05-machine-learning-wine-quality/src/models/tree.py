"""Decision-tree regression model."""

from sklearn.tree import DecisionTreeRegressor


def build_model():
    """Return a small reproducible tree for the first comparison."""
    return DecisionTreeRegressor(
        max_depth=5,
        min_samples_leaf=5,
        random_state=42,
    )


def parameter_grid():
    """Test a small range from simple trees to the team's unrestricted tree."""
    return [
        {
            "max_depth": [3, 5, 8, None],
            "min_samples_split": [2, 10],
            "min_samples_leaf": [1, 5, 10],
        },
        {
            # Exact additional configuration from the newer team submission.
            "max_depth": [5],
            "min_samples_split": [15],
            "min_samples_leaf": [6],
        },
    ]

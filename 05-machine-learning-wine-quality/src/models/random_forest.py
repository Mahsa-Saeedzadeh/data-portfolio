"""Random-forest regression model submitted by the tree-model group."""

from sklearn.ensemble import RandomForestRegressor


def build_model():
    """Return the team's submitted 100-tree random forest unchanged."""
    return RandomForestRegressor(
        n_estimators=100,
        random_state=42,
    )


def parameter_grid():
    """Keep 100 trees in the search and test a few complexity controls."""
    return {
        "n_estimators": [100, 200],
        "max_depth": [None, 10],
        "min_samples_leaf": [1, 3],
        "max_features": [1.0, "sqrt"],
    }

"""K-nearest-neighbours regression model."""

from sklearn.neighbors import KNeighborsRegressor

from src.preprocessing import make_scaled_pipeline


def build_model():
    """Scale the inputs and use the team's submitted five-neighbour model."""
    return make_scaled_pipeline(KNeighborsRegressor(n_neighbors=5))


def parameter_grid():
    """Search common neighbour counts, weights, and distance measures."""
    return {
        "model__n_neighbors": [3, 5, 7, 9, 11, 15],
        "model__weights": ["uniform", "distance"],
        "model__p": [1, 2],
    }

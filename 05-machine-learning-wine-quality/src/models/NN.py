"""Neural-network regression model."""

from sklearn.compose import TransformedTargetRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

from src.preprocessing import make_scaled_pipeline


def build_model():
    """Scale the inputs and target before fitting the tuned network."""
    # Two layers captured more useful non-linear patterns than the original
    # one-layer network. Scaling y also made training faster and more stable.
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64),
        activation="relu",
        solver="adam",
        alpha=0.01,
        learning_rate_init=0.001,
        early_stopping=True,
        validation_fraction=0.10,
        n_iter_no_change=30,
        max_iter=1000,
        tol=0.0001,
        random_state=42,
    )
    target_scaled_model = TransformedTargetRegressor(
        regressor=model,
        transformer=StandardScaler(),
    )
    return make_scaled_pipeline(target_scaled_model)


def parameter_grid():
    """Compare the documented finalists plus two layer-size alternatives."""
    common = {
        "model__regressor__activation": ["relu"],
        "model__regressor__solver": ["adam"],
    }
    configurations = [
        {
            "model__regressor__hidden_layer_sizes": [(128, 64)],
            "model__regressor__alpha": [0.01],
            "model__regressor__learning_rate_init": [0.001],
        },
        {
            "model__regressor__hidden_layer_sizes": [(128, 64)],
            "model__regressor__alpha": [0.1],
            "model__regressor__learning_rate_init": [0.001],
        },
        {
            "model__regressor__hidden_layer_sizes": [(128, 64)],
            "model__regressor__alpha": [0.001],
            "model__regressor__learning_rate_init": [0.002],
        },
        {
            "model__regressor__hidden_layer_sizes": [(64, 32)],
            "model__regressor__alpha": [0.01],
            "model__regressor__learning_rate_init": [0.001],
        },
        {
            "model__regressor__hidden_layer_sizes": [(128, 64, 32)],
            "model__regressor__alpha": [0.01],
            "model__regressor__learning_rate_init": [0.001],
        },
    ]
    return [{**common, **configuration} for configuration in configurations]

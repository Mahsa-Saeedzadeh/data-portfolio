"""Locked training-CV winners available to the one-time final test."""

from copy import deepcopy

from sklearn.base import BaseEstimator, clone
from sklearn.linear_model import Ridge

from src.models import FINAL_TEST_MODEL_NAMES, build_model
from src.preprocessing import make_scaled_pipeline


SHARED_XGBOOST = {
    "colsample_bytree": 0.8,
    "gamma": 0.25,
    "learning_rate": 0.025,
    "max_depth": 4,
    "min_child_weight": 1,
    "n_estimators": 350,
    "n_jobs": 1,
    "objective": "reg:squarederror",
    "random_state": 42,
    "reg_alpha": 0.0,
    "reg_lambda": 2.0,
    "subsample": 0.7,
    "verbosity": 0,
}

SHARED_NEURAL_NETWORK = {
    "model__regressor__activation": "relu",
    "model__regressor__alpha": 0.1,
    "model__regressor__hidden_layer_sizes": (128, 64),
    "model__regressor__learning_rate_init": 0.001,
    "model__regressor__solver": "adam",
}


BEST_MODEL_PARAMETERS = {
    "red": {
        "baseline": {"strategy": "median"},
        "tree": {
            "max_depth": 5,
            "min_samples_leaf": 10,
            "min_samples_split": 2,
        },
        "random_forest": {
            "max_depth": None,
            "max_features": 1.0,
            "min_samples_leaf": 3,
            "n_estimators": 200,
        },
        "knn": {
            "model__n_neighbors": 15,
            "model__p": 1,
            "model__weights": "distance",
        },
        "svm": {
            "model__C": 1.0,
            "model__epsilon": 0.05,
            "model__gamma": 0.03,
        },
        "linear": {
            "model__fit_intercept": True,
            "model__positive": False,
        },
        "ridge": {"model__alpha": 10},
        "lasso": {"model__alpha": 0.001},
        "bayes": {
            "model__alpha_1": 1e-6,
            "model__alpha_2": 1e-6,
            "model__lambda_1": 1e-5,
            "model__lambda_2": 1e-5,
        },
        "xgboost": SHARED_XGBOOST,
        "nn": SHARED_NEURAL_NETWORK,
        "voting": {
            "forest__max_depth": None,
            "forest__max_features": 1.0,
            "forest__min_samples_leaf": 3,
            "forest__n_estimators": 200,
            "nn": "drop",
            "ridge": "drop",
            "svm__model__C": 1.0,
            "svm__model__epsilon": 0.05,
            "svm__model__gamma": 0.03,
            "weights": [1, 0, 0, 2, 0],
            "xgboost": "drop",
        },
        "stacking": {
            "final_estimator": make_scaled_pipeline(Ridge(alpha=0.001)),
            "forest__max_depth": None,
            "forest__max_features": 1.0,
            "forest__min_samples_leaf": 3,
            "forest__n_estimators": 200,
            "passthrough": False,
            "svm__model__C": 1.0,
            "svm__model__epsilon": 0.05,
            "svm__model__gamma": 0.03,
        },
    },
    "white": {
        "baseline": {"strategy": "median"},
        "tree": {
            "max_depth": 5,
            "min_samples_leaf": 1,
            "min_samples_split": 10,
        },
        "random_forest": {
            "max_depth": None,
            "max_features": "sqrt",
            "min_samples_leaf": 1,
            "n_estimators": 200,
        },
        "knn": {
            "model__n_neighbors": 15,
            "model__p": 1,
            "model__weights": "distance",
        },
        "svm": {
            "model__C": 0.5,
            "model__epsilon": 0.05,
            "model__gamma": 0.1,
        },
        "linear": {
            "model__fit_intercept": True,
            "model__positive": False,
        },
        "ridge": {"model__alpha": 0.1},
        "lasso": {"model__alpha": 0.0001},
        "bayes": {
            "model__alpha_1": 1e-6,
            "model__alpha_2": 1e-6,
            "model__lambda_1": 1e-5,
            "model__lambda_2": 1e-5,
        },
        "xgboost": SHARED_XGBOOST,
        "nn": SHARED_NEURAL_NETWORK,
        "voting": {
            "forest__max_depth": None,
            "forest__max_features": "sqrt",
            "forest__min_samples_leaf": 1,
            "forest__n_estimators": 200,
            "nn": "drop",
            "ridge": "drop",
            "svm__model__C": 0.5,
            "svm__model__epsilon": 0.05,
            "svm__model__gamma": 0.1,
            "weights": [1, 0, 0, 1, 0],
            "xgboost": "drop",
        },
        "stacking": {
            "final_estimator": make_scaled_pipeline(Ridge(alpha=0.1)),
            "forest__max_depth": None,
            "forest__max_features": "sqrt",
            "forest__min_samples_leaf": 1,
            "forest__n_estimators": 200,
            "passthrough": True,
            "svm__model__C": 0.5,
            "svm__model__epsilon": 0.05,
            "svm__model__gamma": 0.1,
        },
    },
}


# These two models were chosen before opening the final 20% holdout.
FINAL_SELECTIONS = {
    "red": {"primary": "voting", "comparison": "stacking"},
    "white": {"primary": "voting", "comparison": "stacking"},
}


def _fresh_parameter(value):
    """Copy parameters so fitted estimators never modify the stored config."""
    if isinstance(value, BaseEstimator):
        return clone(value)
    return deepcopy(value)


def best_parameters(wine: str, model_name: str) -> dict:
    """Return a fresh copy of one locked training-CV parameter set."""
    try:
        parameters = BEST_MODEL_PARAMETERS[wine][model_name]
    except KeyError as error:
        raise ValueError(
            f"No locked parameters for wine={wine!r}, model={model_name!r}."
        ) from error
    return {
        name: _fresh_parameter(value)
        for name, value in parameters.items()
    }


def build_best_model(wine: str, model_name: str):
    """Build any registered model with its locked best training-CV settings."""
    model = build_model(model_name)
    model.set_params(**best_parameters(wine, model_name))
    return model


def validate_best_model_configs() -> None:
    """Check that both wines cover every model and all deep names are valid."""
    expected_models = set(FINAL_TEST_MODEL_NAMES)
    for wine, configurations in BEST_MODEL_PARAMETERS.items():
        configured_models = set(configurations)
        if configured_models != expected_models:
            missing = sorted(expected_models - configured_models)
            extra = sorted(configured_models - expected_models)
            raise ValueError(
                f"Invalid {wine} config coverage; missing={missing}, extra={extra}."
            )
        for model_name in FINAL_TEST_MODEL_NAMES:
            build_best_model(wine, model_name)

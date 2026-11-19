"""A diverse voting ensemble built from the strongest training-CV models."""

from sklearn.ensemble import VotingRegressor

from src.models.NN import build_model as build_neural_network
from src.models.random_forest import build_model as build_random_forest
from src.models.ridge import build_model as build_ridge
from src.models.svm import build_model as build_svm
from src.models.xgboost import build_model as build_xgboost


ESTIMATOR_ORDER = ("forest", "xgboost", "ridge", "svm", "nn")

TUNED_PROFILES = {
    "red": {
        "forest__n_estimators": 200,
        "forest__max_depth": None,
        "forest__min_samples_leaf": 3,
        "forest__max_features": 1.0,
        "svm__model__C": 1.0,
        "svm__model__epsilon": 0.05,
        "svm__model__gamma": 0.03,
    },
    "white": {
        "forest__n_estimators": 200,
        "forest__max_depth": None,
        "forest__min_samples_leaf": 1,
        "forest__max_features": "sqrt",
        "svm__model__C": 0.5,
        "svm__model__epsilon": 0.05,
        "svm__model__gamma": 0.1,
    },
}

# Each weight list follows ESTIMATOR_ORDER. A zero belongs to a dropped model.
VOTING_RECIPES = [
    ([1, 0, 0, 1, 0], ("xgboost", "ridge", "nn"), False),
    ([1, 0, 0, 2, 0], ("xgboost", "ridge", "nn"), False),
    ([2, 0, 0, 1, 0], ("xgboost", "ridge", "nn"), False),
    ([1, 1, 0, 1, 0], ("ridge", "nn"), False),
    ([1, 1, 0, 2, 0], ("ridge", "nn"), False),
    ([1, 0, 0, 1, 1], ("xgboost", "ridge"), True),
    ([1, 0, 0, 2, 1], ("xgboost", "ridge"), True),
    ([1, 1, 0, 1, 1], ("ridge",), True),
]


def _tuned_forest():
    """Use the profile that was robust across both wine datasets."""
    model = build_random_forest()
    model.set_params(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=1,
        max_features="sqrt",
    )
    return model


def _tuned_svm():
    """Use the shared fixed SVM profile selected from training CV."""
    model = build_svm()
    model.set_params(model__C=0.5, model__epsilon=0.05, model__gamma=0.1)
    return model


def _tuned_neural_network():
    """Use the NN regularization value that led both separate searches."""
    model = build_neural_network()
    model.set_params(model__regressor__alpha=0.1)
    return model


def build_model():
    """Return the improved fixed vote: equal tuned Random Forest and SVM."""
    return VotingRegressor(
        estimators=[
            ("forest", _tuned_forest()),
            ("xgboost", build_xgboost()),
            ("ridge", build_ridge()),
            ("svm", _tuned_svm()),
            ("nn", _tuned_neural_network()),
        ],
        # XGBoost, Ridge and NN stay available to the optional grid below,
        # but do not contribute to this robust fixed two-model vote.
        weights=[1, 0, 0, 1, 0],
        n_jobs=1,
    )


def parameter_grid():
    """Pair two tuned profiles with eight diverse member/weight recipes."""
    candidates = []
    for profile in TUNED_PROFILES.values():
        for weights, dropped_models, uses_neural_network in VOTING_RECIPES:
            candidate = {name: [value] for name, value in profile.items()}
            candidate["weights"] = [weights]
            for model_name in dropped_models:
                candidate[model_name] = ["drop"]
            if uses_neural_network:
                candidate["nn__model__regressor__alpha"] = [0.1]
            candidates.append(candidate)
    return candidates

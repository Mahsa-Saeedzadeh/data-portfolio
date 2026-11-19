"""A tuned stacking ensemble with diverse base and final estimators."""

from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Lasso, Ridge

from src.models.random_forest import build_model as build_random_forest
from src.models.ridge import build_model as build_ridge
from src.models.svm import build_model as build_svm
from src.models.xgboost import build_model as build_xgboost
from src.preprocessing import make_scaled_pipeline


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


def _tuned_forest():
    """Return the red-oriented fixed forest used by the robust stack."""
    model = build_random_forest()
    model.set_params(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=3,
        max_features=1.0,
    )
    return model


def _tuned_svm():
    """Return the red-oriented fixed SVM used by the robust stack."""
    model = build_svm()
    model.set_params(model__C=1.0, model__epsilon=0.05, model__gamma=0.03)
    return model


def _scaled_ridge(alpha: float):
    return make_scaled_pipeline(Ridge(alpha=alpha))


def _scaled_lasso(alpha: float):
    # Stacked predictors can be strongly correlated, so Lasso needs more than
    # its default 1,000 iterations to finish this comparison cleanly.
    return make_scaled_pipeline(Lasso(alpha=alpha, max_iter=20000))


def _small_final_forest():
    return RandomForestRegressor(
        n_estimators=200,
        max_depth=3,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=1,
    )


def build_model():
    """Return the improved fixed stack selected with training-only CV."""
    return StackingRegressor(
        estimators=[
            ("forest", _tuned_forest()),
            ("xgboost", build_xgboost()),
            ("svm", _tuned_svm()),
            ("ridge", build_ridge()),
        ],
        final_estimator=_scaled_ridge(alpha=0.001),
        cv=5,
        passthrough=False,
        n_jobs=1,
    )


def parameter_grid():
    """Test paired wine profiles with five small meta-model choices."""
    meta_choices = [
        (_scaled_ridge(alpha=0.001), False),
        (_scaled_ridge(alpha=1.0), False),
        (_scaled_ridge(alpha=0.1), True),
        (_scaled_lasso(alpha=0.001), True),
        (_small_final_forest(), True),
    ]

    candidates = []
    for profile in TUNED_PROFILES.values():
        for final_estimator, passthrough in meta_choices:
            candidate = {name: [value] for name, value in profile.items()}
            candidate["final_estimator"] = [final_estimator]
            candidate["passthrough"] = [passthrough]
            candidates.append(candidate)
    return candidates

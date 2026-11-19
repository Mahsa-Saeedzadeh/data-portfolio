"""Create models through one shared interface for the main program."""

from importlib import import_module


MODEL_MODULES = {
    "baseline": "src.models.baseline",
    "tree": "src.models.tree",
    "random_forest": "src.models.random_forest",
    "knn": "src.models.knn",
    "svm": "src.models.svm",
    "linear": "src.models.linear",
    "ridge": "src.models.ridge",
    "polynomial_ridge": "src.models.polynomial_ridge",
    "lasso": "src.models.lasso",
    "bayes": "src.models.bayes",
    "xgboost": "src.models.xgboost",
    "nn": "src.models.NN",
    "voting": "src.models.voting",
    "stacking": "src.models.stacking",
}
MODEL_NAMES = tuple(MODEL_MODULES)

# These are the 13 models that existed when the one-time final-test lock was
# frozen. Later development models must not be presented as holdout candidates.
FINAL_TEST_MODEL_NAMES = (
    "baseline",
    "tree",
    "random_forest",
    "knn",
    "svm",
    "linear",
    "ridge",
    "lasso",
    "bayes",
    "xgboost",
    "nn",
    "voting",
    "stacking",
)


def build_model(model_name: str):
    """Load the selected model file and return its estimator."""
    module = import_module(MODEL_MODULES[model_name])
    return module.build_model()


def parameter_grid(model_name: str):
    """Load the training-only search space owned by the selected model."""
    module = import_module(MODEL_MODULES[model_name])
    return module.parameter_grid()

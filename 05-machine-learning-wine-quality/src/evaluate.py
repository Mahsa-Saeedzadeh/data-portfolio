"""Calculate the agreed MAE, RMSE, and R2 regression scores."""

from math import sqrt

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_validate


def regression_scores(y_true, y_prediction) -> dict[str, float]:
    """Return the three project metrics for a final prediction set."""
    mae = mean_absolute_error(y_true, y_prediction)
    rmse = sqrt(mean_squared_error(y_true, y_prediction))
    r2 = r2_score(y_true, y_prediction)
    return {"MAE": float(mae), "RMSE": float(rmse), "R2": float(r2)}


def cross_validation_scores(model, x_train, y_train, folds: int = 5) -> dict:
    """Measure MAE, RMSE, and R2 using only the training part of the data."""
    scores = cross_validate(
        model,
        x_train,
        y_train,
        cv=folds,
        scoring={
            "MAE": "neg_mean_absolute_error",
            "RMSE": "neg_root_mean_squared_error",
            "R2": "r2",
        },
    )
    return {
        "MAE": -scores["test_MAE"],
        "RMSE": -scores["test_RMSE"],
        # R2 is already returned in its normal direction: higher is better.
        "R2": scores["test_R2"],
    }

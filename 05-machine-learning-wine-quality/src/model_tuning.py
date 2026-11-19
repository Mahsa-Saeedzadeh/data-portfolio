"""Shared training-only grid search for every registered model."""

import json
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.model_selection import GridSearchCV, ParameterGrid


SEARCH_SCORING = {
    "MAE": "neg_mean_absolute_error",
    "RMSE": "neg_root_mean_squared_error",
    "R2": "r2",
}


@dataclass
class GridSearchOutcome:
    """The selected model and the details needed by the shared reports."""

    best_estimator: object
    best_parameters: dict
    best_parameters_text: str
    candidate_count: int
    fold_scores: dict[str, list[float]]
    candidate_table: pd.DataFrame


def _clean_parameter_name(name: str) -> str:
    """Remove pipeline prefixes from names shown in reports."""
    return name.replace("model__regressor__", "").replace("model__", "")


def _json_safe(value):
    """Convert grid values, including estimators, to compact report text."""
    if isinstance(value, BaseEstimator):
        # sklearn's repr shows the useful non-default settings. Collapsing its
        # whitespace keeps Pipeline and ensemble descriptions on one table line.
        return " ".join(repr(value).split())
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value


def readable_parameters(parameters: dict) -> str:
    """Create one stable, compact JSON description of a parameter choice."""
    cleaned = {
        _clean_parameter_name(name): _json_safe(value)
        for name, value in parameters.items()
    }
    return json.dumps(cleaned, sort_keys=True)


def _validate_parameter_grid(model, parameter_grid) -> None:
    """Fail early with a clear message when a pipeline prefix is wrong."""
    valid_names = set(model.get_params(deep=True))
    grid_parts = parameter_grid if isinstance(parameter_grid, list) else [parameter_grid]
    invalid_names = sorted({
        name
        for grid_part in grid_parts
        for name in grid_part
        if name not in valid_names
    })
    if invalid_names:
        raise ValueError(
            "Unknown grid-search parameter(s): " + ", ".join(invalid_names)
        )


def run_grid_search(model, parameter_grid, x_train, y_train, folds: int = 5):
    """Choose parameters with training CV and leave reserved test rows unused."""
    _validate_parameter_grid(model, parameter_grid)
    candidate_count = len(ParameterGrid(parameter_grid))
    search = GridSearchCV(
        estimator=model,
        param_grid=parameter_grid,
        scoring=SEARCH_SCORING,
        refit="MAE",
        cv=folds,
        n_jobs=-1,
        error_score="raise",
        return_train_score=False,
    )
    search.fit(x_train, y_train)

    search_results = search.cv_results_
    best_index = search.best_index_
    candidate_table = pd.DataFrame({
        "search_rank": search_results["rank_test_MAE"],
        "parameters": [
            readable_parameters(parameters)
            for parameters in search_results["params"]
        ],
        "CV_MAE": -search_results["mean_test_MAE"],
        "CV_RMSE": -search_results["mean_test_RMSE"],
        "CV_R2": search_results["mean_test_R2"],
        "CV_MAE_std": search_results["std_test_MAE"],
        "fit_seconds": search_results["mean_fit_time"],
    }).sort_values(["search_rank", "CV_MAE"], ignore_index=True)

    fold_scores = {
        "MAE": [
            -search_results[f"split{fold}_test_MAE"][best_index]
            for fold in range(folds)
        ],
        "RMSE": [
            -search_results[f"split{fold}_test_RMSE"][best_index]
            for fold in range(folds)
        ],
        "R2": [
            search_results[f"split{fold}_test_R2"][best_index]
            for fold in range(folds)
        ],
    }
    best_parameters = search.best_params_
    return GridSearchOutcome(
        best_estimator=search.best_estimator_,
        best_parameters=best_parameters,
        best_parameters_text=readable_parameters(best_parameters),
        candidate_count=candidate_count,
        fold_scores=fold_scores,
        candidate_table=candidate_table,
    )

"""Shared preprocessing helpers used by models that need scaled data."""

import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def make_scaled_pipeline(model):
    """Keep scaling inside a pipeline so it learns from training data only."""
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", model),
    ])


def _training_outlier_analysis(
    x_train: pd.DataFrame,
    iqr_multiplier: float = 3.0,
) -> tuple[pd.DataFrame, pd.Series]:
    """Return the training-only outlier report and one combined row mask."""
    rows = []
    any_outlier = pd.Series(False, index=x_train.index)

    for column in x_train.columns:
        q1 = x_train[column].quantile(0.25)
        q3 = x_train[column].quantile(0.75)
        iqr = q3 - q1
        lower_limit = q1 - iqr_multiplier * iqr
        upper_limit = q3 + iqr_multiplier * iqr
        column_mask = (
            (x_train[column] < lower_limit)
            | (x_train[column] > upper_limit)
        )
        any_outlier |= column_mask

        rows.append({
            "feature": column,
            "lower_limit": lower_limit,
            "upper_limit": upper_limit,
            "flagged_training_rows": int(column_mask.sum()),
            "flagged_share_percent": 100 * column_mask.mean(),
        })

    report = pd.DataFrame(rows).sort_values(
        "flagged_training_rows",
        ascending=False,
    )
    return report, any_outlier


def training_outlier_report(
    x_train: pd.DataFrame,
    iqr_multiplier: float = 3.0,
) -> tuple[pd.DataFrame, int]:
    """Report extreme values using training data only; do not delete rows."""
    report, outlier_mask = _training_outlier_analysis(
        x_train,
        iqr_multiplier,
    )
    return report, int(outlier_mask.sum())


def handle_training_outliers(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    remove_outliers: bool,
    iqr_multiplier: float = 3.0,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, int, int]:
    """Apply the selected training-only outlier policy to X and y together."""
    report, outlier_mask = _training_outlier_analysis(
        x_train,
        iqr_multiplier,
    )
    outliers_found = int(outlier_mask.sum())

    if remove_outliers:
        rows_to_keep = ~outlier_mask
        prepared_x_train = x_train.loc[rows_to_keep].reset_index(drop=True)
        prepared_y_train = y_train.loc[rows_to_keep].reset_index(drop=True)
        outliers_removed = outliers_found
    else:
        prepared_x_train = x_train.reset_index(drop=True)
        prepared_y_train = y_train.reset_index(drop=True)
        outliers_removed = 0

    if prepared_x_train.empty:
        raise ValueError("Outlier removal left no training rows.")

    return (
        prepared_x_train,
        prepared_y_train,
        report,
        outliers_found,
        outliers_removed,
    )

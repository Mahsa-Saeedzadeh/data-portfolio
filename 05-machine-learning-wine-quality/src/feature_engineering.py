"""Optional row-wise feature transformations for controlled experiments."""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


RATIO_SOURCE_COLUMNS = (
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "alcohol",
)

RATIO_FEATURE_COLUMNS = (
    "sweetness_index",
    "sugar_acid_ratio",
    "alcohol_acid_ratio",
    "volatile_fixed_ratio",
    "sulfur_ratio",
)

LOG_FEATURE_COLUMNS = (
    "residual sugar",
    "total sulfur dioxide",
    "sulphates",
    "free sulfur dioxide",
)


def _check_finite(table: pd.DataFrame, columns, description: str) -> None:
    """Raise a clear error instead of passing invalid values to a model."""
    values = table.loc[:, list(columns)].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{description} contains a missing or infinite value.")


def add_ratio_features(data: pd.DataFrame) -> pd.DataFrame:
    """Append the five ratios proposed in the submitted feature experiment."""
    missing_columns = [
        column for column in RATIO_SOURCE_COLUMNS if column not in data.columns
    ]
    if missing_columns:
        raise ValueError(
            "Ratio feature engineering needs these selected inputs: "
            + ", ".join(missing_columns)
            + ". Use --features all or include every listed input."
        )

    prepared = data.copy()
    _check_finite(prepared, RATIO_SOURCE_COLUMNS, "Ratio source data")

    sweetness_denominator = (
        prepared["fixed acidity"]
        + prepared["volatile acidity"]
        + prepared["citric acid"]
    )
    denominators = {
        "sweetness_index": sweetness_denominator,
        "sugar_acid_ratio": prepared["fixed acidity"],
        "alcohol_acid_ratio": prepared["fixed acidity"],
        "volatile_fixed_ratio": prepared["fixed acidity"],
        "sulfur_ratio": prepared["total sulfur dioxide"],
    }
    for name, denominator in denominators.items():
        if (denominator <= 0).any():
            raise ValueError(
                f"Cannot calculate {name}: its denominator must be positive."
            )

    prepared["sweetness_index"] = (
        prepared["residual sugar"] / sweetness_denominator
    )
    prepared["sugar_acid_ratio"] = (
        prepared["residual sugar"] / prepared["fixed acidity"]
    )
    prepared["alcohol_acid_ratio"] = (
        prepared["alcohol"] / prepared["fixed acidity"]
    )
    prepared["volatile_fixed_ratio"] = (
        prepared["volatile acidity"] / prepared["fixed acidity"]
    )
    prepared["sulfur_ratio"] = (
        prepared["free sulfur dioxide"]
        / prepared["total sulfur dioxide"]
    )
    _check_finite(prepared, RATIO_FEATURE_COLUMNS, "Engineered ratio data")
    return prepared


class SelectiveLog1p(BaseEstimator, TransformerMixin):
    """Optionally log-transform the four skewed wine features by name."""

    def __init__(self, enabled: bool = True, columns=LOG_FEATURE_COLUMNS):
        self.enabled = enabled
        self.columns = columns

    def fit(self, x, y=None):
        """Record the input names; the transformation learns no statistics."""
        if not isinstance(x, pd.DataFrame):
            raise TypeError("SelectiveLog1p expects a pandas DataFrame.")
        self.feature_names_in_ = np.asarray(x.columns, dtype=object)
        return self

    def transform(self, x):
        """Return a copy with log1p applied when this option is enabled."""
        if not isinstance(x, pd.DataFrame):
            raise TypeError("SelectiveLog1p expects a pandas DataFrame.")
        prepared = x.copy()
        if not self.enabled:
            return prepared

        selected_columns = [
            column for column in self.columns if column in prepared.columns
        ]
        if not selected_columns:
            return prepared

        _check_finite(prepared, selected_columns, "Log-transform source data")
        if (prepared[selected_columns] < 0).any().any():
            raise ValueError("Log-transformed wine features must be non-negative.")
        prepared[selected_columns] = np.log1p(prepared[selected_columns])
        return prepared

    def get_feature_names_out(self, input_features=None):
        """The transformation changes values but keeps the same columns."""
        if input_features is None:
            return self.feature_names_in_.copy()
        return np.asarray(input_features, dtype=object)

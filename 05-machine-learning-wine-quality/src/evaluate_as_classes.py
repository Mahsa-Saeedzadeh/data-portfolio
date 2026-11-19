"""View regression predictions as rounded wine-quality classes."""

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_predict


MINIMUM_QUALITY = 0
MAXIMUM_QUALITY = 10


def rounded_quality_predictions(y_prediction) -> np.ndarray:
    """Round continuous predictions and keep them on the 0-to-10 scale."""
    rounded = np.rint(np.asarray(y_prediction, dtype=float))
    return np.clip(rounded, MINIMUM_QUALITY, MAXIMUM_QUALITY).astype(int)


def class_view_scores(
    y_true,
    y_prediction,
    margin: int = 1,
) -> dict[str, float]:
    """Calculate supplementary scores after rounding regression predictions."""
    if not MINIMUM_QUALITY <= margin <= MAXIMUM_QUALITY:
        raise ValueError("The class margin must be between 0 and 10.")

    actual_classes = np.asarray(y_true, dtype=int)
    predicted_classes = rounded_quality_predictions(y_prediction)
    actual_quality_levels = np.unique(actual_classes)

    return {
        "Accuracy": float(
            accuracy_score(actual_classes, predicted_classes)
        ),
        "Within_Margin_Accuracy": float(
            np.mean(np.abs(actual_classes - predicted_classes) <= margin)
        ),
        "Balanced_Accuracy": float(
            recall_score(
                actual_classes,
                predicted_classes,
                labels=actual_quality_levels,
                average="macro",
                zero_division=0,
            )
        ),
        "Macro_Precision": float(
            precision_score(
                actual_classes,
                predicted_classes,
                average="macro",
                zero_division=0,
            )
        ),
        "Macro_F1": float(
            f1_score(
                actual_classes,
                predicted_classes,
                average="macro",
                zero_division=0,
            )
        ),
    }


def class_confusion_table(y_true, y_prediction) -> pd.DataFrame:
    """Return a readable confusion matrix for the classes that occurred."""
    actual_classes = np.asarray(y_true, dtype=int)
    predicted_classes = rounded_quality_predictions(y_prediction)
    quality_classes = np.union1d(actual_classes, predicted_classes)

    matrix = confusion_matrix(
        actual_classes,
        predicted_classes,
        labels=quality_classes,
    )
    return pd.DataFrame(
        matrix,
        index=[f"actual_{value}" for value in quality_classes],
        columns=[f"predicted_{value}" for value in quality_classes],
    )


def cross_validation_class_view(
    model,
    x_train,
    y_train,
    folds: int = 5,
    margin: int = 1,
) -> tuple[dict[str, float], pd.DataFrame]:
    """Evaluate rounded out-of-fold predictions without touching test data."""
    predictions = cross_val_predict(
        model,
        x_train,
        y_train,
        cv=folds,
        method="predict",
    )
    scores = class_view_scores(y_train, predictions, margin=margin)
    confusion_table = class_confusion_table(y_train, predictions)
    return scores, confusion_table

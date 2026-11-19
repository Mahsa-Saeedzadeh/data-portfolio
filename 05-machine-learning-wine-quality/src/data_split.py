"""Load the wine data and create the shared 80/20 split."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split as sklearn_train_test_split


EXPECTED_COLUMNS = [
    "fixed acidity",
    "volatile acidity",
    "citric acid",
    "residual sugar",
    "chlorides",
    "free sulfur dioxide",
    "total sulfur dioxide",
    "density",
    "pH",
    "sulphates",
    "alcohol",
    "quality",
]
FEATURE_COLUMNS = EXPECTED_COLUMNS[:-1]
TEST_SIZE = 0.20
RANDOM_STATE = 42


def load_wine_data(csv_path: Path) -> pd.DataFrame:
    """Read one original UCI CSV file and check its columns."""
    data = pd.read_csv(csv_path, sep=";")
    if data.columns.tolist() != EXPECTED_COLUMNS:
        raise ValueError(f"Unexpected columns in {csv_path.name}")
    return data


def handle_duplicates(
    data: pd.DataFrame,
    remove_duplicates: bool,
) -> tuple[pd.DataFrame, int, int]:
    """Apply the selected duplicate policy before the train/test split."""
    duplicates_found = int(data.duplicated().sum())

    if remove_duplicates:
        prepared_data = data.drop_duplicates(keep="first").reset_index(drop=True)
        duplicates_removed = duplicates_found
    else:
        prepared_data = data.copy()
        duplicates_removed = 0

    return prepared_data, duplicates_found, duplicates_removed


def resolve_feature_columns(feature_text: str) -> list[str]:
    """Turn 'all' or a comma-separated feature list into valid column names."""
    if feature_text.strip().lower() == "all":
        return FEATURE_COLUMNS.copy()

    requested_names = [
        name.strip()
        for name in feature_text.split(",")
        if name.strip()
    ]
    if not requested_names:
        raise ValueError("Choose 'all' or at least one feature name.")

    name_lookup = {
        column.lower().replace("_", " "): column
        for column in FEATURE_COLUMNS
    }
    selected_columns = []
    unknown_names = []

    for requested_name in requested_names:
        normalized_name = requested_name.lower().replace("_", " ")
        if normalized_name in name_lookup:
            selected_columns.append(name_lookup[normalized_name])
        else:
            unknown_names.append(requested_name)

    if unknown_names:
        raise ValueError(
            "Unknown feature(s): "
            + ", ".join(unknown_names)
            + ". Use --features all to use every input."
        )
    if len(selected_columns) != len(set(selected_columns)):
        raise ValueError("Each selected feature may only be listed once.")

    return selected_columns


def _composite_feature_rank(data: pd.DataFrame) -> pd.Series:
    """Give each row one average percentile rank across all 11 features."""
    feature_ranks = data[FEATURE_COLUMNS].rank(method="average", pct=True)
    return feature_ranks.mean(axis=1)


def _evenly_spaced_positions(group_size: int, rows_to_pick: int) -> np.ndarray:
    """Choose positions across a sorted group instead of taking one end."""
    if rows_to_pick <= 0:
        return np.array([], dtype=int)

    step = group_size / rows_to_pick
    positions = np.floor((np.arange(rows_to_pick) + 0.5) * step).astype(int)
    return np.clip(positions, 0, group_size - 1)


def _ranked_split_indices(
    data: pd.DataFrame,
    stratified: bool,
) -> tuple[np.ndarray, np.ndarray]:
    """Create deterministic train/test indices using the downloaded method."""
    feature_rank = _composite_feature_rank(data)

    if stratified:
        # First get sklearn's exact 80/20 quality counts. The ranked method
        # then chooses evenly spaced rows instead of sklearn's random rows.
        positions = np.arange(len(data))
        _, temporary_test = sklearn_train_test_split(
            positions,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=data["quality"].to_numpy(),
        )
        test_counts = (
            data["quality"].iloc[temporary_test].value_counts().to_dict()
        )
        groups = data.groupby("quality", sort=True).groups.items()
    else:
        # Ranking can also be used once across the complete dataset.
        test_counts = {"all": int(np.ceil(len(data) * TEST_SIZE))}
        groups = [("all", data.index)]

    train_parts = []
    test_parts = []

    for group_name, group_indices in groups:
        group_indices = np.asarray(group_indices)
        sorted_indices = group_indices[
            np.argsort(
                feature_rank.loc[group_indices].to_numpy(),
                kind="mergesort",
            )
        ]
        test_count = test_counts.get(group_name, 0)
        if not 0 <= test_count < len(sorted_indices):
            raise ValueError(
                "The selected split cannot keep rows in both train and test."
            )
        test_positions = _evenly_spaced_positions(
            len(sorted_indices),
            test_count,
        )

        is_training_row = np.ones(len(sorted_indices), dtype=bool)
        is_training_row[test_positions] = False
        train_parts.append(sorted_indices[is_training_row])
        if test_count:
            test_parts.append(sorted_indices[test_positions])

    if not test_parts:
        raise ValueError("Not enough rows to create a test set.")

    train_indices = np.concatenate(train_parts)
    test_indices = np.concatenate(test_parts)

    # Ranked membership is deterministic. This fixed shuffle only prevents
    # the later CV folds from following the original CSV row order.
    random_generator = np.random.default_rng(RANDOM_STATE)
    random_generator.shuffle(train_indices)
    random_generator.shuffle(test_indices)
    return train_indices, test_indices


def split_wine_data(
    data: pd.DataFrame,
    feature_columns: list[str] | None = None,
    stratified: bool = True,
    ranked: bool = True,
):
    """Use the selected split rules and keep about 20% for final testing."""
    if feature_columns is None:
        selected_columns = FEATURE_COLUMNS
    elif not feature_columns:
        raise ValueError("Choose at least one input feature.")
    else:
        selected_columns = feature_columns

    prepared_data = data.reset_index(drop=True)
    x = prepared_data[selected_columns].copy()
    y = prepared_data["quality"].copy()

    if ranked:
        train_indices, test_indices = _ranked_split_indices(
            prepared_data,
            stratified=stratified,
        )
        return (
            x.iloc[train_indices].reset_index(drop=True),
            x.iloc[test_indices].reset_index(drop=True),
            y.iloc[train_indices].reset_index(drop=True),
            y.iloc[test_indices].reset_index(drop=True),
        )

    x_train, x_test, y_train, y_test = sklearn_train_test_split(
        x,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y if stratified else None,
    )
    return (
        x_train.reset_index(drop=True),
        x_test.reset_index(drop=True),
        y_train.reset_index(drop=True),
        y_test.reset_index(drop=True),
    )


def save_split(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    dataset_key: str,
    output_folder: Path,
) -> None:
    """Save the exact shared train and test rows for the whole team."""
    output_folder.mkdir(parents=True, exist_ok=True)

    train_data = x_train.copy()
    train_data["quality"] = y_train
    test_data = x_test.copy()
    test_data["quality"] = y_test

    train_data.to_csv(output_folder / f"{dataset_key}_train.csv", index=False)
    test_data.to_csv(output_folder / f"{dataset_key}_test.csv", index=False)

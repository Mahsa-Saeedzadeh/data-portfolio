"""Run selected wine-quality models with one shared workflow."""

import argparse
from hashlib import sha1
from pathlib import Path

import pandas as pd

from src.data_split import (
    FEATURE_COLUMNS,
    handle_duplicates,
    load_wine_data,
    resolve_feature_columns,
    save_split,
    split_wine_data,
)
from src.evaluate import cross_validation_scores
from src.evaluate_as_classes import cross_validation_class_view
from src.feature_engineering import add_ratio_features
from src.model_tuning import run_grid_search
from src.models import MODEL_NAMES, build_model, parameter_grid
from src.preprocessing import handle_training_outliers


PROJECT_FOLDER = Path(__file__).resolve().parent
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw-input"
PREPROCESSED_FOLDER = PROJECT_FOLDER / "data" / "pre-processed"
RESULTS_FOLDER = PROJECT_FOLDER / "data" / "results"
EVALUATION_FOLDER = PROJECT_FOLDER / "data" / "evaluate"

DEFAULT_WINE = "red"
DEFAULT_MODEL = "baseline"
DEFAULT_FEATURES = FEATURE_COLUMNS.copy()
DEFAULT_REMOVE_DUPLICATES = True
DEFAULT_REMOVE_OUTLIERS = True
DEFAULT_STRATIFIED_SPLIT = True
DEFAULT_RANKED_SPLIT = True
DEFAULT_CLASS_EVALUATION = True
DEFAULT_CLASS_MARGIN = 1
DEFAULT_GRID_SEARCH = False
DEFAULT_FEATURE_ENGINEERING = "none"

DATASETS = {
    "red": ("Red wine", "red_wine", RAW_FOLDER / "winequality-red.csv"),
    "white": ("White wine", "white_wine", RAW_FOLDER / "winequality-white.csv"),
}


def feature_argument(feature_text: str) -> list[str]:
    """Validate the feature text while argparse builds the command line."""
    try:
        return resolve_feature_columns(feature_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def class_margin_argument(margin_text: str) -> int:
    """Accept a whole-number class margin between 0 and 10."""
    try:
        margin = int(margin_text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "The class margin must be a whole number from 0 to 10."
        ) from error

    if not 0 <= margin <= 10:
        raise argparse.ArgumentTypeError(
            "The class margin must be a whole number from 0 to 10."
        )
    return margin


def feature_configuration_key(feature_columns: list[str]) -> str:
    """Create a short stable filename label for the selected features."""
    if feature_columns == FEATURE_COLUMNS:
        return "all_features"

    feature_text = ",".join(feature_columns)
    short_hash = sha1(feature_text.encode("utf-8")).hexdigest()[:8]
    return f"{len(feature_columns)}_features_{short_hash}"


def split_configuration(
    stratified_split: bool,
    ranked_split: bool,
) -> tuple[str, str]:
    """Return a filename key and readable name for the selected split."""
    if stratified_split and ranked_split:
        return "stratified_ranked", "quality-stratified + feature-ranked"
    if stratified_split:
        return "stratified_random", "quality-stratified random"
    if ranked_split:
        return "unstratified_ranked", "feature-ranked without quality strata"
    return "random", "plain random"


def parse_arguments() -> argparse.Namespace:
    """Read the project choices from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wine",
        choices=("red", "white", "both"),
        default=DEFAULT_WINE,
        help="Choose red wine, white wine, or both (default: red).",
    )
    parser.add_argument(
        "--model",
        choices=(*MODEL_NAMES, "all"),
        default=DEFAULT_MODEL,
        help="Choose one model or test all available models (default: baseline).",
    )
    parser.add_argument(
        "--grid-search",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_GRID_SEARCH,
        help=(
            "Choose model parameters with training-only GridSearchCV "
            "(default: disabled)."
        ),
    )
    parser.add_argument(
        "--remove-duplicates",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_REMOVE_DUPLICATES,
        help=(
            "Remove exact duplicates before splitting (default: enabled; "
            "use --no-remove-duplicates to keep them)."
        ),
    )
    parser.add_argument(
        "--remove-outliers",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_REMOVE_OUTLIERS,
        help=(
            "Remove 3 x IQR outliers from training only (default: enabled; "
            "use --no-remove-outliers to keep them)."
        ),
    )
    parser.add_argument(
        "--stratified-split",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_STRATIFIED_SPLIT,
        help=(
            "Balance the split by quality class (default: enabled; "
            "use --no-stratified-split to disable it)."
        ),
    )
    parser.add_argument(
        "--ranked-split",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_RANKED_SPLIT,
        help=(
            "Spread low and high feature ranks across the split "
            "(default: enabled; use --no-ranked-split to disable it)."
        ),
    )
    parser.add_argument(
        "--features",
        type=feature_argument,
        default=DEFAULT_FEATURES.copy(),
        metavar='"FEATURE_1,FEATURE_2"',
        help="Use 'all' or a quoted comma-separated feature list (default: all).",
    )
    parser.add_argument(
        "--feature-engineering",
        choices=("none", "ratios"),
        default=DEFAULT_FEATURE_ENGINEERING,
        help=(
            "Optionally add five submitted ratio features after the split and "
            "training-only outlier handling (default: none)."
        ),
    )
    parser.add_argument(
        "--class-evaluation",
        action=argparse.BooleanOptionalAction,
        default=DEFAULT_CLASS_EVALUATION,
        help=(
            "Add a rounded classification-style view (default: enabled; "
            "use --no-class-evaluation to skip it)."
        ),
    )
    parser.add_argument(
        "--class-margin",
        type=class_margin_argument,
        default=DEFAULT_CLASS_MARGIN,
        metavar="POINTS",
        help="Accept predictions within this many quality points (default: 1).",
    )
    return parser.parse_args()


def selected_datasets(wine_choice: str) -> list[tuple[str, str, Path]]:
    """Return the dataset entries requested by the user."""
    if wine_choice == "both":
        return list(DATASETS.values())
    return [DATASETS[wine_choice]]


def selected_models(model_choice: str) -> list[str]:
    """Return one requested model name or every available model name."""
    if model_choice == "all":
        return list(MODEL_NAMES)
    return [model_choice]


def run_dataset(
    dataset_name: str,
    dataset_key: str,
    csv_path: Path,
    model_names: list[str],
    remove_duplicates: bool,
    remove_outliers: bool,
    stratified_split: bool,
    ranked_split: bool,
    feature_columns: list[str],
    feature_engineering: str,
    class_evaluation: bool,
    class_margin: int,
    grid_search: bool,
) -> list[dict]:
    """Prepare one dataset and cross-validate the selected models."""
    raw_data = load_wine_data(csv_path)
    data, duplicates_found, duplicates_removed = handle_duplicates(
        raw_data,
        remove_duplicates,
    )

    # The selected duplicate policy is applied before this shared split.
    x_train, x_test, y_train, y_test = split_wine_data(
        data,
        feature_columns,
        stratified=stratified_split,
        ranked=ranked_split,
    )
    training_rows_before_outliers = len(x_train)
    (
        x_train,
        y_train,
        outlier_table,
        outlier_rows,
        outliers_removed,
    ) = handle_training_outliers(
        x_train,
        y_train,
        remove_outliers,
        iqr_multiplier=3.0,
    )

    if feature_engineering == "ratios":
        x_train = add_ratio_features(x_train)
        x_test = add_ratio_features(x_test)
    actual_feature_columns = x_train.columns.tolist()

    duplicate_key = "duplicates_removed" if remove_duplicates else "duplicates_kept"
    outlier_key = "remove_outliers" if remove_outliers else "keep_outliers"
    split_key, split_name = split_configuration(
        stratified_split,
        ranked_split,
    )
    feature_key = feature_configuration_key(feature_columns)
    engineering_key = (
        "_ratio_features" if feature_engineering == "ratios" else ""
    )
    run_key = (
        f"{dataset_key}_{duplicate_key}_{outlier_key}_{split_key}_{feature_key}"
        f"{engineering_key}"
    )

    save_split(
        x_train,
        x_test,
        y_train,
        y_test,
        run_key,
        PREPROCESSED_FOLDER,
    )

    EVALUATION_FOLDER.mkdir(parents=True, exist_ok=True)
    outlier_table.to_csv(
        EVALUATION_FOLDER / f"{run_key}_training_outliers.csv",
        index=False,
    )

    duplicate_action = "removed" if remove_duplicates else "kept"
    outlier_policy = "remove" if remove_outliers else "keep"
    training_share = 100 * training_rows_before_outliers / len(data)
    test_share = 100 * len(x_test) / len(data)
    print(f"\n{dataset_name}")
    print("-" * len(dataset_name))
    print(f"Original rows          : {len(raw_data):,}")
    print(f"Exact duplicates found : {duplicates_found:,}")
    print(f"Duplicate action       : {duplicate_action}")
    print(f"Rows used for split    : {len(data):,}")
    print(f"Split method           : {split_name}")
    print(f"Feature engineering    : {feature_engineering}")
    print(f"Inputs prepared        : {x_train.shape[1]}")
    print(f"Selected features      : {', '.join(actual_feature_columns)}")
    print(
        f"Training rows before   : {training_rows_before_outliers:,} "
        f"({training_share:.1f}%)"
    )
    print(f"Extreme rows found     : {outlier_rows:,} (3 x IQR)")
    print(f"Outlier policy         : {outlier_policy}")
    print(f"Training rows for CV   : {len(x_train):,}")
    print(
        f"Test rows              : {len(x_test):,} "
        f"({test_share:.1f}%, kept untouched)"
    )
    results = []
    for model_name in model_names:
        model = build_model(model_name)
        evaluation_model = model
        best_parameters = "Fixed submitted/default settings"
        candidate_count = 1
        evaluation_key = "grid_search" if grid_search else "fixed"

        if grid_search:
            search_outcome = run_grid_search(
                model,
                parameter_grid(model_name),
                x_train,
                y_train,
                folds=5,
            )
            fold_scores = search_outcome.fold_scores
            evaluation_model = search_outcome.best_estimator
            best_parameters = search_outcome.best_parameters_text
            candidate_count = search_outcome.candidate_count
            search_outcome.candidate_table.to_csv(
                EVALUATION_FOLDER
                / f"{run_key}_{model_name}_grid_search_candidates.csv",
                index=False,
            )
            print(
                f"{model_name:<13} | Grid candidates: {candidate_count}"
                f" | best: {best_parameters}"
            )
        else:
            fold_scores = cross_validation_scores(
                model,
                x_train,
                y_train,
                folds=5,
            )

        cv_table = pd.DataFrame({
            "fold": range(1, 6),
            "MAE": fold_scores["MAE"],
            "RMSE": fold_scores["RMSE"],
            "R2": fold_scores["R2"],
        })
        cv_table.to_csv(
            EVALUATION_FOLDER
            / f"{run_key}_{model_name}_{evaluation_key}_cv_scores.csv",
            index=False,
        )

        average_mae = cv_table["MAE"].mean()
        average_rmse = cv_table["RMSE"].mean()
        average_r2 = cv_table["R2"].mean()
        print(
            f"{model_name:<10} | CV MAE: {average_mae:.3f}"
            f" | CV RMSE: {average_rmse:.3f}"
            f" | CV R2: {average_r2:.3f}"
        )

        class_scores = None
        if class_evaluation:
            class_scores, confusion_table = cross_validation_class_view(
                evaluation_model,
                x_train,
                y_train,
                folds=5,
                margin=class_margin,
            )
            confusion_table.to_csv(
                EVALUATION_FOLDER
                / f"{run_key}_{model_name}_{evaluation_key}_class_confusion_matrix.csv",
                index=True,
            )
            print(
                f"{'':<10} | OOF accuracy: {class_scores['Accuracy']:.3f}"
                f" | within +/-{class_margin}: "
                f"{class_scores['Within_Margin_Accuracy']:.3f}"
                f" | macro precision: {class_scores['Macro_Precision']:.3f}"
                f" | balanced: {class_scores['Balanced_Accuracy']:.3f}"
                f" | macro F1: {class_scores['Macro_F1']:.3f}"
            )

        result_row = {
            "dataset": dataset_name,
            "model": model_name,
            "duplicates": duplicate_action,
            "outliers": outlier_policy,
            "stratified_split": stratified_split,
            "ranked_split": ranked_split,
            "split_method": split_name,
            "original_rows": len(raw_data),
            "duplicates_found": duplicates_found,
            "duplicates_removed": duplicates_removed,
            "rows_after_duplicate_handling": len(data),
            "feature_count": x_train.shape[1],
            "features": ", ".join(actual_feature_columns),
            "feature_engineering": feature_engineering,
            "training_rows_before_outliers": training_rows_before_outliers,
            "training_rows": len(x_train),
            "test_rows": len(x_test),
            "extreme_training_rows": outlier_rows,
            "outliers_removed": outliers_removed,
            "CV_MAE": round(average_mae, 4),
            "CV_RMSE": round(average_rmse, 4),
            "CV_R2": round(average_r2, 4),
            "Grid_Search": grid_search,
            "Grid_Candidates": candidate_count,
            "Best_Parameters": best_parameters,
            "Selection_Metric": "CV MAE" if grid_search else "Not applicable",
        }
        if class_scores is not None:
            result_row.update({
                "Class_Margin": class_margin,
                "OOF_Accuracy": round(
                    class_scores["Accuracy"],
                    4,
                ),
                "OOF_Within_Margin_Accuracy": round(
                    class_scores["Within_Margin_Accuracy"],
                    4,
                ),
                "OOF_Macro_Precision": round(
                    class_scores["Macro_Precision"],
                    4,
                ),
                "OOF_Balanced_Accuracy": round(
                    class_scores["Balanced_Accuracy"],
                    4,
                ),
                "OOF_Macro_F1": round(class_scores["Macro_F1"], 4),
            })
        results.append(result_row)

    return results


def main(
    wine_choice: str = DEFAULT_WINE,
    model_choice: str = DEFAULT_MODEL,
    remove_duplicates: bool = DEFAULT_REMOVE_DUPLICATES,
    remove_outliers: bool = DEFAULT_REMOVE_OUTLIERS,
    stratified_split: bool = DEFAULT_STRATIFIED_SPLIT,
    ranked_split: bool = DEFAULT_RANKED_SPLIT,
    feature_columns: list[str] | None = None,
    feature_engineering: str = DEFAULT_FEATURE_ENGINEERING,
    class_evaluation: bool = DEFAULT_CLASS_EVALUATION,
    class_margin: int = DEFAULT_CLASS_MARGIN,
    grid_search: bool = DEFAULT_GRID_SEARCH,
) -> None:
    """Run the chosen dataset and model configuration."""
    if not 0 <= class_margin <= 10:
        raise ValueError("The class margin must be between 0 and 10.")
    if feature_engineering not in {"none", "ratios"}:
        raise ValueError("Feature engineering must be 'none' or 'ratios'.")

    model_names = selected_models(model_choice)
    selected_features = feature_columns or DEFAULT_FEATURES.copy()
    duplicate_key = "remove_duplicates" if remove_duplicates else "keep_duplicates"
    outlier_key = "remove_outliers" if remove_outliers else "keep_outliers"
    split_key, split_name = split_configuration(
        stratified_split,
        ranked_split,
    )
    feature_key = feature_configuration_key(selected_features)
    engineering_key = (
        "_ratio_features" if feature_engineering == "ratios" else ""
    )
    class_key = (
        f"class_margin_{class_margin}"
        if class_evaluation
        else "no_class_evaluation"
    )

    print("=" * 70)
    print("Wine Quality Project - shared model comparison")
    print(f"Wine selection : {wine_choice}")
    print(f"Model selection: {model_choice}")
    print(f"Grid search    : {'enabled' if grid_search else 'disabled'}")
    print(f"Duplicates     : {'remove' if remove_duplicates else 'keep'}")
    print(f"Outliers       : {'remove from training' if remove_outliers else 'keep'}")
    print(f"Split method   : {split_name}")
    print(f"Raw features   : {', '.join(selected_features)}")
    print(f"Feature eng.   : {feature_engineering}")
    print("Split size     : about 80% training / 20% test")
    print("Evaluation     : 5-fold training CV with MAE, RMSE, and R2")
    if class_evaluation:
        print(f"Class view     : enabled | accepted margin: +/-{class_margin}")
    else:
        print("Class view     : disabled")
    print("=" * 70)

    results = []
    for dataset_name, dataset_key, csv_path in selected_datasets(wine_choice):
        results.extend(
            run_dataset(
                dataset_name,
                dataset_key,
                csv_path,
                model_names,
                remove_duplicates,
                remove_outliers,
                stratified_split,
                ranked_split,
                selected_features,
                feature_engineering,
                class_evaluation,
                class_margin,
                grid_search,
            )
        )

    result_table = pd.DataFrame(results)
    RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)
    result_path = RESULTS_FOLDER / (
        f"{wine_choice}_{model_choice}_{duplicate_key}_{outlier_key}_"
        f"{split_key}_{feature_key}{engineering_key}_{class_key}_"
        f"{'grid_search' if grid_search else 'fixed'}_results.csv"
    )
    result_table.to_csv(result_path, index=False)

    print("\nComparison")
    print("----------")
    comparison_columns = [
        "dataset",
        "model",
        "duplicates",
        "outliers",
        "stratified_split",
        "ranked_split",
        "feature_engineering",
        "feature_count",
        "CV_MAE",
        "CV_RMSE",
        "CV_R2",
    ]
    if class_evaluation:
        comparison_columns.extend([
            "Class_Margin",
            "OOF_Accuracy",
            "OOF_Within_Margin_Accuracy",
            "OOF_Macro_Precision",
            "OOF_Balanced_Accuracy",
            "OOF_Macro_F1",
        ])

    print(
        result_table[comparison_columns]
        .sort_values(["dataset", "CV_MAE"])
        .to_string(index=False)
    )
    print(f"\nSaved results: {result_path}")
    print("The 20% test data has not been scored and stays reserved for the final model.")


if __name__ == "__main__":
    arguments = parse_arguments()
    main(
        wine_choice=arguments.wine,
        model_choice=arguments.model,
        remove_duplicates=arguments.remove_duplicates,
        remove_outliers=arguments.remove_outliers,
        stratified_split=arguments.stratified_split,
        ranked_split=arguments.ranked_split,
        feature_columns=arguments.features,
        feature_engineering=arguments.feature_engineering,
        class_evaluation=arguments.class_evaluation,
        class_margin=arguments.class_margin,
        grid_search=arguments.grid_search,
    )

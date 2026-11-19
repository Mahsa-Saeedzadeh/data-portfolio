"""Run a locked, one-time evaluation on the reserved 20% holdout."""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd

from src.best_model_configs import (
    FINAL_SELECTIONS,
    best_parameters,
    build_best_model,
    validate_best_model_configs,
)
from src.data_split import (
    FEATURE_COLUMNS,
    handle_duplicates,
    load_wine_data,
    split_wine_data,
)
from src.evaluate import regression_scores
from src.evaluate_as_classes import (
    class_confusion_table,
    class_view_scores,
    rounded_quality_predictions,
)
from src.model_tuning import readable_parameters
from src.models import FINAL_TEST_MODEL_NAMES
from src.preprocessing import handle_training_outliers


PROJECT_FOLDER = Path(__file__).resolve().parent
RAW_FOLDER = PROJECT_FOLDER / "data" / "raw-input"
FINAL_RESULTS_FOLDER = PROJECT_FOLDER / "data" / "final-results"
LOCK_PATH = PROJECT_FOLDER / "FINAL_TEST_LOCK.json"
RESULTS_PATH = FINAL_RESULTS_FOLDER / "final_test_results.csv"
PREDICTIONS_PATH = FINAL_RESULTS_FOLDER / "final_test_predictions.csv"
CONFUSION_PATH = FINAL_RESULTS_FOLDER / "final_test_confusion.csv"
STARTED_PATH = FINAL_RESULTS_FOLDER / "FINAL_TEST_STARTED.json"
COMPLETED_PATH = FINAL_RESULTS_FOLDER / "FINAL_TEST_COMPLETED.json"
FAILED_PATH = FINAL_RESULTS_FOLDER / "FINAL_TEST_FAILED.json"
REPORT_PATH = PROJECT_FOLDER / "FINAL_TEST_RESULTS.md"

DATASETS = {
    "red": ("Red wine", RAW_FOLDER / "winequality-red.csv"),
    "white": ("White wine", RAW_FOLDER / "winequality-white.csv"),
}

EXPECTED_COUNTS = {
    "red": {
        "raw_rows": 1599,
        "duplicates": 240,
        "training_rows_before_outliers": 1087,
        "outliers": 117,
        "training_rows": 970,
        "test_rows": 272,
    },
    "white": {
        "raw_rows": 4898,
        "duplicates": 937,
        "training_rows_before_outliers": 3168,
        "outliers": 145,
        "training_rows": 3023,
        "test_rows": 793,
    },
}

CLASS_MARGIN = 1
POLICY = {
    "remove_duplicates": True,
    "remove_training_outliers": True,
    "iqr_multiplier": 3.0,
    "stratified_split": True,
    "ranked_split": True,
    "features": FEATURE_COLUMNS,
    "class_margin": CLASS_MARGIN,
    "selection_metric": "five-fold training CV MAE",
}

RESULT_METRICS = [
    "CV_MAE",
    "CV_RMSE",
    "CV_R2",
    "Test_MAE",
    "Test_RMSE",
    "Test_R2",
    "Test_Accuracy",
    "Test_Within_Margin_Accuracy",
    "Test_Macro_Precision",
    "Test_Balanced_Accuracy",
    "Test_Macro_F1",
]


def parse_arguments() -> argparse.Namespace:
    """Read the deliberately guarded final-test command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wine",
        choices=("red", "white", "both"),
        default="both",
        help="Lock red, white, or both wine configurations.",
    )
    parser.add_argument(
        "--model",
        choices=("finalists", *FINAL_TEST_MODEL_NAMES),
        default="finalists",
        help=(
            "Lock the two declared finalists or one configured model. "
            "The official project choice is 'finalists'."
        ),
    )
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--freeze-lock",
        action="store_true",
        help="Create the immutable pre-test lock without fitting or scoring.",
    )
    action.add_argument(
        "--dry-run",
        action="store_true",
        help="Verify the frozen lock and print the required confirmation.",
    )
    action.add_argument(
        "--execute-final-test",
        action="store_true",
        help="Fit the locked models and score the reserved holdout once.",
    )
    action.add_argument(
        "--rebuild-report",
        action="store_true",
        help="Rebuild Markdown only from verified completed result files.",
    )
    parser.add_argument(
        "--confirm",
        default="",
        help="Exact confirmation phrase printed by --dry-run.",
    )
    return parser.parse_args()


def _canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256(path: Path) -> str:
    """Return the SHA-256 hash of one file."""
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for block in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _payload_hash(payload: dict) -> str:
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _table_hash(table: pd.DataFrame) -> str:
    """Hash a prepared table without saving or displaying its holdout rows."""
    metadata = {
        "columns": table.columns.tolist(),
        "dtypes": [str(dtype) for dtype in table.dtypes],
        "shape": list(table.shape),
    }
    row_hashes = pd.util.hash_pandas_object(table, index=True).to_numpy()
    digest = hashlib.sha256(_canonical_json(metadata).encode("utf-8"))
    digest.update(row_hashes.tobytes())
    return digest.hexdigest()


def _wine_choices(wine_choice: str) -> list[str]:
    return ["red", "white"] if wine_choice == "both" else [wine_choice]


def _selected_specs(wine_choice: str, model_choice: str) -> list[dict]:
    """Return the declared finalists or one alternative lock scope."""
    specifications = []
    for wine in _wine_choices(wine_choice):
        roles = FINAL_SELECTIONS[wine]
        if model_choice == "finalists":
            selected = list(roles.items())
        else:
            role = next(
                (name for name, model in roles.items() if model == model_choice),
                "additional",
            )
            selected = [(role, model_choice)]
        for role, model_name in selected:
            specifications.append({
                "wine": wine,
                "role": role,
                "model": model_name,
            })
    return specifications


def _candidate_path(wine: str, model_name: str) -> Path:
    return PROJECT_FOLDER / "data" / "evaluate" / (
        f"{wine}_wine_duplicates_removed_remove_outliers_stratified_ranked_"
        f"all_features_{model_name}_grid_search_candidates.csv"
    )


def _validated_cv_result(wine: str, model_name: str) -> dict:
    """Match one config to its saved rank-one training-CV candidate."""
    candidate_path = _candidate_path(wine, model_name)
    if not candidate_path.exists():
        raise FileNotFoundError(f"Missing CV evidence: {candidate_path.name}")

    candidates = pd.read_csv(candidate_path)
    required_columns = {
        "search_rank",
        "parameters",
        "CV_MAE",
        "CV_RMSE",
        "CV_R2",
    }
    missing_columns = sorted(required_columns - set(candidates.columns))
    if candidates.empty or missing_columns:
        raise ValueError(
            f"Invalid CV evidence in {candidate_path.name}; "
            f"missing columns={missing_columns}."
        )

    configured_text = readable_parameters(best_parameters(wine, model_name))
    winner = candidates.iloc[0]
    if int(winner["search_rank"]) != 1:
        raise ValueError(f"First candidate is not rank one in {candidate_path.name}.")
    if winner["parameters"] != configured_text:
        raise ValueError(
            f"Locked config does not match {candidate_path.name}. "
            "Do not freeze or run the final test until this is reviewed."
        )

    metrics = winner[["CV_MAE", "CV_RMSE", "CV_R2"]].astype(float)
    if not np.isfinite(metrics.to_numpy()).all():
        raise ValueError(f"Non-finite CV result in {candidate_path.name}.")

    return {
        "parameters": configured_text,
        "CV_MAE": float(winner["CV_MAE"]),
        "CV_RMSE": float(winner["CV_RMSE"]),
        "CV_R2": float(winner["CV_R2"]),
        "candidate_file": str(candidate_path.relative_to(PROJECT_FOLDER)).replace(
            "\\", "/"
        ),
        "candidate_sha256": _sha256(candidate_path),
    }


def _configuration_catalog() -> tuple[list[dict], dict]:
    """Validate and record all 26 wine/model configurations."""
    catalog = []
    lookup = {}
    for wine in DATASETS:
        for model_name in FINAL_TEST_MODEL_NAMES:
            # Construction catches invalid deep pipeline parameter names.
            build_best_model(wine, model_name)
            evidence = _validated_cv_result(wine, model_name)
            record = {"wine": wine, "model": model_name, **evidence}
            catalog.append(record)
            lookup[(wine, model_name)] = evidence
    return catalog, lookup


def _prepare_dataset(wine: str) -> dict:
    """Reproduce the frozen policy and verify every prepared row count."""
    dataset_name, csv_path = DATASETS[wine]
    raw_data = load_wine_data(csv_path)
    data, duplicates_found, duplicates_removed = handle_duplicates(
        raw_data,
        remove_duplicates=True,
    )
    x_train, x_test, y_train, y_test = split_wine_data(
        data,
        FEATURE_COLUMNS,
        stratified=True,
        ranked=True,
    )
    training_rows_before_outliers = len(x_train)
    (
        x_train,
        y_train,
        _outlier_report,
        outliers_found,
        outliers_removed,
    ) = handle_training_outliers(
        x_train,
        y_train,
        remove_outliers=True,
        iqr_multiplier=3.0,
    )

    actual_counts = {
        "raw_rows": len(raw_data),
        "duplicates": duplicates_found,
        "training_rows_before_outliers": training_rows_before_outliers,
        "outliers": outliers_found,
        "training_rows": len(x_train),
        "test_rows": len(x_test),
    }
    if actual_counts != EXPECTED_COUNTS[wine]:
        raise ValueError(
            f"Prepared {wine} row counts changed: {actual_counts}. "
            "The final test is blocked until this is reviewed."
        )
    if duplicates_removed != duplicates_found or outliers_removed != outliers_found:
        raise ValueError("The frozen duplicate/outlier policy was not reproduced.")

    train_table = x_train.copy()
    train_table["quality"] = y_train.to_numpy()
    test_table = x_test.copy()
    test_table["quality"] = y_test.to_numpy()

    return {
        "dataset_name": dataset_name,
        "x_train": x_train,
        "x_test": x_test,
        "y_train": y_train,
        "y_test": y_test,
        "counts": actual_counts,
        "train_sha256": _table_hash(train_table),
        "test_sha256": _table_hash(test_table),
    }


def _source_hashes() -> dict:
    source_files = [PROJECT_FOLDER / "main.py", PROJECT_FOLDER / "final_test.py"]
    source_files.extend(sorted((PROJECT_FOLDER / "src").rglob("*.py")))
    return {
        str(path.relative_to(PROJECT_FOLDER)).replace("\\", "/"): _sha256(path)
        for path in source_files
    }


def _run_preflight(
    specifications: list[dict],
    requested_scope: dict,
    frozen_at: str,
) -> tuple[dict, dict, list[dict]]:
    """Validate all non-scoring inputs and build unfitted estimators."""
    validate_best_model_configs()
    catalog, catalog_lookup = _configuration_catalog()

    prepared_data = {}
    for wine in dict.fromkeys(item["wine"] for item in specifications):
        prepared_data[wine] = _prepare_dataset(wine)

    prepared_models = []
    selected_records = []
    for specification in specifications:
        wine = specification["wine"]
        model_name = specification["model"]
        evidence = catalog_lookup[(wine, model_name)]
        selected_record = {**specification, **evidence}
        selected_records.append(selected_record)
        prepared_models.append({
            "specification": specification,
            "cv_result": evidence,
            "estimator": build_best_model(wine, model_name),
        })

    prepared_fingerprints = {
        wine: {
            "counts": values["counts"],
            "train_sha256": values["train_sha256"],
            "test_sha256": values["test_sha256"],
        }
        for wine, values in prepared_data.items()
    }
    payload = {
        "schema": 2,
        "lock_metadata": {
            "status": "frozen",
            "frozen_at": frozen_at,
            "requested_scope": requested_scope,
        },
        "policy": POLICY,
        "expected_counts": {
            wine: EXPECTED_COUNTS[wine]
            for wine in prepared_data
        },
        "data_sha256": {
            wine: _sha256(csv_path)
            for wine, (_, csv_path) in DATASETS.items()
        },
        "prepared_data": prepared_fingerprints,
        "source_sha256": _source_hashes(),
        "reference_sha256": {
            "requirements.txt": _sha256(PROJECT_FOLDER / "requirements.txt"),
        },
        "packages": {
            package: version(package)
            for package in ("numpy", "pandas", "scikit-learn", "xgboost")
        },
        "configuration_catalog": catalog,
        "selected_models": selected_records,
    }
    return payload, prepared_data, prepared_models


def _write_json_exclusive(path: Path, value: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as file_handle:
        json.dump(value, file_handle, indent=2, sort_keys=True, allow_nan=False)
        file_handle.write("\n")


def _read_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as file_handle:
            value = json.load(file_handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read valid JSON from {path}.") from error
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return value


def _existing_final_test() -> bool:
    """Return True if any start, failure, result, or report already exists."""
    if REPORT_PATH.exists():
        return True
    if not FINAL_RESULTS_FOLDER.exists():
        return False
    return any(FINAL_RESULTS_FOLDER.iterdir())


def _freeze_lock(arguments, specifications: list[dict]) -> None:
    """Create the reviewed lock before any model receives holdout rows."""
    if LOCK_PATH.exists():
        raise RuntimeError(
            "FINAL_TEST_LOCK.json already exists and cannot be overwritten."
        )
    if _existing_final_test():
        raise RuntimeError("Final-test output already exists; a lock cannot be frozen.")

    frozen_at = datetime.now().astimezone().isoformat(timespec="seconds")
    requested_scope = {
        "wine": arguments.wine,
        "model": arguments.model,
    }
    payload, _prepared_data, _prepared_models = _run_preflight(
        specifications,
        requested_scope,
        frozen_at,
    )
    full_lock_hash = _payload_hash(payload)
    lock_id = full_lock_hash[:12]
    lock_record = {
        "status": "frozen",
        "frozen_at": frozen_at,
        "lock_id": lock_id,
        "full_lock_sha256": full_lock_hash,
        "requested_scope": requested_scope,
        "lock_payload": payload,
    }
    _write_json_exclusive(LOCK_PATH, lock_record)

    print("Final-test lock frozen")
    print("----------------------")
    print(f"Lock            : {lock_id}")
    print(f"Wine scope      : {arguments.wine}")
    print(f"Model scope     : {arguments.model}")
    print(f"Locked rows     : {len(specifications)}")
    print("All 26 best-parameter mappings were included in the lock.")
    print("No model was fitted and no holdout prediction or score was produced.")
    print("\nNext safe check:")
    print(
        f"python final_test.py --wine {arguments.wine} "
        f"--model {arguments.model} --dry-run"
    )


def _load_frozen_lock() -> dict:
    if not LOCK_PATH.exists():
        raise FileNotFoundError(
            "FINAL_TEST_LOCK.json is missing. Review the choices and run "
            "--freeze-lock before a dry run."
        )
    lock_record = _read_json(LOCK_PATH)
    required = {
        "status",
        "frozen_at",
        "lock_id",
        "full_lock_sha256",
        "requested_scope",
        "lock_payload",
    }
    missing = sorted(required - set(lock_record))
    extra = sorted(set(lock_record) - required)
    if missing or extra or lock_record.get("status") != "frozen":
        raise ValueError(
            f"Invalid final-test lock; missing={missing}, extra={extra}."
        )

    try:
        frozen_time = datetime.fromisoformat(lock_record["frozen_at"])
    except (TypeError, ValueError) as error:
        raise ValueError("The frozen lock has an invalid timestamp.") from error
    if frozen_time.tzinfo is None:
        raise ValueError("The frozen lock timestamp must include its timezone.")

    expected_metadata = {
        "status": lock_record["status"],
        "frozen_at": lock_record["frozen_at"],
        "requested_scope": lock_record["requested_scope"],
    }
    if lock_record["lock_payload"].get("lock_metadata") != expected_metadata:
        raise ValueError("The outer lock metadata differs from its hashed payload.")

    calculated_hash = _payload_hash(lock_record["lock_payload"])
    if calculated_hash != lock_record["full_lock_sha256"]:
        raise ValueError("FINAL_TEST_LOCK.json has been changed after freezing.")
    if lock_record["lock_id"] != calculated_hash[:12]:
        raise ValueError("The short lock ID does not match the frozen payload.")
    return lock_record


def _check_requested_scope(arguments, lock_record: dict) -> None:
    requested_scope = {
        "wine": arguments.wine,
        "model": arguments.model,
    }
    if requested_scope != lock_record["requested_scope"]:
        raise ValueError(
            "This command does not match the frozen scope. Use exactly "
            f"--wine {lock_record['requested_scope']['wine']} --model "
            f"{lock_record['requested_scope']['model']}."
        )


def _check_current_state(payload: dict, lock_record: dict) -> None:
    current_hash = _payload_hash(payload)
    if (
        current_hash != lock_record["full_lock_sha256"]
        or payload != lock_record["lock_payload"]
    ):
        raise ValueError(
            "Data, source, packages, CV evidence, preparation, or model "
            "configuration changed after the final-test lock was frozen. "
            "The holdout must not be scored until this is reviewed."
        )


def _print_lock_summary(arguments, specifications: list[dict], lock_id: str) -> None:
    print("Final holdout evaluation")
    print("------------------------")
    print(f"Wines           : {arguments.wine}")
    print(f"Model choice    : {arguments.model}")
    print(f"Locked rows     : {len(specifications)}")
    print(f"Configuration   : {lock_id}")
    for specification in specifications:
        print(
            f"  {specification['wine']:<5} | {specification['role']:<10} "
            f"| {specification['model']}"
        )


def _evaluate_locked_models(
    prepared_models: list[dict],
    prepared_data: dict,
    lock_id: str,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Fit the frozen estimators once and retain their holdout outputs."""
    result_rows = []
    prediction_tables = []
    confusion_tables = []
    run_time = datetime.now().astimezone().isoformat(timespec="seconds")

    for prepared_model in prepared_models:
        specification = prepared_model["specification"]
        cv_result = prepared_model["cv_result"]
        model = prepared_model["estimator"]
        wine = specification["wine"]
        model_name = specification["model"]
        data = prepared_data[wine]
        x_train = data["x_train"]
        x_test = data["x_test"]
        y_train = data["y_train"]
        y_test = data["y_test"]
        counts = data["counts"]

        start = perf_counter()
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        fit_and_predict_seconds = perf_counter() - start

        regression = regression_scores(y_test, predictions)
        class_scores = class_view_scores(
            y_test,
            predictions,
            margin=CLASS_MARGIN,
        )
        rounded_predictions = rounded_quality_predictions(predictions)

        result_rows.append({
            "run_time": run_time,
            "lock_id": lock_id,
            "role": specification["role"],
            "wine": wine,
            "dataset": data["dataset_name"],
            "model": model_name,
            "training_rows": counts["training_rows"],
            "test_rows": counts["test_rows"],
            "duplicates_removed": counts["duplicates"],
            "training_outliers_removed": counts["outliers"],
            "feature_count": len(FEATURE_COLUMNS),
            "parameters": cv_result["parameters"],
            "CV_MAE": cv_result["CV_MAE"],
            "CV_RMSE": cv_result["CV_RMSE"],
            "CV_R2": cv_result["CV_R2"],
            "Test_MAE": regression["MAE"],
            "Test_RMSE": regression["RMSE"],
            "Test_R2": regression["R2"],
            "Class_Margin": CLASS_MARGIN,
            "Test_Accuracy": class_scores["Accuracy"],
            "Test_Within_Margin_Accuracy": class_scores[
                "Within_Margin_Accuracy"
            ],
            "Test_Macro_Precision": class_scores["Macro_Precision"],
            "Test_Balanced_Accuracy": class_scores["Balanced_Accuracy"],
            "Test_Macro_F1": class_scores["Macro_F1"],
            "fit_and_predict_seconds": fit_and_predict_seconds,
        })

        actual_values = y_test.to_numpy()
        prediction_tables.append(pd.DataFrame({
            "lock_id": lock_id,
            "wine": wine,
            "model": model_name,
            "role": specification["role"],
            "test_position": range(len(y_test)),
            "actual_quality": actual_values,
            "predicted_quality": predictions,
            "rounded_prediction": rounded_predictions,
            "absolute_error": np.abs(actual_values - predictions),
            "within_margin": (
                np.abs(actual_values - rounded_predictions) <= CLASS_MARGIN
            ),
        }))

        confusion = class_confusion_table(y_test, predictions)
        long_confusion = (
            confusion.rename_axis("actual_class")
            .reset_index()
            .melt(
                id_vars="actual_class",
                var_name="predicted_class",
                value_name="count",
            )
        )
        long_confusion["actual_class"] = long_confusion["actual_class"].map(
            lambda value: int(str(value).removeprefix("actual_"))
        )
        long_confusion["predicted_class"] = long_confusion[
            "predicted_class"
        ].map(lambda value: int(str(value).removeprefix("predicted_")))
        long_confusion.insert(0, "role", specification["role"])
        long_confusion.insert(0, "model", model_name)
        long_confusion.insert(0, "wine", wine)
        long_confusion.insert(0, "lock_id", lock_id)
        confusion_tables.append(long_confusion)

    return (
        pd.DataFrame(result_rows),
        pd.concat(prediction_tables, ignore_index=True),
        pd.concat(confusion_tables, ignore_index=True),
    )


def _wine_choices_from_rows(rows: list[dict]) -> list[str]:
    return list(dict.fromkeys(item["wine"] for item in rows))


def _markdown_cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def build_report(results: pd.DataFrame) -> str:
    """Create the permanent human-readable record from verified metrics."""
    run_time = results["run_time"].iloc[0]
    lock_id = results["lock_id"].iloc[0]
    role_order = {"primary": 0, "comparison": 1, "additional": 2}
    report_rows = results.copy()
    report_rows["role_order"] = report_rows["role"].map(role_order).fillna(3)
    report_rows = report_rows.sort_values(["wine", "role_order", "model"])

    primary_rows = report_rows[report_rows["role"] == "primary"]
    comparison_rows = report_rows[report_rows["role"] == "comparison"]
    if not primary_rows.empty and not comparison_rows.empty:
        primary_names = ", ".join(sorted(primary_rows["model"].unique()))
        comparison_names = ", ".join(sorted(comparison_rows["model"].unique()))
        selection_note = (
            f"{primary_names} was declared as the primary model and "
            f"{comparison_names} as the single comparison before these rows "
            "were scored."
        )
    else:
        selected_names = ", ".join(sorted(report_rows["model"].unique()))
        selection_note = (
            f"The locked {selected_names} configuration was selected before "
            "these rows were scored."
        )

    wines = _wine_choices_from_rows(report_rows.to_dict("records"))
    if wines == ["red", "white"]:
        wine_policy = "Red and white wines were evaluated separately."
    else:
        wine_policy = f"{wines[0].capitalize()} wine was evaluated separately."

    lines = [
        "# Final Holdout Results",
        "",
        "Status: **COMPLETE - the reserved 20% holdout has now been consumed.**",
        "",
        f"Run time: `{run_time}`  ",
        f"Configuration lock: `{lock_id}`",
        "",
        selection_note + " The test data was not used for preprocessing "
        "choices, feature selection, or parameter tuning.",
        "",
        "> Do not tune models or test additional alternatives against these "
        "same rows. A new development cycle needs new unseen data or a newly "
        "defined evaluation protocol.",
        "",
        "## Frozen test policy",
        "",
        wine_policy + " Exact duplicates were removed before the fixed "
        "quality-stratified and feature-ranked 80/20 split. All 11 features "
        "were used. The 3 x IQR rule removed rows from training only; no "
        "holdout row was removed. Each model was fitted once on the prepared "
        "training portion, and the rounded class view used margin 1.",
        "",
        "## Metric legend",
        "",
        "| Metric | Simple meaning | Better direction |",
        "|---|---|---|",
        "| Test MAE | Average absolute error in quality points; the primary measure. | Lower |",
        "| Test RMSE | Error in quality points with larger misses penalized more. | Lower |",
        "| Test R2 | Holdout variation explained relative to predicting the mean. | Higher |",
        "| Test accuracy | Exact match after rounding to a quality class. | Higher |",
        "| Test +/-1 | Rounded prediction is within one quality point. | Higher |",
        "| Macro precision | Per-class precision averaged across classes. | Higher |",
        "| Balanced accuracy | Per-class recall averaged across true classes. | Higher |",
        "| Macro F1 | Per-class F1 averaged across classes. | Higher |",
        "",
        "## One-time results",
        "",
        "| Role | Wine | Model | Train rows | Test rows | CV MAE | Test MAE | "
        "Test RMSE | Test R2 | Test accuracy | Test +/-1 | Macro precision | "
        "Balanced | Macro F1 | Locked setup |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in report_rows.iterrows():
        role = row["role"].capitalize()
        wine = row["wine"].capitalize()
        setup = _markdown_cell(row["parameters"])
        lines.append(
            f"| {role} | {wine} | {row['model']} | "
            f"{int(row['training_rows']):,} | {int(row['test_rows']):,} | "
            f"{row['CV_MAE']:.6f} | {row['Test_MAE']:.6f} | "
            f"{row['Test_RMSE']:.6f} | {row['Test_R2']:.6f} | "
            f"{row['Test_Accuracy']:.6f} | "
            f"{row['Test_Within_Margin_Accuracy']:.6f} | "
            f"{row['Test_Macro_Precision']:.6f} | "
            f"{row['Test_Balanced_Accuracy']:.6f} | "
            f"{row['Test_Macro_F1']:.6f} | {setup} |"
        )

    lines.extend(["", "## Interpretation", ""])
    paired_interpretation = False
    for wine in wines:
        wine_rows = report_rows[report_rows["wine"] == wine]
        primary = wine_rows[wine_rows["role"] == "primary"]
        comparison = wine_rows[wine_rows["role"] == "comparison"]
        if primary.empty or comparison.empty:
            continue
        paired_interpretation = True
        primary_row = primary.iloc[0]
        comparison_row = comparison.iloc[0]
        primary_name = str(primary_row["model"]).replace("_", " ").title()
        comparison_name = str(comparison_row["model"]).replace("_", " ").title()
        difference = comparison_row["Test_MAE"] - primary_row["Test_MAE"]
        if difference >= 0:
            conclusion = (
                f"{primary_name} remained lower by {difference:.6f} MAE points."
            )
        else:
            conclusion = (
                f"{comparison_name} was lower by {abs(difference):.6f} MAE "
                f"points, but {primary_name} remains the predeclared primary "
                "result."
            )
        lines.append(
            f"- **{wine.capitalize()}:** {primary_name} test MAE is "
            f"{primary_row['Test_MAE']:.6f}; {comparison_name} test MAE is "
            f"{comparison_row['Test_MAE']:.6f}. {conclusion}"
        )

    if not paired_interpretation:
        for _, row in report_rows.iterrows():
            model_name = str(row["model"]).replace("_", " ").title()
            lines.append(
                f"- **{row['wine'].capitalize()}:** {model_name} test MAE is "
                f"{row['Test_MAE']:.6f}, test RMSE is {row['Test_RMSE']:.6f}, "
                f"and test R2 is {row['Test_R2']:.6f}."
            )

    lines.extend([
        "",
        "The prediction-level audit trail is saved in "
        "`data/final-results/final_test_predictions.csv`; the long-form "
        "confusion counts are in `final_test_confusion.csv`.",
        "",
        "## Integrity note",
        "",
        "`FINAL_TEST_LOCK.json`, `FINAL_TEST_STARTED.json`, and "
        "`FINAL_TEST_COMPLETED.json` permanently record this run. The script "
        "refuses another final evaluation in this project folder. "
        "`--rebuild-report` may recreate this Markdown file only after it "
        "verifies the completed CSV hashes and row structure; it never fits "
        "or predicts again.",
        "",
    ])
    return "\n".join(lines)


def _expected_specs(lock_record: dict) -> list[tuple[str, str, str]]:
    return sorted(
        (
            item["wine"],
            item["role"],
            item["model"],
        )
        for item in lock_record["lock_payload"]["selected_models"]
    )


def _validate_result_tables(
    results: pd.DataFrame,
    predictions: pd.DataFrame,
    confusion: pd.DataFrame,
    lock_record: dict,
) -> None:
    """Check complete row coverage before publishing or rebuilding a report."""
    lock_id = lock_record["lock_id"]
    required_results = {
        "lock_id",
        "wine",
        "role",
        "model",
        "training_rows",
        "test_rows",
        *RESULT_METRICS,
    }
    required_predictions = {
        "lock_id",
        "wine",
        "role",
        "model",
        "test_position",
        "actual_quality",
        "predicted_quality",
        "rounded_prediction",
        "absolute_error",
        "within_margin",
    }
    required_confusion = {
        "lock_id",
        "wine",
        "role",
        "model",
        "actual_class",
        "predicted_class",
        "count",
    }
    for table_name, table, required in (
        ("results", results, required_results),
        ("predictions", predictions, required_predictions),
        ("confusion", confusion, required_confusion),
    ):
        missing = sorted(required - set(table.columns))
        if table.empty or missing:
            raise ValueError(f"Invalid {table_name} table; missing={missing}.")
        if set(table["lock_id"].astype(str)) != {lock_id}:
            raise ValueError(f"Unexpected lock ID in {table_name} table.")

    metric_values = results[RESULT_METRICS].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(metric_values.to_numpy()).all():
        raise ValueError("Final result metrics contain a missing or infinite value.")

    prediction_values = predictions[
        [
            "test_position",
            "actual_quality",
            "predicted_quality",
            "rounded_prediction",
            "absolute_error",
        ]
    ].apply(pd.to_numeric, errors="coerce")
    if not np.isfinite(prediction_values.to_numpy()).all():
        raise ValueError("Saved predictions contain a missing or infinite value.")

    confusion_counts = pd.to_numeric(confusion["count"], errors="coerce")
    if (
        not np.isfinite(confusion_counts.to_numpy()).all()
        or (confusion_counts < 0).any()
        or not np.equal(confusion_counts, np.floor(confusion_counts)).all()
    ):
        raise ValueError("Confusion counts must be finite non-negative integers.")

    actual_specs = sorted(
        tuple(values)
        for values in results[["wine", "role", "model"]].itertuples(
            index=False,
            name=None,
        )
    )
    expected_specs = _expected_specs(lock_record)
    if actual_specs != expected_specs:
        raise ValueError(
            f"Final result rows differ from the frozen selection: {actual_specs}."
        )

    for table_name, table in (
        ("predictions", predictions),
        ("confusion", confusion),
    ):
        table_specs = sorted({
            tuple(values)
            for values in table[["wine", "role", "model"]].itertuples(
                index=False,
                name=None,
            )
        })
        if table_specs != expected_specs:
            raise ValueError(
                f"{table_name.capitalize()} groups differ from the frozen "
                f"selection: {table_specs}."
            )

    prepared_records = lock_record["lock_payload"]["prepared_data"]
    for wine, role, model_name in expected_specs:
        result_row = results[
            (results["wine"] == wine)
            & (results["role"] == role)
            & (results["model"] == model_name)
        ]
        prediction_rows = predictions[
            (predictions["wine"] == wine)
            & (predictions["role"] == role)
            & (predictions["model"] == model_name)
        ]
        confusion_rows = confusion[
            (confusion["wine"] == wine)
            & (confusion["role"] == role)
            & (confusion["model"] == model_name)
        ]
        if len(result_row) != 1:
            raise ValueError(f"Expected one result for {wine}/{role}/{model_name}.")

        expected_train = prepared_records[wine]["counts"]["training_rows"]
        expected_test = prepared_records[wine]["counts"]["test_rows"]
        row = result_row.iloc[0]
        if (
            int(row["training_rows"]) != expected_train
            or int(row["test_rows"]) != expected_test
        ):
            raise ValueError(f"Saved row counts changed for {wine}/{model_name}.")
        if len(prediction_rows) != expected_test:
            raise ValueError(f"Prediction coverage changed for {wine}/{model_name}.")
        positions = sorted(
            pd.to_numeric(
                prediction_rows["test_position"], errors="coerce"
            ).astype(int)
        )
        if positions != list(range(expected_test)):
            raise ValueError(f"Test positions changed for {wine}/{model_name}.")
        confusion_total = pd.to_numeric(
            confusion_rows["count"], errors="coerce"
        ).sum()
        if not np.isfinite(confusion_total) or int(confusion_total) != expected_test:
            raise ValueError(f"Confusion counts changed for {wine}/{model_name}.")


def _staged_path(final_path: Path) -> Path:
    return final_path.with_name(final_path.name + ".pending")


def _stage_csv(data: pd.DataFrame, final_path: Path) -> Path:
    staged_path = _staged_path(final_path)
    data.to_csv(
        staged_path,
        index=False,
        mode="x",
        lineterminator="\n",
    )
    return staged_path


def _stage_text(text: str, final_path: Path) -> Path:
    staged_path = _staged_path(final_path)
    with staged_path.open("x", encoding="utf-8", newline="\n") as file_handle:
        file_handle.write(text)
    return staged_path


def _write_failure(lock_id: str, error: Exception) -> None:
    """Keep a permanent explanation when execution fails after STARTED."""
    if FAILED_PATH.exists() or COMPLETED_PATH.exists():
        return
    failure_record = {
        "status": "failed",
        "failed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "lock_id": lock_id,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "note": "STARTED remains permanent; do not delete markers and retry.",
    }
    try:
        _write_json_exclusive(FAILED_PATH, failure_record)
    except OSError:
        pass


def _load_verified_completed_run() -> tuple[pd.DataFrame, str, dict]:
    """Load saved results only after checking the completed audit trail."""
    lock_record = _load_frozen_lock()
    required_paths = (
        STARTED_PATH,
        COMPLETED_PATH,
        RESULTS_PATH,
        PREDICTIONS_PATH,
        CONFUSION_PATH,
    )
    missing = [str(path) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "A complete final run is required before rebuilding; missing="
            + ", ".join(missing)
        )
    if FAILED_PATH.exists():
        raise RuntimeError("A permanent failure marker exists; report rebuild is blocked.")

    started = _read_json(STARTED_PATH)
    completed = _read_json(COMPLETED_PATH)
    lock_id = lock_record["lock_id"]
    if started.get("status") != "started" or completed.get("status") != "complete":
        raise ValueError("Invalid started/completed status.")
    if {
        started.get("lock_id"),
        completed.get("lock_id"),
    } != {lock_id}:
        raise ValueError("Lock IDs differ across the final-test audit files.")
    if (
        started.get("full_lock_sha256") != lock_record["full_lock_sha256"]
        or completed.get("full_lock_sha256") != lock_record["full_lock_sha256"]
    ):
        raise ValueError("Full lock hashes differ across the audit files.")
    if started.get("frozen_lock_file_sha256") != _sha256(LOCK_PATH):
        raise ValueError("The frozen lock file differs from the started record.")

    artifact_paths = {
        RESULTS_PATH.name: RESULTS_PATH,
        PREDICTIONS_PATH.name: PREDICTIONS_PATH,
        CONFUSION_PATH.name: CONFUSION_PATH,
    }
    recorded_hashes = completed.get("artifacts", {})
    for artifact_name, artifact_path in artifact_paths.items():
        if recorded_hashes.get(artifact_name) != _sha256(artifact_path):
            raise ValueError(f"Saved artifact hash changed: {artifact_name}.")

    results = pd.read_csv(RESULTS_PATH, dtype={"lock_id": "string"})
    predictions = pd.read_csv(PREDICTIONS_PATH, dtype={"lock_id": "string"})
    confusion = pd.read_csv(CONFUSION_PATH, dtype={"lock_id": "string"})
    _validate_result_tables(results, predictions, confusion, lock_record)
    if completed.get("result_rows") != len(results):
        raise ValueError("Completed result-row count does not match the CSV.")
    if completed.get("prediction_rows") != len(predictions):
        raise ValueError("Completed prediction-row count does not match the CSV.")

    report_text = build_report(results)
    if recorded_hashes.get(REPORT_PATH.name) != _text_sha256(report_text):
        raise ValueError(
            "The report generator no longer reproduces the completed report hash."
        )
    return results, report_text, completed


def _atomic_report_write(report_text: str) -> None:
    rebuild_path = REPORT_PATH.with_name(REPORT_PATH.name + ".rebuild")
    staged_path = _stage_text(report_text, rebuild_path)
    staged_path.replace(REPORT_PATH)


def rebuild_report() -> None:
    """Recreate Markdown from verified CSVs without fitting or predicting."""
    _results, report_text, _completed = _load_verified_completed_run()
    _atomic_report_write(report_text)
    print(f"Rebuilt verified report without scoring: {REPORT_PATH}")


def _execute_final_test(
    arguments,
    lock_record: dict,
    prepared_data: dict,
    prepared_models: list[dict],
) -> None:
    lock_id = lock_record["lock_id"]
    confirmation = f"EVALUATE-LOCK-{lock_id.upper()}"
    if arguments.confirm != confirmation:
        raise ValueError(
            "Confirmation does not match the frozen configuration. "
            "Run --dry-run first and copy its exact phrase."
        )

    FINAL_RESULTS_FOLDER.mkdir(parents=True, exist_ok=True)
    started_record = {
        "status": "started",
        "started_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "lock_id": lock_id,
        "full_lock_sha256": lock_record["full_lock_sha256"],
        "frozen_lock_file_sha256": _sha256(LOCK_PATH),
        "command": sys.argv,
        "selected_models": lock_record["lock_payload"]["selected_models"],
    }
    try:
        _write_json_exclusive(STARTED_PATH, started_record)
    except FileExistsError as error:
        raise RuntimeError(
            "Another process already claimed this one-time final test."
        ) from error
    except Exception as error:
        if STARTED_PATH.exists():
            _write_failure(lock_id, error)
        raise

    print("\nThe permanent STARTED marker is locked. Scoring the holdout now.")
    try:
        results, predictions, confusion = _evaluate_locked_models(
            prepared_models,
            prepared_data,
            lock_id,
        )
        _validate_result_tables(
            results,
            predictions,
            confusion,
            lock_record,
        )
        report_text = build_report(results)

        staged_results = _stage_csv(results, RESULTS_PATH)
        staged_predictions = _stage_csv(predictions, PREDICTIONS_PATH)
        staged_confusion = _stage_csv(confusion, CONFUSION_PATH)
        staged_report = _stage_text(report_text, REPORT_PATH)

        # Read the staged CSVs back before any file is published.
        staged_result_data = pd.read_csv(
            staged_results,
            dtype={"lock_id": "string"},
        )
        staged_prediction_data = pd.read_csv(
            staged_predictions,
            dtype={"lock_id": "string"},
        )
        staged_confusion_data = pd.read_csv(
            staged_confusion,
            dtype={"lock_id": "string"},
        )
        _validate_result_tables(
            staged_result_data,
            staged_prediction_data,
            staged_confusion_data,
            lock_record,
        )

        staged_results.rename(RESULTS_PATH)
        staged_predictions.rename(PREDICTIONS_PATH)
        staged_confusion.rename(CONFUSION_PATH)

        completed_record = {
            "status": "complete",
            "completed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "lock_id": lock_id,
            "full_lock_sha256": lock_record["full_lock_sha256"],
            "result_rows": len(results),
            "prediction_rows": len(predictions),
            "artifacts": {
                RESULTS_PATH.name: _sha256(RESULTS_PATH),
                PREDICTIONS_PATH.name: _sha256(PREDICTIONS_PATH),
                CONFUSION_PATH.name: _sha256(CONFUSION_PATH),
                REPORT_PATH.name: _sha256(staged_report),
            },
        }
        staged_completed = _staged_path(COMPLETED_PATH)
        _write_json_exclusive(staged_completed, completed_record)
        staged_completed.rename(COMPLETED_PATH)

        # Only a completed audit record may make a report saying COMPLETE visible.
        staged_report.rename(REPORT_PATH)
        verified_results, _report, _completed = _load_verified_completed_run()
        if _sha256(REPORT_PATH) != completed_record["artifacts"][REPORT_PATH.name]:
            raise ValueError("Published report hash does not match completion record.")
    except Exception as error:
        _write_failure(lock_id, error)
        raise

    print("\nOne-time final results")
    print("----------------------")
    print(
        verified_results[
            [
                "wine",
                "role",
                "model",
                "Test_MAE",
                "Test_RMSE",
                "Test_R2",
                "Test_Accuracy",
                "Test_Within_Margin_Accuracy",
            ]
        ].to_string(index=False)
    )
    print(f"\nSaved report: {REPORT_PATH}")
    print("The holdout is now consumed. Do not use it for further tuning.")


def main() -> None:
    arguments = parse_arguments()
    if arguments.rebuild_report:
        rebuild_report()
        return

    specifications = _selected_specs(arguments.wine, arguments.model)
    if arguments.freeze_lock:
        _freeze_lock(arguments, specifications)
        return

    lock_record = _load_frozen_lock()
    _check_requested_scope(arguments, lock_record)
    if _existing_final_test():
        raise RuntimeError(
            "A final test was already started in this project folder. "
            "Only --rebuild-report is allowed after a completed run."
        )

    # This reproduces and hashes the split but does not fit or predict.
    payload, prepared_data, prepared_models = _run_preflight(
        specifications,
        lock_record["requested_scope"],
        lock_record["frozen_at"],
    )
    _check_current_state(payload, lock_record)
    lock_id = lock_record["lock_id"]
    confirmation = f"EVALUATE-LOCK-{lock_id.upper()}"
    _print_lock_summary(arguments, specifications, lock_id)

    if arguments.dry_run:
        print(
            "\nPreflight passed. The split was reproduced only for integrity "
            "checks; no model was fitted and no prediction or score was made."
        )
        print("Run exactly once with:")
        print(
            f"python final_test.py --wine {arguments.wine} "
            f"--model {arguments.model} --execute-final-test "
            f"--confirm {confirmation}"
        )
        return

    _execute_final_test(
        arguments,
        lock_record,
        prepared_data,
        prepared_models,
    )


if __name__ == "__main__":
    main()

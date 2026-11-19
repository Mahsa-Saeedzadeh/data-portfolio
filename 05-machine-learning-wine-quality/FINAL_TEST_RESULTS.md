# Final Holdout Results

Status: **COMPLETE - the reserved 20% holdout has now been consumed.**

Run time: `2026-08-26T19:19:23+02:00`  
Configuration lock: `7662d24197ed`

voting was declared as the primary model and stacking as the single comparison before these rows were scored. The test data was not used for preprocessing choices, feature selection, or parameter tuning.

> Do not tune models or test additional alternatives against these same rows. A new development cycle needs new unseen data or a newly defined evaluation protocol.

## Frozen test policy

Red and white wines were evaluated separately. Exact duplicates were removed before the fixed quality-stratified and feature-ranked 80/20 split. All 11 features were used. The 3 x IQR rule removed rows from training only; no holdout row was removed. Each model was fitted once on the prepared training portion, and the rounded class view used margin 1.

## Metric legend

| Metric | Simple meaning | Better direction |
|---|---|---|
| Test MAE | Average absolute error in quality points; the primary measure. | Lower |
| Test RMSE | Error in quality points with larger misses penalized more. | Lower |
| Test R2 | Holdout variation explained relative to predicting the mean. | Higher |
| Test accuracy | Exact match after rounding to a quality class. | Higher |
| Test +/-1 | Rounded prediction is within one quality point. | Higher |
| Macro precision | Per-class precision averaged across classes. | Higher |
| Balanced accuracy | Per-class recall averaged across true classes. | Higher |
| Macro F1 | Per-class F1 averaged across classes. | Higher |

## One-time results

| Role | Wine | Model | Train rows | Test rows | CV MAE | Test MAE | Test RMSE | Test R2 | Test accuracy | Test +/-1 | Macro precision | Balanced | Macro F1 | Locked setup |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Primary | Red | voting | 970 | 272 | 0.470944 | 0.490612 | 0.635476 | 0.398019 | 0.573529 | 0.977941 | 0.270347 | 0.266801 | 0.263604 | {"forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03, "weights": [1, 0, 0, 2, 0], "xgboost": "drop"} |
| Comparison | Red | stacking | 970 | 272 | 0.479308 | 0.490624 | 0.632676 | 0.403312 | 0.566176 | 0.974265 | 0.271219 | 0.264048 | 0.262267 | {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge(alpha=0.001))])", "forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "passthrough": false, "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03} |
| Primary | White | voting | 3,023 | 793 | 0.529906 | 0.538425 | 0.704472 | 0.374355 | 0.563682 | 0.954603 | 0.237132 | 0.233723 | 0.230308 | {"forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1, "weights": [1, 0, 0, 1, 0], "xgboost": "drop"} |
| Comparison | White | stacking | 3,023 | 793 | 0.530087 | 0.541157 | 0.703210 | 0.376594 | 0.558638 | 0.954603 | 0.324997 | 0.248777 | 0.250476 | {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge(alpha=0.1))])", "forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "passthrough": true, "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1} |

## Interpretation

- **Red:** Voting test MAE is 0.490612; Stacking test MAE is 0.490624. Voting remained lower by 0.000012 MAE points.
- **White:** Voting test MAE is 0.538425; Stacking test MAE is 0.541157. Voting remained lower by 0.002732 MAE points.

The prediction-level audit trail is saved in `data/final-results/final_test_predictions.csv`; the long-form confusion counts are in `final_test_confusion.csv`.

## Integrity note

`FINAL_TEST_LOCK.json`, `FINAL_TEST_STARTED.json`, and `FINAL_TEST_COMPLETED.json` permanently record this run. The script refuses another final evaluation in this project folder. `--rebuild-report` may recreate this Markdown file only after it verifies the completed CSV hashes and row structure; it never fits or predicts again.

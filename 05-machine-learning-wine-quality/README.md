# Wine Quality Project

Course project (Machine Learning module, 2026) on predicting sensory wine quality from 11 physicochemical measurements of the UCI red- and white-wine datasets. It was developed as a team project: each small group contributed one model family, and the shared pipeline below makes every model use the same data preparation, 80/20 split, and evaluation method, so results stay fair and easy to consolidate.

The current program provides a reproducible first comparison using five-fold training cross-validation with MAE, RMSE, and R2. By default, it also gives a supplementary classification-style view of rounded quality predictions.

> `main.py` never scores the reserved 20% holdout. Only the separate `final_test.py` workflow may open it after `FINAL_TEST_LOCK.json` is explicitly frozen and verified. Once `FINAL_TEST_STARTED.json` is created, the holdout is treated as consumed and must not be used for further tuning or model selection.

**Current status:** The one-time final comparison completed under lock `7662d24197ed`. The holdout is consumed; see [FINAL_TEST_RESULTS.md](FINAL_TEST_RESULTS.md) for the permanent Voting-versus-Stacking results.

Polynomial Ridge and the optional ratio features were added after that final comparison. They are available for new training-only cross-validation experiments, but they are not part of the frozen 13-model lock and must not be tested on the consumed holdout.

## Contents

- [Quick start](#quick-start)
- [Run choices](#run-choices)
- [Shared ML pipeline](#shared-ml-pipeline)
- [Fair comparison rules](#fair-comparison-rules)
- [Optional classification-style view](#optional-classification-style-view)
- [Models and tuning](#models-and-tuning)
- [One-time final holdout test](#one-time-final-holdout-test)
- [Model experiment register](MODEL_EXPERIMENT_RESULTS.md)
- [Grid-search results report](GRID_SEARCH_RESULTS.md)
- [Generated final-test report](FINAL_TEST_RESULTS.md)
- [Saved outputs](#saved-outputs)
- [Project reference](#project-reference)
- [Adding a new model](#adding-a-new-model)

## Quick start

All paths are relative to the folder containing `main.py`. Copying the complete project folder to another computer therefore requires no source-code path changes.

### Create the Python environment

Python 3.12 is recommended. From the project folder, run:

```text
python -m venv .venv
# Windows
.venv\Scripts\python.exe -m pip install -r requirements.txt
# macOS / Linux
.venv/bin/python -m pip install -r requirements.txt
```

In PyCharm, select the interpreter inside `.venv` as the project interpreter.

### Run the default configuration

With the environment activated:

```text
python main.py
```

Without activating it:

```text
.venv\Scripts\python.exe main.py
```

The default run uses red wine and the baseline model. It removes exact duplicates, creates a quality-stratified and feature-ranked split, removes extreme rows from training only, uses all 11 input features without adding ratio features, and enables the rounded class view with a one-point margin. Grid search is off, so every model uses its recorded fixed settings unless `--grid-search` is added.

## Run choices

These options belong to `main.py`, which is the training-CV development workflow. The one-time holdout uses the separate `final_test.py` command described later.

| Option | Purpose | Default |
|---|---|---|
| `--wine {red,white,both}` | Run red wine, white wine, or both as separate evaluations. | `red` |
| `--model {baseline,tree,random_forest,knn,svm,linear,ridge,polynomial_ridge,lasso,bayes,xgboost,nn,voting,stacking,all}` | Run one model or all registered models. | `baseline` |
| `--grid-search` / `--no-grid-search` | Automatically select parameters with five-fold training-only `GridSearchCV`. | Disabled |
| `--remove-duplicates` / `--no-remove-duplicates` | Remove duplicates or keep them before splitting. | Remove |
| `--remove-outliers` / `--no-remove-outliers` | Remove flagged training outliers or only report and keep them. | Remove |
| `--stratified-split` / `--no-stratified-split` | Keep the quality-class proportions represented in the split. | Enabled |
| `--ranked-split` / `--no-ranked-split` | Select evenly spaced test rows along a combined feature-rank axis. | Enabled |
| `--features all` or a quoted list | Use all inputs or a selected feature set. | All 11 features |
| `--feature-engineering {none,ratios}` | Keep the original inputs or append five row-wise ratio features. | `none` |
| `--class-evaluation` / `--no-class-evaluation` | Enable or skip the supplementary rounded class view. | Enabled |
| `--class-margin POINTS` | Count a rounded prediction as acceptable when it is within this many quality points. | `1` |

Examples:

```text
# White wine with KNN
python main.py --wine white --model knn

# Keep duplicates and extreme training rows instead of removing them
python main.py --wine white --model knn --no-remove-duplicates --no-remove-outliers

# Use a random quality-stratified split without feature ranking
python main.py --wine red --model svm --no-ranked-split

# Reproduce the earlier plain random split
python main.py --wine red --model svm --no-stratified-split --no-ranked-split

# Use a manually selected feature set
python main.py --wine red --model linear --features "alcohol,volatile acidity,sulphates"

# Run Polynomial Ridge with its fixed degree-two, log-enabled setup
python main.py --wine red --model polynomial_ridge

# Add the five ratio features to a training-CV experiment
python main.py --wine both --model polynomial_ridge --feature-engineering ratios

# Evaluate every model on red and white wine separately
python main.py --wine both --model all

# Search every registered model without changing its fixed settings
python main.py --wine both --model all --grid-search

# Search only the submitted SVM grid on red wine
python main.py --wine red --model svm --grid-search

# Search all 56 Polynomial Ridge combinations on white wine
python main.py --wine white --model polynomial_ridge --grid-search

# Run the two enhanced ensemble models separately
python main.py --wine red --model voting
python main.py --wine red --model stacking

# Accept rounded predictions up to two quality points away
python main.py --wine both --model all --class-margin 2

# Run only the regression evaluation and save computation time
python main.py --wine both --model all --no-class-evaluation
```

Feature names containing spaces should be placed inside quotes. Underscores are also accepted, so `volatile_acidity` and `volatile acidity` mean the same input.

### Optional ratio features

`--feature-engineering ratios` keeps the selected original inputs and appends these five features:

- `sweetness_index` = residual sugar / (fixed acidity + volatile acidity + citric acid)
- `sugar_acid_ratio` = residual sugar / fixed acidity
- `alcohol_acid_ratio` = alcohol / fixed acidity
- `volatile_fixed_ratio` = volatile acidity / fixed acidity
- `sulfur_ratio` = free sulfur dioxide / total sulfur dioxide

The calculation needs all seven source columns: `fixed acidity`, `volatile acidity`, `citric acid`, `residual sugar`, `free sulfur dioxide`, `total sulfur dioxide`, and `alcohol`. Therefore, a custom `--features` list used together with `ratios` must contain every one of them. The target is never used in these calculations.

All four data-policy switches are independent and are enabled by default:

- Duplicate removal acts before the 80/20 split. Use `--no-remove-duplicates` to keep repeated rows.
- Outlier removal acts after the split and only on training rows. The 3 x IQR limits are calculated once from the complete training portion before cross-validation. A row is flagged when at least one selected feature falls outside its limits. The matching `X_train` and `y_train` rows are removed together; test rows are never changed. Use `--no-remove-outliers` to report and keep them.
- With both split switches enabled, rows are grouped by `quality`, sorted by their combined feature rank inside each group, and evenly spaced rows are placed in the test set.
- With only stratification enabled, scikit-learn selects random rows inside the quality classes. With only ranking enabled, all rows share one ranked group. Disabling both reproduces the earlier plain random split.

See all choices with:

```text
python main.py --help
```

## Shared ML pipeline

The pipeline runs in this order:

1. Load the selected original CSV from `data/raw-input/`.
2. Count and remove exact duplicates by default. Keeping them is an optional comparison.
3. Separate the selected input features from the unchanged `quality` target.
4. Create the 80% training and 20% test split. By default, quality classes are stratified and test rows are selected at evenly spaced points along the average percentile rank of all 11 original features.
5. Calculate and save the training-only 3 x IQR report, then remove flagged training rows and their matching target values by default.
6. After splitting and training-only outlier handling, optionally append the same five row-wise ratio features to training and test inputs. No row or target value is changed.
7. When grid search is off, evaluate the fixed model. When `--grid-search` is used, select parameters with five-fold `GridSearchCV` on the prepared training rows and refit the selected training-only estimator.
8. Fit `StandardScaler` inside every training fold for models that require scaling.
9. Average and save MAE, RMSE, and R2 across the five folds. Lower is better for MAE and RMSE; higher is better for R2. Grid search selects the lowest CV MAE.
10. When the class view is enabled, create one out-of-fold prediction for every training row, round it to the 0-to-10 quality scale, and calculate the supplementary class metrics.
11. Stop after training-only CV and keep the 20% holdout unscored. Because the official holdout is already consumed, post-final options such as Polynomial Ridge and ratio features remain training-CV experiments only.

## Fair comparison rules

The following settings remain fixed while models are compared:

- The same wine dataset, feature set, feature-engineering setting, duplicate policy, and outlier policy
- The same stratified and ranked split policies
- The same 80/20 train/test membership. `random_state=42` is used for random split choices and the fixed ordering of ranked training rows.
- Five cross-validation folds
- MAE, RMSE, and R2 calculated in the same way
- The same class margin when classification-style results are compared
- Red and white wine evaluated separately; `--wine both` does not merge them

MAE and RMSE remain the main project measures because they show the prediction error in wine-quality points. R2 is a useful supporting measure: `1.0` is perfect, `0.0` means the model is no better than predicting the average quality, and it can be negative. For example, `R2 = 0.70` means that the model explains about 70% of the variation in quality; it does not mean that 70% of predictions are correct.

Because the metrics may prefer different models, one must be agreed as the primary selection score before tuning. The others remain important supporting scores.

### Optional classification-style view

The models still predict a continuous number and remain regression models. The optional view rounds each out-of-fold prediction to the nearest whole quality class and reports:

- **Accuracy (margin 0):** the rounded prediction equals the true quality exactly.
- **Within-margin accuracy:** the difference is no larger than `--class-margin`. With margin 2, for example, quality 2 accepts predictions from 0 through 4.
- **Macro precision:** precision is calculated for every quality class and then averaged. This shows how reliable the model's predictions are across both common and rare classes.
- **Balanced accuracy:** recall is calculated for every quality class and then averaged, so common classes do not dominate the result.
- **Macro F1:** F1 is calculated separately for every class and then averaged.
- **Confusion matrix:** shows which quality classes are confused with one another.

The default margin is 1. If the true quality is 6, margin 0 accepts only 6, margin 1 accepts 5, 6, or 7, and margin 2 accepts 4 through 8. A margin of 0 makes within-margin accuracy equal OOF accuracy. A larger margin is easier to achieve, so models must use the same margin for a fair comparison. OOF accuracy, macro precision, balanced accuracy, macro F1, and the confusion matrix do not change when only the margin changes.

This view uses `cross_val_predict` on training data only. It trains each model an additional five times, so `--no-class-evaluation` is useful for a quick regression-only run. The experiment register uses the shared default margin of 1.

### Controlled data experiments

**Feature selection:** The first official comparison uses all 11 features. Smaller, clearly named sets may be compared using training cross-validation only. An automatic selector such as `SelectKBest` or recursive feature elimination must be placed inside the cross-validation pipeline so it learns from training folds only.

**Feature engineering:** `none` is the default and reproduces the original input shape. `ratios` appends five deterministic row-wise features only after splitting and outlier handling, so it does not influence test membership or the training-only outlier limits. Compare the two settings with the same wine, split, feature sources, and model settings. When ratios are enabled, all seven required source columns must be present.

**Duplicate policy:** Removal is the default. It prevents an identical complete row from appearing in both partitions, although genuine repeated measurements may also be discarded. Keeping duplicates remains a recorded comparison and should have a data-based reason.

**Outlier policy:** Training-only removal is the default. Extreme measurements may still be genuine wines, so keeping them remains an important recorded comparison. The test set must never decide which policy is selected and is never filtered.

**Split policy:** Quality stratification helps rare quality values appear in both parts. Ranking uses the full predictor distribution to make the holdout deliberately representative along one combined feature-rank axis. It does not train the model on test rows, but it is a systematic, distribution-informed split rather than an independent random sample. For a more standard course comparison, use `--no-ranked-split`; to reproduce the earlier split, disable both split switches.

The rank axis always uses all 11 original features, even when a smaller model feature set is requested. This keeps train/test membership unchanged during feature-selection experiments. It spreads rows along the combined rank, but does not guarantee that every individual feature has identical minimum and maximum coverage.

**Scaling:** Scaling is based on the needs of the algorithm. It is not switched on and off simply to search for a better result.

### Experiment record

For every important run, record:

- The exact command
- Wine and model
- Selected features
- Feature-engineering setting
- Duplicate, outlier, stratification, and ranking policies
- Number of training rows removed
- Model parameters
- Mean CV MAE, RMSE, and R2
- Whether the class view was enabled, its margin, and its five summary scores

The normal run evaluates each model using its fixed settings. `--grid-search` activates the shared optional search without changing those defaults. The selected search score is a conventional training-CV result, not a nested-CV estimate, so very small improvements should be confirmed before the final one-time test.

After the frozen lock is used to execute the final test, none of these development searches may use the resulting holdout scores to choose a new model or setting.

## Models and tuning

### Current starter models

| CLI name | Current estimator | Scaled? |
|---|---|---:|
| `baseline` | `DummyRegressor(strategy="mean")` | No |
| `tree` | Small `DecisionTreeRegressor` | No |
| `random_forest` | Team `RandomForestRegressor(n_estimators=100, random_state=42)` | No |
| `knn` | Team `KNeighborsRegressor(n_neighbors=5)` | Yes |
| `svm` | Team-base RBF `SVR(C=1, epsilon=0.1, gamma="scale")` | Yes |
| `linear` | Ordinary `LinearRegression` | Yes |
| `ridge` | Latest team `Ridge(alpha=0.001)` | Yes |
| `polynomial_ridge` | Log-enabled degree-two polynomial features with `Ridge(alpha=1)` | Yes |
| `lasso` | Latest team `Lasso(alpha=0.001)` | Yes |
| `bayes` | `BayesianRidge` | Yes |
| `xgboost` | Tuned `XGBRegressor` with 350 moderately shallow trees | No |
| `nn` | Target-scaled `MLPRegressor` with 128- and 64-unit layers | Yes |
| `voting` | Equal vote from tuned Random Forest and SVM; optional XGBoost/NN candidates | Mixed internally |
| `stacking` | Tuned Random Forest, XGBoost, SVM, and Ridge with a learned combiner | Mixed internally |

Normal runs use the fixed settings recorded in this file, even when grid search finds a better candidate. The individual submitted models keep their own defaults; the two ensemble defaults include the later training-CV improvements described below. Each model file owns its search space, while `src/model_tuning.py` contains the shared `GridSearchCV` procedure. For scaled pipelines, parameter names use the `model__` prefix, for example `model__n_neighbors`. The neural network is nested inside a target transformer, so its parameters use `model__regressor__`, for example `model__regressor__hidden_layer_sizes`. Ensemble searches can also tune named members such as `forest__max_features`, choose a final estimator, or enable `passthrough`. Polynomial Ridge was registered after the final lock; `--model all` now includes it for training CV, but the frozen holdout configuration remains unchanged.

### Baseline

Compare mean and median prediction. Mean often suits RMSE while median can suit MAE. This remains a reference rather than a model that needs extensive tuning.

### Decision tree

The search tests `max_depth`, `min_samples_split`, and `min_samples_leaf`, including the team's unrestricted-tree option. It also tests the exact newer submission: depth 5, minimum split 15, and minimum leaf 6. These settings balance a tree that is too simple against one that memorizes the training rows.

### Random Forest

The fixed model is exactly the team's 100-tree submission. The optional search keeps that setting and compares 100/200 trees, unrestricted/depth-10 trees, leaf sizes 1/3, and all/square-root feature choices.

### KNN

The search tests 3, 5, 7, 9, 11, and 15 neighbours, `weights="uniform"` versus `weights="distance"`, and Manhattan versus Euclidean distance (`p=1` or `p=2`). The submitted fixed setting remains five neighbours with uniform Euclidean distance. Scaling remains enabled.

### SVM

The exact submitted RBF grid is used: `C` = 0.5, 1, 3, or 10; `epsilon` = 0.05, 0.1, or 0.2; and `gamma` = 0.03, 0.1, or `scale`. They control the error penalty, tolerated error, and curve flexibility.

### Linear regression

Ordinary linear regression has little useful parameter tuning. The small search checks whether the intercept is fitted and whether coefficients must be positive. Ridge and Lasso remain separate models rather than silently changing `linear`.

### Polynomial Ridge regression

The fixed pipeline first applies `log1p` to `residual sugar`, `total sulfur dioxide`, `sulphates`, and `free sulfur dioxide`, then creates degree-two polynomial features, scales them, and fits Ridge with `alpha=1`. The log step changes only these skewed input values; it does not transform `quality`.

The optional grid search compares log off/on, polynomial degrees 1, 2, 3, and 4, and the seven submitted Ridge alpha values from 0.0001 through 100. This gives 56 candidates and preserves the degree choices from the submitted `linear_models.py` work. High degrees should be used carefully: degree 4 together with all 11 original and five ratio features expands the input to 4,844 columns, which costs more memory and can overfit.

### Ridge and Lasso

Both use the submitted alpha series: 0.0001, 0.001, 0.01, 0.1, 1, 10, and 100. Their latest submitted fixed alpha is 0.001, which avoids the excessive coefficient shrinkage seen with Lasso alpha 1.

### Bayesian regression

The `bayes` model is Bayesian Ridge regression, not Naive Bayes classification. Begin with its defaults. If needed, test a small number of `alpha_1`, `alpha_2`, `lambda_1`, and `lambda_2` settings to examine different regularization strengths.

### XGBoost

The current search compares the three XGBoost configurations already documented in the experiment register. They vary depth, learning rate, tree count, row/column sampling, gamma, and regularization without creating a very large Cartesian search. `random_state=42` remains fixed.

### Neural network

The search compares the three documented finalists and two layer alternatives. It varies `hidden_layer_sizes`, `alpha`, and `learning_rate_init` while keeping both scalers, ReLU, Adam, early stopping, and `random_state=42` inside the estimator.

### Voting ensemble

The improved fixed vote gives equal weight to a tuned Random Forest and a tuned scaled SVM. It was chosen as one shared setting because it improved both wine datasets. The optional search has 16 controlled candidates: a red-oriented and a white-oriented base profile, each paired with eight member/weight recipes. It can change the Random Forest/SVM balance and optionally add XGBoost or the tuned neural network. Red and white choose independently through training-only CV. Reported weight lists use the order Random Forest, XGBoost, Ridge, SVM, NN; a zero means that model was excluded from that recipe.

### Stacking ensemble

The improved stack creates out-of-fold predictions from tuned Random Forest, XGBoost, tuned scaled SVM, and scaled Ridge. Its fixed combiner is scaled Ridge with `alpha=0.001`, with `passthrough=False`. The 10-candidate search pairs red- and white-oriented base profiles with scaled Ridge, scaled Lasso, and shallow Random Forest combiners, and it tests whether the original features should pass through to the combiner. Stacking is the slowest search because its internal five-fold training runs inside the project's outer CV.

## One-time final holdout test

`main.py` is used for development and training-only cross-validation. `final_test.py` is a separate guarded program for the one-time evaluation of the unchanged 20% holdout.

### What is locked

`src/best_model_configs.py` records the best saved training-CV parameters separately for red and white wine for the 13 models that were registered when the final lock was frozen. This made the final runner generic before the holdout was consumed. Polynomial Ridge and ratio-feature experiments were added later and are deliberately absent from that immutable lock. For the official comparison, `FINAL_SELECTIONS` declared Voting as the **primary** model and Stacking as the single **comparison** before the holdout was read.

| Wine | Primary | Comparison |
|---|---|---|
| Red | Voting: tuned Random Forest and SVM, weighted 1:2 | Stacking: tuned Random Forest, XGBoost, SVM, and Ridge; scaled Ridge `alpha=0.001` combiner; `passthrough=False` |
| White | Voting: tuned Random Forest and SVM, equal weight | Stacking: tuned Random Forest, XGBoost, SVM, and Ridge; scaled Ridge `alpha=0.1` combiner; `passthrough=True` |

Voting is the reported primary result because it had the lowest selected training-CV MAE for both wines. Stacking is a planned comparison with a strong alternative error profile. A better holdout number from Stacking would be reported honestly, but it would not reopen tuning or start a search through more alternatives.

The final policy is also fixed: both wines, all 11 features, no ratio feature engineering, exact duplicates removed before the existing quality-stratified and feature-ranked 80/20 split, 3 x IQR outliers removed from training only, no holdout filtering, class margin 1, and no new grid search. The runner checks the selected settings against the saved rank-one candidate rows and locks hashes of the raw data, Python source, package versions, policy, and selected configurations.

### Step 1: freeze the reviewed lock

```text
python final_test.py --wine both --model finalists --freeze-lock
```

This creates the immutable root file `FINAL_TEST_LOCK.json`. Freezing reproduces the split, verifies the expected prepared row counts, hashes the prepared training and holdout tables, validates all 26 wine/model parameter mappings against their saved rank-one CV candidates, and builds the estimators without fitting them. It also records the source, raw-data, requirements, package, CV-evidence, policy, and configuration hashes. It does not fit a model, predict a holdout value, or calculate a holdout score. The lock cannot be overwritten.

Do not edit the Python source, raw data, requirements, saved candidate files, model settings, or environment between freezing and execution. A changed locked input blocks the run.

### Step 2: verify the frozen lock without scoring

```text
python final_test.py --wine both --model finalists --dry-run
```

The dry run requires `FINAL_TEST_LOCK.json` and the same `--wine` and `--model` scope used when it was frozen. It reproduces the preparation and hashes again, then checks that the complete current payload still matches the frozen lock. It reads and hashes the prepared holdout table only for integrity; it does not fit, predict, calculate a holdout metric, create a final-results marker, or consume the holdout as a scored test. If verification passes, it prints the exact confirmation phrase and execution command.

### Step 3: execute exactly once

Copy the complete command printed by the dry run. It has this form:

```text
python final_test.py --wine both --model finalists --execute-final-test --confirm EVALUATE-LOCK-XXXXXXXXXXXX
```

Do not invent the confirmation value; copy the current phrase from the dry run. The official final evaluation uses `--wine both --model finalists`. Although the script can validate any individual locked model configuration, that ability must not be used to try extra alternatives on the same holdout.

Execution creates permanent `FINAL_TEST_STARTED.json` before fitting and then scores the four frozen finalist rows. A successful run writes the three CSV artifacts, the Markdown report, and `FINAL_TEST_COMPLETED.json`. If an exception occurs after STARTED, the script writes permanent `FINAL_TEST_FAILED.json`; STARTED and FAILED must not be deleted, and the run must not be retried on the same holdout.

> Once STARTED exists, treat the holdout as consumed even if execution fails. Do not delete the lock, markers, pending/final artifacts, or report to obtain another attempt. Do not tune, change preprocessing, score another model, or select between Voting and Stacking from these rows. Further development requires new unseen data or a newly defined evaluation protocol.

After a successful completed run, the Markdown report may be rebuilt without fitting, predicting, or reading the raw datasets:

```text
python final_test.py --rebuild-report
```

Rebuild is allowed only when the frozen lock, STARTED marker, COMPLETED marker, three final CSVs, lock IDs, full lock hashes, recorded artifact hashes, expected result/prediction/confusion coverage, finite metrics, and saved report-generator hash all verify. A FAILED marker blocks rebuilding. The command then recreates only `FINAL_TEST_RESULTS.md` from the verified saved metrics.

## Saved outputs

Output names include the wine, model, duplicate policy, outlier policy, split policy, feature configuration, and class-evaluation setting, preventing different configurations from silently overwriting one another. Runs with ratio features receive the suffix `_ratio_features`; the default `none` setting adds no feature-engineering suffix.

| Folder | Contents |
|---|---|
| `data/pre-processed/` | Exact training rows used by cross-validation and untouched test rows |
| `data/evaluate/` | Training-only outlier reports, fixed/search fold scores, optional confusion matrices, and complete grid candidate tables |
| `data/results/` | Compact fixed and grid-search comparison tables |
| `data/final-results/` | Permanent one-time metrics, row-level predictions, confusion counts, and STARTED/COMPLETED-or-FAILED audit markers |

| Final-test artifact | Purpose |
|---|---|
| `FINAL_TEST_LOCK.json` | Immutable root pre-test lock created by `--freeze-lock`; records the scope and complete hashed payload before scoring. |
| `data/final-results/final_test_results.csv` | One summary row per wine and predeclared model, including CV references and final test metrics. |
| `data/final-results/final_test_predictions.csv` | Row-level actual, continuous, rounded, absolute-error, and within-one results. |
| `data/final-results/final_test_confusion.csv` | Long-form confusion counts for the rounded class view. |
| `data/final-results/FINAL_TEST_STARTED.json` | Permanent start record containing the command, selected models, and frozen lock ID/hash; its creation marks the holdout consumed. |
| `data/final-results/FINAL_TEST_FAILED.json` | Permanent error type/message if execution fails after STARTED; it blocks retry and report rebuild. |
| `data/final-results/FINAL_TEST_COMPLETED.json` | Completion record containing lock hashes, row counts, and hashes for all three CSVs plus the generated report. |
| `FINAL_TEST_RESULTS.md` | Human-readable final report generated after the one-time execution. |

`FINAL_TEST_LOCK.json`, STARTED, and whichever terminal marker exists (COMPLETED or FAILED) are permanent audit records. Do not delete or overwrite them or any pending/final artifact to obtain another attempt.

The terminal prints the selected configuration—including both split switches—preparation row counts and policies, regression scores, and, when enabled, the rounded class scores. Compact comparison CSVs record both split settings, the class margin, whether grid search ran, candidate counts, selected parameters, and summary metrics. Grid-search candidate CSVs retain every tested setup.

The feature-engineering setting is also printed in the terminal and saved in the compact result rows. This makes `none` and `ratios` runs easy to distinguish in both filenames and tables.

Fixed and grid-search files have different names, so one mode does not overwrite the other. Hyperparameters and complete candidate rankings remain recorded inside the CSV result files.

The consolidated training-only search rankings, selected parameters, and model-by-model conclusions are also preserved in the standalone [GRID_SEARCH_RESULTS.md](GRID_SEARCH_RESULTS.md) report. It does not score or reopen the reserved holdout.

## Project reference

### Folder structure

```text
Wine_Quality_Project/
|-- main.py
|-- final_test.py
|-- FINAL_TEST_LOCK.json
|-- requirements.txt
|-- README.md
|-- MODEL_EXPERIMENT_RESULTS.md
|-- GRID_SEARCH_RESULTS.md
|-- FINAL_TEST_RESULTS.md
|-- src/
|   |-- data_split.py
|   |-- preprocessing.py
|   |-- feature_engineering.py
|   |-- evaluate.py
|   |-- evaluate_as_classes.py
|   |-- model_tuning.py
|   |-- best_model_configs.py
|   └── models/
|       |-- baseline.py
|       |-- tree.py
|       |-- random_forest.py
|       |-- knn.py
|       |-- svm.py
|       |-- linear.py
|       |-- ridge.py
|       |-- polynomial_ridge.py
|       |-- lasso.py
|       |-- bayes.py
|       |-- xgboost.py
|       |-- NN.py
|       |-- voting.py
|       └── stacking.py
└── data/
    |-- raw-input/
    |-- pre-processed/
    |-- evaluate/
    |-- final-results/
    └── results/
```

`FINAL_TEST_LOCK.json` is generated by `--freeze-lock`; `FINAL_TEST_RESULTS.md` is generated only after successful execution or a verified rebuild. Split preparation is handled directly by `main.py` and `src/data_split.py`.

### Raw data and target

The two original UCI files remain unchanged in:

```text
data/raw-input/winequality-red.csv
data/raw-input/winequality-white.csv
```

`quality` is the numeric value predicted by every model. It is the target, not an input feature.

### The 11 input features

| Feature | Simple meaning |
|---|---|
| `fixed acidity` | Acids that do not evaporate easily |
| `volatile acidity` | Acids that may create a vinegar-like taste when high |
| `citric acid` | Amount of citric acid |
| `residual sugar` | Sugar left after fermentation |
| `chlorides` | Salt content |
| `free sulfur dioxide` | Sulfur dioxide that is not chemically bound |
| `total sulfur dioxide` | Total free and bound sulfur dioxide |
| `density` | Density of the wine |
| `pH` | How acidic or basic the wine is |
| `sulphates` | Amount of sulphates |
| `alcohol` | Alcohol level |

## Adding a new model

Each file in `src/models/` only defines how to build one model. Data loading, splitting, evaluation, and saving stay in the shared pipeline.

### 1. Create the model file

For example, create `src/models/random_forest.py`:

```python
from sklearn.ensemble import RandomForestRegressor


def build_model():
    return RandomForestRegressor(
        n_estimators=100,
        random_state=42,
    )


def parameter_grid():
    return {
        "n_estimators": [100, 200],
        "max_depth": [None, 10],
    }
```

`build_model()` takes no arguments and returns a fresh, unfitted, scikit-learn-compatible regression estimator. `parameter_grid()` returns the choices used only when `--grid-search` is enabled. Include the fixed default in that search space so it receives a fair comparison.

### 2. Register the model

Add this line inside the existing `MODEL_MODULES` dictionary in `src/models/__init__.py`:

```python
"random_forest": "src.models.random_forest",
```

That one entry adds `random_forest` to both `--model random_forest` and `--model all`. A normal model requires no change to `main.py` or `evaluate.py`.

Before an unconsumed final-test lock can validate a newly registered model, add its best saved training-CV parameter mapping for both wines to `BEST_MODEL_PARAMETERS` in `src/best_model_configs.py`. Do this only before the final holdout is opened. Once the holdout is consumed, adding a model does not authorize another final-test run.

### 3. Check the model contract

- Use a regression estimator with `fit(X, y)` and `predict(X)`.
- Return an unfitted model; do not load, split, fit, evaluate, or save data inside the model file.
- Accept any feature subset rather than hard-coding all 11 columns.
- Use `random_state=42` for stochastic algorithms.
- Wrap scale-sensitive estimators with `make_scaled_pipeline()` from `src.preprocessing`.
- Give every model a small valid `parameter_grid()`. Pipeline parameters require the `model__` prefix; the shared tuner checks names before fitting.
- Add any new external dependency and its agreed version to `requirements.txt`.
- Add a short description to the current-model table above.

### 4. Test it

Run the new model by itself first:

```text
python main.py --wine red --model random_forest
```

Then check its optional search:

```text
python main.py --wine red --model random_forest --grid-search
```

Then confirm the complete comparison runs successfully:

```text
python main.py --wine red --model all
```

A missing dependency or error in one registered model will also stop `--model all`, which is why the individual check comes first.

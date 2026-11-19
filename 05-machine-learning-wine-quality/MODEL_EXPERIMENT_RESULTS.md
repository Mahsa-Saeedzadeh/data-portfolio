# Model Experiment Results

Last updated: 2026-08-28

This file records experiments using the current shared data policy. Lower MAE and RMSE are better; higher R2 and class-view scores are better.

## Current shared-default rules

- Original UCI red and white wine data
- Exact duplicates removed before the split
- Fixed 80/20 membership: 1,087/272 rows for red and 3,168/793 for white before training-only outlier removal
- Quality-stratified split, so sklearn's 80/20 class quotas are preserved
- Feature-ranked selection inside each quality class: rows are sorted by their mean percentile rank across all 11 predictors and evenly spaced rows enter the test set
- Ranked training membership is deterministically shuffled with `random_state=42` before cross-validation, so folds do not follow original CSV order
- Training rows outside any selected feature's 3 x IQR limits are removed; test rows are never filtered
- Five-fold cross-validation on the training portion only
- R2 is the mean of the five fold scores and may be negative
- Class-view scores use rounded out-of-fold predictions and the shared margin of +/-1
- Reserved 20% test data not scored
- All 11 features in the current comparison
- `core_3` rows mean `alcohol`, `volatile acidity`, and `sulphates`
- Scaling remains inside the model pipeline
- Outlier limits are calculated once from the complete training portion before CV

The ranked split is distribution-informed: it deliberately spreads the holdout along one combined feature-rank axis. It does not fit a model on test rows, but it is less independent than a random holdout. The README explains how to disable ranking for the more standard stratified-random alternative.

CV and OOF results are training-only comparisons, not final test results. Every populated result row below removes duplicates and training outliers and uses the same stratified, ranked split.

Polynomial Ridge and the ratio-feature experiments were added after the one-time final holdout had already been used. They are post-final training-CV development results only, not frozen-model or holdout results, and they do not change the recorded final test outcome.

## Column legend

| Column | Simple meaning |
|---|---|
| Rank | The row's role or order. A rank is meaningful only among rows that use the same data and split policies. |
| Wine | Red or white wine; the datasets are never mixed. |
| Duplicates | Exact duplicate rows are removed before the split in every populated result. |
| Outliers | Training rows flagged by the 3 x IQR rule are removed in every populated result. Test rows are never filtered. |
| Features | All 11 chemical inputs or the smaller named feature set used in that run. |
| Training rows | Rows available for model fitting and cross-validation after the selected data rules. |
| Model setup | The estimator and important parameter values used for that row. |
| CV MAE | Mean absolute error across five validation folds, measured in quality points. Lower is better. |
| CV RMSE | Root mean squared error across five validation folds. It penalizes larger mistakes more strongly; lower is better. |
| CV R2 | Mean R2 across five validation folds. `1` is perfect, `0` is baseline-level, and negative values are possible; higher is better. |
| OOF accuracy | Accuracy after rounding each out-of-fold regression prediction to a quality class. The rounded class must match exactly (margin 0). |
| OOF +/-1 | Share of rounded out-of-fold predictions no more than one quality point from the true class. The default class margin is 1. |
| OOF macro precision | Precision calculated separately for every quality class and then averaged. It shows how reliable the predictions are across common and rare classes. |
| OOF balanced | Mean recall across the true quality classes. Each class receives equal weight, including rare classes. |
| OOF macro F1 | F1 calculated separately for every quality class and then averaged, so common classes do not dominate. |

`CV` means five-fold cross-validation. `OOF` means out-of-fold: every training row is predicted by a fold model that was not trained on that row. Bold values mark selected or especially relevant results inside their own section; they are not evidence across different split policies.

**Class margin example:** If the true quality is 6, margin 0 accepts only 6, margin 1 accepts rounded predictions 5, 6, or 7, and margin 2 accepts 4 through 8. A larger margin therefore makes the within-margin score easier to achieve. Every matrix row below uses margin 1 so the results remain comparable; OOF accuracy, macro precision, balanced accuracy, and macro F1 do not depend on this margin.

Split policy is stated for each section rather than added as another column, keeping every model table in the same 15-column shape.

## Current shared-default comparison — 2026-08-28

Command: `python main.py --wine both --model all`

Saved comparison name: `both_all_remove_duplicates_remove_outliers_stratified_ranked_all_features_class_margin_1_fixed_results.csv`

These rows all remove duplicates, use the quality-stratified and feature-ranked split, remove training-only 3 x IQR outliers, and use all 11 features. Red and white are ranked separately by CV MAE. Bold values are the best result for that wine and metric; tied best values are both bold.

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Enhanced Voting: equal tuned Random Forest and SVM | **0.473876** | 0.629565 | 0.389858 | **0.618557** | 0.967010 | 0.303874 | 0.284400 | 0.284770 |
| 2 | Red | Removed | Removed | All 11 | 970 | Enhanced Stacking: tuned Random Forest, XGBoost, SVM and Ridge with a scaled Ridge combiner | 0.479308 | **0.628203** | **0.393264** | 0.611340 | **0.971134** | 0.295771 | 0.282481 | 0.282153 |
| 3 | Red | Removed | Removed | All 11 | 970 | Team RBF SVM, C=1, epsilon=.1, gamma=scale | 0.483963 | 0.644668 | 0.358889 | 0.605155 | 0.965979 | 0.294935 | 0.283866 | 0.283668 |
| 4 | Red | Removed | Removed | All 11 | 970 | Neural network A balanced | 0.490249 | 0.635712 | 0.379141 | 0.603093 | 0.969072 | 0.288389 | 0.286226 | 0.284816 |
| 5 | Red | Removed | Removed | All 11 | 970 | Team Random Forest, 100 trees | 0.491340 | 0.640334 | 0.369382 | 0.608247 | 0.970103 | 0.323921 | 0.289339 | 0.291927 |
| 6 | Red | Removed | Removed | All 11 | 970 | Polynomial Ridge fixed default: log on, degree=2, alpha=1 | 0.494057 | 0.646846 | 0.356985 | **0.618557** | 0.969072 | **0.354877** | **0.295532** | **0.302419** |
| 7 | Red | Removed | Removed | All 11 | 970 | Team Lasso, alpha=.001 | 0.494344 | 0.641067 | 0.369537 | 0.602062 | 0.969072 | 0.292937 | 0.272009 | 0.271634 |
| 8 | Red | Removed | Removed | All 11 | 970 | Scaled BayesianRidge defaults | 0.494458 | 0.641195 | 0.369457 | 0.605155 | 0.968041 | 0.298341 | 0.274252 | 0.274558 |
| 9 | Red | Removed | Removed | All 11 | 970 | Team Ridge, alpha=.001 | 0.494852 | 0.641483 | 0.368649 | 0.602062 | 0.969072 | 0.292733 | 0.273007 | 0.272787 |
| 10 | Red | Removed | Removed | All 11 | 970 | Scaled ordinary linear regression | 0.494852 | 0.641483 | 0.368649 | 0.602062 | 0.969072 | 0.292733 | 0.273007 | 0.272787 |
| 11 | Red | Removed | Removed | All 11 | 970 | XGBoost A robust | 0.496491 | 0.643433 | 0.362701 | 0.616495 | 0.968041 | 0.295478 | 0.290669 | 0.289701 |
| 12 | Red | Removed | Removed | All 11 | 970 | Team KNN, k=5, uniform, Euclidean | 0.526804 | 0.681810 | 0.283410 | 0.561856 | 0.965979 | 0.291677 | 0.273739 | 0.274701 |
| 13 | Red | Removed | Removed | All 11 | 970 | Tree depth=5, min leaf=5 | 0.540391 | 0.708038 | 0.225866 | 0.584536 | 0.957732 | 0.311370 | 0.292714 | 0.298167 |
| 14 | Red | Removed | Removed | All 11 | 970 | Predict training-fold mean | 0.685633 | 0.809527 | -0.001505 | 0.403093 | 0.943299 | 0.067182 | 0.166667 | 0.095763 |
| 1 | White | Removed | Removed | All 11 | 3,023 | Enhanced Voting: equal tuned Random Forest and SVM | **0.529906** | 0.693663 | 0.376442 | **0.566325** | 0.962620 | 0.241769 | 0.233392 | 0.231128 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Enhanced Stacking: tuned Random Forest, XGBoost, SVM and Ridge with a scaled Ridge combiner | 0.535589 | **0.691887** | **0.379596** | 0.562024 | **0.964605** | 0.332228 | 0.242526 | 0.241516 |
| 3 | White | Removed | Removed | All 11 | 3,023 | Team RBF SVM, C=1, epsilon=.1, gamma=scale | 0.539150 | 0.712046 | 0.342802 | 0.553755 | 0.956004 | **0.377265** | 0.231690 | 0.231668 |
| 4 | White | Removed | Removed | All 11 | 3,023 | XGBoost A robust | 0.541075 | 0.695717 | 0.372637 | 0.558055 | 0.962951 | 0.294820 | 0.243935 | 0.246203 |
| 5 | White | Removed | Removed | All 11 | 3,023 | Team Random Forest, 100 trees | 0.543267 | 0.701592 | 0.362219 | 0.554416 | 0.962289 | 0.334634 | 0.240851 | 0.242434 |
| 6 | White | Removed | Removed | All 11 | 3,023 | Polynomial Ridge fixed default: log on, degree=2, alpha=1 | 0.553217 | 0.710344 | 0.345726 | 0.549785 | 0.963943 | 0.359379 | 0.238843 | 0.245003 |
| 7 | White | Removed | Removed | All 11 | 3,023 | Neural network A balanced | 0.553614 | 0.714774 | 0.338020 | 0.549454 | 0.959974 | 0.350477 | **0.247810** | **0.254941** |
| 8 | White | Removed | Removed | All 11 | 3,023 | Team Ridge, alpha=.001 | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| 9 | White | Removed | Removed | All 11 | 3,023 | Scaled ordinary linear regression | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| 10 | White | Removed | Removed | All 11 | 3,023 | Team Lasso, alpha=.001 | 0.572318 | 0.735403 | 0.299087 | 0.527291 | 0.951042 | 0.221887 | 0.213869 | 0.211336 |
| 11 | White | Removed | Removed | All 11 | 3,023 | Scaled BayesianRidge defaults | 0.572527 | 0.735786 | 0.298378 | 0.527291 | 0.949719 | 0.221962 | 0.213554 | 0.211022 |
| 12 | White | Removed | Removed | All 11 | 3,023 | Team KNN, k=5, uniform, Euclidean | 0.579764 | 0.759475 | 0.252351 | 0.517036 | 0.949719 | 0.345737 | 0.225946 | 0.225880 |
| 13 | White | Removed | Removed | All 11 | 3,023 | Tree depth=5, min leaf=5 | 0.594408 | 0.757842 | 0.256183 | 0.525968 | 0.950050 | 0.271475 | 0.237456 | 0.240383 |
| 14 | White | Removed | Removed | All 11 | 3,023 | Predict training-fold mean | 0.662868 | 0.879825 | -0.002977 | 0.455177 | 0.926894 | 0.065025 | 0.142857 | 0.089371 |

With the enhanced fixed settings, Voting has the lowest MAE for both wines and the best exact rounded accuracy for white wine. Red Polynomial Ridge ties Voting on exact accuracy and has the strongest red macro precision, balanced accuracy, and macro F1. Stacking still has the best RMSE, R2, and within-one accuracy for both wines. These are training-CV results; Polynomial Ridge was added post-final and the reserved test sets were not reopened.

## Per-model results — current data policy

Every populated row below removes duplicates and training outliers and uses the stratified, ranked split. Placeholder rows inherit the same removal policy.

## Baseline

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | Predict training-fold mean | 0.685633 | 0.809527 | -0.001505 | 0.403093 | 0.943299 | 0.067182 | 0.166667 | 0.095763 |
| Current | White | Removed | Removed | All 11 | 3,023 | Predict training-fold mean | 0.662868 | 0.879825 | -0.002977 | 0.455177 | 0.926894 | 0.065025 | 0.142857 | 0.089371 |
| 1 | TBD | Removed | Removed | TBD | — | Mean or median | — | — | — | — | — | — | — | — |
| 2 | TBD | Removed | Removed | TBD | — | Alternative baseline check | — | — | — | — | — | — | — | — |
| 3 | TBD | Removed | Removed | TBD | — | Alternative baseline check | — | — | — | — | — | — | — | — |

## Decision tree

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | depth=5, min leaf=5 | 0.540391 | 0.708038 | 0.225866 | 0.584536 | 0.957732 | 0.311370 | 0.292714 | 0.298167 |
| Current | White | Removed | Removed | All 11 | 3,023 | depth=5, min leaf=5 | 0.594408 | 0.757842 | 0.256183 | 0.525968 | 0.950050 | 0.271475 | 0.237456 | 0.240383 |
| 1 | TBD | Removed | Removed | TBD | — | Test depth and minimum leaf size | — | — | — | — | — | — | — | — |
| 2 | TBD | Removed | Removed | TBD | — | Test split limits and pruning | — | — | — | — | — | — | — | — |
| 3 | TBD | Removed | Removed | TBD | — | Best later tree setup | — | — | — | — | — | — | — | — |

## KNN

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | team default: scaled, k=5, uniform, Euclidean | 0.526804 | 0.681810 | 0.283410 | 0.561856 | 0.965979 | 0.291677 | 0.273739 | 0.274701 |
| Current | White | Removed | Removed | All 11 | 3,023 | team default: scaled, k=5, uniform, Euclidean | 0.579764 | 0.759475 | 0.252351 | 0.517036 | 0.949719 | 0.345737 | 0.225946 | 0.225880 |
| 1 | TBD | Removed | Removed | TBD | — | Test number of neighbours | — | — | — | — | — | — | — | — |
| 2 | TBD | Removed | Removed | TBD | — | Test uniform/distance weights and p=1/2 | — | — | — | — | — | — | — | — |
| 3 | TBD | Removed | Removed | TBD | — | Best later KNN setup | — | — | — | — | — | — | — | — |

## SVM

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | team base: scaled RBF, C=1, epsilon=.1, gamma=scale | 0.483963 | 0.644668 | 0.358889 | 0.605155 | 0.965979 | 0.294935 | 0.283866 | 0.283668 |
| Current | White | Removed | Removed | All 11 | 3,023 | team base: scaled RBF, C=1, epsilon=.1, gamma=scale | 0.539150 | 0.712046 | 0.342802 | 0.553755 | 0.956004 | 0.377265 | 0.231690 | 0.231668 |
| 1 | TBD | Removed | Removed | TBD | — | Test C and epsilon | — | — | — | — | — | — | — | — |
| 2 | TBD | Removed | Removed | TBD | — | Test gamma and kernel | — | — | — | — | — | — | — | — |
| 3 | TBD | Removed | Removed | TBD | — | Best later SVM setup | — | — | — | — | — | — | — | — |

## Linear regression

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | Scaled ordinary linear regression | 0.494852 | 0.641483 | 0.368649 | 0.602062 | 0.969072 | 0.292733 | 0.273007 | 0.272787 |
| Current | White | Removed | Removed | All 11 | 3,023 | Scaled ordinary linear regression | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| 1 | TBD | Removed | Removed | TBD | — | Residual-pattern check | — | — | — | — | — | — | — | — |
| 2 | TBD | Removed | Removed | TBD | — | Agreed feature experiment | — | — | — | — | — | — | — | — |
| 3 | TBD | Removed | Removed | TBD | — | Ridge/Lasso only as separate models | — | — | — | — | — | — | — | — |

## Ridge regression

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | Latest team default: scaled Ridge, alpha=.001 | 0.494852 | 0.641483 | 0.368649 | 0.602062 | 0.969072 | 0.292733 | 0.273007 | 0.272787 |
| Current | White | Removed | Removed | All 11 | 3,023 | Latest team default: scaled Ridge, alpha=.001 | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |

## Polynomial Ridge regression

These runs were made after the final holdout had already been evaluated. They compare configurations only through the shared five-fold training CV; none is a frozen or holdout result. "Log on" means that the model applies `log1p` to the four selected non-negative, skewed features before polynomial expansion, scaling, and Ridge regression.

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Fixed original | Red | Removed | Removed | All 11 | 970 | log on, degree=2, alpha=1 | 0.494057 | 0.646846 | 0.356985 | 0.618557 | 0.969072 | 0.354877 | 0.295532 | 0.302419 |
| Grid selected original | Red | Removed | Removed | All 11 | 970 | log on, degree=3, alpha=100 | **0.488699** | **0.634621** | **0.381026** | 0.614433 | 0.971134 | 0.341175 | 0.286889 | 0.291073 |
| Fixed ratios | Red | Removed | Removed | All 11 + 5 ratios | 970 | log on, degree=2, alpha=1 | 0.498723 | 0.653932 | 0.342462 | 0.614433 | 0.963918 | 0.335858 | 0.295789 | 0.301323 |
| Grid selected ratios | Red | Removed | Removed | All 11 + 5 ratios | 970 | log on, degree=2, alpha=10 | **0.493612** | **0.642550** | **0.365283** | 0.606186 | 0.972165 | 0.326309 | 0.283512 | 0.287133 |
| Fixed original | White | Removed | Removed | All 11 | 3,023 | log on, degree=2, alpha=1 | 0.553217 | 0.710344 | 0.345726 | 0.549785 | 0.963943 | 0.359379 | 0.238843 | 0.245003 |
| Grid selected original | White | Removed | Removed | All 11 | 3,023 | log on, degree=4, alpha=100 | **0.548982** | **0.706170** | **0.353520** | 0.551108 | 0.962620 | 0.447683 | 0.239493 | 0.246273 |
| Fixed ratios | White | Removed | Removed | All 11 + 5 ratios | 3,023 | log on, degree=2, alpha=1 | 0.553004 | 0.710208 | 0.345824 | 0.551108 | 0.960635 | 0.362149 | 0.243499 | 0.252231 |
| Grid selected ratios | White | Removed | Removed | All 11 + 5 ratios | 3,023 | log on, degree=3, alpha=100 | **0.549892** | **0.707329** | **0.351443** | 0.549785 | 0.962620 | 0.380594 | 0.239443 | 0.247246 |

The ratio features did not improve the selected Polynomial Ridge MAE: the original inputs were better for both red (`0.488699` versus `0.493612`) and white wine (`0.548982` versus `0.549892`). The small mixed changes in the other scores are not a reason to replace the simpler original feature set.

## Lasso regression

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | Latest team default: scaled Lasso, alpha=.001 | 0.494344 | 0.641067 | 0.369537 | 0.602062 | 0.969072 | 0.292937 | 0.272009 | 0.271634 |
| Current | White | Removed | Removed | All 11 | 3,023 | Latest team default: scaled Lasso, alpha=.001 | 0.572318 | 0.735403 | 0.299087 | 0.527291 | 0.951042 | 0.221887 | 0.213869 | 0.211336 |

### Ratio feature experiment

This compact post-final training-CV check compares each grid-selected linear model with and without the five ratio features. The class-view metrics were not recorded for the compact ratio-selection runs and are therefore shown as `—`; no holdout values are included.

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Original | Red | Removed | Removed | All 11 | 970 | Linear: fit_intercept=true, positive=false | **0.494852** | **0.641483** | **0.368649** | 0.602062 | 0.969072 | 0.292733 | 0.273007 | 0.272787 |
| Ratios | Red | Removed | Removed | All 11 + 5 ratios | 970 | Linear: fit_intercept=true, positive=false | 0.501572 | 0.649555 | 0.352438 | — | — | — | — | — |
| Original | Red | Removed | Removed | All 11 | 970 | Ridge: alpha=10 | **0.494500** | **0.641258** | **0.369200** | 0.601031 | 0.969072 | 0.292320 | 0.272581 | 0.272383 |
| Ratios | Red | Removed | Removed | All 11 + 5 ratios | 970 | Ridge: alpha=100 | 0.496437 | 0.643443 | 0.365077 | — | — | — | — | — |
| Original | Red | Removed | Removed | All 11 | 970 | Lasso: alpha=.001 | **0.494344** | **0.641067** | **0.369537** | 0.602062 | 0.969072 | 0.292937 | 0.272009 | 0.271634 |
| Ratios | Red | Removed | Removed | All 11 + 5 ratios | 970 | Lasso: alpha=.01 | 0.495007 | 0.641567 | 0.368853 | — | — | — | — | — |
| Original | White | Removed | Removed | All 11 | 3,023 | Linear: fit_intercept=true, positive=false | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| Ratios | White | Removed | Removed | All 11 + 5 ratios | 3,023 | Linear: fit_intercept=true, positive=false | **0.571089** | **0.731694** | **0.306178** | — | — | — | — | — |
| Original | White | Removed | Removed | All 11 | 3,023 | Ridge: alpha=.1 | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| Ratios | White | Removed | Removed | All 11 + 5 ratios | 3,023 | Ridge: alpha=.0001 | **0.571089** | **0.731694** | **0.306178** | — | — | — | — | — |
| Original | White | Removed | Removed | All 11 | 3,023 | Lasso: alpha=.0001 | 0.572299 | 0.735408 | 0.299061 | 0.527952 | 0.951373 | 0.221970 | 0.214567 | 0.212021 |
| Ratios | White | Removed | Removed | All 11 + 5 ratios | 3,023 | Lasso: alpha=.0001 | **0.571267** | **0.731616** | **0.306315** | — | — | — | — | — |

The ratio features made every selected red linear model slightly worse and every white model slightly better on MAE. Because the direction changes by wine and the gains are small, there is no consistent improvement; the original 11 features remain the simpler shared default.

## Bayesian Ridge

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | Scaled BayesianRidge defaults | 0.494458 | 0.641195 | 0.369457 | 0.605155 | 0.968041 | 0.298341 | 0.274252 | 0.274558 |
| Current | White | Removed | Removed | All 11 | 3,023 | Scaled BayesianRidge defaults | 0.572527 | 0.735786 | 0.298378 | 0.527291 | 0.949719 | 0.221962 | 0.213554 | 0.211022 |
| 1 | TBD | Removed | Removed | TBD | — | Small prior-strength grid | — | — | — | — | — | — | — | — |
| 2 | TBD | Removed | Removed | TBD | — | Alternative prior-strength grid | — | — | — | — | — | — | — | — |
| 3 | TBD | Removed | Removed | TBD | — | Best later Bayesian setup | — | — | — | — | — | — | — | — |

## XGBoost

### Current three parameter settings

All rows remove duplicates and training outliers, use the stratified and ranked split, and use all 11 features. Config A remains the implemented model and gives the strongest main regression results under this policy.

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 selected | Red | Removed | Removed | All 11 | 970 | A robust: 350 trees, depth 4, lr=.025, child=1, row=.70, column=.80, gamma=.25, alpha=0, lambda=2 | **0.496491** | **0.643433** | **0.362701** | **0.616495** | **0.968041** | 0.295478 | 0.290669 | 0.289701 |
| 1 selected | White | Removed | Removed | All 11 | 3,023 | A robust: 350 trees, depth 4, lr=.025, child=1, row=.70, column=.80, gamma=.25, alpha=0, lambda=2 | **0.541075** | **0.695717** | **0.372637** | **0.558055** | **0.962951** | 0.294820 | 0.243935 | 0.246203 |
| 2 optional | Red | Removed | Removed | All 11 | 970 | B fast aggressive: 250 trees, depth 6, lr=.10, child=2, row=.95, column=.95, gamma=.01, alpha=.01, lambda=1 | 0.506385 | 0.667661 | 0.313701 | 0.598969 | 0.962887 | 0.338410 | 0.292424 | 0.299424 |
| 2 optional | White | Removed | Removed | All 11 | 3,023 | B fast aggressive: 250 trees, depth 6, lr=.10, child=2, row=.95, column=.95, gamma=.01, alpha=.01, lambda=1 | 0.546701 | 0.710912 | 0.344928 | 0.554085 | 0.957327 | **0.394878** | **0.263525** | **0.276391** |
| 3 diagnostic | Red | Removed | Removed | All 11 | 970 | C deep aggressive: 900 trees, depth 7, lr=.075, child=5, row=.95, column=.65, gamma=.025, alpha=.001, lambda=1 | 0.506411 | 0.665608 | 0.318997 | 0.601031 | 0.961856 | **0.353307** | **0.298452** | **0.306972** |
| 3 diagnostic | White | Removed | Removed | All 11 | 3,023 | C deep aggressive: 900 trees, depth 7, lr=.075, child=5, row=.95, column=.65, gamma=.025, alpha=.001, lambda=1 | 0.545924 | 0.712072 | 0.342669 | 0.548793 | 0.957658 | 0.360750 | 0.257129 | 0.268465 |

Config A remains the current estimator in `src/models/xgboost.py`. It is still a strong fixed model, especially for white-wine RMSE and R2, but the newly integrated team models now lead some measures.

### Current feature-setting rows using Config A

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | A robust | **0.496491** | **0.643433** | **0.362701** | **0.616495** | **0.968041** | 0.295478 | **0.290669** | **0.289701** |
| 2 | White | Removed | Removed | All 11 | 3,023 | A robust | **0.541075** | **0.695717** | **0.372637** | **0.558055** | **0.962951** | 0.294820 | **0.243935** | **0.246203** |
| 3 | Red | Removed | Removed | core_3 | 1,075 | A robust | 0.517862 | 0.672463 | 0.329503 | 0.590698 | 0.963721 | **0.301206** | 0.278763 | 0.280761 |
| 4 | White | Removed | Removed | core_3 | 3,131 | A robust | 0.584325 | 0.754512 | 0.272984 | 0.526030 | 0.946024 | **0.298736** | 0.223204 | 0.225747 |
| 5 | TBD | Removed | Removed | TBD | — | Next feature set | — | — | — | — | — | — | — | — |
| 6 | TBD | Removed | Removed | TBD | — | Next feature set | — | — | — | — | — | — | — | — |
| 7 | TBD | Removed | Removed | TBD | — | Best later feature setting | — | — | — | — | — | — | — | — |

The `core_3` runs retain more training rows because the outlier rule checks only the selected inputs. Even with those extra rows, all 11 features give the stronger regression results.

### Effect of the data-policy changes

- Duplicate removal caused the largest consistent score reduction. With the earlier random split, red MAE changed from `0.466377` to `0.502305`, and white MAE changed from `0.524102` to `0.543172`.
- Outlier removal alone improved MAE to `0.453800` for red and `0.521325` for white.
- After both removals, changing from the random split to the stratified and ranked split changed MAE only from `0.492360` to `0.496491` for red and from `0.541816` to `0.541075` for white.

**So what:** The lower XGBoost scores mainly come from removing repeated rows, not from stratification and ranking. The new comparison is stricter and less dependent on repeated observations, so a lower score does not automatically mean that the model itself became worse.

## Neural network

### Current three parameter settings

All rows remove duplicates and training outliers and use the stratified and ranked split. The three finalists scale X inside a pipeline and y through `TransformedTargetRegressor`, use two layers `(128, 64)`, ReLU, Adam, early stopping, patience 30, tolerance `1e-4`, and `random_state=42`.

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 implemented | Red | Removed | Removed | All 11 | 970 | A balanced: `(128, 64)`, alpha=.01, lr=.001, X/y scaled | 0.490249 | **0.635712** | 0.379141 | **0.603093** | 0.969072 | 0.288389 | 0.286226 | 0.284816 |
| 2 implemented | White | Removed | Removed | All 11 | 3,023 | A balanced: `(128, 64)`, alpha=.01, lr=.001, X/y scaled | 0.553614 | 0.714774 | 0.338020 | 0.549454 | **0.959974** | 0.350477 | **0.247810** | **0.254941** |
| 1 current best | Red | Removed | Removed | All 11 | 970 | B stronger regularization: `(128, 64)`, alpha=.10, lr=.001, X/y scaled | **0.489673** | 0.635811 | **0.379274** | 0.597938 | **0.970103** | **0.308912** | **0.289070** | **0.290359** |
| 1 current best | White | Removed | Removed | All 11 | 3,023 | B stronger regularization: `(128, 64)`, alpha=.10, lr=.001, X/y scaled | **0.551749** | **0.711325** | **0.344305** | 0.551770 | 0.959312 | **0.365934** | 0.246594 | 0.251835 |
| 3 optional | Red | Removed | Removed | All 11 | 970 | C faster learning: `(128, 64)`, alpha=.001, lr=.002, X/y scaled | 0.494163 | 0.640673 | 0.368868 | 0.590722 | **0.970103** | 0.278259 | 0.279098 | 0.276621 |
| 3 optional | White | Removed | Removed | All 11 | 3,023 | C faster learning: `(128, 64)`, alpha=.001, lr=.002, X/y scaled | 0.553244 | 0.713336 | 0.340523 | **0.553424** | 0.959312 | 0.350833 | 0.244943 | 0.250189 |

Config A remains the estimator in `src/models/NN.py`, and none of these runs produced convergence warnings. Config B is now slightly stronger under the current data policy, so changing the implemented model should be considered after a repeated robustness check.

### Current feature-setting rows using implemented Config A

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | A balanced | **0.490249** | **0.635712** | **0.379141** | **0.603093** | **0.969072** | 0.288389 | **0.286226** | **0.284816** |
| 2 | White | Removed | Removed | All 11 | 3,023 | A balanced | **0.553614** | **0.714774** | **0.338020** | **0.549454** | **0.959974** | **0.350477** | **0.247810** | **0.254941** |
| 3 | Red | Removed | Removed | core_3 | 1,075 | A balanced | 0.511340 | 0.661417 | 0.351659 | 0.593488 | 0.968372 | **0.291840** | 0.269256 | 0.268738 |
| 4 | White | Removed | Removed | core_3 | 3,131 | A balanced | 0.583946 | 0.756043 | 0.270213 | 0.536570 | 0.947301 | 0.297991 | 0.221320 | 0.221408 |
| 5 | TBD | Removed | Removed | TBD | — | Next feature set | — | — | — | — | — | — | — | — |
| 6 | TBD | Removed | Removed | TBD | — | Next feature set | — | — | — | — | — | — | — | — |
| 7 | TBD | Removed | Removed | TBD | — | Best later feature setting | — | — | — | — | — | — | — | — |

The `core_3` runs retain more training rows because fewer features are checked by the outlier rule. All 11 features still give the stronger regression results.

### Effect of the data-policy changes

- Duplicate removal caused the largest consistent shift. With the earlier random split, red MAE changed from `0.489906` to `0.514148`, and white MAE changed from `0.529428` to `0.548892`.
- Outlier removal alone improved red MAE to `0.480229`, but white MAE moved slightly upward to `0.535021`.
- After both removals, changing from the random split to the stratified and ranked split improved red MAE from `0.495374` to `0.490249`, while white MAE changed from `0.549058` to `0.553614`.

**So what:** Duplicate removal explains most of the consistent reduction. Outlier removal depends on the wine, and the split change has a smaller mixed effect. The current results are therefore more conservative, especially for white wine.

## Voting ensemble

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | Equal vote: tuned Random Forest (200 trees, unrestricted, leaf 1, sqrt features) and scaled RBF SVM (C=.5, epsilon=.05, gamma=.1); other member weights are zero | **0.473876** | 0.629565 | 0.389858 | **0.618557** | 0.967010 | 0.303874 | 0.284400 | 0.284770 |
| Current | White | Removed | Removed | All 11 | 3,023 | Equal vote: tuned Random Forest (200 trees, unrestricted, leaf 1, sqrt features) and scaled RBF SVM (C=.5, epsilon=.05, gamma=.1); other member weights are zero | **0.529906** | 0.693663 | 0.376442 | **0.566325** | 0.962620 | 0.241769 | 0.233392 | 0.231128 |

## Stacking ensemble

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | Tuned Random Forest (200 trees, leaf 3, all features), XGBoost, tuned SVM (C=1, epsilon=.05, gamma=.03), and scaled Ridge; scaled Ridge alpha=.001 combiner; passthrough=False | 0.479308 | **0.628203** | **0.393264** | 0.611340 | **0.971134** | 0.295771 | 0.282481 | 0.282153 |
| Current | White | Removed | Removed | All 11 | 3,023 | Tuned Random Forest (200 trees, leaf 3, all features), XGBoost, tuned SVM (C=1, epsilon=.05, gamma=.03), and scaled Ridge; scaled Ridge alpha=.001 combiner; passthrough=False | 0.535589 | **0.691887** | **0.379596** | 0.562024 | **0.964605** | 0.332228 | 0.242526 | 0.241516 |

## Random forest

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Current | Red | Removed | Removed | All 11 | 970 | Team default: 100 trees, unrestricted, all features | 0.491340 | 0.640334 | 0.369382 | 0.608247 | 0.970103 | 0.323921 | 0.289339 | 0.291927 |
| Current | White | Removed | Removed | All 11 | 3,023 | Team default: 100 trees, unrestricted, all features | 0.543267 | 0.701592 | 0.362219 | 0.554416 | 0.962289 | 0.334634 | 0.240851 | 0.242434 |

## PCA decision

PCA is not used in the current shared default. The project has only 11 input features, so dimensionality and runtime are already manageable, and keeping the original columns makes the model easier to explain.

PCA may be tested later for KNN, SVM, linear regression, Bayesian Ridge, or the neural network. The safe order is:

```python
Pipeline([
    ("scaler", StandardScaler()),
    ("pca", PCA(n_components=...)),
    ("model", model),
])
```

Compare no PCA against a few small choices such as 5, 7, or 9 components inside training cross-validation. Do not fit PCA before the split or on the complete dataset. PCA is generally not recommended for Decision Tree or XGBoost because rotated components reduce interpretability and usually do not help tree splits.

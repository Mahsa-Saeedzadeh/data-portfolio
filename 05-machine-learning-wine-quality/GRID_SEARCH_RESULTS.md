# Grid Search Results

Last updated: 2026-08-28

Original comparison command: `python main.py --wine both --model all --grid-search`

Post-final Polynomial Ridge commands: `python main.py --wine both --model polynomial_ridge --grid-search` and the same command with `--feature-engineering ratios`.

The main ranking uses the same removed-duplicate, training-only outlier, quality-stratified, feature-ranked, all-11-feature data policy as the fixed comparison. The separate ratio rows add five engineered inputs after splitting and outlier handling. Grid search remains disabled by default and does not overwrite the current fixed model settings.

The search selected the lowest mean five-fold CV MAE. RMSE, R2, and the rounded class view are supporting measures. Only training rows were used; the reserved 20% test sets were not scored.

> These are search-CV results, not an independent nested-CV estimate. The same training folds helped choose and report each winning setup, so small improvements should be treated cautiously. Polynomial Ridge and the ratio experiments were added after the one-time holdout was consumed; they are training-CV development results only and must not reopen that holdout.

## Column legend

The columns have the same meaning as in `MODEL_EXPERIMENT_RESULTS.md`. OOF means out-of-fold. OOF accuracy requires an exact rounded quality match; OOF +/-1 accepts a rounded prediction within one quality point. Class scores are calculated only for the selected candidate in each search, so other top-candidate rows show a dash in those columns.

Voting weight lists follow this order: Random Forest, XGBoost, Ridge, SVM, neural network. A zero and the word `drop` mean that member was not used in that candidate. In Stacking, `passthrough=true` means the original 11 inputs were also given to the final combiner.

## Search coverage

| Model | Candidates per wine | Search source |
|---|---:|---|
| Baseline | 2 | Shared comparison of mean and median |
| Decision tree | 25 | Shared small complexity grid including an unrestricted tree |
| Random forest | 16 | Shared small grid containing the submitted 100-tree default |
| KNN | 24 | Shared small grid containing the submitted k=5 default |
| SVM | 36 | Exact grid submitted by the SVM group |
| Linear regression | 4 | Shared fit-intercept and positive-coefficient checks |
| Ridge regression | 7 | Exact seven alpha values submitted by the linear group |
| Polynomial Ridge | 56 | Log off/on x degrees 1-4 x the seven submitted Ridge alpha values |
| Lasso regression | 7 | Exact seven alpha values submitted by the linear group |
| Bayesian Ridge | 5 | Shared small prior-strength grid |
| XGBoost | 3 | Three previously documented training-CV configurations |
| Neural network | 5 | Three documented finalists plus two layer alternatives |
| Voting ensemble | 16 | Two tuned RF/SVM profiles with eight member and weight recipes |
| Stacking ensemble | 10 | Two tuned base profiles with five combiner and passthrough choices |

## Selected configurations across all models

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Voting ensemble: {"forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03, "weights": [1, 0, 0, 2, 0], "xgboost": "drop"} | 0.470944 | 0.627789 | 0.393325 | 0.616495 | 0.971134 | 0.300794 | 0.285460 | 0.285341 |
| 2 | Red | Removed | Removed | All 11 | 970 | SVM: {"C": 1.0, "epsilon": 0.05, "gamma": 0.03} | 0.473737 | 0.636503 | 0.375750 | 0.612371 | 0.969072 | 0.301274 | 0.281708 | 0.281763 |
| 3 | Red | Removed | Removed | All 11 | 970 | Stacking ensemble: {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge(alpha=0.001))])", "forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "passthrough": false, "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03} | 0.479308 | 0.628203 | 0.393264 | 0.611340 | 0.971134 | 0.295771 | 0.282481 | 0.282153 |
| 4 | Red | Removed | Removed | All 11 | 970 | Random forest: {"max_depth": null, "max_features": 1.0, "min_samples_leaf": 3, "n_estimators": 200} | 0.486291 | 0.633751 | 0.382834 | 0.616495 | 0.972165 | 0.298435 | 0.289754 | 0.289687 |
| 5 | Red | Removed | Removed | All 11 | 970 | Polynomial Ridge: {"alpha": 100, "log__enabled": true, "poly__degree": 3} | 0.488699 | 0.634621 | 0.381026 | 0.614433 | 0.971134 | 0.341175 | 0.286889 | 0.291073 |
| 6 | Red | Removed | Removed | All 11 | 970 | Neural network: {"activation": "relu", "alpha": 0.1, "hidden_layer_sizes": [128, 64], "learning_rate_init": 0.001, "solver": "adam"} | 0.489673 | 0.635811 | 0.379274 | 0.597938 | 0.970103 | 0.308912 | 0.289070 | 0.290359 |
| 7 | Red | Removed | Removed | All 11 | 970 | Lasso regression: {"alpha": 0.001} | 0.494344 | 0.641067 | 0.369537 | 0.602062 | 0.969072 | 0.292937 | 0.272009 | 0.271634 |
| 8 | Red | Removed | Removed | All 11 | 970 | Bayesian Ridge: {"alpha_1": 1e-06, "alpha_2": 1e-06, "lambda_1": 1e-05, "lambda_2": 1e-05} | 0.494458 | 0.641195 | 0.369457 | 0.605155 | 0.968041 | 0.298341 | 0.274252 | 0.274558 |
| 9 | Red | Removed | Removed | All 11 | 970 | Ridge regression: {"alpha": 10} | 0.494500 | 0.641258 | 0.369200 | 0.601031 | 0.969072 | 0.292320 | 0.272581 | 0.272383 |
| 10 | Red | Removed | Removed | All 11 | 970 | Linear regression: {"fit_intercept": true, "positive": false} | 0.494852 | 0.641483 | 0.368649 | 0.602062 | 0.969072 | 0.292733 | 0.273007 | 0.272787 |
| 11 | Red | Removed | Removed | All 11 | 970 | XGBoost: {"colsample_bytree": 0.8, "gamma": 0.25, "learning_rate": 0.025, "max_depth": 4, "min_child_weight": 1, "n_estimators": 350, "n_jobs": 1, "objective": "reg:squarederror", "random_state": 42, "reg_alpha": 0.0, "reg_lambda": 2.0, "subsample": 0.7, "verbosity": 0} | 0.496491 | 0.643433 | 0.362701 | 0.616495 | 0.968041 | 0.295478 | 0.290669 | 0.289701 |
| 12 | Red | Removed | Removed | All 11 | 970 | KNN: {"n_neighbors": 15, "p": 1, "weights": "distance"} | 0.501927 | 0.642325 | 0.367267 | 0.601031 | 0.963918 | 0.291087 | 0.273797 | 0.273431 |
| 13 | Red | Removed | Removed | All 11 | 970 | Decision tree: {"max_depth": 5, "min_samples_leaf": 10, "min_samples_split": 2} | 0.530079 | 0.685119 | 0.280359 | 0.592784 | 0.958763 | 0.321469 | 0.288088 | 0.295475 |
| 14 | Red | Removed | Removed | All 11 | 970 | Baseline: {"strategy": "median"} | 0.658763 | 0.889232 | -0.210091 | 0.403093 | 0.943299 | 0.067182 | 0.166667 | 0.095763 |
| 1 | White | Removed | Removed | All 11 | 3,023 | Voting ensemble: {"forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1, "weights": [1, 0, 0, 1, 0], "xgboost": "drop"} | 0.529906 | 0.693663 | 0.376442 | 0.566325 | 0.962620 | 0.241769 | 0.233392 | 0.231128 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Stacking ensemble: {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge(alpha=0.1))])", "forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "passthrough": true, "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1} | 0.530087 | 0.685568 | 0.390702 | 0.567648 | 0.965266 | 0.382540 | 0.247369 | 0.247503 |
| 3 | White | Removed | Removed | All 11 | 3,023 | Random forest: {"max_depth": null, "max_features": "sqrt", "min_samples_leaf": 1, "n_estimators": 200} | 0.536664 | 0.690850 | 0.381515 | 0.560370 | 0.963943 | 0.237989 | 0.235581 | 0.233010 |
| 4 | White | Removed | Removed | All 11 | 3,023 | SVM: {"C": 0.5, "epsilon": 0.05, "gamma": 0.1} | 0.537761 | 0.714490 | 0.338354 | 0.555739 | 0.956996 | 0.234936 | 0.226016 | 0.222825 |
| 5 | White | Removed | Removed | All 11 | 3,023 | XGBoost: {"colsample_bytree": 0.8, "gamma": 0.25, "learning_rate": 0.025, "max_depth": 4, "min_child_weight": 1, "n_estimators": 350, "n_jobs": 1, "objective": "reg:squarederror", "random_state": 42, "reg_alpha": 0.0, "reg_lambda": 2.0, "subsample": 0.7, "verbosity": 0} | 0.541075 | 0.695717 | 0.372637 | 0.558055 | 0.962951 | 0.294820 | 0.243935 | 0.246203 |
| 6 | White | Removed | Removed | All 11 | 3,023 | Polynomial Ridge: {"alpha": 100, "log__enabled": true, "poly__degree": 4} | 0.548982 | 0.706170 | 0.353520 | 0.551108 | 0.962620 | 0.447683 | 0.239493 | 0.246273 |
| 7 | White | Removed | Removed | All 11 | 3,023 | KNN: {"n_neighbors": 15, "p": 1, "weights": "distance"} | 0.549965 | 0.714991 | 0.337546 | 0.557724 | 0.955012 | 0.239427 | 0.233476 | 0.231771 |
| 8 | White | Removed | Removed | All 11 | 3,023 | Neural network: {"activation": "relu", "alpha": 0.1, "hidden_layer_sizes": [128, 64], "learning_rate_init": 0.001, "solver": "adam"} | 0.551749 | 0.711325 | 0.344305 | 0.551770 | 0.959312 | 0.365934 | 0.246594 | 0.251835 |
| 9 | White | Removed | Removed | All 11 | 3,023 | Lasso regression: {"alpha": 0.0001} | 0.572299 | 0.735408 | 0.299061 | 0.527952 | 0.951373 | 0.221970 | 0.214567 | 0.212021 |
| 10 | White | Removed | Removed | All 11 | 3,023 | Ridge regression: {"alpha": 0.1} | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| 11 | White | Removed | Removed | All 11 | 3,023 | Linear regression: {"fit_intercept": true, "positive": false} | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| 12 | White | Removed | Removed | All 11 | 3,023 | Bayesian Ridge: {"alpha_1": 1e-06, "alpha_2": 1e-06, "lambda_1": 1e-05, "lambda_2": 1e-05} | 0.572527 | 0.735785 | 0.298378 | 0.527291 | 0.949719 | 0.221962 | 0.213554 | 0.211022 |
| 13 | White | Removed | Removed | All 11 | 3,023 | Decision tree: {"max_depth": 5, "min_samples_leaf": 1, "min_samples_split": 10} | 0.590352 | 0.759440 | 0.252605 | 0.527622 | 0.950380 | 0.284292 | 0.241470 | 0.246791 |
| 14 | White | Removed | Removed | All 11 | 3,023 | Baseline: {"strategy": "median"} | 0.622565 | 0.886940 | -0.019116 | 0.455177 | 0.926894 | 0.065025 | 0.142857 | 0.089371 |

The best selected red-wine MAE is Voting ensemble; the best selected white-wine MAE is Voting ensemble. These winners are based on MAE; another metric can prefer a different model.

## Effect compared with the latest fixed defaults

A positive MAE improvement means grid search reduced the error.

| Wine | Model | Fixed CV MAE | Grid CV MAE | MAE improvement |
|---|---|---:|---:|---:|
| Red | Voting ensemble | 0.473876 | 0.470944 | +0.002931 |
| Red | SVM | 0.483963 | 0.473737 | +0.010226 |
| Red | Stacking ensemble | 0.479308 | 0.479308 | +0.000000 |
| Red | Random forest | 0.491340 | 0.486291 | +0.005049 |
| Red | Polynomial Ridge | 0.494057 | 0.488699 | +0.005358 |
| Red | Neural network | 0.490249 | 0.489673 | +0.000576 |
| Red | Lasso regression | 0.494344 | 0.494344 | -0.000000 |
| Red | Bayesian Ridge | 0.494458 | 0.494458 | +0.000000 |
| Red | Ridge regression | 0.494852 | 0.494500 | +0.000352 |
| Red | Linear regression | 0.494852 | 0.494852 | +0.000000 |
| Red | XGBoost | 0.496491 | 0.496491 | +0.000000 |
| Red | KNN | 0.526804 | 0.501927 | +0.024877 |
| Red | Decision tree | 0.540391 | 0.530079 | +0.010311 |
| Red | Baseline | 0.685633 | 0.658763 | +0.026871 |
| White | Voting ensemble | 0.529906 | 0.529906 | +0.000000 |
| White | Stacking ensemble | 0.535589 | 0.530087 | +0.005502 |
| White | Random forest | 0.543267 | 0.536664 | +0.006603 |
| White | SVM | 0.539150 | 0.537761 | +0.001388 |
| White | XGBoost | 0.541075 | 0.541075 | +0.000000 |
| White | Polynomial Ridge | 0.553217 | 0.548982 | +0.004235 |
| White | KNN | 0.579764 | 0.549965 | +0.029799 |
| White | Neural network | 0.553614 | 0.551749 | +0.001865 |
| White | Lasso regression | 0.572318 | 0.572299 | +0.000018 |
| White | Ridge regression | 0.572302 | 0.572302 | +0.000000 |
| White | Linear regression | 0.572302 | 0.572302 | +0.000000 |
| White | Bayesian Ridge | 0.572527 | 0.572527 | +0.000000 |
| White | Decision tree | 0.594408 | 0.590352 | +0.004056 |
| White | Baseline | 0.662868 | 0.622565 | +0.040303 |

The effect table shows which searches produced a meaningful MAE change and which fixed settings were already close to the best tested option. A lower MAE can still come with a weaker RMSE or R2, so one metric does not tell the whole story.

## Best options inside each model

### Baseline

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Baseline: {"strategy": "median"} | 0.658763 | 0.889232 | -0.210091 | 0.403093 | 0.943299 | 0.067182 | 0.166667 | 0.095763 |
| 2 | Red | Removed | Removed | All 11 | 970 | Baseline: {"strategy": "mean"} | 0.685633 | 0.809527 | -0.001505 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Baseline: {"strategy": "median"} | 0.622565 | 0.886940 | -0.019116 | 0.455177 | 0.926894 | 0.065025 | 0.142857 | 0.089371 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Baseline: {"strategy": "mean"} | 0.662868 | 0.879825 | -0.002977 | â€” | â€” | â€” | â€” | â€” |

### Decision tree

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Decision tree: {"max_depth": 5, "min_samples_leaf": 10, "min_samples_split": 2} | 0.530079 | 0.685119 | 0.280359 | 0.592784 | 0.958763 | 0.321469 | 0.288088 | 0.295475 |
| 2 | Red | Removed | Removed | All 11 | 970 | Decision tree: {"max_depth": 5, "min_samples_leaf": 10, "min_samples_split": 10} | 0.530079 | 0.685119 | 0.280359 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Decision tree: {"max_depth": 3, "min_samples_leaf": 10, "min_samples_split": 2} | 0.535228 | 0.687579 | 0.274371 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Decision tree: {"max_depth": 5, "min_samples_leaf": 1, "min_samples_split": 10} | 0.590352 | 0.759440 | 0.252605 | 0.527622 | 0.950380 | 0.284292 | 0.241470 | 0.246791 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Decision tree: {"max_depth": 5, "min_samples_leaf": 1, "min_samples_split": 2} | 0.591621 | 0.761571 | 0.248426 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Decision tree: {"max_depth": 5, "min_samples_leaf": 10, "min_samples_split": 2} | 0.594208 | 0.758394 | 0.254880 | â€” | â€” | â€” | â€” | â€” |

### Random forest

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Random forest: {"max_depth": null, "max_features": 1.0, "min_samples_leaf": 3, "n_estimators": 200} | 0.486291 | 0.633751 | 0.382834 | 0.616495 | 0.972165 | 0.298435 | 0.289754 | 0.289687 |
| 2 | Red | Removed | Removed | All 11 | 970 | Random forest: {"max_depth": null, "max_features": "sqrt", "min_samples_leaf": 3, "n_estimators": 200} | 0.486553 | 0.631614 | 0.387817 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Random forest: {"max_depth": 10, "max_features": 1.0, "min_samples_leaf": 3, "n_estimators": 200} | 0.487007 | 0.634086 | 0.382109 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Random forest: {"max_depth": null, "max_features": "sqrt", "min_samples_leaf": 1, "n_estimators": 200} | 0.536664 | 0.690850 | 0.381515 | 0.560370 | 0.963943 | 0.237989 | 0.235581 | 0.233010 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Random forest: {"max_depth": null, "max_features": "sqrt", "min_samples_leaf": 1, "n_estimators": 100} | 0.537584 | 0.692134 | 0.379164 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Random forest: {"max_depth": null, "max_features": "sqrt", "min_samples_leaf": 3, "n_estimators": 100} | 0.538216 | 0.690938 | 0.381424 | â€” | â€” | â€” | â€” | â€” |

### KNN

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | KNN: {"n_neighbors": 15, "p": 1, "weights": "distance"} | 0.501927 | 0.642325 | 0.367267 | 0.601031 | 0.963918 | 0.291087 | 0.273797 | 0.273431 |
| 2 | Red | Removed | Removed | All 11 | 970 | KNN: {"n_neighbors": 11, "p": 1, "weights": "distance"} | 0.503824 | 0.647671 | 0.355019 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | KNN: {"n_neighbors": 9, "p": 2, "weights": "distance"} | 0.505365 | 0.653208 | 0.344655 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | KNN: {"n_neighbors": 15, "p": 1, "weights": "distance"} | 0.549965 | 0.714991 | 0.337546 | 0.557724 | 0.955012 | 0.239427 | 0.233476 | 0.231771 |
| 2 | White | Removed | Removed | All 11 | 3,023 | KNN: {"n_neighbors": 11, "p": 1, "weights": "distance"} | 0.552430 | 0.718074 | 0.331770 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | KNN: {"n_neighbors": 9, "p": 1, "weights": "distance"} | 0.554580 | 0.721154 | 0.325955 | â€” | â€” | â€” | â€” | â€” |

### SVM

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | SVM: {"C": 1.0, "epsilon": 0.05, "gamma": 0.03} | 0.473737 | 0.636503 | 0.375750 | 0.612371 | 0.969072 | 0.301274 | 0.281708 | 0.281763 |
| 2 | Red | Removed | Removed | All 11 | 970 | SVM: {"C": 0.5, "epsilon": 0.05, "gamma": "scale"} | 0.474239 | 0.639912 | 0.367918 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | SVM: {"C": 0.5, "epsilon": 0.05, "gamma": 0.1} | 0.475532 | 0.641356 | 0.365102 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | SVM: {"C": 0.5, "epsilon": 0.05, "gamma": 0.1} | 0.537761 | 0.714490 | 0.338354 | 0.555739 | 0.956996 | 0.234936 | 0.226016 | 0.222825 |
| 2 | White | Removed | Removed | All 11 | 3,023 | SVM: {"C": 0.5, "epsilon": 0.05, "gamma": "scale"} | 0.538134 | 0.714279 | 0.338743 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | SVM: {"C": 1.0, "epsilon": 0.05, "gamma": "scale"} | 0.538411 | 0.713779 | 0.339516 | â€” | â€” | â€” | â€” | â€” |

### Linear regression

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Linear regression: {"fit_intercept": true, "positive": false} | 0.494852 | 0.641483 | 0.368649 | 0.602062 | 0.969072 | 0.292733 | 0.273007 | 0.272787 |
| 2 | Red | Removed | Removed | All 11 | 970 | Linear regression: {"fit_intercept": true, "positive": true} | 0.508339 | 0.664719 | 0.323606 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Linear regression: {"fit_intercept": false, "positive": false} | 5.629139 | 5.665679 | -48.525069 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Linear regression: {"fit_intercept": true, "positive": false} | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Linear regression: {"fit_intercept": true, "positive": true} | 0.593259 | 0.759207 | 0.253154 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Linear regression: {"fit_intercept": false, "positive": false} | 5.882953 | 5.928529 | -44.649119 | â€” | â€” | â€” | â€” | â€” |

### Ridge regression

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Ridge regression: {"alpha": 10} | 0.494500 | 0.641258 | 0.369200 | 0.601031 | 0.969072 | 0.292320 | 0.272581 | 0.272383 |
| 2 | Red | Removed | Removed | All 11 | 970 | Ridge regression: {"alpha": 1} | 0.494804 | 0.641453 | 0.368719 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Ridge regression: {"alpha": 0.1} | 0.494847 | 0.641480 | 0.368656 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Ridge regression: {"alpha": 0.1} | 0.572302 | 0.735417 | 0.299043 | 0.527622 | 0.951373 | 0.221721 | 0.214463 | 0.211922 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Ridge regression: {"alpha": 0.01} | 0.572302 | 0.735417 | 0.299043 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Ridge regression: {"alpha": 0.001} | 0.572302 | 0.735417 | 0.299043 | â€” | â€” | â€” | â€” | â€” |

### Polynomial Ridge

This post-final development search tested 56 combinations: log transformation off/on, polynomial degrees 1 through 4, and seven Ridge alpha values. The selected setup used the log transformation for both wines.

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Polynomial Ridge: {"alpha": 100, "log__enabled": true, "poly__degree": 3} | 0.488699 | 0.634621 | 0.381026 | 0.614433 | 0.971134 | 0.341175 | 0.286889 | 0.291073 |
| 2 | Red | Removed | Removed | All 11 | 970 | Polynomial Ridge: {"alpha": 10, "log__enabled": true, "poly__degree": 2} | 0.488925 | 0.634919 | 0.380359 | — | — | — | — | — |
| 3 | Red | Removed | Removed | All 11 | 970 | Polynomial Ridge: {"alpha": 100, "log__enabled": true, "poly__degree": 4} | 0.490593 | 0.640975 | 0.368553 | — | — | — | — | — |
| 1 | White | Removed | Removed | All 11 | 3,023 | Polynomial Ridge: {"alpha": 100, "log__enabled": true, "poly__degree": 4} | 0.548982 | 0.706170 | 0.353520 | 0.551108 | 0.962620 | 0.447683 | 0.239493 | 0.246273 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Polynomial Ridge: {"alpha": 10, "log__enabled": true, "poly__degree": 3} | 0.549924 | 0.706723 | 0.352415 | — | — | — | — | — |
| 3 | White | Removed | Removed | All 11 | 3,023 | Polynomial Ridge: {"alpha": 10, "log__enabled": true, "poly__degree": 4} | 0.550920 | 0.708586 | 0.349111 | — | — | — | — | — |

The same search was repeated after adding five ratio features. These rows are kept separate because they use 16 inputs instead of the original 11.

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 + 5 ratios | 970 | Polynomial Ridge: {"alpha": 10, "log__enabled": true, "poly__degree": 2} | 0.493612 | 0.642550 | 0.365283 | 0.606186 | 0.972165 | 0.326309 | 0.283512 | 0.287133 |
| 2 | Red | Removed | Removed | All 11 + 5 ratios | 970 | Polynomial Ridge: {"alpha": 100, "log__enabled": false, "poly__degree": 3} | 0.493630 | 0.641906 | 0.367193 | — | — | — | — | — |
| 3 | Red | Removed | Removed | All 11 + 5 ratios | 970 | Polynomial Ridge: {"alpha": 100, "log__enabled": true, "poly__degree": 3} | 0.494789 | 0.644682 | 0.361364 | — | — | — | — | — |
| 1 | White | Removed | Removed | All 11 + 5 ratios | 3,023 | Polynomial Ridge: {"alpha": 100, "log__enabled": true, "poly__degree": 3} | 0.549892 | 0.707329 | 0.351443 | 0.549785 | 0.962620 | 0.380594 | 0.239443 | 0.247246 |
| 2 | White | Removed | Removed | All 11 + 5 ratios | 3,023 | Polynomial Ridge: {"alpha": 10, "log__enabled": true, "poly__degree": 3} | 0.550989 | 0.710087 | 0.346268 | — | — | — | — | — |
| 3 | White | Removed | Removed | All 11 + 5 ratios | 3,023 | Polynomial Ridge: {"alpha": 100, "log__enabled": true, "poly__degree": 4} | 0.551479 | 0.711927 | 0.342993 | — | — | — | — | — |

For Polynomial Ridge, the ratio features did not improve the selected CV MAE: red changed from 0.488699 to 0.493612, and white changed from 0.548982 to 0.549892. The original 11 features therefore remain the better tested choice for this model.

#### Ratio features in the simpler linear models

This compact check compares each model's selected original-feature grid result with its selected ratio-feature result. A positive MAE change means the ratio version was worse.

| Wine | Model | Original CV MAE | Ratio CV MAE | MAE change | Ratio CV RMSE | Ratio CV R2 | Ratio-selected setup |
|---|---|---:|---:|---:|---:|---:|---|
| Red | Linear regression | 0.494852 | 0.501572 | +0.006720 | 0.649555 | 0.352438 | {"fit_intercept": true, "positive": false} |
| Red | Ridge regression | 0.494500 | 0.496437 | +0.001937 | 0.643443 | 0.365077 | {"alpha": 100} |
| Red | Lasso regression | 0.494344 | 0.495007 | +0.000663 | 0.641567 | 0.368853 | {"alpha": 0.01} |
| White | Linear regression | 0.572302 | 0.571089 | -0.001213 | 0.731694 | 0.306178 | {"fit_intercept": true, "positive": false} |
| White | Ridge regression | 0.572302 | 0.571089 | -0.001213 | 0.731694 | 0.306178 | {"alpha": 0.0001} |
| White | Lasso regression | 0.572299 | 0.571267 | -0.001032 | 0.731616 | 0.306315 | {"alpha": 0.0001} |

The ratios slightly helped the simple white-wine linear models but hurt all three red-wine results. This is not a consistent enough gain to make ratio engineering the shared default.

### Lasso regression

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Lasso regression: {"alpha": 0.001} | 0.494344 | 0.641067 | 0.369537 | 0.602062 | 0.969072 | 0.292937 | 0.272009 | 0.271634 |
| 2 | Red | Removed | Removed | All 11 | 970 | Lasso regression: {"alpha": 0.01} | 0.494729 | 0.640251 | 0.371512 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Lasso regression: {"alpha": 0.0001} | 0.494788 | 0.641436 | 0.368748 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Lasso regression: {"alpha": 0.0001} | 0.572299 | 0.735408 | 0.299061 | 0.527952 | 0.951373 | 0.221970 | 0.214567 | 0.212021 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Lasso regression: {"alpha": 0.001} | 0.572318 | 0.735403 | 0.299087 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Lasso regression: {"alpha": 0.01} | 0.575813 | 0.740167 | 0.290107 | â€” | â€” | â€” | â€” | â€” |

### Bayesian Ridge

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Bayesian Ridge: {"alpha_1": 1e-06, "alpha_2": 1e-06, "lambda_1": 1e-05, "lambda_2": 1e-05} | 0.494458 | 0.641195 | 0.369457 | 0.605155 | 0.968041 | 0.298341 | 0.274252 | 0.274558 |
| 2 | Red | Removed | Removed | All 11 | 970 | Bayesian Ridge: {"alpha_1": 1e-05, "alpha_2": 1e-05, "lambda_1": 1e-05, "lambda_2": 1e-05} | 0.494458 | 0.641195 | 0.369457 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Bayesian Ridge: {"alpha_1": 1e-06, "alpha_2": 1e-06, "lambda_1": 1e-06, "lambda_2": 1e-06} | 0.494458 | 0.641195 | 0.369457 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Bayesian Ridge: {"alpha_1": 1e-06, "alpha_2": 1e-06, "lambda_1": 1e-05, "lambda_2": 1e-05} | 0.572527 | 0.735785 | 0.298378 | 0.527291 | 0.949719 | 0.221962 | 0.213554 | 0.211022 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Bayesian Ridge: {"alpha_1": 1e-05, "alpha_2": 1e-05, "lambda_1": 1e-05, "lambda_2": 1e-05} | 0.572527 | 0.735785 | 0.298378 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Bayesian Ridge: {"alpha_1": 1e-06, "alpha_2": 1e-06, "lambda_1": 1e-06, "lambda_2": 1e-06} | 0.572527 | 0.735786 | 0.298378 | â€” | â€” | â€” | â€” | â€” |

### XGBoost

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | XGBoost: {"colsample_bytree": 0.8, "gamma": 0.25, "learning_rate": 0.025, "max_depth": 4, "min_child_weight": 1, "n_estimators": 350, "n_jobs": 1, "objective": "reg:squarederror", "random_state": 42, "reg_alpha": 0.0, "reg_lambda": 2.0, "subsample": 0.7, "verbosity": 0} | 0.496491 | 0.643433 | 0.362701 | 0.616495 | 0.968041 | 0.295478 | 0.290669 | 0.289701 |
| 2 | Red | Removed | Removed | All 11 | 970 | XGBoost: {"colsample_bytree": 0.95, "gamma": 0.01, "learning_rate": 0.1, "max_depth": 6, "min_child_weight": 2, "n_estimators": 250, "n_jobs": 1, "objective": "reg:squarederror", "random_state": 42, "reg_alpha": 0.01, "reg_lambda": 1.0, "subsample": 0.95, "verbosity": 0} | 0.506385 | 0.667661 | 0.313701 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | XGBoost: {"colsample_bytree": 0.65, "gamma": 0.025, "learning_rate": 0.075, "max_depth": 7, "min_child_weight": 5, "n_estimators": 900, "n_jobs": 1, "objective": "reg:squarederror", "random_state": 42, "reg_alpha": 0.001, "reg_lambda": 1.0, "subsample": 0.95, "verbosity": 0} | 0.506411 | 0.665608 | 0.318997 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | XGBoost: {"colsample_bytree": 0.8, "gamma": 0.25, "learning_rate": 0.025, "max_depth": 4, "min_child_weight": 1, "n_estimators": 350, "n_jobs": 1, "objective": "reg:squarederror", "random_state": 42, "reg_alpha": 0.0, "reg_lambda": 2.0, "subsample": 0.7, "verbosity": 0} | 0.541075 | 0.695717 | 0.372637 | 0.558055 | 0.962951 | 0.294820 | 0.243935 | 0.246203 |
| 2 | White | Removed | Removed | All 11 | 3,023 | XGBoost: {"colsample_bytree": 0.65, "gamma": 0.025, "learning_rate": 0.075, "max_depth": 7, "min_child_weight": 5, "n_estimators": 900, "n_jobs": 1, "objective": "reg:squarederror", "random_state": 42, "reg_alpha": 0.001, "reg_lambda": 1.0, "subsample": 0.95, "verbosity": 0} | 0.545924 | 0.712072 | 0.342669 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | XGBoost: {"colsample_bytree": 0.95, "gamma": 0.01, "learning_rate": 0.1, "max_depth": 6, "min_child_weight": 2, "n_estimators": 250, "n_jobs": 1, "objective": "reg:squarederror", "random_state": 42, "reg_alpha": 0.01, "reg_lambda": 1.0, "subsample": 0.95, "verbosity": 0} | 0.546701 | 0.710912 | 0.344928 | â€” | â€” | â€” | â€” | â€” |

### Neural network

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Neural network: {"activation": "relu", "alpha": 0.1, "hidden_layer_sizes": [128, 64], "learning_rate_init": 0.001, "solver": "adam"} | 0.489673 | 0.635811 | 0.379274 | 0.597938 | 0.970103 | 0.308912 | 0.289070 | 0.290359 |
| 2 | Red | Removed | Removed | All 11 | 970 | Neural network: {"activation": "relu", "alpha": 0.01, "hidden_layer_sizes": [128, 64], "learning_rate_init": 0.001, "solver": "adam"} | 0.490249 | 0.635712 | 0.379141 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Neural network: {"activation": "relu", "alpha": 0.01, "hidden_layer_sizes": [128, 64, 32], "learning_rate_init": 0.001, "solver": "adam"} | 0.493944 | 0.636669 | 0.376980 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Neural network: {"activation": "relu", "alpha": 0.1, "hidden_layer_sizes": [128, 64], "learning_rate_init": 0.001, "solver": "adam"} | 0.551749 | 0.711325 | 0.344305 | 0.551770 | 0.959312 | 0.365934 | 0.246594 | 0.251835 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Neural network: {"activation": "relu", "alpha": 0.001, "hidden_layer_sizes": [128, 64], "learning_rate_init": 0.002, "solver": "adam"} | 0.553244 | 0.713336 | 0.340523 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Neural network: {"activation": "relu", "alpha": 0.01, "hidden_layer_sizes": [128, 64], "learning_rate_init": 0.001, "solver": "adam"} | 0.553614 | 0.714774 | 0.338020 | â€” | â€” | â€” | â€” | â€” |

### Voting ensemble

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Voting ensemble: {"forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03, "weights": [1, 0, 0, 2, 0], "xgboost": "drop"} | 0.470944 | 0.627789 | 0.393325 | 0.616495 | 0.971134 | 0.300794 | 0.285460 | 0.285341 |
| 2 | Red | Removed | Removed | All 11 | 970 | Voting ensemble: {"forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1, "weights": [1, 0, 0, 2, 0], "xgboost": "drop"} | 0.471922 | 0.631723 | 0.385105 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Voting ensemble: {"forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "nn__alpha": 0.1, "ridge": "drop", "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03, "weights": [1, 0, 0, 2, 1], "xgboost": "drop"} | 0.472651 | 0.624991 | 0.399041 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Voting ensemble: {"forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1, "weights": [1, 0, 0, 1, 0], "xgboost": "drop"} | 0.529906 | 0.693663 | 0.376442 | 0.566325 | 0.962620 | 0.241769 | 0.233392 | 0.231128 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Voting ensemble: {"forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1, "weights": [1, 1, 0, 2, 0]} | 0.530163 | 0.693500 | 0.376677 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Voting ensemble: {"forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1, "weights": [1, 0, 0, 2, 0], "xgboost": "drop"} | 0.530552 | 0.698654 | 0.367414 | â€” | â€” | â€” | â€” | â€” |

### Stacking ensemble

| Rank | Wine | Duplicates | Outliers | Features | Training rows | Model setup | CV MAE | CV RMSE | CV R2 | OOF accuracy | OOF +/-1 | OOF macro precision | OOF balanced | OOF macro F1 |
|---:|---|---|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | Red | Removed | Removed | All 11 | 970 | Stacking ensemble: {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge(alpha=0.001))])", "forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "passthrough": false, "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03} | 0.479308 | 0.628203 | 0.393264 | 0.611340 | 0.971134 | 0.295771 | 0.282481 | 0.282153 |
| 2 | Red | Removed | Removed | All 11 | 970 | Stacking ensemble: {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge())])", "forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "passthrough": false, "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03} | 0.479344 | 0.628148 | 0.393370 | â€” | â€” | â€” | â€” | â€” |
| 3 | Red | Removed | Removed | All 11 | 970 | Stacking ensemble: {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge(alpha=0.001))])", "forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "passthrough": false, "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1} | 0.479450 | 0.629503 | 0.390679 | â€” | â€” | â€” | â€” | â€” |
| 1 | White | Removed | Removed | All 11 | 3,023 | Stacking ensemble: {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge(alpha=0.1))])", "forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "passthrough": true, "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1} | 0.530087 | 0.685568 | 0.390702 | 0.567648 | 0.965266 | 0.382540 | 0.247369 | 0.247503 |
| 2 | White | Removed | Removed | All 11 | 3,023 | Stacking ensemble: {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Lasso(alpha=0.001, max_iter=20000))])", "forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "passthrough": true, "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1} | 0.530164 | 0.685748 | 0.390368 | â€” | â€” | â€” | â€” | â€” |
| 3 | White | Removed | Removed | All 11 | 3,023 | Stacking ensemble: {"final_estimator": "Pipeline(steps=[('scaler', StandardScaler()), ('model', Ridge(alpha=0.001))])", "forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "passthrough": false, "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1} | 0.530976 | 0.687659 | 0.387118 | â€” | â€” | â€” | â€” | â€” |

## Practical conclusion

For red wine, Voting ensemble with `{"forest__max_depth": null, "forest__max_features": 1.0, "forest__min_samples_leaf": 3, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 1.0, "svm__epsilon": 0.05, "svm__gamma": 0.03, "weights": [1, 0, 0, 2, 0], "xgboost": "drop"}` still has the lowest tested CV MAE (0.470944). For white wine, Voting ensemble with `{"forest__max_depth": null, "forest__max_features": "sqrt", "forest__min_samples_leaf": 1, "forest__n_estimators": 200, "nn": "drop", "ridge": "drop", "svm__C": 0.5, "svm__epsilon": 0.05, "svm__gamma": 0.1, "weights": [1, 0, 0, 1, 0], "xgboost": "drop"}` still leads with 0.529906.

Polynomial Ridge reaches 0.488699 for red wine and 0.548982 for white wine with the original 11 features, placing fifth and sixth respectively in this CV ranking. Adding the five ratio features made its selected MAE slightly worse (0.493612 red and 0.549892 white), so the ratios are not recommended as the shared default. Polynomial Ridge and the ratio experiments are post-final training-CV work only: the one-time 20% holdout remains closed, and neither `FINAL_TEST_LOCK.json` nor `FINAL_TEST_RESULTS.md` was changed.

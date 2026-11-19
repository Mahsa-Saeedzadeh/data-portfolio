"""XGBoost regression model."""


def build_model():
    """Return the training-CV-selected XGBoost configuration."""
    try:
        from xgboost import XGBRegressor
    except ImportError as error:
        raise ImportError(
            "XGBoost is not installed. Run: python -m pip install xgboost"
        ) from error

    # This moderate setup improved both wines and stayed stable when exact
    # duplicates were either kept or removed. Deeper alternatives scored very
    # well only when duplicates were kept, which suggested memorization.
    return XGBRegressor(
        n_estimators=350,
        max_depth=4,
        learning_rate=0.025,
        min_child_weight=1,
        subsample=0.7,
        colsample_bytree=0.8,
        gamma=0.25,
        reg_alpha=0.0,
        reg_lambda=2.0,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=1,
        verbosity=0,
    )


def parameter_grid():
    """Compare the three training-CV configurations already documented."""
    common = {
        "objective": ["reg:squarederror"],
        "random_state": [42],
        "n_jobs": [1],
        "verbosity": [0],
    }
    configurations = [
        {
            "n_estimators": [350], "max_depth": [4],
            "learning_rate": [0.025], "min_child_weight": [1],
            "subsample": [0.7], "colsample_bytree": [0.8],
            "gamma": [0.25], "reg_alpha": [0.0], "reg_lambda": [2.0],
        },
        {
            "n_estimators": [250], "max_depth": [6],
            "learning_rate": [0.1], "min_child_weight": [2],
            "subsample": [0.95], "colsample_bytree": [0.95],
            "gamma": [0.01], "reg_alpha": [0.01], "reg_lambda": [1.0],
        },
        {
            "n_estimators": [900], "max_depth": [7],
            "learning_rate": [0.075], "min_child_weight": [5],
            "subsample": [0.95], "colsample_bytree": [0.65],
            "gamma": [0.025], "reg_alpha": [0.001], "reg_lambda": [1.0],
        },
    ]
    return [{**common, **configuration} for configuration in configurations]

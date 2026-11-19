"""Support-vector regression model."""

from sklearn.svm import SVR

from src.preprocessing import make_scaled_pipeline


def build_model():
    """Scale the inputs before fitting the team's RBF support-vector model."""
    return make_scaled_pipeline(
        SVR(kernel="rbf", C=1.0, epsilon=0.1, gamma="scale")
    )


def parameter_grid():
    """Return the RBF parameter grid exactly as submitted by the SVM group."""
    return {
        "model__C": [0.5, 1.0, 3.0, 10.0],
        "model__epsilon": [0.05, 0.1, 0.2],
        "model__gamma": [0.03, 0.1, "scale"],
    }

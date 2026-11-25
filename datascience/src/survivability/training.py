import numpy as np
from lightgbm import LGBMClassifier
from sklearn.metrics import precision_recall_curve
from sklearn.pipeline import Pipeline

from .preprocessing import make_preprocessor


def create_model_pipeline() -> Pipeline:
    """Create the tuned LightGBM survivability pipeline."""

    pipeline = Pipeline(
        [
            ("preprocess", make_preprocessor()),
            (
                "model",
                LGBMClassifier(
                    subsample=1.0,
                    reg_lambda=1.0,
                    reg_alpha=1.0,
                    num_leaves=255,
                    n_estimators=200,
                    min_child_samples=100,
                    learning_rate=0.1,
                    colsample_bytree=1.0,
                    class_weight="balanced",
                    random_state=42,
                    verbose=-1,
                ),
            ),
        ]
    )

    return pipeline


def train_model(x_train, y_train) -> Pipeline:
    """Train the survivability model using training data."""

    pipeline = create_model_pipeline()

    pipeline.fit(x_train, y_train)

    return pipeline


def calculate_optimal_threshold(pipeline, x_val, y_val) -> float:
    """Calculate the optimal death probability threshold using F2 score."""

    # Calculate survival probabilities
    y_prob = pipeline.predict_proba(x_val)[:, 1]

    # Calculate precision and recall for the died class
    precisions, recalls, thresholds = precision_recall_curve(y_val, 1 - y_prob, pos_label=0)

    # Calculate F2 scores for available thresholds
    f2_scores = (5 * precisions[:-1] * recalls[:-1]) / (4 * precisions[:-1] + recalls[:-1] + 1e-9)

    # Find the threshold with the highest F2 score
    best_idx = np.argmax(f2_scores)

    return float(thresholds[best_idx])

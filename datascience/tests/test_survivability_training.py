from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
from lightgbm import LGBMClassifier
from sklearn.pipeline import Pipeline

from src.survivability.preprocessing import FEATURES
from src.survivability.training import (
    calculate_optimal_threshold,
    create_model_pipeline,
    train_model,
)


def test_create_model_pipeline():
    pipeline = create_model_pipeline()

    assert isinstance(pipeline, Pipeline)

    assert "preprocess" in pipeline.named_steps
    assert "model" in pipeline.named_steps

    model = pipeline.named_steps["model"]

    assert isinstance(model, LGBMClassifier)
    assert model.n_estimators == 200
    assert model.num_leaves == 255
    assert model.learning_rate == 0.1
    assert model.class_weight == "balanced"
    assert model.random_state == 42


def test_train_model():
    x = pd.DataFrame({feature: np.arange(240, dtype=float) for feature in FEATURES})

    x["correct_tree_species_name"] = ["Mango", "Mahogany"] * 120

    y = np.array([0, 1] * 120)

    pipeline = train_model(x, y)

    probabilities = pipeline.predict_proba(x)

    assert isinstance(pipeline, Pipeline)
    assert probabilities.shape == (240, 2)

    assert np.all(probabilities >= 0)
    assert np.all(probabilities <= 1)

    np.testing.assert_allclose(probabilities.sum(axis=1), 1.0)


def test_calculate_optimal_threshold():
    pipeline = Mock()

    pipeline.predict_proba.return_value = np.array(
        [
            [0.9, 0.1],
            [0.8, 0.2],
            [0.2, 0.8],
            [0.1, 0.9],
        ]
    )

    x_val = pd.DataFrame({"feature": [1, 2, 3, 4]})
    y_val = np.array([0, 0, 1, 1])

    threshold = calculate_optimal_threshold(pipeline, x_val, y_val)

    assert threshold == pytest.approx(0.8)

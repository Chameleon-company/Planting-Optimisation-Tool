import pytest
import numpy as np
from sklearn.dummy import DummyClassifier

from src.survivability.model_io import save_model, load_model


def test_save_and_load_model(tmp_path):
    # Create a simple trained model for testing
    X = [[0], [1], [2], [3]]
    y = [0, 1, 0, 1]

    pipeline = DummyClassifier(strategy="prior")
    pipeline.fit(X, y)

    threshold = 0.6218

    model_path = tmp_path / "models" / "survivability_pipeline.joblib"

    # Save the model
    save_model(pipeline, threshold, model_path)

    assert model_path.exists()

    # Load the model
    loaded_pipeline, loaded_threshold = load_model(model_path)

    assert loaded_threshold == pytest.approx(threshold)

    # Verify predictions remain unchanged
    np.testing.assert_allclose(
        pipeline.predict_proba(X),
        loaded_pipeline.predict_proba(X)
    )


def test_load_missing_model(tmp_path):
    model_path = tmp_path / "missing_model.joblib"

    with pytest.raises(FileNotFoundError):
        load_model(model_path)
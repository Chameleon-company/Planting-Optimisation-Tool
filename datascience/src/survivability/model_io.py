from pathlib import Path
import joblib


def save_model(pipeline, threshold, model_path):
    """Save the trained pipeline and decision threshold."""

    model_path = Path(model_path)

    model_path.parent.mkdir(parents=True, exist_ok=True)

    model_data = {
        "pipeline": pipeline,
        "threshold": float(threshold)
    }

    joblib.dump(model_data, model_path)


def load_model(model_path):
    """Load the trained pipeline and decision threshold."""

    model_data = joblib.load(model_path)

    return model_data["pipeline"], model_data["threshold"]
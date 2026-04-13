"""
Imputation service for missing farm environmental variables.

Loads a trained IterativeImputer + RandomForest pipeline and fills None values
in a farm profile dict. Returns the filled profile and a list of which fields
were imputed.

Expected input keys (matching training feature names):
    Base (always required, never None): latitude, longitude, area_ha, coastal, riparian
    Targets (may be None):             elevation_m, slope, temperature_celsius, rainfall_mm, ph
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MODELS_DIR = Path(__file__).parent.parent / "models" / "imputation"

BASE_FEATURES = ["latitude", "longitude", "area_ha", "coastal", "riparian"]
TARGET_FEATURES = ["elevation_m", "slope", "temperature_celsius", "rainfall_mm", "ph"]

# ---------------------------------------------------------------------------
# Lazy-loaded model state
# ---------------------------------------------------------------------------

_imputer = None
_feature_columns: list[str] | None = None


def _load() -> None:
    global _imputer, _feature_columns
    if _imputer is not None:
        return
    pipeline_path = _MODELS_DIR / "imputation_pipeline.joblib"
    columns_path = _MODELS_DIR / "feature_columns.joblib"
    if not pipeline_path.exists() or not columns_path.exists():
        raise RuntimeError(f"Imputation model files not found in {_MODELS_DIR}. Run the imputation_model_training notebook and save the artefacts first.")
    _imputer = joblib.load(pipeline_path)
    _feature_columns = joblib.load(columns_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def impute_missing(profile: dict) -> tuple[dict, list[str]]:
    """
    Fill missing target values in a farm profile using the trained imputer.

    Base features (latitude, longitude, area_ha, coastal, riparian) must be
    present and non-None — they are always derivable from farm geometry.

    Target features (elevation_m, slope, temperature_celsius, rainfall_mm, ph)
    may be None; missing ones will be imputed and returned as floats rounded to
    3 decimal places.

    Args:
        profile: Dict with keys matching the training feature names.

    Returns:
        Tuple of:
            - profile copy with None target values filled in
            - list of field names that were imputed (empty if nothing was missing)

    Raises:
        ValueError:  If any base feature is None or missing.
        RuntimeError: If model artefacts have not been saved yet.

    Example:
        filled, imputed = impute_missing({
            "latitude": -8.57, "longitude": 126.68, "area_ha": 1.2,
            "coastal": False, "riparian": False,
            "elevation_m": None, "slope": None,
            "temperature_celsius": 24.0, "rainfall_mm": None, "ph": 6.5,
        })
        # filled["elevation_m"] is now a float
        # imputed == ["elevation_m", "slope", "rainfall_mm"]
    """
    _load()

    missing_base = [f for f in BASE_FEATURES if profile.get(f) is None]
    if missing_base:
        raise ValueError(f"Base features required for imputation are missing or None: {missing_base}")

    imputed_fields = [f for f in TARGET_FEATURES if profile.get(f) is None]
    if not imputed_fields:
        return profile.copy(), []

    row = {col: profile.get(col) for col in _feature_columns}
    row["coastal"] = int(bool(row.get("coastal", False)))
    row["riparian"] = int(bool(row.get("riparian", False)))

    df = pd.DataFrame([row])[_feature_columns]
    imputed_array = _imputer.transform(df)
    imputed_row = dict(zip(_feature_columns, imputed_array[0]))

    filled_profile = profile.copy()
    for field in imputed_fields:
        value = imputed_row.get(field)
        if value is not None and not np.isnan(value):
            filled_profile[field] = round(float(value), 3)

    return filled_profile, imputed_fields

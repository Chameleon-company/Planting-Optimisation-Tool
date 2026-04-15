"""
Tests for imputation.imputation_service.

Model artefacts are not committed to the repo, so the imputer and feature
columns are mocked in all tests that exercise impute_missing().
"""

import numpy as np
import pytest

import imputation.imputation_service as svc  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BASE = {
    "latitude": -8.57,
    "longitude": 126.68,
    "area_ha": 1.2,
    "coastal": False,
    "riparian": False,
}

FEATURE_COLUMNS = [
    "latitude",
    "longitude",
    "area_ha",
    "coastal",
    "riparian",
    "elevation_m",
    "slope",
    "temperature_celsius",
    "rainfall_mm",
    "ph",
]


def _make_mock_imputer(return_values: dict):
    """Return a mock imputer whose transform() fills provided values."""

    class MockImputer:
        def transform(self, df):
            row = df.iloc[0].to_dict()
            for col, val in return_values.items():
                row[col] = val
            return np.array([[row[c] for c in FEATURE_COLUMNS]])

    return MockImputer()


def _patch_models(mocker, return_values: dict | None = None):
    """Inject mock imputer and feature columns into the service module."""
    svc._imputer = _make_mock_imputer(return_values or {})
    svc._feature_columns = FEATURE_COLUMNS
    mocker.patch("imputation.imputation_service._load")


# ---------------------------------------------------------------------------
# Tests — no missing values
# ---------------------------------------------------------------------------


def test_no_missing_values_returns_copy_unchanged(mocker):
    _patch_models(mocker)
    profile = {**BASE, "elevation_m": 500, "slope": 10.0, "temperature_celsius": 24.0, "rainfall_mm": 1500, "ph": 6.5}
    filled, imputed = svc.impute_missing(profile)
    assert imputed == []
    assert filled == profile
    assert filled is not profile  # must be a copy


# ---------------------------------------------------------------------------
# Tests — single missing value
# ---------------------------------------------------------------------------


def test_single_missing_field_is_imputed(mocker):
    _patch_models(mocker, {"elevation_m": 350.0})
    profile = {**BASE, "elevation_m": None, "slope": 10.0, "temperature_celsius": 24.0, "rainfall_mm": 1500, "ph": 6.5}
    filled, imputed = svc.impute_missing(profile)
    assert imputed == ["elevation_m"]
    assert filled["elevation_m"] == pytest.approx(350.0, abs=0.001)


def test_imputed_value_is_rounded_to_3dp(mocker):
    _patch_models(mocker, {"ph": 6.12345})
    profile = {**BASE, "elevation_m": 500, "slope": 10.0, "temperature_celsius": 24.0, "rainfall_mm": 1500, "ph": None}
    filled, imputed = svc.impute_missing(profile)
    assert filled["ph"] == pytest.approx(6.123, abs=0.0001)


# ---------------------------------------------------------------------------
# Tests — multiple missing values
# ---------------------------------------------------------------------------


def test_multiple_missing_fields_all_imputed(mocker):
    _patch_models(mocker, {"elevation_m": 200.0, "rainfall_mm": 1200.0, "slope": 5.5})
    profile = {**BASE, "elevation_m": None, "slope": None, "temperature_celsius": 24.0, "rainfall_mm": None, "ph": 6.5}
    filled, imputed = svc.impute_missing(profile)
    assert set(imputed) == {"elevation_m", "slope", "rainfall_mm"}
    assert filled["elevation_m"] == pytest.approx(200.0, abs=0.001)
    assert filled["rainfall_mm"] == pytest.approx(1200.0, abs=0.001)
    assert filled["slope"] == pytest.approx(5.5, abs=0.001)


def test_non_missing_fields_are_unchanged(mocker):
    _patch_models(mocker, {"elevation_m": 200.0})
    profile = {**BASE, "elevation_m": None, "slope": 10.0, "temperature_celsius": 24.0, "rainfall_mm": 1500, "ph": 6.5}
    filled, _ = svc.impute_missing(profile)
    assert filled["slope"] == 10.0
    assert filled["temperature_celsius"] == 24.0
    assert filled["rainfall_mm"] == 1500
    assert filled["ph"] == 6.5


# ---------------------------------------------------------------------------
# Tests — base feature validation
# ---------------------------------------------------------------------------


def test_missing_base_feature_raises_value_error(mocker):
    _patch_models(mocker)
    profile = {**BASE, "latitude": None, "elevation_m": None, "slope": 10.0, "temperature_celsius": 24.0, "rainfall_mm": 1500, "ph": 6.5}
    with pytest.raises(ValueError, match="latitude"):
        svc.impute_missing(profile)


def test_multiple_missing_base_features_raises_value_error(mocker):
    _patch_models(mocker)
    profile = {
        "latitude": None,
        "longitude": None,
        "area_ha": 1.2,
        "coastal": False,
        "riparian": False,
        "elevation_m": None,
        "slope": 10.0,
        "temperature_celsius": 24.0,
        "rainfall_mm": 1500,
        "ph": 6.5,
    }
    with pytest.raises(ValueError, match="latitude"):
        svc.impute_missing(profile)


# ---------------------------------------------------------------------------
# Tests — model not loaded
# ---------------------------------------------------------------------------


def test_missing_model_files_raise_runtime_error(mocker, tmp_path):
    svc._imputer = None
    svc._feature_columns = None
    mocker.patch("imputation.imputation_service._MODELS_DIR", tmp_path)
    profile = {**BASE, "elevation_m": None, "slope": 10.0, "temperature_celsius": 24.0, "rainfall_mm": 1500, "ph": 6.5}
    with pytest.raises(RuntimeError, match="not found"):
        svc.impute_missing(profile)

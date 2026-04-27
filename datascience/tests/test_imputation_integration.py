"""
Integration tests for imputation_service — loads the real trained model.

Requires model artefacts in datascience/src/models/imputation/.
Run the imputation_model_training notebook first if they are missing.
"""

import pytest

from imputation import impute_missing

BASE = {
    "latitude": -8.57,
    "longitude": 126.68,
    "area_ha": 1.2,
    "coastal": False,
    "riparian": False,
}


def test_imputes_missing_elevation():
    profile = {**BASE, "elevation_m": None, "slope": 10.0, "temperature_celsius": 24, "rainfall_mm": 1500, "ph": 6.5}
    filled, imputed = impute_missing(profile)
    assert "elevation_m" in imputed
    assert filled["elevation_m"] is not None
    assert 0 <= filled["elevation_m"] <= 3000


def test_imputes_multiple_missing_fields():
    profile = {**BASE, "elevation_m": None, "slope": None, "temperature_celsius": 24, "rainfall_mm": None, "ph": 6.5}
    filled, imputed = impute_missing(profile)
    assert set(imputed) == {"elevation_m", "slope", "rainfall_mm"}
    assert filled["elevation_m"] is not None
    assert filled["slope"] is not None
    assert filled["rainfall_mm"] is not None


def test_no_missing_values_unchanged():
    profile = {**BASE, "elevation_m": 500, "slope": 10.0, "temperature_celsius": 24, "rainfall_mm": 1500, "ph": 6.5}
    filled, imputed = impute_missing(profile)
    assert imputed == []
    assert filled == profile


def test_imputed_values_are_floats_rounded_to_3dp():
    profile = {**BASE, "elevation_m": None, "slope": 10.0, "temperature_celsius": 24, "rainfall_mm": 1500, "ph": 6.5}
    filled, _ = impute_missing(profile)
    val = filled["elevation_m"]
    assert isinstance(val, float)
    assert round(val, 3) == val


def test_missing_base_feature_raises():
    profile = {**BASE, "latitude": None, "elevation_m": None, "slope": 10.0, "temperature_celsius": 24, "rainfall_mm": 1500, "ph": 6.5}
    with pytest.raises(ValueError, match="latitude"):
        impute_missing(profile)

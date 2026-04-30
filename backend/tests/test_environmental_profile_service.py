"""Tests for the imputation logic in EnvironmentalProfileService."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from shapely.geometry import Polygon

from src.services.environmental_profile import EnvironmentalProfileService, ImputationError

_FULL_PROFILE = {
    "id": 1,
    "latitude": -8.57,
    "longitude": 126.68,
    "area_ha": 1.2,
    "coastal": False,
    "riparian": False,
    "elevation_m": 450,
    "slope_degrees": 10.0,
    "temperature_celsius": 24,
    "rainfall_mm": 1500,
    "soil_ph": 6.5,
    "soil_texture_id": 3,
}

_PROFILE_WITH_MISSING = {**_FULL_PROFILE, "elevation_m": None, "soil_ph": None}


def _full_profile():
    return dict(_FULL_PROFILE)


def _missing_profile():
    """Return a fresh copy so in-place mutations in the service don't leak between tests."""
    return dict(_PROFILE_WITH_MISSING)


def _make_db():
    poly = Polygon([(126.68, -8.57), (126.69, -8.57), (126.69, -8.58), (126.68, -8.57)])
    boundary = MagicMock()
    boundary.boundary = MagicMock()
    # Use a plain MagicMock for the execute result so scalar_one_or_none()
    # returns a value synchronously rather than a coroutine.
    result = MagicMock()
    result.scalar_one_or_none.return_value = boundary
    db = AsyncMock()
    db.execute.return_value = result
    return db, poly


@pytest.mark.asyncio
@patch("src.services.environmental_profile.to_shape")
@patch("src.services.environmental_profile.build_farm_profile")
@patch("src.services.environmental_profile.impute_missing")
async def test_imputation_not_called_when_complete(mock_impute, mock_build, mock_to_shape):
    db, poly = _make_db()
    mock_to_shape.return_value = poly
    mock_build.side_effect = lambda **_: _full_profile()

    profile = await EnvironmentalProfileService.run_environmental_profile(db, farm_id=1)

    mock_impute.assert_not_called()
    assert "elevation_m_imputed" not in profile


@pytest.mark.asyncio
@patch("src.services.environmental_profile.to_shape")
@patch("src.services.environmental_profile.build_farm_profile")
@patch("src.services.environmental_profile.impute_missing")
async def test_imputed_values_and_flags_set(mock_impute, mock_build, mock_to_shape):
    db, poly = _make_db()
    mock_to_shape.return_value = poly
    mock_build.side_effect = lambda **_: _missing_profile()
    mock_impute.return_value = ({**_missing_profile(), "elevation_m": 320.0, "ph": 6.2}, ["elevation_m", "ph"])

    profile = await EnvironmentalProfileService.run_environmental_profile(db, farm_id=1)

    assert profile["elevation_m"] == 320.0
    assert profile["elevation_m_imputed"] is True
    assert profile["ph_imputed"] is True


@pytest.mark.asyncio
@patch("src.services.environmental_profile.to_shape")
@patch("src.services.environmental_profile.build_farm_profile")
@patch("src.services.environmental_profile.impute_missing")
async def test_non_imputed_fields_have_no_flag(mock_impute, mock_build, mock_to_shape):
    db, poly = _make_db()
    mock_to_shape.return_value = poly
    mock_build.side_effect = lambda **_: _missing_profile()
    mock_impute.return_value = ({**_missing_profile(), "elevation_m": 320.0, "ph": 6.2}, ["elevation_m", "ph"])

    profile = await EnvironmentalProfileService.run_environmental_profile(db, farm_id=1)

    assert "slope_imputed" not in profile
    assert "rainfall_mm_imputed" not in profile


@pytest.mark.asyncio
@patch("src.services.environmental_profile.to_shape")
@patch("src.services.environmental_profile.build_farm_profile")
@patch("src.services.environmental_profile.impute_missing", side_effect=RuntimeError("model not found"))
async def test_model_unavailable_raises_imputation_error(mock_impute, mock_build, mock_to_shape):
    db, poly = _make_db()
    mock_to_shape.return_value = poly
    mock_build.side_effect = lambda **_: _missing_profile()

    with pytest.raises(ImputationError, match="unavailable"):
        await EnvironmentalProfileService.run_environmental_profile(db, farm_id=1)


@pytest.mark.asyncio
@patch("src.services.environmental_profile.to_shape")
@patch("src.services.environmental_profile.build_farm_profile")
@patch("src.services.environmental_profile.impute_missing")
async def test_no_gee_profile_returns_none(mock_impute, mock_build, mock_to_shape):
    db, poly = _make_db()
    mock_to_shape.return_value = poly
    mock_build.return_value = None

    result = await EnvironmentalProfileService.run_environmental_profile(db, farm_id=1)

    assert result is None
    mock_impute.assert_not_called()

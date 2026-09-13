"""Integration tests for the Backend -> GIS environmental profile pipeline (US-075).

These call EnvironmentalProfileService.run_environmental_profile end to end with no
mocking of run_environmental_profile itself or of build_farm_profile's return value.
The `force_gee_unavailable` fixture below patches only the single, actual GEE data-fetch
call inside build_farm_profile so it raises the same ee.EEException build_farm_profile's
own try/except already handles for real ("Earth Engine client library not initialized",
confirmed by calling ee.Image() directly with no credentials configured). This makes the
fallback precondition explicit and deterministic rather than relying on this environment
currently having no GEE credentials in CI, so the coverage doesn't silently change if
credentials are ever added later. Everything above that one call (build_farm_profile's own
control flow, and run_environmental_profile's fallback reconstruction from stored farm
data) runs for real.
"""

from unittest.mock import patch

import pytest
from ee.ee_exception import EEException
from geoalchemy2 import WKTElement

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.models.waterways import Waterway
from src.services.environmental_profile import EnvironmentalProfileService

_BOUNDARY_WKT = "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))"


@pytest.fixture(autouse=True)
def force_gee_unavailable():
    """Deterministically forces the GEE-unavailable fallback precondition for every
    test in this file, instead of relying on this environment's ambient lack of GEE
    credentials. See the module docstring for why only this one call is patched."""
    with patch(
        "core.farm_profile.get_rainfall",
        side_effect=EEException("Earth Engine client library not initialized. See http://goo.gle/ee-auth."),
    ):
        yield


async def test_environmental_profile_returns_ph(async_session):
    farm = Farm(
        rainfall_mm=1000,
        temperature_celsius=25,
        elevation_m=100,
        ph=6.5,
        soil_texture_id=1,
        area_ha=10,
        latitude=0,
        longitude=0,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=5,
    )
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(_BOUNDARY_WKT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    profile = await EnvironmentalProfileService.run_environmental_profile(db=async_session, farm_id=farm.id)

    assert profile is not None
    assert profile.get("status") != "failed"
    # force_gee_unavailable deterministically forces GIS/GEE to fail, so this is
    # exercising the real fallback reconstruction from stored farm data.
    assert profile["data_source"] == "fallback"
    assert "soil_ph" in profile
    assert profile["soil_ph"] is not None


async def test_environmental_profile_fallback_when_no_ph(async_session):
    farm = Farm(
        rainfall_mm=1000,
        temperature_celsius=25,
        elevation_m=100,
        ph=0.0,  # simulate missing/invalid pH
        soil_texture_id=1,
        area_ha=10,
        latitude=0,
        longitude=0,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=5,
    )
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(_BOUNDARY_WKT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    profile = await EnvironmentalProfileService.run_environmental_profile(db=async_session, farm_id=farm.id)

    assert profile is not None
    assert profile.get("status") != "failed"
    assert profile["data_source"] == "fallback"
    assert "soil_ph" in profile
    assert profile["soil_ph"] is not None
    # The out-of-range pH (0.0) is nulled out by the fallback path, and there is no
    # local soil_ph raster row at these coordinates, so this real (unmocked) call
    # actually goes through the imputation service to fill it in.
    assert profile.get("ph_imputed") is True


async def test_environmental_profile_returns_texture(async_session):
    farm = Farm(
        rainfall_mm=1000,
        temperature_celsius=25,
        elevation_m=100,
        ph=6.5,
        soil_texture_id=2,
        area_ha=10,
        latitude=0,
        longitude=0,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=5,
    )
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(_BOUNDARY_WKT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    profile = await EnvironmentalProfileService.run_environmental_profile(db=async_session, farm_id=farm.id)

    assert profile is not None
    assert profile.get("status") != "failed"
    assert profile["data_source"] == "fallback"
    assert "soil_texture" in profile
    assert profile["soil_texture"] is not None


async def test_environmental_profile_full_shape_end_to_end(async_session):
    """The full profile returned end to end has every expected key, with the
    normalisation (rounding) step applied, not just individual fields checked
    in isolation."""
    farm = Farm(
        rainfall_mm=1500,
        temperature_celsius=24,
        elevation_m=450,
        ph=6.53,
        soil_texture_id=1,
        area_ha=1.2,
        latitude=-8.57,
        longitude=126.68,
        coastal=True,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=10.126,
    )
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(_BOUNDARY_WKT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    profile = await EnvironmentalProfileService.run_environmental_profile(db=async_session, farm_id=farm.id)

    assert profile is not None
    assert profile["data_source"] == "fallback"

    expected_keys = {
        "id",
        "rainfall_mm",
        "temperature_celsius",
        "elevation_m",
        "soil_ph",
        "soil_texture_id",
        "soil_texture",
        "area_ha",
        "latitude",
        "longitude",
        "coastal",
        "riparian",
        "nitrogen_fixing",
        "shade_tolerant",
        "bank_stabilising",
        "slope_degrees",
        "status",
        "data_source",
    }
    assert expected_keys.issubset(profile.keys())

    # Normalisation: temperature/rainfall rounded to int, pH to 1dp, slope to 2dp.
    assert profile["temperature_celsius"] == 24
    assert isinstance(profile["temperature_celsius"], int)
    assert profile["rainfall_mm"] == 1500
    assert isinstance(profile["rainfall_mm"], int)
    assert profile["soil_ph"] == 6.5
    assert profile["slope_degrees"] == 10.13


async def test_environmental_profile_riparian_true_for_real_waterway_intersection(async_session):
    """A real PostGIS intersection query against the Waterway table, not an
    assumed or mocked riparian flag."""
    farm = Farm(
        rainfall_mm=1000,
        temperature_celsius=25,
        elevation_m=100,
        ph=6.5,
        soil_texture_id=1,
        area_ha=10,
        latitude=-9.001,
        longitude=125.001,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=5,
    )
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(_BOUNDARY_WKT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    # A waterway line running straight through the boundary of the test farm.
    waterway = Waterway(
        name="Test River",
        waterway="river",
        geometry=WKTElement("LINESTRING (125 -9.003, 125.003 -8.999)", srid=4326),
    )
    async_session.add(waterway)
    await async_session.flush()

    profile = await EnvironmentalProfileService.run_environmental_profile(db=async_session, farm_id=farm.id)

    assert profile is not None
    assert profile["riparian"] is True


async def test_environmental_profile_endpoint_end_to_end(
    async_client,
    async_session,
    setup_soil_texture,
    test_admin_user,
    admin_auth_headers,
):
    """Exercises the real GET /profile/{farm_id} endpoint (auth, farm lookup,
    caching, response schema) with run_environmental_profile and the GIS boundary
    both unmocked, covering the full endpoint -> service -> GIS/database flow
    that US-075 asks for, not just the service function in isolation."""
    farm = Farm(
        rainfall_mm=1200,
        temperature_celsius=26,
        elevation_m=200,
        ph=6.2,
        soil_texture_id=1,
        area_ha=3.0,
        latitude=-9.001,
        longitude=125.001,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=8.0,
    )
    farm.owners = [test_admin_user]
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(_BOUNDARY_WKT, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    response = await async_client.get(f"/profile/{farm.id}", headers=admin_auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["data_source"] == "fallback"
    assert body["ph"] is not None

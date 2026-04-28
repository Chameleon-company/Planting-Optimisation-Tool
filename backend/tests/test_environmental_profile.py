import pytest
from geoalchemy2 import WKTElement

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.services.environmental_profile import EnvironmentalProfileService


@pytest.mark.asyncio
async def test_environmental_profile_returns_ph(async_session):
    # Create farm (with valid pH)
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

    # Add boundary
    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(
            "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))",
            srid=4326,
        ),
    )
    async_session.add(boundary)
    await async_session.flush()

    # Run service
    profile = await EnvironmentalProfileService.run_environmental_profile(db=async_session, farm_id=farm.id)

    # Assertions
    assert profile is not None
    assert profile.get("status") != "failed"
    assert "soil_ph" in profile
    assert profile["soil_ph"] is not None


# fallback case
@pytest.mark.asyncio
async def test_environmental_profile_fallback_when_no_ph(async_session):
    # Create farm with "missing" pH (simulate invalid value)
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

    # Add boundary
    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(
            "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))",
            srid=4326,
        ),
    )
    async_session.add(boundary)
    await async_session.flush()

    # Run service
    profile = await EnvironmentalProfileService.run_environmental_profile(db=async_session, farm_id=farm.id)

    # Assertions
    assert profile is not None
    assert profile.get("status") != "failed"
    assert "soil_ph" in profile

    # Key check: fallback should still give a usable value
    assert profile["soil_ph"] is not None


@pytest.mark.asyncio
async def test_environmental_profile_returns_texture(async_session):
    farm = Farm(
        rainfall_mm=1000,
        temperature_celsius=25,
        elevation_m=100,
        ph=6.5,
        soil_texture_id=2,  # valid texture
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
        boundary=WKTElement(
            "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))",
            srid=4326,
        ),
    )
    async_session.add(boundary)
    await async_session.flush()

    profile = await EnvironmentalProfileService.run_environmental_profile(db=async_session, farm_id=farm.id)

    assert profile is not None
    assert profile.get("status") != "failed"
    assert "soil_texture" in profile
    assert profile["soil_texture"] is not None

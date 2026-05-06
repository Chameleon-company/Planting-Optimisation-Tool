from unittest.mock import patch

import pytest
from geoalchemy2 import WKTElement
from sqlalchemy import text

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm


@pytest.fixture
async def setup_farm(async_session, test_officer_user):  # sapling_estimation router requires OFFICER role or higher
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(
        text(
            """
            INSERT INTO dem_table (rast)
            VALUES (
                ST_AddBand(
                    ST_MakeEmptyRaster(
                        5, 5,
                        125, -8.9995,
                        0.001, -0.001,
                        0, 0,
                        4326
                    ),
                    1,
                    '32BF',
                    100
                )
            );
            """
        )
    )
    await async_session.flush()

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
        user_id=test_officer_user.id,
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

    return farm


# Cache Miss Test
@pytest.mark.asyncio
async def test_cache_miss(
    async_client,
    setup_farm,
    officer_auth_headers,
):
    farm = setup_farm

    payload = {
        "farm_id": farm.id,
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    request = await async_client.post(
        "/sapling_estimation/calculate",
        json=payload,
        headers=officer_auth_headers,
    )

    assert request.status_code == 200  # Request should return 200
    data = request.json()

    assert "aligned_count" in data
    assert data["aligned_count"] > 0
    assert "pre_slope_count" in data
    assert data["pre_slope_count"] >= data["aligned_count"]


# Cache Hit Test
@pytest.mark.asyncio
async def test_cache_hit(
    async_client,
    setup_farm,
    officer_auth_headers,
):
    farm = setup_farm

    payload = {
        "farm_id": farm.id,
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    # First request creates cache by populating redis
    request = await async_client.post(
        "/sapling_estimation/calculate",
        json=payload,
        headers=officer_auth_headers,
    )
    assert request.status_code == 200  # First request should return 200
    cache = request.json()

    # Second request should access and return cached result
    with patch(  # Patch run_estimation function so it cannot recompute
        "src.services.sapling_estimation.SaplingEstimationService.run_estimation",
        side_effect=Exception("Cache hit error: Second request should access cache and not call service"),
    ):
        request2 = await async_client.post(
            "/sapling_estimation/calculate",
            json=payload,
            headers=officer_auth_headers,
        )

    # The second request succeeds if results come from cache/Redis
    assert request2.status_code == 200  # Second request should return 200
    assert request2.json() == cache  # Second request should return the same result as cache

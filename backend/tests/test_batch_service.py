import json
from unittest.mock import AsyncMock, patch

import pytest
from geoalchemy2 import WKTElement
from sqlalchemy import text

from src import cache
from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.services.batch_estimation import SaplingBatchEstimationService


@pytest.fixture
async def setup_farms(async_session, test_officer_user):
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(text("TRUNCATE farms RESTART IDENTITY CASCADE;"))
    await async_session.execute(text("TRUNCATE boundary RESTART IDENTITY CASCADE;"))

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

    farms = []
    for _ in range(5):
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

        farms.append(farm)

    return farms


# Cache Miss Test
async def test_cache_miss(
    async_session,
    setup_farms,
    test_officer_user,
):
    mock_result = {
        "status": "success",
        "pre_slope_count": 100,
        "aligned_count": 80,
        "optimal_angle": 10,
        "rotation_average": 5.0,
        "rotation_std_dev": 1.0,
    }

    with patch(
        "src.services.sapling_estimation.SaplingEstimationService.run_estimation",
        new=AsyncMock(return_value=mock_result),
    ) as mock_run_estimation:
        result = await SaplingBatchEstimationService().run_batch_estimation(
            db=async_session,
            user_id=test_officer_user.id,
            spacing_x=10,
            spacing_y=10,
            max_slope=15,
        )

    assert result["farm_count"] == 5
    assert len(result["results"]) == 5
    assert mock_run_estimation.await_count == 5


# Cache Hit Test
async def test_cache_hit(
    async_session,
    setup_farms,
    test_officer_user,
):
    farms = setup_farms

    mock_cache = {
        "status": "success",
        "pre_slope_count": 100,
        "aligned_count": 80,
        "optimal_angle": 10,
        "rotation_average": 5.0,
        "rotation_std_dev": 1.0,
    }

    for farm in farms:
        cache_key = f"sapling:{farm.id}:10:10:15"
        await cache.set(cache_key, json.dumps(mock_cache))

    with patch(
        "src.services.sapling_estimation.SaplingEstimationService.run_estimation",
        new=AsyncMock(side_effect=Exception("Cache hit error: Request should access cache and not call service")),
    ):
        result = await SaplingBatchEstimationService().run_batch_estimation(
            db=async_session,
            user_id=test_officer_user.id,
            spacing_x=10,
            spacing_y=10,
            max_slope=15,
        )

    assert result["farm_count"] == 5  #
    assert result["results"][0]["aligned_count"] == 80
    assert result["results"][1]["aligned_count"] == 80

import pytest
from geoalchemy2 import WKTElement
from sqlalchemy import text

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.services.sapling_estimation import SaplingEstimationService


@pytest.mark.asyncio
async def test_run_estimation_basic(async_session, setup_soil_texture):
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

    result = await SaplingEstimationService.run_estimation(async_session, farm_id=farm.id, spacing_m=10)

    assert result is not None
    assert result.get("status") != "failed", f"Service failed: {result}"
    assert "sapling_count" in result
    assert result["sapling_count"] > 0

    rows = await async_session.execute(
        text("SELECT COUNT(*) FROM planting_estimates WHERE farm_id = :id"),
        {"id": farm.id},
    )

    assert rows.scalar_one() == result["sapling_count"]

from geoalchemy2 import WKTElement
from sqlalchemy import text

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.services.sapling_estimation import SaplingEstimationService


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

    result = await SaplingEstimationService.run_estimation(async_session, farm_id=farm.id, spacing_x=10, spacing_y=10, max_slope=15)

    assert result is not None
    assert result.get("status") != "failed", f"Service failed: {result}"
    assert "aligned_count" in result
    assert result["aligned_count"] > 0

    assert "pre_slope_count" in result
    assert result["pre_slope_count"] >= result["aligned_count"]

    # -------------------------
    # US-045 (Rotation stats #280)
    # -------------------------
    assert "rotation_average" in result
    assert "rotation_std_dev" in result

    assert isinstance(result["rotation_average"], (float, int))
    assert isinstance(result["rotation_std_dev"], (float, int))

    assert result["rotation_std_dev"] >= 0
    assert result["rotation_average"] >= 0

    rows = await async_session.execute(
        text("SELECT COUNT(*) FROM planting_estimates WHERE farm_id = :id"),
        {"id": farm.id},
    )

    assert rows.scalar_one() == result["aligned_count"]

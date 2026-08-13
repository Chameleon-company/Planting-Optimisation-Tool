import pytest
from geoalchemy2 import WKTElement
from sqlalchemy import text

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.services.sapling_estimation import SaplingEstimationService


DEM_INSERT = text(
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


async def _add_farm(async_session, boundary_wkt, baseline_tree_count=0):  # farm + boundary inside the DEM extent
    farm = Farm(
        rainfall_mm=1000,
        temperature_celsius=25,
        elevation_m=100,
        ph=6.5,
        soil_texture_id=1,
        area_ha=10,
        baseline_tree_count=baseline_tree_count,
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
        boundary=WKTElement(boundary_wkt, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    return farm


async def test_run_estimation_basic(async_session):
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(DEM_INSERT)
    await async_session.flush()

    farm = await _add_farm(
        async_session,
        "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))",
    )

    service = SaplingEstimationService()
    estimation_results = await service.run_estimation(async_session, farm_ids=[farm.id], spacing_x=10, spacing_y=10, max_slope=15)

    result = estimation_results["results"][0]
    assert result.get("status") != "failed", f"Service failed: {result}"
    assert result["farm_id"] == farm.id
    assert "aligned_count" in result
    assert result["aligned_count"] > 0
    assert result["baseline_tree_count"] == baseline_tree_count
    assert result["additional_sapling_count"] == max(
        result["aligned_count"] - baseline_tree_count,
        0,
    )
    assert result["additional_sapling_count"] >= 0
    assert result["additional_sapling_count"] <= result["aligned_count"]

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


# Batch: several farms estimated in one call
async def test_run_estimation_multiple_farms(async_session):
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(DEM_INSERT)
    await async_session.flush()

    farm_a = await _add_farm(
        async_session,
        "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))",
    )
    farm_b = await _add_farm(
        async_session,
        "MULTIPOLYGON (((125.0025 -9.0005, 125.0025 -9.0025, 125.0045 -9.0025, 125.0045 -9.0005, 125.0025 -9.0005)))",
    )

    service = SaplingEstimationService()
    result = await service.run_estimation(
        async_session, farm_ids=[farm_a.id, farm_b.id], spacing_x=10, spacing_y=10, max_slope=15
    )

    assert result["status"] == "success"
    assert result["farm_count"] == 2
    assert len(result["results"]) == 2

    # Results come back in the same order as the requested farm_ids
    assert [item["farm_id"] for item in result["results"]] == [farm_a.id, farm_b.id]
    for item in result["results"]:
        assert item.get("status") != "failed", f"Service failed: {item}"
        assert item["aligned_count"] > 0


# Batch: a missing farm fails on its own without sinking the others
async def test_run_estimation_partial_missing(async_session):
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(DEM_INSERT)
    await async_session.flush()

    farm = await _add_farm(
        async_session,
        "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))",
    )
    missing_id = farm.id + 999999  # id that does not exist

    service = SaplingEstimationService()
    result = await service.run_estimation(
        async_session, farm_ids=[farm.id, missing_id], spacing_x=10, spacing_y=10, max_slope=15
    )

    assert result["status"] == "success"  # envelope should succeed, per-farm status has the failures
    assert result["farm_count"] == 2

    by_id = {item["farm_id"]: item for item in result["results"]}

    assert by_id[farm.id].get("status") != "failed"
    assert by_id[farm.id]["aligned_count"] > 0

    assert by_id[missing_id]["status"] == "failed"
    assert by_id[missing_id]["message"] == "Farm not found"
    
    
import pytest
from geoalchemy2 import WKTElement
from sqlalchemy import text

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.services.sapling_estimation import SaplingEstimationService


@pytest.mark.asyncio
async def test_run_estimation_basic(async_session, setup_soil_texture):
    """Test sapling estimation service with minimal DEM + boundary."""

    # Ensure dem_table exists in the test DB
    await async_session.execute(
        text("""
        CREATE TABLE IF NOT EXISTS dem_table (
            rid SERIAL PRIMARY KEY,
            rast RASTER
        );
    """)
    )

    # Clean DEM table
    await async_session.execute(text("DELETE FROM dem_table;"))

    # Insert a very small raster
    await async_session.execute(
        text("""
        INSERT INTO dem_table (rast)
        SELECT ST_AddBand(
            ST_MakeEmptyRaster(10, 10, 0, 100, 10, -10, 0, 0, 4326),
            '32BF'::text,
            1
        );
    """)
    )

    await async_session.commit()

    # Create farm first (boundary has FK to farms.id)
    farm = Farm(
        id=1,
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
    await async_session.commit()

    # Insert boundary
    wkt = "MULTIPOLYGON (((0 0, 0 50, 50 50, 50 0, 0 0)))"
    boundary = FarmBoundary(
        id=1,
        external_id=123,
        boundary=WKTElement(wkt, srid=4326),
    )
    async_session.add(boundary)
    await async_session.commit()

    # Run service in lightweight test mode
    result = await SaplingEstimationService.run_estimation(
        async_session,
        farm_id=1,
        spacing_m=100,
        test_mode=True,
    )

    assert result is not None
    assert "sapling_count" in result
    assert result["sapling_count"] >= 0
    assert "optimal_angle" in result

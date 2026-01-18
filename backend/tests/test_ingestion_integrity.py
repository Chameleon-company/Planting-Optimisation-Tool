import pytest
from httpx import AsyncClient
from sqlalchemy import select
from src.models.boundaries import FarmBoundary


@pytest.mark.asyncio
async def test_farm_and_boundary_link(
    async_client: AsyncClient, async_session, auth_user_headers, setup_soil_texture
):
    """Verify that a farm and boundary link correctly via shared PK and External ID."""

    # Create a Farm
    farm_payload = {
        "external_id": 999,
        "name": "Spatial Farm",
        "soil_texture_id": 1,
        "area_ha": 10.5,
        "rainfall_mm": 1500,
        "temperature_celsius": 25,
        "elevation_m": 500,
        "ph": 6.5,
        "latitude": -8.5,
        "longitude": 126.5,
        "coastal": False,
        "riparian": False,
        "nitrogen_fixing": False,
        "shade_tolerant": False,
        "bank_stabilising": False,
        "slope": 5.0,
    }
    farm_resp = await async_client.post(
        "/farms", json=farm_payload, headers=auth_user_headers
    )
    assert farm_resp.status_code == 201, f"Farm creation failed: {farm_resp.text}"
    farm_id = farm_resp.json()["id"]

    # Directly create a Boundary (simulating the import_boundaries script)
    wkt = "MULTIPOLYGON (((126.67 -8.56, 126.68 -8.56, 126.68 -8.57, 126.67 -8.56)))"
    boundary = FarmBoundary(id=farm_id, external_id=999, boundary=f"SRID=4326;{wkt}")
    async_session.add(boundary)
    await async_session.commit()

    # Verify spatial retrieval
    result = await async_session.execute(
        select(FarmBoundary).where(FarmBoundary.id == farm_id)
    )
    retrieved = result.scalar_one()
    assert retrieved.external_id == 999

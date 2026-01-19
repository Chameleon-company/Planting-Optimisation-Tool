import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.farm import Farm
from src.models.user import User
from src.main import app
from src.database import get_db_session


@pytest.mark.asyncio
async def test_read_farm_success_and_authorization_check(
    async_client: AsyncClient,
    async_session: AsyncSession,
    auth_user_headers: dict,
    test_user_a: User,
    test_user_b: User,
    setup_soil_texture,
):
    app.dependency_overrides[get_db_session] = lambda: async_session

    # Setup: Create farms
    farm_data_a = {
        "rainfall_mm": 1000,
        "temperature_celsius": 25.0,
        "elevation_m": 100,
        "ph": 6.5,
        "soil_texture_id": 1,
        "area_ha": 5.0,
        "latitude": 34.0,
        "longitude": -118.0,
        "coastal": False,
        "riparian": True,
        "nitrogen_fixing": True,
        "shade_tolerant": False,
        "bank_stabilising": True,
        "slope": 10.0,
    }

    farm_a = Farm(**farm_data_a, user_id=test_user_a.id)
    farm_b = Farm(**farm_data_a, user_id=test_user_b.id)

    async_session.add_all([farm_a, farm_b])
    await async_session.commit()
    await async_session.refresh(farm_a)

    farm_a_id = farm_a.id
    farm_b_id = farm_b.id

    # Test 1: SUCCESS (User A reads their own farm)
    url = f"/farms/{farm_a_id}"
    response = await async_client.get(url, headers=auth_user_headers)

    assert response.status_code == 200

    data = response.json()

    # Check that we got a list back with one item
    assert isinstance(data, dict), "Response should be a single farm object"
    assert data["id"] == farm_a_id
    assert data["user_id"] == test_user_a.id

    # Test 2: AUTHORIZATION FAILURE (User A tries to read User B's farm)
    url = f"/farms/{farm_b_id}"
    response = await async_client.get(url, headers=auth_user_headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

    # Test 3: UNAUTHENTICATED FAILURE
    url = f"/farms/{farm_a_id}"
    response = await async_client.get(url)
    assert response.status_code == 401

    app.dependency_overrides.clear()

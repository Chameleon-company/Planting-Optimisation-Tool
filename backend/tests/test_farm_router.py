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
    auth_user_b_headers: dict,
    test_user_a: User,
    test_user_b: User,
    setup_soil_texture,
):
    """
    This tells FastAPI: "Whenever a dependency asks for 'get_db_session',
    don't run the real function. Instead, just give it the 'async_session'
    we are already using in this test.
    """
    app.dependency_overrides[get_db_session] = lambda: async_session

    """
    Tests that a user can read their own farm (200 OK)
    and that they cannot read another user's farm (404 Not Found).
    """

    #  Setup: Create two farms, one for User A and one for User B

    # Farm for User A (Owner)
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
    # Same data different owner.
    farm_b = Farm(**farm_data_a, user_id=test_user_b.id)

    async_session.add_all([farm_a, farm_b])
    await async_session.commit()
    await async_session.refresh(farm_a)
    await async_session.refresh(farm_b)

    farm_a_id = farm_a.id
    farm_b_id = farm_b.id

    # Test 1: SUCCESS (User A reads their own farm)
    url = f"/farms/{farm_a_id}"
    response = await async_client.get(url, headers=auth_user_headers)

    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code} for owner access."
    )
    data = response.json()
    assert data["id"] == farm_a_id
    assert data["user_id"] == test_user_a.id

    # Test 2: AUTHORIZATION FAILURE (User A tries to read User B's farm)
    url = f"/farms/{farm_b_id}"
    response = await async_client.get(url, headers=auth_user_headers)

    # We expect a 404 NOT FOUND because the service query filters by owner ID,
    # making it appear as though the resource doesn't exist for User A.
    assert response.status_code == 404, (
        f"Expected 404 for unauthorized access, got {response.status_code}."
    )
    assert "not found" in response.json()["detail"]

    #  Test 3: UNAUTHENTICATED FAILURE (No headers)
    url = f"/farms/{farm_a_id}"
    response = await async_client.get(url)

    assert response.status_code == 401, (
        f"Expected 401 for unauthenticated access, got {response.status_code}."
    )
    assert "Not authenticated" in response.json()["detail"]
    app.dependency_overrides.clear()

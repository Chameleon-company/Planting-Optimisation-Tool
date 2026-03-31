import pytest
from geoalchemy2.elements import WKTElement
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import create_access_token
from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.models.user import User
from src.schemas.user import Role
from src.utils.security import get_password_hash

VALID_FARM_PAYLOAD = {
    "rainfall_mm": 1500,
    "temperature_celsius": 22,
    "elevation_m": 500,
    "ph": 6.5,
    "soil_texture_id": 1,
    "area_ha": 5.0,
    "latitude": -8.5,
    "longitude": 126.5,
    "coastal": False,
    "riparian": False,
    "nitrogen_fixing": False,
    "shade_tolerant": False,
    "bank_stabilising": False,
    "slope": 10.5,
}


@pytest.mark.asyncio
async def test_read_farm_success_and_authorization_check(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
):
    # Create two test users
    user_a = User(
        name="User A",
        email="usera@test.com",
        hashed_password=get_password_hash("passworda"),
        role=Role.OFFICER.value,
    )
    user_b = User(
        name="User B",
        email="userb@test.com",
        hashed_password=get_password_hash("passwordb"),
        role=Role.OFFICER.value,
    )

    async_session.add_all([user_a, user_b])
    await async_session.flush()
    await async_session.refresh(user_a)
    await async_session.refresh(user_b)

    # Create auth headers for user_a
    access_token = create_access_token(data={"sub": str(user_a.id), "role": user_a.role})
    auth_headers = {"Authorization": f"Bearer {access_token}"}

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

    farm_a = Farm(**farm_data_a, user_id=user_a.id)
    farm_b = Farm(**farm_data_a, user_id=user_b.id)

    async_session.add_all([farm_a, farm_b])
    await async_session.commit()
    await async_session.refresh(farm_a)
    await async_session.refresh(farm_b)

    farm_a_id = farm_a.id
    farm_b_id = farm_b.id

    # Test 1: SUCCESS (User A reads their own farm)
    url = f"/farms/{farm_a_id}"
    response = await async_client.get(url, headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    # Check that we got a single farm object back
    assert isinstance(data, dict), "Response should be a single farm object"
    assert data["id"] == farm_a_id
    assert data["user_id"] == user_a.id

    # Test 2: AUTHORIZATION FAILURE (User A tries to read User B's farm)
    url = f"/farms/{farm_b_id}"
    response = await async_client.get(url, headers=auth_headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

    # Test 3: UNAUTHENTICATED FAILURE
    url = f"/farms/{farm_a_id}"
    response = await async_client.get(url)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_profile_owner_access(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
):
    user_a = User(
        name="Env Owner",
        email="env_owner@test.com",
        hashed_password=get_password_hash("passworda"),
        role=Role.OFFICER.value,
    )
    async_session.add(user_a)
    await async_session.flush()
    await async_session.refresh(user_a)

    access_token = create_access_token(data={"sub": str(user_a.id), "role": user_a.role})
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    farm_data = {
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

    farm = Farm(**farm_data, user_id=user_a.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=12345,
        boundary=WKTElement(
            "MULTIPOLYGON (((126.67 -8.56, 126.68 -8.56, 126.68 -8.57, 126.67 -8.56)))",
            srid=4326,
        ),
    )
    async_session.add(boundary)
    await async_session.commit()

    response = await async_client.get(
        f"/profile/{farm.id}",
        headers=auth_headers,
    )

    assert response.status_code == 200


async def test_profile_blocks_non_owner(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
):
    user_a = User(
        name="User A",
        email="usera@test.com",
        hashed_password=get_password_hash("passworda"),
        role=Role.OFFICER.value,
    )
    user_b = User(
        name="User B",
        email="userb@test.com",
        hashed_password=get_password_hash("passwordb"),
        role=Role.OFFICER.value,
    )

    async_session.add_all([user_a, user_b])
    await async_session.flush()
    await async_session.refresh(user_a)
    await async_session.refresh(user_b)

    access_token = create_access_token(data={"sub": str(user_a.id), "role": user_a.role})
    auth_headers = {"Authorization": f"Bearer {access_token}"}

    farm_data = {
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

    farm_b = Farm(**farm_data, user_id=user_b.id)
    async_session.add(farm_b)
    await async_session.flush()
    await async_session.refresh(farm_b)

    boundary = FarmBoundary(
        id=farm_b.id,
        external_id=54321,
        boundary=WKTElement(
            "MULTIPOLYGON (((126.67 -8.56, 126.68 -8.56, 126.68 -8.57, 126.67 -8.56)))",
            srid=4326,
        ),
    )
    async_session.add(boundary)
    await async_session.commit()

    response = await async_client.get(
        f"/profile/{farm_b.id}",
        headers=auth_headers,
    )

    # Your service returns None → router returns 404
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_farm_success(
    async_client: AsyncClient,
    test_officer_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    """Officer creates a farm; verifies 201 and that user_id is set to the officer's ID."""
    response = await async_client.post("/farms", json=VALID_FARM_PAYLOAD, headers=officer_auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_officer_user.id


@pytest.mark.asyncio
async def test_create_farm_unauthenticated(
    async_client: AsyncClient,
    setup_soil_texture,
):
    """Unauthenticated request to create a farm returns 401."""
    response = await async_client.post("/farms", json=VALID_FARM_PAYLOAD)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_supervisor_can_read_any_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_supervisor_user: User,
    supervisor_auth_headers: dict,
    setup_soil_texture,
):
    """Supervisor can read a farm belonging to a different user (no ownership filter applied)."""
    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get(f"/farms/{farm.id}", headers=supervisor_auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == farm.id


@pytest.mark.asyncio
async def test_admin_can_read_any_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    """Admin can read a farm belonging to a different user (no ownership filter applied)."""
    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get(f"/farms/{farm.id}", headers=admin_auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == farm.id


@pytest.mark.asyncio
async def test_read_farm_not_found(
    async_client: AsyncClient,
    officer_auth_headers: dict,
    test_officer_user: User,
):
    """Reading a non-existent farm returns 404."""
    response = await async_client.get("/farms/99999999", headers=officer_auth_headers)
    assert response.status_code == 404

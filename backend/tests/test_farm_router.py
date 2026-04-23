import pytest
from geoalchemy2.elements import WKTElement
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import src.routers.farm as farm_router
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
async def test_officer_cannot_create_farm_blocked(
    async_client: AsyncClient,
    test_officer_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    """Officer cannot create a farm and receives 403."""
    response = await async_client.post("/farms", json=VALID_FARM_PAYLOAD, headers=officer_auth_headers)

    assert response.status_code == 403


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
    await async_session.commit()
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
    await async_session.commit()
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


@pytest.mark.asyncio
async def test_officer_cannot_create_farm(
    async_client: AsyncClient,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    response = await async_client.post("/farms", json=VALID_FARM_PAYLOAD, headers=officer_auth_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_supervisor_cannot_create_farm(
    async_client: AsyncClient,
    supervisor_auth_headers: dict,
    setup_soil_texture,
):
    response = await async_client.post("/farms", json=VALID_FARM_PAYLOAD, headers=supervisor_auth_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_create_farm_success(
    async_client: AsyncClient,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    response = await async_client.post("/farms", json=VALID_FARM_PAYLOAD, headers=admin_auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == test_admin_user.id
    assert data["rainfall_mm"] == VALID_FARM_PAYLOAD["rainfall_mm"]


@pytest.mark.asyncio
async def test_admin_can_update_farm_lat_long_and_recompute_riparian(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    async def fake_get_riparian_flags(db, latitude, longitude):
        assert latitude == -8.6
        assert longitude == 126.6
        return {"riparian": True}

    monkeypatch.setattr(farm_router, "get_riparian_flags", fake_get_riparian_flags)

    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    update_payload = {
        "latitude": -8.6,
        "longitude": 126.6,
    }

    response = await async_client.put(
        f"/farms/{farm.id}",
        json=update_payload,
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert float(data["latitude"]) == -8.6
    assert float(data["longitude"]) == 126.6
    assert data["riparian"] is True


@pytest.mark.asyncio
async def test_admin_can_update_farm_with_empty_agroforestry_ids(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.put(
        f"/farms/{farm.id}",
        json={"agroforestry_type_ids": []},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == farm.id
    assert data["agroforestry_type"] == []


@pytest.mark.asyncio
async def test_admin_can_update_farm_partially(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    async def fake_get_riparian_flags(db, latitude, longitude):
        return {"riparian": False}

    monkeypatch.setattr(farm_router, "get_riparian_flags", fake_get_riparian_flags)

    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    update_payload = {
        "area_ha": 8.5,
        "slope": 12.0,
    }

    response = await async_client.put(
        f"/farms/{farm.id}",
        json=update_payload,
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == farm.id
    assert float(data["area_ha"]) == 8.5
    assert float(data["slope"]) == 12.0
    assert data["rainfall_mm"] == VALID_FARM_PAYLOAD["rainfall_mm"]


@pytest.mark.asyncio
async def test_supervisor_can_update_own_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_supervisor_user: User,
    supervisor_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    async def fake_get_riparian_flags(db, latitude, longitude):
        return {"riparian": False}

    monkeypatch.setattr(farm_router, "get_riparian_flags", fake_get_riparian_flags)

    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_supervisor_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.put(
        f"/farms/{farm.id}",
        json={"area_ha": 9.0},
        headers=supervisor_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == farm.id
    assert float(data["area_ha"]) == 9.0


@pytest.mark.asyncio
async def test_supervisor_cannot_update_other_users_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    supervisor_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    async def fake_get_riparian_flags(db, latitude, longitude):
        return {"riparian": False}

    monkeypatch.setattr(farm_router, "get_riparian_flags", fake_get_riparian_flags)

    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.put(
        f"/farms/{farm.id}",
        json={"area_ha": 9.0},
        headers=supervisor_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_officer_cannot_update_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.put(
        f"/farms/{farm.id}",
        json={"area_ha": 9.0},
        headers=officer_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_farm_not_found(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    response = await async_client.put(
        "/farms/99999999",
        json={"area_ha": 7.5},
        headers=admin_auth_headers,
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_admin_can_delete_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.delete(f"/farms/{farm.id}", headers=admin_auth_headers)

    assert response.status_code == 204

    check_response = await async_client.get(f"/farms/{farm.id}", headers=admin_auth_headers)
    assert check_response.status_code == 404


@pytest.mark.asyncio
async def test_officer_cannot_delete_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.delete(f"/farms/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_supervisor_cannot_delete_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    supervisor_auth_headers: dict,
    setup_soil_texture,
):
    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.delete(
        f"/farms/{farm.id}",
        headers=supervisor_auth_headers,
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_farm_not_found(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.delete("/farms/99999999", headers=admin_auth_headers)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_farm_rejects_negative_elevation(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    invalid_payload = {**VALID_FARM_PAYLOAD, "elevation_m": -1}

    response = await async_client.post("/farms", json=invalid_payload, headers=admin_auth_headers)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_farm_rejects_negative_area(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    invalid_payload = {**VALID_FARM_PAYLOAD, "area_ha": -5}

    response = await async_client.post("/farms", json=invalid_payload, headers=admin_auth_headers)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_farm_rejects_invalid_latitude(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    invalid_payload = {**VALID_FARM_PAYLOAD, "latitude": -95}

    response = await async_client.post("/farms", json=invalid_payload, headers=admin_auth_headers)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_farm_rejects_invalid_slope(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    farm = Farm(**VALID_FARM_PAYLOAD, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.put(
        f"/farms/{farm.id}",
        json={"slope": -1},
        headers=admin_auth_headers,
    )

    assert response.status_code == 422

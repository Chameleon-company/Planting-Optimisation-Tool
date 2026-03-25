import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.farm import Farm
from src.models.user import User

pytestmark = pytest.mark.asyncio

VALID_FARM_DATA = {
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


async def test_officer_items_returns_own_farms(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    """Officer's /auth/users/me/items returns only farms belonging to them."""
    farm = Farm(**VALID_FARM_DATA, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    response = await async_client.get("/auth/users/me/items", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(f["id"] == farm.id for f in data)
    assert all(f["user_id"] == test_officer_user.id for f in data)


async def test_officer_items_excludes_other_users_farms(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_supervisor_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    """Officer's /auth/users/me/items does not include farms belonging to other users."""
    other_users_farm = Farm(**VALID_FARM_DATA, user_id=test_supervisor_user.id)
    async_session.add(other_users_farm)
    await async_session.flush()
    await async_session.refresh(other_users_farm)

    response = await async_client.get("/auth/users/me/items", headers=officer_auth_headers)

    assert response.status_code == 200
    farm_ids = [f["id"] for f in response.json()]
    assert other_users_farm.id not in farm_ids


async def test_items_returns_empty_list_when_no_farms(
    async_client: AsyncClient,
    test_officer_user: User,
    officer_auth_headers: dict,
):
    """Officer with no farms gets an empty list, not a 404."""
    response = await async_client.get("/auth/users/me/items", headers=officer_auth_headers)

    assert response.status_code == 200
    assert response.json() == []


async def test_items_unauthenticated_returns_401(async_client: AsyncClient):
    """Unauthenticated request to /auth/users/me/items returns 401."""
    response = await async_client.get("/auth/users/me/items")
    assert response.status_code == 401

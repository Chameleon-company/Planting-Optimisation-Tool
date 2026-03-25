import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

VALID_SPECIES_PAYLOAD = {
    "name": "Test Species",
    "common_name": "Testy",
    "rainfall_mm_min": 1000,
    "rainfall_mm_max": 2000,
    "temperature_celsius_min": 20,
    "temperature_celsius_max": 25,
    "elevation_m_min": 100,
    "elevation_m_max": 500,
    "ph_min": 5.5,
    "ph_max": 7.5,
    "coastal": False,
    "riparian": False,
    "nitrogen_fixing": False,
    "shade_tolerant": False,
    "bank_stabilising": False,
}


async def test_create_species_by_supervisor_success(
    async_client: AsyncClient,
    test_supervisor_user,
    supervisor_auth_headers: dict,
):
    """Supervisor can create a species (minimum required role)."""
    response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=supervisor_auth_headers)
    assert response.status_code == 201


async def test_create_species_by_admin_success(
    async_client: AsyncClient,
    test_admin_user,
    admin_auth_headers: dict,
):
    """Admin can create a species (hierarchical access above supervisor)."""
    response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    assert response.status_code == 201


async def test_create_species_by_officer_fails(
    async_client: AsyncClient,
    test_officer_user,
    officer_auth_headers: dict,
):
    """Officer cannot create a species; requires SUPERVISOR role or higher."""
    response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=officer_auth_headers)
    assert response.status_code == 403


async def test_create_species_unauthenticated(async_client: AsyncClient):
    """Unauthenticated request to create a species returns 401."""
    response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD)
    assert response.status_code == 401

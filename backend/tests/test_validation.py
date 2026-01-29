import pytest
from httpx import AsyncClient


# Species validation tests
@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("rainfall_mm_min", 150),
        ("rainfall_mm_max", 6000),
        ("temperature_celsius_min", 5),
        ("ph_min", 3.5),
        ("ph_max", 9.0),
        ("elevation_m_max", 3500),
    ],
)
@pytest.mark.asyncio
async def test_species_create_constraints(
    async_client: AsyncClient, test_admin_user, admin_auth_headers, field, invalid_value
):
    """Verifies Pydantic Field constraints for Species creation."""
    payload = {
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

    payload[field] = invalid_value

    response = await async_client.post(
        "/species", json=payload, headers=admin_auth_headers
    )

    assert response.status_code == 422
    assert field in response.text


# Farm validation tests
@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("rainfall_mm", 500),
        ("ph", 9.5),
        ("area_ha", 150),
        ("latitude", 100),
        ("slope", -5),
    ],
)
@pytest.mark.asyncio
async def test_farm_create_constraints(
    async_client: AsyncClient,
    test_admin_user,
    admin_auth_headers,
    setup_soil_texture,
    field,
    invalid_value,
):
    """Verifies Pydantic Field constraints for Farm creation."""
    payload = {
        "rainfall_mm": 1500,
        "temperature_celsius": 22,
        "elevation_m": 500,
        "ph": 6.5,
        "soil_texture_id": 1,
        "area_ha": 50.0,
        "latitude": -8.5,
        "longitude": 126.5,
        "coastal": False,
        "riparian": False,
        "nitrogen_fixing": False,
        "shade_tolerant": False,
        "bank_stabilising": False,
        "slope": 10.5,
    }

    payload[field] = invalid_value

    response = await async_client.post(
        "/farms", json=payload, headers=admin_auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_species_with_soil_textures(
    async_client: AsyncClient, test_admin_user, admin_auth_headers, setup_soil_texture
):
    """Tests that a species can be created with multiple soil texture associations."""
    payload = {
        "name": "Casuarina",
        "common_name": "She Oak",
        "rainfall_mm_min": 800,
        "rainfall_mm_max": 2000,
        "temperature_celsius_min": 15,
        "temperature_celsius_max": 30,
        "elevation_m_min": 0,
        "elevation_m_max": 1000,
        "ph_min": 5.0,
        "ph_max": 8.0,
        "coastal": True,
        "riparian": True,
        "nitrogen_fixing": True,
        "shade_tolerant": False,
        "bank_stabilising": True,
        "soil_textures": [1, 2, 4],
    }

    response = await async_client.post(
        "/species", json=payload, headers=admin_auth_headers
    )
    assert response.status_code == 201

    data = response.json()
    assert len(data["soil_textures"]) == 3
    assert data["soil_textures"][0]["name"] is not None

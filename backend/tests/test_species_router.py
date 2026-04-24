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

INVALID_RAINFALL_RANGE_PAYLOAD = {
    **VALID_SPECIES_PAYLOAD,
    "rainfall_mm_min": 2500,
    "rainfall_mm_max": 2000,
}

INVALID_TEMPERATURE_RANGE_PAYLOAD = {
    **VALID_SPECIES_PAYLOAD,
    "temperature_celsius_min": 30,
    "temperature_celsius_max": 25,
}

INVALID_ELEVATION_RANGE_PAYLOAD = {
    **VALID_SPECIES_PAYLOAD,
    "elevation_m_min": 700,
    "elevation_m_max": 500,
}

INVALID_PH_RANGE_PAYLOAD = {
    **VALID_SPECIES_PAYLOAD,
    "ph_min": 7.8,
    "ph_max": 7.0,
}


async def test_create_species_by_admin_success(
    async_client: AsyncClient,
    test_admin_user,
    admin_auth_headers: dict,
):
    response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    assert response.status_code == 201


async def test_create_species_by_supervisor_fails(
    async_client: AsyncClient,
    test_supervisor_user,
    supervisor_auth_headers: dict,
):
    response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=supervisor_auth_headers)
    assert response.status_code == 403


async def test_create_species_by_officer_fails(
    async_client: AsyncClient,
    test_officer_user,
    officer_auth_headers: dict,
):
    response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=officer_auth_headers)
    assert response.status_code == 403


async def test_create_species_unauthenticated(async_client: AsyncClient):
    response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD)
    assert response.status_code == 401


async def test_create_species_rejects_invalid_rainfall_range(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.post(
        "/species",
        json=INVALID_RAINFALL_RANGE_PAYLOAD,
        headers=admin_auth_headers,
    )

    assert response.status_code == 422


async def test_create_species_rejects_invalid_temperature_range(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.post(
        "/species",
        json=INVALID_TEMPERATURE_RANGE_PAYLOAD,
        headers=admin_auth_headers,
    )

    assert response.status_code == 422


async def test_create_species_rejects_invalid_elevation_range(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.post(
        "/species",
        json=INVALID_ELEVATION_RANGE_PAYLOAD,
        headers=admin_auth_headers,
    )

    assert response.status_code == 422


async def test_create_species_rejects_invalid_ph_range(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.post(
        "/species",
        json=INVALID_PH_RANGE_PAYLOAD,
        headers=admin_auth_headers,
    )

    assert response.status_code == 422


async def test_update_species_by_admin_success(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    create_response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]
    update_payload = {"common_name": "Updated Testy"}

    response = await async_client.put(
        f"/species/{species_id}",
        json=update_payload,
        headers=admin_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["common_name"] == "Updated Testy"


async def test_update_species_by_supervisor_fails(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    supervisor_auth_headers: dict,
):
    create_response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.put(
        f"/species/{species_id}",
        json={"common_name": "Not Allowed"},
        headers=supervisor_auth_headers,
    )
    assert response.status_code == 403


async def test_update_species_by_officer_fails(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    officer_auth_headers: dict,
):
    create_response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.put(
        f"/species/{species_id}",
        json={"common_name": "Not Allowed"},
        headers=officer_auth_headers,
    )
    assert response.status_code == 403


async def test_delete_species_by_admin_success(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    create_response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.delete(f"/species/{species_id}", headers=admin_auth_headers)
    assert response.status_code == 204


async def test_delete_species_by_supervisor_fails(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    supervisor_auth_headers: dict,
):
    create_response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.delete(f"/species/{species_id}", headers=supervisor_auth_headers)
    assert response.status_code == 403


async def test_delete_species_by_officer_fails(
    async_client: AsyncClient,
    admin_auth_headers: dict,
    officer_auth_headers: dict,
):
    create_response = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.delete(f"/species/{species_id}", headers=officer_auth_headers)
    assert response.status_code == 403


async def test_update_species_not_found(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.put(
        "/species/99999",
        json={"common_name": "Ghost"},
        headers=admin_auth_headers,
    )
    assert response.status_code == 404


async def test_delete_species_not_found(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.delete(
        "/species/99999",
        headers=admin_auth_headers,
    )
    assert response.status_code == 404


async def test_update_species_partial_fields(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    create = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    species = create.json()

    response = await async_client.put(
        f"/species/{species['id']}",
        json={"ph_min": 6.0},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert float(data["ph_min"]) == 6.0


async def test_update_species_rejects_temperature_max_below_existing_min(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    create_response = await async_client.post(
        "/species",
        json=VALID_SPECIES_PAYLOAD,
        headers=admin_auth_headers,
    )
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.put(
        f"/species/{species_id}",
        json={"temperature_celsius_max": 15},
        headers=admin_auth_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Minimum temperature cannot be greater than maximum temperature."


async def test_update_species_rejects_rainfall_min_above_existing_max(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    create_response = await async_client.post(
        "/species",
        json=VALID_SPECIES_PAYLOAD,
        headers=admin_auth_headers,
    )
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.put(
        f"/species/{species_id}",
        json={"rainfall_mm_min": 2501},
        headers=admin_auth_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Minimum rainfall cannot be greater than maximum rainfall."


async def test_update_species_rejects_elevation_range_when_both_fields_sent(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    create_response = await async_client.post(
        "/species",
        json=VALID_SPECIES_PAYLOAD,
        headers=admin_auth_headers,
    )
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.put(
        f"/species/{species_id}",
        json={
            "elevation_m_min": 900,
            "elevation_m_max": 500,
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 422


async def test_update_species_rejects_ph_min_above_existing_max(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    create_response = await async_client.post(
        "/species",
        json=VALID_SPECIES_PAYLOAD,
        headers=admin_auth_headers,
    )
    assert create_response.status_code == 201

    species_id = create_response.json()["id"]

    response = await async_client.put(
        f"/species/{species_id}",
        json={"ph_min": 8.0},
        headers=admin_auth_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Minimum pH cannot be greater than maximum pH."


async def test_delete_species_removes_record(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    create = await async_client.post("/species", json=VALID_SPECIES_PAYLOAD, headers=admin_auth_headers)
    species_id = create.json()["id"]

    await async_client.delete(f"/species/{species_id}", headers=admin_auth_headers)

    # Try deleting again → should be 404
    response = await async_client.delete(f"/species/{species_id}", headers=admin_auth_headers)
    assert response.status_code == 404

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.parameters import Parameter
from src.models.species import Species
from src.models.user import User


def make_species() -> Species:
    return Species(
        name="Tectona grandis",
        common_name="Teak",
        rainfall_mm_min=500,
        rainfall_mm_max=3000,
        temperature_celsius_min=15,
        temperature_celsius_max=35,
        elevation_m_min=0,
        elevation_m_max=2000,
        ph_min=5.0,
        ph_max=8.0,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
    )


def make_parameter(species_id: int) -> Parameter:
    return Parameter(
        species_id=species_id,
        feature="rainfall",
        score_method="trapezoid",
        weight=0.4,
        trap_left_tol=100.0,
        trap_right_tol=200.0,
    )


# --- GET /parameters ---


@pytest.mark.asyncio
async def test_list_parameters_admin(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that admin can list all parameters."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()

    response = await async_client.get("/parameters", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(p["feature"] == "rainfall" for p in data)


@pytest.mark.asyncio
async def test_list_parameters_officer_forbidden(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    """Test that officer cannot list parameters, requires ADMIN role."""
    response = await async_client.get("/parameters", headers=officer_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_parameters_supervisor_forbidden(
    async_client: AsyncClient,
    supervisor_auth_headers: dict,
):
    """Test that supervisor cannot list parameters, requires ADMIN role."""
    response = await async_client.get("/parameters", headers=supervisor_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_parameters_unauthenticated(async_client: AsyncClient):
    """Test that unauthenticated request is rejected."""
    response = await async_client.get("/parameters")
    assert response.status_code == 401


# --- GET /parameters/species/{species_id} ---


@pytest.mark.asyncio
async def test_list_parameters_by_species(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that admin can list parameters filtered by species."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()

    response = await async_client.get(f"/parameters/species/{species.id}", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(p["species_id"] == species.id for p in data)
    assert any(p["feature"] == "rainfall" for p in data)


@pytest.mark.asyncio
async def test_list_parameters_by_species_empty(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that an empty list is returned when the species has no parameters."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    response = await async_client.get(f"/parameters/species/{species.id}", headers=admin_auth_headers)

    assert response.status_code == 200
    assert response.json() == []


# --- GET /parameters/{parameter_id} ---


@pytest.mark.asyncio
async def test_get_parameter_by_id(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that admin can fetch a single parameter by ID."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()
    await async_session.refresh(param)

    response = await async_client.get(f"/parameters/{param.id}", headers=admin_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == param.id
    assert data["species_id"] == species.id
    assert data["feature"] == "rainfall"
    assert data["score_method"] == "trapezoid"
    assert data["weight"] == pytest.approx(0.4)
    assert data["trap_left_tol"] == pytest.approx(100.0)
    assert data["trap_right_tol"] == pytest.approx(200.0)


@pytest.mark.asyncio
async def test_get_parameter_not_found(
    async_client: AsyncClient,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that 404 is returned for a non-existent parameter ID."""
    response = await async_client.get("/parameters/999999", headers=admin_auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Parameter not found"


# --- POST /parameters ---


@pytest.mark.asyncio
async def test_create_parameter(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that admin can create a new parameter."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    payload = {
        "species_id": species.id,
        "feature": "temperature",
        "score_method": "trapezoid",
        "weight": 0.3,
        "trap_left_tol": 5.0,
        "trap_right_tol": 5.0,
    }

    response = await async_client.post("/parameters", json=payload, headers=admin_auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["species_id"] == species.id
    assert data["feature"] == "temperature"
    assert data["score_method"] == "trapezoid"
    assert data["weight"] == pytest.approx(0.3)
    assert "id" in data


@pytest.mark.asyncio
async def test_create_parameter_officer_forbidden(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    officer_auth_headers: dict,
):
    """Test that officer cannot create a parameter."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    payload = {
        "species_id": species.id,
        "feature": "temperature",
        "score_method": "trapezoid",
        "weight": 0.3,
    }

    response = await async_client.post("/parameters", json=payload, headers=officer_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_parameter_invalid_species(
    async_client: AsyncClient,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that 422 is returned when the species_id does not exist."""
    payload = {
        "species_id": 999999,
        "feature": "temperature",
        "score_method": "trapezoid",
        "weight": 0.3,
    }

    response = await async_client.post("/parameters", json=payload, headers=admin_auth_headers)
    assert response.status_code == 422
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_parameter_invalid_weight(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that weight above 1.0 is rejected."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    payload = {
        "species_id": species.id,
        "feature": "temperature",
        "score_method": "trapezoid",
        "weight": 1.5,  # above maximum
    }

    response = await async_client.post("/parameters", json=payload, headers=admin_auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_parameter_weight_below_minimum(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that weight below 0.0 is rejected."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    payload = {
        "species_id": species.id,
        "feature": "temperature",
        "score_method": "trapezoid",
        "weight": -0.1,  # below minimum
    }

    response = await async_client.post("/parameters", json=payload, headers=admin_auth_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_parameter_without_optional_fields(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that creating a parameter without trap tolerance fields defaults them to null."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    payload = {
        "species_id": species.id,
        "feature": "elevation",
        "score_method": "trapezoid",
        "weight": 0.2,
        # trap_left_tol and trap_right_tol not included
    }

    response = await async_client.post("/parameters", json=payload, headers=admin_auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["trap_left_tol"] is None
    assert data["trap_right_tol"] is None


# --- PUT /parameters/{parameter_id} ---


@pytest.mark.asyncio
async def test_update_parameter(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that admin can update an existing parameter."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()
    await async_session.refresh(param)

    response = await async_client.put(
        f"/parameters/{param.id}",
        json={"weight": 0.6, "trap_left_tol": 150.0},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["weight"] == pytest.approx(0.6)
    assert data["trap_left_tol"] == pytest.approx(150.0)
    # Fields not included in the update should remain unchanged
    assert data["feature"] == "rainfall"


@pytest.mark.asyncio
async def test_update_parameter_invalid_weight(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that weight outside 0-1 range is rejected on update."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()
    await async_session.refresh(param)

    response = await async_client.put(
        f"/parameters/{param.id}",
        json={"weight": 2.0},  # invalid
        headers=admin_auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_parameter_empty_body(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that updating with an empty body leaves all fields unchanged."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()
    await async_session.refresh(param)

    response = await async_client.put(
        f"/parameters/{param.id}",
        json={},
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["feature"] == "rainfall"
    assert data["weight"] == pytest.approx(0.4)


@pytest.mark.asyncio
async def test_update_parameter_invalid_species(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that 422 is returned when updating a parameter to a non-existent species_id."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()
    await async_session.refresh(param)

    response = await async_client.put(
        f"/parameters/{param.id}",
        json={"species_id": 999999},
        headers=admin_auth_headers,
    )
    assert response.status_code == 422
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_parameter_not_found(
    async_client: AsyncClient,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that 404 is returned when updating a non-existent parameter."""
    response = await async_client.put(
        "/parameters/999999",
        json={"weight": 0.5},
        headers=admin_auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Parameter not found"


# --- DELETE /parameters/{parameter_id} ---


@pytest.mark.asyncio
async def test_delete_parameter(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that admin can delete an existing parameter."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()
    await async_session.refresh(param)

    response = await async_client.delete(f"/parameters/{param.id}", headers=admin_auth_headers)
    assert response.status_code == 204

    # Verify it's gone
    get_response = await async_client.get(f"/parameters/{param.id}", headers=admin_auth_headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_parameter_not_found(
    async_client: AsyncClient,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    """Test that 404 is returned when deleting a non-existent parameter."""
    response = await async_client.delete("/parameters/999999", headers=admin_auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Parameter not found"


@pytest.mark.asyncio
async def test_delete_parameter_officer_forbidden(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    officer_auth_headers: dict,
):
    """Test that officer cannot delete a parameter."""
    species = make_species()
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)

    param = make_parameter(species.id)
    async_session.add(param)
    await async_session.flush()
    await async_session.refresh(param)

    response = await async_client.delete(f"/parameters/{param.id}", headers=officer_auth_headers)
    assert response.status_code == 403

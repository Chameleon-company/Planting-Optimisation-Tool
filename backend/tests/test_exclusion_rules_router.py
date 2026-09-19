import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.species import Species


async def add_species(
    async_session: AsyncSession,
    suffix: str,
) -> Species:
    species = Species(
        name=f"US031 Species {suffix}",
        common_name=f"US031 Common {suffix}",
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
    async_session.add(species)
    await async_session.flush()
    await async_session.refresh(species)
    return species


async def test_exclusion_rule_crud(
    async_client: AsyncClient,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    species = await add_species(async_session, "Rule CRUD")

    create_response = await async_client.post(
        "/exclusion-rules",
        json={
            "species_id": species.id,
            "feature": "ph",
            "operator": "<",
            "value": 5.5,
            "reason": "Soil pH is too low",
        },
        headers=admin_auth_headers,
    )

    assert create_response.status_code == 201
    created = create_response.json()
    rule_id = created["id"]
    assert created["species_id"] == species.id
    assert created["feature"] == "ph"
    assert created["operator"] == "<"
    assert created["value"] == pytest.approx(5.5)

    get_response = await async_client.get(
        f"/exclusion-rules/{rule_id}",
        headers=admin_auth_headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == rule_id

    list_response = await async_client.get(
        "/exclusion-rules",
        headers=admin_auth_headers,
    )

    assert list_response.status_code == 200
    listed_rules = list_response.json()
    assert any(rule["id"] == rule_id for rule in listed_rules)
    listed_ids = [rule["id"] for rule in listed_rules]
    assert listed_ids == sorted(listed_ids)

    update_response = await async_client.patch(
        f"/exclusion-rules/{rule_id}",
        json={
            "operator": "<=",
            "value": 6.0,
            "reason": "Updated pH requirement",
        },
        headers=admin_auth_headers,
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["operator"] == "<="
    assert updated["value"] == pytest.approx(6.0)
    assert updated["reason"] == "Updated pH requirement"
    assert updated["feature"] == "ph"

    delete_response = await async_client.delete(
        f"/exclusion-rules/{rule_id}",
        headers=admin_auth_headers,
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    deleted_get_response = await async_client.get(
        f"/exclusion-rules/{rule_id}",
        headers=admin_auth_headers,
    )
    assert deleted_get_response.status_code == 404


async def test_exclusion_rules_require_admin(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    unauthenticated_response = await async_client.get("/exclusion-rules")
    assert unauthenticated_response.status_code == 401

    forbidden_response = await async_client.get(
        "/exclusion-rules",
        headers=officer_auth_headers,
    )
    assert forbidden_response.status_code == 403

    forbidden_create_response = await async_client.post(
        "/exclusion-rules",
        json={
            "species_id": 1,
            "feature": "ph",
            "operator": "<",
            "value": 5.5,
            "reason": "Not authorised",
        },
        headers=officer_auth_headers,
    )
    assert forbidden_create_response.status_code == 403


async def test_create_exclusion_rule_rejects_invalid_species(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.post(
        "/exclusion-rules",
        json={
            "species_id": 999999,
            "feature": "ph",
            "operator": "<",
            "value": 5.5,
            "reason": "Invalid species",
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 422
    assert "not found" in response.json()["detail"]


async def test_create_exclusion_rule_rejects_invalid_input(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    invalid_operator_response = await async_client.post(
        "/exclusion-rules",
        json={
            "species_id": 1,
            "feature": "ph",
            "operator": "invalid_operator",
            "value": 5.5,
            "reason": "Invalid operator",
        },
        headers=admin_auth_headers,
    )
    assert invalid_operator_response.status_code == 422

    invalid_id_response = await async_client.post(
        "/exclusion-rules",
        json={
            "species_id": 0,
            "feature": "ph",
            "operator": "<",
            "value": 5.5,
            "reason": "Invalid ID",
        },
        headers=admin_auth_headers,
    )
    assert invalid_id_response.status_code == 422


async def test_update_exclusion_rule_rejects_null(
    async_client: AsyncClient,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    species = await add_species(async_session, "Null Update")

    create_response = await async_client.post(
        "/exclusion-rules",
        json={
            "species_id": species.id,
            "feature": "rainfall_mm",
            "operator": "<",
            "value": 700,
            "reason": "Insufficient rainfall",
        },
        headers=admin_auth_headers,
    )
    assert create_response.status_code == 201

    rule_id = create_response.json()["id"]
    response = await async_client.patch(
        f"/exclusion-rules/{rule_id}",
        json={"reason": None},
        headers=admin_auth_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Exclusion rule fields cannot be null"


async def test_exclusion_rule_not_found_responses(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    get_response = await async_client.get(
        "/exclusion-rules/999999",
        headers=admin_auth_headers,
    )
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Exclusion rule not found"

    update_response = await async_client.patch(
        "/exclusion-rules/999999",
        json={"reason": "Missing rule"},
        headers=admin_auth_headers,
    )
    assert update_response.status_code == 404

    delete_response = await async_client.delete(
        "/exclusion-rules/999999",
        headers=admin_auth_headers,
    )
    assert delete_response.status_code == 404


async def test_species_dependency_crud(
    async_client: AsyncClient,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    focal_species = await add_species(async_session, "Dependency Focal")
    first_partner = await add_species(async_session, "Dependency Partner One")
    second_partner = await add_species(async_session, "Dependency Partner Two")

    create_response = await async_client.post(
        "/species-dependencies",
        json={
            "focal_species_id": focal_species.id,
            "required_partner_id": first_partner.id,
        },
        headers=admin_auth_headers,
    )

    assert create_response.status_code == 201
    created = create_response.json()
    dependency_id = created["id"]
    assert created["focal_species_id"] == focal_species.id
    assert created["required_partner_id"] == first_partner.id

    get_response = await async_client.get(
        f"/species-dependencies/{dependency_id}",
        headers=admin_auth_headers,
    )

    assert get_response.status_code == 200
    assert get_response.json()["id"] == dependency_id

    list_response = await async_client.get(
        "/species-dependencies",
        headers=admin_auth_headers,
    )

    assert list_response.status_code == 200
    listed_dependencies = list_response.json()
    assert any(dependency["id"] == dependency_id for dependency in listed_dependencies)
    listed_ids = [dependency["id"] for dependency in listed_dependencies]
    assert listed_ids == sorted(listed_ids)

    update_response = await async_client.patch(
        f"/species-dependencies/{dependency_id}",
        json={"required_partner_id": second_partner.id},
        headers=admin_auth_headers,
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["focal_species_id"] == focal_species.id
    assert updated["required_partner_id"] == second_partner.id

    delete_response = await async_client.delete(
        f"/species-dependencies/{dependency_id}",
        headers=admin_auth_headers,
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    deleted_get_response = await async_client.get(
        f"/species-dependencies/{dependency_id}",
        headers=admin_auth_headers,
    )
    assert deleted_get_response.status_code == 404


async def test_species_dependencies_require_admin(
    async_client: AsyncClient,
    officer_auth_headers: dict,
):
    unauthenticated_response = await async_client.get("/species-dependencies")
    assert unauthenticated_response.status_code == 401

    forbidden_response = await async_client.get(
        "/species-dependencies",
        headers=officer_auth_headers,
    )
    assert forbidden_response.status_code == 403

    forbidden_create_response = await async_client.post(
        "/species-dependencies",
        json={
            "focal_species_id": 1,
            "required_partner_id": 2,
        },
        headers=officer_auth_headers,
    )
    assert forbidden_create_response.status_code == 403


async def test_create_dependency_rejects_missing_species(
    async_client: AsyncClient,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    existing_species = await add_species(
        async_session,
        "Dependency Existing",
    )

    missing_focal_response = await async_client.post(
        "/species-dependencies",
        json={
            "focal_species_id": 999998,
            "required_partner_id": existing_species.id,
        },
        headers=admin_auth_headers,
    )

    assert missing_focal_response.status_code == 422
    assert "not found" in missing_focal_response.json()["detail"]

    missing_partner_response = await async_client.post(
        "/species-dependencies",
        json={
            "focal_species_id": existing_species.id,
            "required_partner_id": 999999,
        },
        headers=admin_auth_headers,
    )

    assert missing_partner_response.status_code == 422
    assert "not found" in missing_partner_response.json()["detail"]


async def test_create_dependency_rejects_self_dependency(
    async_client: AsyncClient,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    species = await add_species(async_session, "Self Dependency")

    response = await async_client.post(
        "/species-dependencies",
        json={
            "focal_species_id": species.id,
            "required_partner_id": species.id,
        },
        headers=admin_auth_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "A species cannot depend on itself"


async def test_dependency_rejects_invalid_id_and_null_update(
    async_client: AsyncClient,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    focal_species = await add_species(async_session, "Invalid Update Focal")
    partner_species = await add_species(
        async_session,
        "Invalid Update Partner",
    )

    invalid_id_response = await async_client.post(
        "/species-dependencies",
        json={
            "focal_species_id": 0,
            "required_partner_id": partner_species.id,
        },
        headers=admin_auth_headers,
    )
    assert invalid_id_response.status_code == 422

    create_response = await async_client.post(
        "/species-dependencies",
        json={
            "focal_species_id": focal_species.id,
            "required_partner_id": partner_species.id,
        },
        headers=admin_auth_headers,
    )
    assert create_response.status_code == 201

    dependency_id = create_response.json()["id"]
    null_update_response = await async_client.patch(
        f"/species-dependencies/{dependency_id}",
        json={"required_partner_id": None},
        headers=admin_auth_headers,
    )

    assert null_update_response.status_code == 422
    assert null_update_response.json()["detail"] == "Dependency fields cannot be null"


async def test_update_dependency_rejects_invalid_relationship(
    async_client: AsyncClient,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    focal_species = await add_species(async_session, "Update Focal")
    partner_species = await add_species(async_session, "Update Partner")

    create_response = await async_client.post(
        "/species-dependencies",
        json={
            "focal_species_id": focal_species.id,
            "required_partner_id": partner_species.id,
        },
        headers=admin_auth_headers,
    )
    assert create_response.status_code == 201

    dependency_id = create_response.json()["id"]

    self_dependency_response = await async_client.patch(
        f"/species-dependencies/{dependency_id}",
        json={"required_partner_id": focal_species.id},
        headers=admin_auth_headers,
    )
    assert self_dependency_response.status_code == 422
    assert self_dependency_response.json()["detail"] == "A species cannot depend on itself"

    missing_species_response = await async_client.patch(
        f"/species-dependencies/{dependency_id}",
        json={"required_partner_id": 999999},
        headers=admin_auth_headers,
    )
    assert missing_species_response.status_code == 422
    assert "not found" in missing_species_response.json()["detail"]


async def test_species_dependency_not_found_responses(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    get_response = await async_client.get(
        "/species-dependencies/999999",
        headers=admin_auth_headers,
    )
    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "Species dependency not found"

    update_response = await async_client.patch(
        "/species-dependencies/999999",
        json={"required_partner_id": 1},
        headers=admin_auth_headers,
    )
    assert update_response.status_code == 404

    delete_response = await async_client.delete(
        "/species-dependencies/999999",
        headers=admin_auth_headers,
    )
    assert delete_response.status_code == 404


async def test_update_exclusion_rule_validates_species(
    async_client: AsyncClient,
    async_session: AsyncSession,
    admin_auth_headers: dict,
):
    original_species = await add_species(async_session, "Original Rule Species")
    replacement_species = await add_species(
        async_session,
        "Replacement Rule Species",
    )

    create_response = await async_client.post(
        "/exclusion-rules",
        json={
            "species_id": original_species.id,
            "feature": "ph",
            "operator": "<",
            "value": 5.5,
            "reason": "Soil pH is too low",
        },
        headers=admin_auth_headers,
    )
    assert create_response.status_code == 201

    rule_id = create_response.json()["id"]

    valid_update_response = await async_client.patch(
        f"/exclusion-rules/{rule_id}",
        json={"species_id": replacement_species.id},
        headers=admin_auth_headers,
    )

    assert valid_update_response.status_code == 200
    assert valid_update_response.json()["species_id"] == replacement_species.id

    missing_species_response = await async_client.patch(
        f"/exclusion-rules/{rule_id}",
        json={"species_id": 999999},
        headers=admin_auth_headers,
    )

    assert missing_species_response.status_code == 422
    assert "not found" in missing_species_response.json()["detail"]

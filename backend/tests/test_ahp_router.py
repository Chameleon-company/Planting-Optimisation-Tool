from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models.parameters import Parameter
from src.models.species import Species


@pytest.mark.asyncio
@patch("src.services.ahp_service.get_recommend_config")
async def test_calculate_and_save_endpoint(mock_get_config, async_client: AsyncClient, async_session, admin_auth_headers):
    """
    Verifies the /ahp/calculate-and-save endpoint accepts valid matrices,
    returns 200 OK, and saves to the DB.
    """
    # Mock YAML Config
    mock_get_config.return_value = {"features": {"rainfall_mm": {"type": "numeric", "default_weight": 0.20}, "temperature_celsius": {"type": "numeric", "default_weight": 0.20}}}

    # Database Setup (Valid Species)
    test_species = Species(
        name="API Test Species",
        common_name="API Test",
        rainfall_mm_min=800,
        rainfall_mm_max=2000,
        temperature_celsius_min=15,
        temperature_celsius_max=30,
        elevation_m_min=0,
        elevation_m_max=1000,
        ph_min=5.0,
        ph_max=8.0,
        coastal=True,
        riparian=True,
        nitrogen_fixing=True,
        shade_tolerant=False,
        bank_stabilising=True,
    )
    async_session.add(test_species)
    await async_session.commit()

    # Prepare HTTP Payload
    payload = {
        "species_id": test_species.id,
        "matrix": [[1.0, 1.0], [1.0, 1.0]],  # Equal weights matrix
    }

    # Make Request
    response = await async_client.post("/ahp/calculate-and-save", json=payload, headers=admin_auth_headers)

    # Verify HTTP Response
    assert response.status_code == 200
    data = response.json()
    assert data["is_consistent"] is True
    assert data["weights"]["rainfall_mm"] == 0.5
    assert data["weights"]["temperature_celsius"] == 0.5

    # Verify Database State
    stmt = select(Parameter).where(Parameter.species_id == test_species.id)
    db_result = await async_session.execute(stmt)
    params = db_result.scalars().all()
    assert len(params) == 2


@pytest.mark.asyncio
async def test_calculate_and_save_unauthorised(async_client: AsyncClient):
    """
    Ensures the endpoint cannot be accessed without proper authentication.
    """
    payload = {"species_id": 1, "matrix": [[1]]}

    response = await async_client.post("/ahp/calculate-and-save", json=payload)

    assert response.status_code in (401, 403)

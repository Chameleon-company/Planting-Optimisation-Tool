import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import limiter
from src.models.farm import Farm
from src.models.user import User

pytestmark = pytest.mark.asyncio

# TODO: Currently sapling_estimation and environmental_profile don't run fast enough
# to hit the rate limit of 10/min, once they're refactored and running faster they can have tests too.


async def test_slowapi_limiter_on_register(async_client: AsyncClient, admin_auth_headers: dict):
    """
    Testing rate limiting on register endpoint (10/min).
    Verifies that:
    - The first response returns 200
    - The last response returns 429
    - Indicating that the rate limit has been hit and the user has been restricted.
    """
    limiter.reset()
    response = await async_client.post(
        "/auth/register",
        json={
            "email": f"rate_limiting_auth_{uuid.uuid4().hex}@test.com",
            "name": f"Rate limiting Test User {uuid.uuid4().hex}",
            "password": "RatesAreL1m1t3d!",
            "role": "officer",
        },
    )
    print(response.json())
    assert response.status_code == 200
    for i in range(0, 11):
        response = await async_client.post(
            "/auth/register",
            json={
                "email": f"rate_limiting_auth_{uuid.uuid4().hex}@test.com",
                "name": f"Rate limiting Test User {uuid.uuid4().hex}",
                "password": "RatesAreL1m1t3d!",
                "role": "officer",
            },
        )
        print(f"{i}: {response.status_code}")
    assert response.status_code == 429


async def test_slowapi_limiter_on_recommendations(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
):
    """
    Testing rate limiting on recommendations endpoint.
    Verifies that:
    - The first response returns 200
    - The last response returns 429
    - Indicating that the rate limit has been hit and the user has been restricted.
    """
    farm = Farm(
        rainfall_mm=1500,
        temperature_celsius=22,
        elevation_m=500,
        ph=6.5,
        soil_texture_id=1,
        area_ha=5.0,
        latitude=-8.5,
        longitude=126.5,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=10.5,
        user_id=test_admin_user.id,
    )
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    limiter.reset()
    response = await async_client.get(f"/recommendations/{farm.id}", headers=admin_auth_headers)
    assert response.status_code == 200
    for i in range(0, 11):
        response = await async_client.get(f"/recommendations/{farm.id}", headers=admin_auth_headers)
    assert response.status_code == 429

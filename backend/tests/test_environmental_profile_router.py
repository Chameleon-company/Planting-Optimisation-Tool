from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.farm import Farm
from src.models.user import User

_FARM_DATA = {
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
    "slope": 10.0,
}

_FAKE_PROFILE = {"id": 1, "rainfall_mm": 1500, "temperature_celsius": 22}


async def test_cache_miss(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    farm = Farm(user_id=test_admin_user.id, **_FARM_DATA)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    with patch(
        "src.services.environmental_profile.EnvironmentalProfileService.run_environmental_profile",
        new_callable=AsyncMock,
        return_value=_FAKE_PROFILE,
    ) as mock_run:
        r = await async_client.get(f"/profile/{farm.id}", headers=admin_auth_headers)
        assert r.status_code == 200
        mock_run.assert_called_once()


async def test_cache_hit(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    farm = Farm(user_id=test_admin_user.id, **_FARM_DATA)
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    with patch(
        "src.services.environmental_profile.EnvironmentalProfileService.run_environmental_profile",
        new_callable=AsyncMock,
        return_value=_FAKE_PROFILE,
    ) as mock_run:
        r1 = await async_client.get(f"/profile/{farm.id}", headers=admin_auth_headers)
        assert r1.status_code == 200
        mock_run.assert_called_once()

        r2 = await async_client.get(f"/profile/{farm.id}", headers=admin_auth_headers)
        assert r2.status_code == 200
        mock_run.assert_called_once()
        assert r2.json() == r1.json()

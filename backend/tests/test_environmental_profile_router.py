from unittest.mock import AsyncMock, patch

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.farm import Farm
from src.models.user import User
from src.services.environmental_profile import ImputationError

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
    farm = Farm(**_FARM_DATA)
    farm.owners = [test_admin_user]
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
    farm = Farm(**_FARM_DATA)
    farm.owners = [test_admin_user]
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


async def test_regenerate_profile_admin_success(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    test_admin_user: User,
    admin_auth_headers: dict,
):
    farm = Farm(**_FARM_DATA)
    farm.owners = [test_admin_user]
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    with (
        patch(
            "src.routers.environmental_profile.cache.invalidate",
            new_callable=AsyncMock,
        ) as mock_invalidate,
        patch(
            "src.routers.environmental_profile.cache.set",
            new_callable=AsyncMock,
        ) as mock_cache_set,
        patch(
            "src.services.environmental_profile.EnvironmentalProfileService.run_environmental_profile",
            new_callable=AsyncMock,
            return_value=_FAKE_PROFILE,
        ) as mock_run,
    ):
        response = await async_client.post(
            f"/profile/{farm.id}/regenerate",
            headers=admin_auth_headers,
        )

        assert response.status_code == 200

        mock_invalidate.assert_awaited_once_with(
            f"profile:{farm.id}",
            f"sapling:{farm.id}",
            f"rec:{farm.id}",
        )

        mock_run.assert_awaited_once_with(
            async_session,
            farm.id,
        )

        mock_cache_set.assert_awaited_once()


async def test_regenerate_profile_supervisor_own_farm_success(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    test_supervisor_user: User,
    supervisor_auth_headers: dict,
):
    farm = Farm(**_FARM_DATA)
    farm.owners = [test_supervisor_user]
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    with (
        patch(
            "src.routers.environmental_profile.cache.invalidate",
            new_callable=AsyncMock,
        ) as mock_invalidate,
        patch(
            "src.routers.environmental_profile.cache.set",
            new_callable=AsyncMock,
        ),
        patch(
            "src.services.environmental_profile.EnvironmentalProfileService.run_environmental_profile",
            new_callable=AsyncMock,
            return_value=_FAKE_PROFILE,
        ) as mock_run,
    ):
        response = await async_client.post(
            f"/profile/{farm.id}/regenerate",
            headers=supervisor_auth_headers,
        )

        assert response.status_code == 200

        mock_invalidate.assert_awaited_once_with(
            f"profile:{farm.id}",
            f"sapling:{farm.id}",
            f"rec:{farm.id}",
        )

        mock_run.assert_awaited_once_with(
            async_session,
            farm.id,
        )


async def test_regenerate_profile_supervisor_other_farm_forbidden(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    test_officer_user: User,
    supervisor_auth_headers: dict,
):
    farm = Farm(**_FARM_DATA)
    farm.owners = [test_officer_user]
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    with patch(
        "src.services.environmental_profile.EnvironmentalProfileService.run_environmental_profile",
        new_callable=AsyncMock,
    ) as mock_run:
        response = await async_client.post(
            f"/profile/{farm.id}/regenerate",
            headers=supervisor_auth_headers,
        )

        assert response.status_code == 403
        assert response.json()["detail"] == ("The user does not have adequate permissions.")

        mock_run.assert_not_awaited()


async def test_regenerate_profile_officer_forbidden(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    test_officer_user: User,
    officer_auth_headers: dict,
):
    farm = Farm(**_FARM_DATA)
    farm.owners = [test_officer_user]
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    with patch(
        "src.services.environmental_profile.EnvironmentalProfileService.run_environmental_profile",
        new_callable=AsyncMock,
    ) as mock_run:
        response = await async_client.post(
            f"/profile/{farm.id}/regenerate",
            headers=officer_auth_headers,
        )

        assert response.status_code == 403
        mock_run.assert_not_awaited()


async def test_regenerate_profile_missing_farm_returns_404(
    async_client: AsyncClient,
    admin_auth_headers: dict,
):
    response = await async_client.post(
        "/profile/999999/regenerate",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == ("Farm with ID 999999 not found.")


async def test_regenerate_profile_imputation_error_returns_503(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    test_supervisor_user: User,
    supervisor_auth_headers: dict,
):
    farm = Farm(**_FARM_DATA)
    farm.owners = [test_supervisor_user]

    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    with (
        patch(
            "src.routers.environmental_profile.cache.invalidate",
            new_callable=AsyncMock,
        ),
        patch(
            "src.routers.environmental_profile.cache.set",
            new_callable=AsyncMock,
        ) as mock_cache_set,
        patch(
            "src.services.environmental_profile.EnvironmentalProfileService.run_environmental_profile",
            new_callable=AsyncMock,
            side_effect=ImputationError("Environmental profile generation failed."),
        ),
    ):
        response = await async_client.post(
            f"/profile/{farm.id}/regenerate",
            headers=supervisor_auth_headers,
        )

    assert response.status_code == 503
    assert response.json()["detail"] == ("Environmental profile generation failed.")

    mock_cache_set.assert_not_awaited()


async def test_regenerate_profile_empty_result_returns_404(
    async_client: AsyncClient,
    async_session: AsyncSession,
    setup_soil_texture,
    test_officer_user: User,
    admin_auth_headers: dict,
):
    farm = Farm(**_FARM_DATA)
    farm.owners = [test_officer_user]

    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    with (
        patch(
            "src.routers.environmental_profile.cache.invalidate",
            new_callable=AsyncMock,
        ),
        patch(
            "src.routers.environmental_profile.cache.set",
            new_callable=AsyncMock,
        ) as mock_cache_set,
        patch(
            "src.services.environmental_profile.EnvironmentalProfileService.run_environmental_profile",
            new_callable=AsyncMock,
            return_value=None,
        ),
    ):
        response = await async_client.post(
            f"/profile/{farm.id}/regenerate",
            headers=admin_auth_headers,
        )

    assert response.status_code == 404
    assert response.json()["detail"] == (f"Farm boundary not found for farm_id: {farm.id}")

    mock_cache_set.assert_not_awaited()

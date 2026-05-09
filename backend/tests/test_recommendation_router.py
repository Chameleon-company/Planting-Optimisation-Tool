import json
from unittest.mock import AsyncMock, MagicMock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import src.routers.recommendation as rec_router
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

_MOCK_REC = {
    "farm_id": None,
    "timestamp_utc": "2025-01-01T00:00:00+00:00",
    "recommendations": [],
    "excluded_species": [],
}


def _patch_dependencies(monkeypatch, pipeline_return_value):
    """Patch cache, species service, and recommendation pipeline for the router."""
    monkeypatch.setattr(rec_router.cache, "get", AsyncMock(return_value=None))
    monkeypatch.setattr(rec_router.cache, "set", AsyncMock())
    monkeypatch.setattr(rec_router.species_service, "get_all_species_for_engine", AsyncMock(return_value=[]))
    monkeypatch.setattr(rec_router.species_service, "get_recommend_config", MagicMock(return_value={}))
    monkeypatch.setattr(
        rec_router.recommendation_service,
        "run_recommendation_pipeline",
        AsyncMock(return_value=pipeline_return_value),
    )


# --- GET /recommendations/{farm_id} ---


async def test_get_recommendations_unauthenticated(async_client: AsyncClient):
    """Test that unauthenticated request to get recommendations is rejected."""
    response = await async_client.get("/recommendations/1")
    assert response.status_code == 401


async def test_get_recommendations_officer_own_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    """Test that officer can get recommendations for their own farm."""
    farm = Farm(**_FARM_DATA, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    _patch_dependencies(monkeypatch, [{**_MOCK_REC, "farm_id": farm.id}])

    response = await async_client.get(f"/recommendations/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    assert response.json()["farm_id"] == farm.id


async def test_get_recommendations_officer_other_farm_forbidden(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_admin_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    """Test that officer cannot get recommendations for another user's farm."""
    farm = Farm(**_FARM_DATA, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.get(f"/recommendations/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Farm not found or access denied"


async def test_get_recommendations_supervisor_any_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_supervisor_user: User,
    supervisor_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    """Test that supervisor can get recommendations for a farm belonging to another user."""
    farm = Farm(**_FARM_DATA, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    _patch_dependencies(monkeypatch, [{**_MOCK_REC, "farm_id": farm.id}])

    response = await async_client.get(f"/recommendations/{farm.id}", headers=supervisor_auth_headers)

    assert response.status_code == 200
    assert response.json()["farm_id"] == farm.id


async def test_get_recommendations_admin_any_farm(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    """Test that admin can get recommendations for a farm belonging to another user."""
    farm = Farm(**_FARM_DATA, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    _patch_dependencies(monkeypatch, [{**_MOCK_REC, "farm_id": farm.id}])

    response = await async_client.get(f"/recommendations/{farm.id}", headers=admin_auth_headers)

    assert response.status_code == 200
    assert response.json()["farm_id"] == farm.id


async def test_get_recommendations_farm_not_found(
    async_client: AsyncClient,
    test_officer_user: User,
    officer_auth_headers: dict,
):
    """Test that 404 is returned when the farm does not exist."""
    response = await async_client.get("/recommendations/999999", headers=officer_auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Farm not found or access denied"


async def test_get_recommendations_cache_hit(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    """Test that a cached result is returned from cache without calling the pipeline."""
    farm = Farm(**_FARM_DATA, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    cached_result = {**_MOCK_REC, "farm_id": farm.id}
    monkeypatch.setattr(rec_router.cache, "get", AsyncMock(return_value=json.dumps(cached_result)))

    mock_pipeline = AsyncMock()
    monkeypatch.setattr(rec_router.recommendation_service, "run_recommendation_pipeline", mock_pipeline)

    response = await async_client.get(f"/recommendations/{farm.id}", headers=officer_auth_headers)

    assert response.status_code == 200
    assert response.json()["farm_id"] == farm.id
    mock_pipeline.assert_not_called()


# --- POST /recommendations/batch ---


async def test_batch_recommendations_unauthenticated(async_client: AsyncClient):
    """Test that an unauthenticated batch request is rejected."""
    response = await async_client.post("/recommendations/batch", json=[1, 2])
    assert response.status_code == 401


async def test_batch_recommendations_officer_own_farms(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    """Test that officer can get batch recommendations for their own farms."""
    farm1 = Farm(**_FARM_DATA, user_id=test_officer_user.id)
    farm2 = Farm(**_FARM_DATA, user_id=test_officer_user.id)
    async_session.add_all([farm1, farm2])
    await async_session.commit()
    await async_session.refresh(farm1)
    await async_session.refresh(farm2)

    mock_results = [
        {**_MOCK_REC, "farm_id": farm1.id},
        {**_MOCK_REC, "farm_id": farm2.id},
    ]
    _patch_dependencies(monkeypatch, mock_results)

    response = await async_client.post(
        "/recommendations/batch",
        json=[farm1.id, farm2.id],
        headers=officer_auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


async def test_batch_recommendations_officer_other_farms_forbidden(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_admin_user: User,
    officer_auth_headers: dict,
    setup_soil_texture,
):
    """Test that officer cannot get batch recommendations for another user's farms."""
    farm = Farm(**_FARM_DATA, user_id=test_admin_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    response = await async_client.post(
        "/recommendations/batch",
        json=[farm.id],
        headers=officer_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No valid farms found"


async def test_batch_recommendations_supervisor_any_farms(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_supervisor_user: User,
    supervisor_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    """Test that supervisor can get batch recommendations for a farm belonging to another user."""
    farm = Farm(**_FARM_DATA, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    _patch_dependencies(monkeypatch, [{**_MOCK_REC, "farm_id": farm.id}])

    response = await async_client.post(
        "/recommendations/batch",
        json=[farm.id],
        headers=supervisor_auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_batch_recommendations_admin_any_farms(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_officer_user: User,
    test_admin_user: User,
    admin_auth_headers: dict,
    setup_soil_texture,
    monkeypatch,
):
    """Test that admin can get batch recommendations for a farm belonging to another user."""
    farm = Farm(**_FARM_DATA, user_id=test_officer_user.id)
    async_session.add(farm)
    await async_session.commit()
    await async_session.refresh(farm)

    _patch_dependencies(monkeypatch, [{**_MOCK_REC, "farm_id": farm.id}])

    response = await async_client.post(
        "/recommendations/batch",
        json=[farm.id],
        headers=admin_auth_headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


async def test_batch_recommendations_no_valid_farms(
    async_client: AsyncClient,
    test_officer_user: User,
    officer_auth_headers: dict,
):
    """Test that 404 is returned when none of the requested farm IDs exist."""
    response = await async_client.post(
        "/recommendations/batch",
        json=[999998, 999999],
        headers=officer_auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No valid farms found"

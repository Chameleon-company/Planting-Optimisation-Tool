from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_cache_miss(async_client, officer_auth_headers):
    payload = {
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    mock_result = {
        "farm_count": 5,
        "results": [{"aligned_count": 80, "pre_slope_count": 100} for _ in range(5)],
    }

    with patch(
        "src.routers.sapling_estimation.SaplingBatchEstimationService.run_batch_estimation",
        new=AsyncMock(return_value=mock_result),
    ) as mock_run_batch_estimation:
        response = await async_client.post(
            "/sapling_estimation/batch_calculate",
            json=payload,
            headers=officer_auth_headers,
        )

    assert response.status_code == 200
    data = response.json()

    assert data["farm_count"] == 5
    assert len(data["results"]) == 5
    assert mock_run_batch_estimation.await_count == 1


@pytest.mark.asyncio
async def test_cache_hit(async_client, officer_auth_headers):
    payload = {
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    mock_cache = {
        "farm_count": 5,
        "results": [{"aligned_count": 80, "pre_slope_count": 100} for _ in range(5)],
    }

    with patch(
        "src.routers.sapling_estimation.SaplingBatchEstimationService.run_batch_estimation",
        new=AsyncMock(return_value=mock_cache),
    ) as mock_run_batch_estimation:
        response = await async_client.post(
            "/sapling_estimation/batch_calculate",
            json=payload,
            headers=officer_auth_headers,
        )

    assert response.status_code == 200
    data = response.json()

    assert data["farm_count"] == 5
    assert data["results"][0]["aligned_count"] == 80
    assert data["results"][1]["aligned_count"] == 80
    assert mock_run_batch_estimation.await_count == 1

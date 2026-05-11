from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_service_request(async_client, officer_auth_headers):
    payload = {
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    mock_result = {
        "status": "success",
        "farm_count": 5,
        "results": [{"farm_id": i, "status": "success", "aligned_count": 80, "pre_slope_count": 100} for i in range(1, 6)],
    }

    with patch(
        "src.services.batch_estimation.SaplingBatchEstimationService.run_batch_estimation",
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
async def test_service_return(async_client, officer_auth_headers):
    payload = {
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    mock_cache = {
        "status": "success",
        "farm_count": 5,
        "results": [{"farm_id": i, "status": "success", "aligned_count": 80, "pre_slope_count": 100} for i in range(1, 6)],
    }

    with patch(
        "src.services.batch_estimation.SaplingBatchEstimationService.run_batch_estimation",
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

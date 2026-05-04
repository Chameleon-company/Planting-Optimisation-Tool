import pytest

from src.models.global_weights import GlobalWeightsRun


@pytest.mark.asyncio
async def test_list_global_weight_runs(
    async_client,
    async_session,
    admin_auth_headers,
):
    """Test listing all global weight runs."""
    unique_hash = "unique_abc_123"
    # Arrange
    run = GlobalWeightsRun(
        dataset_hash=unique_hash,
        bootstraps=100,
        bootstrap_early_stopped=True,
        source="test source",
    )
    async_session.add(run)
    await async_session.commit()

    # Act
    response = await async_client.get(
        "/global-weights/runs",
        headers=admin_auth_headers,
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    target_run = next((item for item in data if item["run_id"] == str(run.id)), None)
    assert target_run is not None, f"Run with ID {run.id} not found in response"
    assert target_run["bootstraps"] == 100
    assert target_run["bootstrap_early_stopped"] is True
    assert target_run["source"] == "test source"

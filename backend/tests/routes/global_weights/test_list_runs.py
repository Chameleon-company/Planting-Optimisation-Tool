import pytest

from src.models.global_weights import GlobalWeightsRun


@pytest.mark.asyncio
async def test_list_global_weight_runs(
    async_client,
    async_session,
    admin_auth_headers,
):
    """Test listing all global weight runs."""
    # Arrange
    run = GlobalWeightsRun(
        dataset_hash="abc",
        rf_bootstraps=100,
        rf_early_stopped=True,
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
    assert len(data) == 1
    assert data[0]["rf_bootstraps"] == 100
    assert data[0]["rf_early_stopped"] is True
    assert data[0]["source"] == "test source"

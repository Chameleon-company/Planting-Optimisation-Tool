from uuid import uuid4

import pytest

from src.models.global_weights import GlobalWeights, GlobalWeightsRun


@pytest.mark.asyncio
async def test_get_global_weight_run_detail(
    async_client,
    async_session,
    admin_auth_headers,
):
    """Test retrieving details of a global weight run."""
    # Arrange
    run = GlobalWeightsRun(
        dataset_hash="hash",
        bootstraps=50,
        bootstrap_early_stopped=False,
        source="test source",
    )
    async_session.add(run)
    await async_session.flush()

    async_session.add(
        GlobalWeights(
            run_id=run.id,
            feature="ph",
            mean_weight=0.11,
            ci_lower=0.0,
            ci_upper=0.25,
            ci_width=0.25,
            touches_zero=True,
        )
    )
    await async_session.commit()

    # Act
    response = await async_client.get(
        f"/global-weights/runs/{run.id}",
        headers=admin_auth_headers,
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()

    assert payload["run_id"] == str(run.id)
    assert payload["bootstraps"] == 50
    assert payload["source"] == "test source"
    assert len(payload["weights"]) == 1
    assert payload["weights"][0]["feature"] == "ph"


@pytest.mark.asyncio
async def test_get_global_weight_run_not_found(
    async_client,
    admin_auth_headers,
):
    """Test retrieving a non-existent global weight run."""
    non_existent_id = uuid4()

    response = await async_client.get(
        f"/global-weights/runs/{non_existent_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Global weight run not found"}

import pytest
from sqlalchemy import select

from src.models.global_weights import GlobalWeights, GlobalWeightsRun


@pytest.mark.asyncio
async def test_delete_global_weight_run(
    async_client,
    async_session,
    admin_auth_headers,
):
    """Test deleting a global weight run and its associated weights."""
    # Arrange
    run = GlobalWeightsRun(
        dataset_hash="hash",
        bootstraps=10,
        bootstrap_early_stopped=True,
        source="test",
    )
    async_session.add(run)
    await async_session.flush()

    weight = GlobalWeights(
        run_id=run.id,
        feature="ph",
        mean_weight=0.1,
        ci_lower=0.0,
        ci_upper=0.2,
        ci_width=0.2,
        touches_zero=True,
    )
    async_session.add(weight)
    await async_session.commit()

    # Act
    resp = await async_client.delete(
        f"/global-weights/runs/{run.id}",
        headers=admin_auth_headers,
    )

    # Assert
    assert resp.status_code == 204

    result = await async_session.execute(select(GlobalWeights).where(GlobalWeights.run_id == run.id))
    remaining = result.scalars().all()
    assert remaining == []

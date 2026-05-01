from uuid import uuid4

import pytest
from sqlalchemy import select

from src.models.global_weights import GlobalWeights, GlobalWeightsRun


@pytest.mark.asyncio
async def test_delete_global_weight_run_cascades(async_session):
    """Test that deleting a global weight run also deletes its associated weights."""
    run = GlobalWeightsRun(
        dataset_hash="hash",
        bootstraps=50,
        bootstrap_early_stopped=False,
    )
    async_session.add(run)
    await async_session.flush()

    async_session.add(
        GlobalWeights(
            run_id=run.id,
            feature="ph",
            mean_weight=0.10,
            ci_lower=0.0,
            ci_upper=0.20,
            ci_width=0.20,
            touches_zero=True,
        )
    )
    await async_session.commit()

    await async_session.delete(run)
    await async_session.commit()

    remaining = (await async_session.execute(select(GlobalWeights))).scalars().all()

    assert remaining == []


@pytest.mark.asyncio
async def test_delete_global_weight_run_not_found(
    async_client,
    admin_auth_headers,
):
    """Test deleting a non-existent global weight run."""
    non_existent_id = uuid4()

    response = await async_client.delete(
        f"/global-weights/runs/{non_existent_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Global weight run not found"}

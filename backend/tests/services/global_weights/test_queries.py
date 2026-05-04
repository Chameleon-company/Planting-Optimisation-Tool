import pytest
from sqlalchemy import delete
from src.models.global_weights import GlobalWeights, GlobalWeightsRun
from src.services.global_weights import get_latest_global_weights


@pytest.mark.asyncio
async def test_get_latest_global_weights(async_session):
    """Test retrieving the latest global weights."""
    run = GlobalWeightsRun(
        dataset_hash="hash",
        bootstraps=100,
        bootstrap_early_stopped=True,
        source="test",
    )
    async_session.add(run)
    await async_session.flush()

    async_session.add_all(
        [
            GlobalWeights(
                run_id=run.id,
                feature="ph",
                mean_weight=0.11,
                ci_lower=0.0,
                ci_upper=0.25,
                ci_width=0.25,
                touches_zero=True,
            ),
            GlobalWeights(
                run_id=run.id,
                feature="soil_texture",
                mean_weight=0.19,
                ci_lower=0.07,
                ci_upper=0.41,
                ci_width=0.34,
                touches_zero=False,
            ),
        ]
    )
    await async_session.commit()

    weights = await get_latest_global_weights(async_session)

    assert weights == {
        "ph": 0.11,
        "soil_texture": 0.19,
    }


@pytest.mark.asyncio
async def test_get_latest_global_weights_no_run(async_session):
    """
    Test that get_latest_global_weights returns None
    when the database has no GlobalWeightsRun records.
    """
    # Delete all runs in this transaction only
    await async_session.execute(delete(GlobalWeightsRun))
    await async_session.flush()  # Send the delete to the DB

    # Query the clean, empty test database
    result = await get_latest_global_weights(db=async_session)

    # It should hit the `if not run:` block and return None
    assert result is None

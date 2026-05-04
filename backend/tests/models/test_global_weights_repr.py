from datetime import datetime

from src.models.global_weights import GlobalWeights, GlobalWeightsRun


def test_global_weights_repr():
    """Test the __repr__ method of GlobalWeights."""
    weight = GlobalWeights(
        id=1,
        run_id=None,  # not needed for repr
        feature="ph",
        mean_weight=0.42,
        ci_lower=0.1,
        ci_upper=0.8,
        ci_width=0.7,
        touches_zero=False,
    )

    result = repr(weight)

    assert "GlobalWeights(" in result
    assert "feature='ph'" in result
    assert "mean_weight=0.42" in result


def test_global_weights_run_repr():
    """Test the __repr__ method of GlobalWeightsRun."""
    created_at = datetime(2024, 1, 1, 12, 0)

    run = GlobalWeightsRun(
        id="00000000-0000-0000-0000-000000000000",
        dataset_hash="test-hash",
        bootstraps=100,
        bootstrap_early_stopped=True,
        source="unit test",
    )

    run.created_at = created_at  # normally set by DB

    result = repr(run)

    assert "GlobalWeightsRun(" in result
    assert "dataset_hash='test-hash'" in result

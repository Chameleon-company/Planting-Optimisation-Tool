import io

import pytest

from src.models.global_weights import GlobalWeights, GlobalWeightsRun
from src.services.global_weights import import_global_weights_from_csv, parse_global_weights_csv


def test_parse_global_weights_csv_valid():
    """Test parsing a valid global weights CSV."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper,rf_bootstraps,rf_early_stopped
__META__,,,,120,true
ph,0.11,0.00,0.25,,
soil_texture,0.19,0.07,0.41,,
"""
    meta, rows = parse_global_weights_csv(io.StringIO(csv_data))

    assert meta.rf_bootstraps == 120
    assert meta.rf_early_stopped is True

    assert len(rows) == 2
    assert rows[0].feature == "ph"
    assert rows[0].mean_weight == pytest.approx(0.11)


def test_parse_global_weights_csv_missing_meta_raises():
    """Test that parsing a CSV without a META row raises an error."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper
ph,0.11,0.00,0.25
"""
    with pytest.raises(ValueError, match="CSV is missing required __META__ row"):
        parse_global_weights_csv(io.StringIO(csv_data))


@pytest.mark.asyncio
async def test_import_global_weights_from_csv(async_session):
    """Test importing global weights from a CSV file."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper,rf_bootstraps,rf_early_stopped
__META__,,,,150,true
ph,0.11,0.00,0.25,,
soil_texture,0.19,0.07,0.41,,
"""

    run_id = await import_global_weights_from_csv(
        db=async_session,
        csv_file=io.StringIO(csv_data),
        dataset_hash="unit-test",
    )

    run = await async_session.get(GlobalWeightsRun, run_id)
    assert run is not None
    assert run.rf_bootstraps == 150
    assert run.rf_early_stopped is True

    result = await async_session.execute(GlobalWeights.__table__.select().where(GlobalWeights.run_id == run_id))
    weights = result.fetchall()

    assert len(weights) == 2


def test_parse_global_weights_csv_missing_rf_bootstraps():
    """Test that parsing a CSV with missing rf_bootstraps in META row raises an error."""
    # rf_bootstraps is empty
    csv_data = """feature,mean_weight,ci_lower,ci_upper,rf_bootstraps,rf_early_stopped
__META__,,,,,true
ph,0.11,0.0,0.25,,
"""

    with pytest.raises(ValueError, match="META row must define rf_bootstraps and rf_early_stopped"):
        parse_global_weights_csv(io.StringIO(csv_data))


def test_parse_global_weights_csv_missing_rf_early_stopped():
    """Test that parsing a CSV with missing rf_early_stopped in META row raises an error."""
    # rf_early_stopped is empty
    csv_data = """feature,mean_weight,ci_lower,ci_upper,rf_bootstraps,rf_early_stopped
__META__,,,,120,
ph,0.11,0.0,0.25,,
"""

    with pytest.raises(ValueError, match="META row must define rf_bootstraps and rf_early_stopped"):
        parse_global_weights_csv(io.StringIO(csv_data))


def test_parse_global_weights_csv_missing_both_meta_fields():
    """Test that parsing a CSV with missing rf_bootstraps and rf_early_stopped in META row raises an error."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper,rf_bootstraps,rf_early_stopped
__META__,,,,,
ph,0.11,0.0,0.25,,
"""

    with pytest.raises(ValueError, match="META row must define rf_bootstraps and rf_early_stopped"):
        parse_global_weights_csv(io.StringIO(csv_data))

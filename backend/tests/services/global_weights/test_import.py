import io

import pytest

from src.models.global_weights import GlobalWeights, GlobalWeightsRun
from src.services.global_weights import GlobalWeightsCSVError, import_global_weights_from_csv, parse_global_weights_csv


def test_parse_global_weights_csv_valid():
    """Test parsing a valid global weights CSV."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,120,true
ph,0.11,0.00,0.25,,
soil_texture,0.19,0.07,0.41,,
elevation_m,0.20,0.10,0.30,,
rainfall_mm,0.30,0.15,0.45,,
temperature_celsius,0.20,0.10,0.30,,
"""
    meta, rows = parse_global_weights_csv(io.StringIO(csv_data))

    assert meta.bootstraps == 120
    assert meta.bootstrap_early_stopped is True

    assert len(rows) == 5
    assert rows[0].feature == "ph"
    assert rows[0].mean_weight == pytest.approx(0.11)


@pytest.mark.asyncio
async def test_import_global_weights_from_csv(async_session):
    """Test importing global weights from a CSV file."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,150,true
ph,0.11,0.00,0.25,,
soil_texture,0.19,0.07,0.41,,
elevation_m,0.20,0.10,0.30,,
rainfall_mm,0.30,0.15,0.45,,
temperature_celsius,0.20,0.10,0.30,,
"""

    run_id = await import_global_weights_from_csv(
        db=async_session,
        csv_file=io.StringIO(csv_data),
        dataset_hash="unit-test",
    )

    run = await async_session.get(GlobalWeightsRun, run_id)
    assert run is not None
    assert run.bootstraps == 150
    assert run.bootstrap_early_stopped is True

    result = await async_session.execute(GlobalWeights.__table__.select().where(GlobalWeights.run_id == run_id))
    weights = result.fetchall()

    assert len(weights) == 5


def test_parse_global_weights_csv_missing_meta_raises():
    """Test that parsing a CSV without a META row raises an error."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper
ph,0.11,0.00,0.25
"""
    with pytest.raises(GlobalWeightsCSVError, match="CSV is missing required __META__ row"):
        parse_global_weights_csv(io.StringIO(csv_data))


def test_parse_global_weights_csv_missing_bootstraps():
    """Test that parsing a CSV with missing bootstraps in META row raises an error."""
    # bootstraps is empty
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,,true
ph,0.11,0.0,0.25,,
"""

    with pytest.raises(GlobalWeightsCSVError, match="META row must define bootstraps and bootstrap_early_stopped"):
        parse_global_weights_csv(io.StringIO(csv_data))


def test_parse_global_weights_csv_missing_bootstrap_early_stopped():
    """Test that parsing a CSV with missing bootstrap_early_stopped in META row raises an error."""
    # bootstrap_early_stopped is empty
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,120,
ph,0.11,0.0,0.25,,
"""

    with pytest.raises(GlobalWeightsCSVError, match="META row must define bootstraps and bootstrap_early_stopped"):
        parse_global_weights_csv(io.StringIO(csv_data))


def test_parse_global_weights_csv_missing_both_meta_fields():
    """Test that parsing a CSV with missing bootstraps and bootstrap_early_stopped in META row raises an error."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,,
ph,0.11,0.0,0.25,,
"""

    with pytest.raises(GlobalWeightsCSVError, match="META row must define bootstraps and bootstrap_early_stopped"):
        parse_global_weights_csv(io.StringIO(csv_data))


def test_parse_global_weights_csv_pydantic_validation_error():
    """Test that violating Pydantic validation rules throws a formatted row error."""
    # Here, ci_lower (0.50) is greater than mean_weight (0.11),
    # which violates the validate_ci_order @model_validator.
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,120,true
ph,0.11,0.50,0.25,,
soil_texture,0.19,0.07,0.41,,
elevation_m,0.20,0.10,0.30,,
rainfall_mm,0.30,0.15,0.45,,
temperature_celsius,0.20,0.10,0.30,,
"""
    # Note the escaped parentheses \(ph\)
    expected_error = r"Row 2 ph: Expected ci_lower ≤ mean_weight ≤ ci_upper"

    with pytest.raises(GlobalWeightsCSVError, match=expected_error):
        parse_global_weights_csv(io.StringIO(csv_data))


def test_parse_global_weights_csv_invalid_numbers():
    """Test that passing text into float columns throws a formatted row error."""
    # Here, we put the word "invalid" instead of a number for mean_weight.
    # This will cause float("invalid") to raise a standard ValueError.
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,120,true
ph,invalid,0.00,0.25,,
soil_texture,0.19,0.07,0.41,,
elevation_m,0.20,0.10,0.30,,
rainfall_mm,0.30,0.15,0.45,,
temperature_celsius,0.20,0.10,0.30,,
"""
    expected_error = r"Row 2 ph: contains invalid numbers."

    with pytest.raises(GlobalWeightsCSVError, match=expected_error):
        parse_global_weights_csv(io.StringIO(csv_data))


def test_parse_global_weights_csv_missing_config_features():
    """Test that omitting a required feature from the config throws an error."""
    # This CSV is perfectly formatted, but we are intentionally leaving out 'temperature_celsius'
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,120,true
ph,0.11,0.00,0.25,,
soil_texture,0.19,0.07,0.41,,
elevation_m,0.20,0.10,0.30,,
rainfall_mm,0.30,0.15,0.45,,
"""
    expected_error = r"CSV is missing required features: temperature_celsius"

    with pytest.raises(GlobalWeightsCSVError, match=expected_error):
        parse_global_weights_csv(io.StringIO(csv_data))

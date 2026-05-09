import io
from uuid import uuid4

import pytest
from sqlalchemy import delete, select

from src.models.global_weights import GlobalWeights, GlobalWeightsRun
from src.services.global_weights import GlobalWeightsCSVError, get_latest_global_weights, import_global_weights_from_csv, parse_global_weights_csv


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

    weight = GlobalWeights(
        run_id=run.id,
        feature="ph",
        mean_weight=0.10,
        ci_lower=0.0,
        ci_upper=0.20,
        ci_width=0.20,
        touches_zero=True,
    )
    async_session.add(weight)
    await async_session.commit()

    await async_session.delete(run)
    await async_session.commit()

    result = await async_session.execute(select(GlobalWeights).where(GlobalWeights.run_id == run.id))
    remaining = result.scalars().all()

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


@pytest.mark.asyncio
async def test_parse_global_weights_csv_empty_file():
    """Test that an empty CSV file raises a clear error."""
    csv_data = ""

    with pytest.raises(
        GlobalWeightsCSVError,
        match="CSV file is empty or missing a header row",
    ):
        parse_global_weights_csv(io.StringIO(csv_data))


@pytest.mark.asyncio
async def test_parse_global_weights_csv_wrong_headers():
    """Test that missing required headers raises an error."""
    csv_data = """feature,mean_weight
__META__,
ph,0.11
"""

    with pytest.raises(
        GlobalWeightsCSVError,
        match=r"CSV is missing required columns: .*ci_lower.*ci_upper",
    ):
        parse_global_weights_csv(io.StringIO(csv_data))


@pytest.mark.asyncio
async def test_parse_global_weights_csv_unknown_feature():
    """Test that unknown features not defined in config are rejected."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,120,true
ph,0.11,0.00,0.25,,
unknown_feature,0.20,0.10,0.30,,
soil_texture,0.19,0.07,0.41,,
elevation_m,0.20,0.10,0.30,,
rainfall_mm,0.30,0.15,0.45,,
temperature_celsius,0.20,0.10,0.30,,
"""

    with pytest.raises(
        GlobalWeightsCSVError,
        match=r"Row 3 has unknown feature: 'unknown_feature'",
    ):
        parse_global_weights_csv(io.StringIO(csv_data))


@pytest.mark.asyncio
async def test_parse_global_weights_csv_invalid_bootstrap_early_stopped_value():
    """Test that invalid bootstrap_early_stopped values are rejected."""
    csv_data = """feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,120,maybe
ph,0.11,0.00,0.25,,
soil_texture,0.19,0.07,0.41,,
elevation_m,0.20,0.10,0.30,,
rainfall_mm,0.30,0.15,0.45,,
temperature_celsius,0.20,0.10,0.30,,
"""

    with pytest.raises(
        GlobalWeightsCSVError,
        match="bootstrap_early_stopped must be 'true' or 'false'",
    ):
        parse_global_weights_csv(io.StringIO(csv_data))

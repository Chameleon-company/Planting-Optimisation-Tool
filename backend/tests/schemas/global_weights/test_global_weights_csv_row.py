import pytest
from pydantic import ValidationError

from src.schemas.global_weights import GlobalWeightsCSVRow


def test_global_weights_csv_row_valid():
    """Test creating a valid GlobalWeightsCSVRow."""
    row = GlobalWeightsCSVRow(
        feature="ph",
        mean_weight=0.5,
        ci_lower=0.2,
        ci_upper=0.8,
    )

    assert row.feature == "ph"
    assert row.mean_weight == 0.5


def test_global_weights_csv_row_invalid_ci_order():
    """Test that ci_lower must be less than or equal to ci_upper."""
    with pytest.raises(ValidationError) as exc:
        GlobalWeightsCSVRow(
            feature="soil_texture",
            mean_weight=0.9,
            ci_lower=0.0,
            ci_upper=0.5,
        )

    assert "Expected ci_lower" in str(exc.value)


def test_global_weights_csv_row_blank_feature():
    """Test that feature name must not be blank."""
    with pytest.raises(ValidationError) as exc:
        GlobalWeightsCSVRow(
            feature="   ",
            mean_weight=0.3,
            ci_lower=0.1,
            ci_upper=0.5,
        )

    assert "Feature name must not be empty" in str(exc.value)


def test_global_weights_csv_row_ci_equal_bounds():
    """Test that ci_lower and ci_upper can be equal."""
    row = GlobalWeightsCSVRow(
        feature="rainfall",
        mean_weight=0.3,
        ci_lower=0.3,
        ci_upper=0.3,
    )

    assert row.mean_weight == 0.3

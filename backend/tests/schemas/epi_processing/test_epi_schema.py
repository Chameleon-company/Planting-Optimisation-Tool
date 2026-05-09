import pytest
from pydantic import ValidationError

from src.schemas.epi import EpiInputRow


def test_epi_input_row_valid():
    """Test that valid data passes validation."""
    data = {"farm_id": 1, "species_id": 42, "farm_mean_epi": 0.75}
    row = EpiInputRow(**data)

    assert row.farm_id == 1
    assert row.species_id == 42
    assert row.farm_mean_epi == 0.75


def test_epi_input_row_invalid_farm_id():
    """Test that farm_id < 1 raises an error."""
    with pytest.raises(ValidationError) as exc_info:
        EpiInputRow(farm_id=0, species_id=42, farm_mean_epi=0.75)

    assert "Input should be greater than or equal to 1" in str(exc_info.value)


def test_epi_input_row_invalid_epi_value():
    """Test that a negative EPI value raises an error."""
    with pytest.raises(ValidationError) as exc_info:
        EpiInputRow(farm_id=1, species_id=42, farm_mean_epi=-0.1)

    assert "Input should be greater than or equal to 0" in str(exc_info.value)

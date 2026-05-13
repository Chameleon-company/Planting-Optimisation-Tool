from unittest.mock import ANY, AsyncMock, Mock, patch

import pandas as pd
import pytest

from src.services.epi_processing import EpiCSVError, process_epi_csv, validate_epi_dataframe


def test_validate_epi_dataframe_missing_columns():
    """Test that missing columns trigger the custom EpiCSVError."""
    # Missing 'farm_mean_epi'
    df = pd.DataFrame({"farm_id": [1], "species_id": [1]})

    with pytest.raises(EpiCSVError) as exc_info:
        validate_epi_dataframe(df)

    assert "Missing required columns" in str(exc_info.value)


def test_validate_epi_dataframe_invalid_rows():
    """Test that schema validation errors are caught and aggregated."""
    # farm_id = 0 is invalid
    df = pd.DataFrame({"farm_id": [0], "species_id": [1], "farm_mean_epi": [0.5]})

    with pytest.raises(EpiCSVError) as exc_info:
        validate_epi_dataframe(df)

    assert "Invalid EPI CSV data" in str(exc_info.value)
    assert "Row 1" in str(exc_info.value)


@patch("src.services.epi_processing.get_species_by_ids", new_callable=AsyncMock)
@patch("src.services.epi_processing.get_farm_by_id", new_callable=AsyncMock)
@patch("src.services.epi_processing.get_raw_scores", new_callable=AsyncMock)
async def test_process_epi_csv_success(mock_get_raw_scores, mock_get_farm, mock_get_species):
    """Test the full CSV processing flow with a mocked DB and service."""

    # Make the validation pass by returning mock objects with the correct IDs
    mock_get_farm.return_value = [Mock(id=1)]
    mock_get_species.return_value = [Mock(id=10)]

    mock_get_raw_scores.return_value = [{"farm_id": 1, "species_id": 10, "raw_score": 0.85}]

    input_csv = b"farm_id,species_id,farm_mean_epi\n1,10,0.75"
    mock_db = AsyncMock()

    result_bytes = await process_epi_csv(db=mock_db, csv_bytes=input_csv)
    result_text = result_bytes.decode("utf-8")

    assert "farm_id,species_id,farm_mean_epi,raw_score" in result_text
    assert "1,10,0.75,0.85" in result_text

    # Ensure get_raw_scores was called with the correct unique lists
    mock_get_raw_scores.assert_called_once_with(db=mock_db, farm_id_list=[1], cfg=ANY, target_species_ids=[10])


@patch("src.services.epi_processing.get_species_by_ids", new_callable=AsyncMock)
@patch("src.services.epi_processing.get_farm_by_id", new_callable=AsyncMock)
async def test_process_epi_csv_database_validation_failure(mock_get_farm, mock_get_species):
    """Test that missing database IDs trigger an EpiCSVError before scoring begins."""

    # Make the database mocks return empty lists (no records found)
    mock_get_farm.return_value = []
    mock_get_species.return_value = []

    # Provide a CSV with IDs that don't exist
    input_csv = b"farm_id,species_id,farm_mean_epi\n99,105,0.75"
    mock_db = AsyncMock()

    # Ensure the custom exception is raised
    with pytest.raises(EpiCSVError) as exc_info:
        await process_epi_csv(db=mock_db, csv_bytes=input_csv)

    # Assert the error message contains the exact missing IDs
    error_msg = str(exc_info.value)
    assert "Database validation failed" in error_msg
    assert "Farm IDs not found: [99]" in error_msg
    assert "Species IDs not found: [105]" in error_msg

    # Ensure our database functions were actually called with the IDs from the CSV
    mock_get_farm.assert_called_once_with(mock_db, [99])
    mock_get_species.assert_called_once_with(mock_db, [105])


async def test_process_epi_csv_invalid_csv_raises_error():
    # Unterminated quote causes pandas ParserError
    bad_csv = b'farm_id,species_id,farm_mean_epi\n1,2,"0.85'

    with pytest.raises(EpiCSVError) as excinfo:
        await process_epi_csv(
            db=None,  # Safe: error occurs before DB usage
            csv_bytes=bad_csv,
        )

    assert "Error reading EPI CSV" in str(excinfo.value)

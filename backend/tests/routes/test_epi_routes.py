from unittest.mock import AsyncMock, patch

from src.services.epi_processing import EpiCSVError


@patch("src.routers.global_weights.process_epi_csv", new_callable=AsyncMock)
async def test_upload_epi_csv_success(
    mock_process_csv,
    async_client,
    admin_auth_headers,
):
    """Test that a valid CSV upload returns 200 and a file."""

    # Mock the service to just return some dummy bytes
    mock_process_csv.return_value = b"farm_id,species_id,farm_mean_epi,raw_score\n1,10,0.5,0.85"

    csv_content = b"farm_id,species_id,farm_mean_epi\n1,10,0.5"
    files = {"file": ("test_epi.csv", csv_content, "text/csv")}

    # Send the request
    response = await async_client.post("/global-weights/epi-add-scores", files=files, headers=admin_auth_headers)

    assert response.status_code == 200
    assert response.content == mock_process_csv.return_value


@patch("src.routers.global_weights.process_epi_csv", new_callable=AsyncMock)
async def test_upload_epi_csv_validation_failure(mock_process_csv, async_client, admin_auth_headers):
    """Test that the custom exception handler catches EpiCSVError and returns 400."""

    # Force the mocked service to raise the custom error
    mock_process_csv.side_effect = EpiCSVError("Invalid EPI CSV data:\nRow 1: Input should be >= 1")

    csv_content = b"farm_id,species_id,farm_mean_epi\n0,10,0.5"  # Invalid farm_id
    files = {"file": ("test_epi.csv", csv_content, "text/csv")}

    response = await async_client.post("/global-weights/epi-add-scores", files=files, headers=admin_auth_headers)

    assert response.status_code == 400

    response_data = response.json()
    assert "detail" in response_data
    assert "Invalid EPI CSV data" in response_data["detail"]


async def test_score_epi_csv_invalid_file_extension(
    async_client,
    admin_auth_headers,
):
    """Test that uploading a file without a .csv extension raises a 400 error."""
    # Create a fake text file instead of a CSV
    file_content = b"just some text content"
    files = {"file": ("test_data.txt", file_content, "text/plain")}

    response = await async_client.post(
        "/global-weights/epi-add-scores",
        headers=admin_auth_headers,
        files=files,
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "File must be a CSV"}


# RBAC Tests for /global-weights/epi-add-scores
async def test_upload_epi_csv_unauthenticated(async_client):
    """Test that unauthenticated request to EPI upload is rejected (401)."""
    response = await async_client.post("/global-weights/epi-add-scores")
    assert response.status_code == 401


async def test_upload_epi_csv_officer_forbidden(async_client, officer_auth_headers):
    """Test that an officer cannot access EPI upload (403)."""
    # We don't need a real file because the 403 should trigger before file processing
    response = await async_client.post("/global-weights/epi-add-scores", headers=officer_auth_headers)
    assert response.status_code == 403


async def test_upload_epi_csv_supervisor_forbidden(async_client, supervisor_auth_headers):
    """Test that a supervisor cannot access EPI upload (403)."""
    # We don't need a real file because the 403 should trigger before file processing
    response = await async_client.post("/global-weights/epi-add-scores", headers=supervisor_auth_headers)
    assert response.status_code == 403

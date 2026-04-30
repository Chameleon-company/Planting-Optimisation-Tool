import pytest


@pytest.mark.asyncio
async def test_import_global_weights_csv(
    async_client,
    admin_auth_headers,
):
    """Test importing global weights from a CSV file."""
    csv_bytes = b"""feature,mean_weight,ci_lower,ci_upper,rf_bootstraps,rf_early_stopped
__META__,,,,120,true
ph,0.11,0.0,0.25,,
soil_texture,0.19,0.07,0.41,,
"""

    files = {"file": ("weights.csv", csv_bytes, "text/csv")}

    response = await async_client.post(
        "/global-weights/import",
        files=files,
        headers=admin_auth_headers,
    )

    assert response.status_code == 201
    body = response.json()
    assert "run_id" in body

import pytest


@pytest.mark.asyncio
async def test_import_global_weights_csv(
    async_client,
    admin_auth_headers,
):
    """Test importing global weights from a CSV file."""
    csv_bytes = b"""feature,mean_weight,ci_lower,ci_upper,bootstraps,bootstrap_early_stopped
__META__,,,,120,true
ph,0.11,0.00,0.25,,
soil_texture,0.19,0.07,0.41,,
elevation_m,0.20,0.10,0.30,,
rainfall_mm,0.30,0.15,0.45,,
temperature_celsius,0.20,0.10,0.30,,
"""

    files = {"file": ("weights.csv", csv_bytes, "text/csv")}

    response = await async_client.post(
        "/global-weights/import",
        files=files,
        headers=admin_auth_headers,
    )

    print(response)
    assert response.status_code == 201
    body = response.json()
    assert "run_id" in body

from uuid import uuid4

from sqlalchemy import select

from src.models.global_weights import GlobalWeights, GlobalWeightsRun


async def test_delete_global_weight_run(
    async_client,
    async_session,
    admin_auth_headers,
):
    """Test deleting a global weight run and its associated weights."""
    # Arrange
    run = GlobalWeightsRun(
        dataset_hash="hash",
        bootstraps=10,
        bootstrap_early_stopped=True,
        source="test",
    )
    async_session.add(run)
    await async_session.flush()

    weight = GlobalWeights(
        run_id=run.id,
        feature="ph",
        mean_weight=0.1,
        ci_lower=0.0,
        ci_upper=0.2,
        ci_width=0.2,
        touches_zero=True,
    )
    async_session.add(weight)
    await async_session.commit()

    # Act
    resp = await async_client.delete(
        f"/global-weights/runs/{run.id}",
        headers=admin_auth_headers,
    )

    # Assert
    assert resp.status_code == 204

    result = await async_session.execute(select(GlobalWeights).where(GlobalWeights.run_id == run.id))
    remaining = result.scalars().all()
    assert remaining == []


async def test_get_global_weight_run_detail(
    async_client,
    async_session,
    admin_auth_headers,
):
    """Test retrieving details of a global weight run."""
    # Arrange
    run = GlobalWeightsRun(
        dataset_hash="hash",
        bootstraps=50,
        bootstrap_early_stopped=False,
        source="test source",
    )
    async_session.add(run)
    await async_session.flush()

    async_session.add(
        GlobalWeights(
            run_id=run.id,
            feature="ph",
            mean_weight=0.11,
            ci_lower=0.0,
            ci_upper=0.25,
            ci_width=0.25,
            touches_zero=True,
        )
    )
    await async_session.commit()

    # Act
    response = await async_client.get(
        f"/global-weights/runs/{run.id}",
        headers=admin_auth_headers,
    )

    # Assert
    assert response.status_code == 200
    payload = response.json()

    assert payload["run_id"] == str(run.id)
    assert payload["bootstraps"] == 50
    assert payload["source"] == "test source"
    assert len(payload["weights"]) == 1
    assert payload["weights"][0]["feature"] == "ph"


async def test_get_global_weight_run_not_found(
    async_client,
    admin_auth_headers,
):
    """Test retrieving a non-existent global weight run."""
    non_existent_id = uuid4()

    response = await async_client.get(
        f"/global-weights/runs/{non_existent_id}",
        headers=admin_auth_headers,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Global weight run not found"}


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


async def test_list_global_weight_runs(
    async_client,
    async_session,
    admin_auth_headers,
):
    """Test listing all global weight runs."""
    unique_hash = "unique_abc_123"
    # Arrange
    run = GlobalWeightsRun(
        dataset_hash=unique_hash,
        bootstraps=100,
        bootstrap_early_stopped=True,
        source="test source",
    )
    async_session.add(run)
    await async_session.commit()

    # Act
    response = await async_client.get(
        "/global-weights/runs",
        headers=admin_auth_headers,
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1

    target_run = next((item for item in data if item["run_id"] == str(run.id)), None)
    assert target_run is not None, f"Run with ID {run.id} not found in response"
    assert target_run["bootstraps"] == 100
    assert target_run["bootstrap_early_stopped"] is True
    assert target_run["source"] == "test source"


async def test_global_weights_csv_invalid_file_extension(
    async_client,
    admin_auth_headers,
):
    """Test that uploading a file without a .csv extension raises a 400 error."""
    # Create a fake text file instead of a CSV
    file_content = b"just some text content"
    files = {"file": ("test_data.txt", file_content, "text/plain")}

    response = await async_client.post(
        "/global-weights/import",
        headers=admin_auth_headers,
        files=files,
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "File must be a CSV"}


# RBAC Tests for /global-weights/runs
async def test_list_global_weights_unauthenticated(async_client):
    """Test that unauthenticated request to list global weights is rejected."""
    response = await async_client.get("/global-weights/runs")
    assert response.status_code == 401


async def test_list_global_weight_runs_officer_forbidden(async_client, officer_auth_headers):
    """Test that officer cannot list global weight runs."""
    response = await async_client.get("/global-weights/runs", headers=officer_auth_headers)
    assert response.status_code == 403


async def test_list_global_weight_runs_supervisor_forbidden(async_client, supervisor_auth_headers):
    """Test that supervisor cannot list global weight runs."""
    response = await async_client.get("/global-weights/runs", headers=supervisor_auth_headers)
    assert response.status_code == 403


# RBAC Tests for /global-weights/runs/{run_id}
async def test_get_global_weight_run_unauthenticated(async_client):
    """Test that unauthenticated request to get global weight run is rejected."""
    response = await async_client.get(f"/global-weights/runs/{uuid4()}")
    assert response.status_code == 401


async def test_get_global_weight_run_officer_forbidden(async_client, officer_auth_headers):
    """Test that officer cannot get global weight run details."""
    response = await async_client.get(f"/global-weights/runs/{uuid4()}", headers=officer_auth_headers)
    assert response.status_code == 403


async def test_get_global_weight_run_supervisor_forbidden(async_client, supervisor_auth_headers):
    """Test that supervisor cannot get global weight run details."""
    response = await async_client.get(f"/global-weights/runs/{uuid4()}", headers=supervisor_auth_headers)
    assert response.status_code == 403


# RBAC Tests for /global-weights/import
async def test_import_global_weights_unauthenticated(async_client):
    """Test that unauthenticated request to import is rejected."""
    response = await async_client.post("/global-weights/import")
    assert response.status_code == 401


async def test_import_global_weights_officer_forbidden(async_client, officer_auth_headers):
    """Test that officer cannot import global weights."""
    response = await async_client.post("/global-weights/import", headers=officer_auth_headers)
    assert response.status_code == 403


async def test_import_global_weights_supervisor_forbidden(async_client, supervisor_auth_headers):
    """Test that supervisor cannot import global weights."""
    response = await async_client.post("/global-weights/import", headers=supervisor_auth_headers)
    assert response.status_code == 403


# RBAC Tests for /global-weights/runs/{run_id}
async def test_delete_global_weights_unauthenticated(async_client):
    """Test that unauthenticated request to delete is rejected."""
    response = await async_client.delete("/global-weights/runs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 401


async def test_delete_global_weight_run_officer_forbidden(async_client, officer_auth_headers):
    """Test that officer cannot delete a global weight run."""
    # Using a random UUID since it should fail on auth before checking existence
    response = await async_client.delete(
        "/global-weights/runs/00000000-0000-0000-0000-000000000000",
        headers=officer_auth_headers,
    )
    assert response.status_code == 403


async def test_delete_global_weight_run_supervisor_forbidden(async_client, supervisor_auth_headers):
    """Test that supervisor cannot delete a global weight run."""
    # Using a random UUID since it should fail on auth before checking existence
    response = await async_client.delete(
        "/global-weights/runs/00000000-0000-0000-0000-000000000000",
        headers=supervisor_auth_headers,
    )
    assert response.status_code == 403

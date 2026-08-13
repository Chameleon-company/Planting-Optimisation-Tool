from unittest.mock import patch

import pytest
from geoalchemy2 import WKTElement
from sqlalchemy import text

from src.models.boundaries import FarmBoundary
from src.models.farm import Farm
from src.models.planting_estimates import PlantingEstimate


@pytest.fixture
async def other_officer_user(async_session):  # a second officer, owns farms other from the caller
    from src.models.user import User

    user = User(
        name="Other Officer",
        email="other_officer@example.com",
        hashed_password="not-a-real-hash",
        role="officer",
    )
    async_session.add(user)
    await async_session.flush()
    await async_session.refresh(user)

    return user


async def _add_owned_farm(async_session, user_id, boundary_wkt):  # extra officer-owned farm inside the DEM extent
    farm = Farm(
        rainfall_mm=1000,
        temperature_celsius=25,
        elevation_m=100,
        ph=6.5,
        soil_texture_id=1,
        area_ha=10,
        latitude=0,
        longitude=0,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=5,
        user_id=user_id,
    )
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(boundary_wkt, srid=4326),
    )
    async_session.add(boundary)
    await async_session.flush()

    return farm


@pytest.fixture
async def setup_farm(async_session, test_officer_user):  # sapling_estimation router requires OFFICER role or higher
    await async_session.execute(text("TRUNCATE dem_table RESTART IDENTITY;"))
    await async_session.execute(
        text(
            """
            INSERT INTO dem_table (rast)
            VALUES (
                ST_AddBand(
                    ST_MakeEmptyRaster(
                        5, 5,
                        125, -8.9995,
                        0.001, -0.001,
                        0, 0,
                        4326
                    ),
                    1,
                    '32BF',
                    100
                )
            );
            """
        )
    )
    await async_session.flush()

    farm = Farm(
        rainfall_mm=1000,
        temperature_celsius=25,
        elevation_m=100,
        ph=6.5,
        soil_texture_id=1,
        area_ha=10,
        baseline_tree_count=0,  # add this line
        latitude=0,
        longitude=0,
        coastal=False,
        riparian=False,
        nitrogen_fixing=False,
        shade_tolerant=False,
        bank_stabilising=False,
        slope=5,
        user_id=test_officer_user.id,
    )
    async_session.add(farm)
    await async_session.flush()
    await async_session.refresh(farm)

    boundary = FarmBoundary(
        id=farm.id,
        external_id=farm.id,
        boundary=WKTElement(
            "MULTIPOLYGON (((125 -9, 125 -9.002, 125.002 -9.002, 125.002 -9, 125 -9)))",
            srid=4326,
        ),
    )
    async_session.add(boundary)
    await async_session.flush()

    return farm


# Batch: single farm returns the batch-shaped envelope
async def test_calculate_single_farm(
    async_client,
    setup_farm,
    officer_auth_headers,
):
    farm = setup_farm

    payload = {
        "farm_ids": [farm.id],
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    request = await async_client.post(
        "/sapling_estimation/calculate",
        json=payload,
        headers=officer_auth_headers,
    )

    assert request.status_code == 200  # Request should return 200
    data = request.json()

    assert data["farm_count"] == 1
    assert len(data["results"]) == 1

    item = data["results"][0]
    assert item["farm_id"] == farm.id
    assert "aligned_count" in item
    assert item["aligned_count"] > 0
    assert "pre_slope_count" in item
    assert item["pre_slope_count"] >= item["aligned_count"]


# Batch: multiple owned farms are all processed in one call
async def test_calculate_multiple_farms(
    async_client,
    async_session,
    setup_farm,
    test_officer_user,
    officer_auth_headers,
):
    farm_a = setup_farm  # first farm + DEM
    farm_b = await _add_owned_farm(
        async_session,
        test_officer_user.id,
        "MULTIPOLYGON (((125.0025 -9.0005, 125.0025 -9.0025, 125.0045 -9.0025, 125.0045 -9.0005, 125.0025 -9.0005)))",
    )

    payload = {
        "farm_ids": [farm_a.id, farm_b.id],
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    request = await async_client.post(
        "/sapling_estimation/calculate",
        json=payload,
        headers=officer_auth_headers,
    )

    assert request.status_code == 200  # Request should return 200
    data = request.json()

    assert data["farm_count"] == 2
    assert [item["farm_id"] for item in data["results"]] == [farm_a.id, farm_b.id]
    for item in data["results"]:
        assert item["aligned_count"] > 0


# Batch: any unknown / unowned id in the list yields a 404
async def test_calculate_partial_not_found(
    async_client,
    setup_farm,
    officer_auth_headers,
):
    farm = setup_farm
    missing_id = farm.id + 999999  # id that does not exist

    payload = {
        "farm_ids": [farm.id, missing_id],
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    request = await async_client.post(
        "/sapling_estimation/calculate",
        json=payload,
        headers=officer_auth_headers,
    )

    assert request.status_code == 207
    body = request.json()
    assert body["farm_count"] == 2

    # make key value pair where the key is the id and value is the results
    by_id = {response["farm_id"]: response for response in body["results"]}
    assert by_id[missing_id]["status"] == "failed"
    assert by_id[farm.id]["status"] != "failed"


# Validation: farm_ids must contain at least one id
async def test_calculate_empty_farm_ids(
    async_client,
    setup_farm,
    officer_auth_headers,
):
    payload = {
        "farm_ids": [],
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    request = await async_client.post(
        "/sapling_estimation/calculate",
        json=payload,
        headers=officer_auth_headers,
    )

    assert request.status_code == 422  # empty list fails Field(min_length=1)


# Security: an officer shouldn't be able to call another officer's farms
async def test_calculate_rejects_unowned_farm(
    async_client,
    async_session,
    setup_farm,
    other_officer_user,
    officer_auth_headers,
):
    # A farm owned by a different officer, not the authenticated caller
    other_farm = await _add_owned_farm(
        async_session,
        other_officer_user.id,
        "MULTIPOLYGON (((125.0025 -9.0005, 125.0025 -9.0025, 125.0045 -9.0025, 125.0045 -9.0005, 125.0025 -9.0005)))",
    )

    payload = {
        "farm_ids": [other_farm.id],
        "spacing_x": 10,
        "spacing_y": 10,
        "max_slope": 15,
    }

    request = await async_client.post(
        "/sapling_estimation/calculate",
        json=payload,
        headers=officer_auth_headers,
    )

    # Ownership filter treats another user's farm as not-found, 404
    assert request.status_code == 404
    assert str(other_farm.id) in request.json()["detail"]


# Cache Hit Test - /grid caches after first DB fetch; second call should not hit DB
async def test_grid_cache_hit(
    async_client,
    async_session,
    setup_farm,
    officer_auth_headers,
):
    farm = setup_farm

    estimate = PlantingEstimate(
        farm_id=farm.id,
        slope=5.0,
        geometry=WKTElement("POINT (125.001 -9.001)", srid=4326),
    )
    async_session.add(estimate)
    await async_session.commit()

    # First request populates the grid cache from DB
    response1 = await async_client.get(f"/sapling_estimation/{farm.id}/grid", headers=officer_auth_headers)
    assert response1.status_code == 200
    first_result = response1.json()

    # Second request should be served from cache - patch DB access to confirm
    with patch(
        "src.services.sapling_estimation.get_planting_grid",
        side_effect=Exception("Cache hit error: Second /grid request should be served from cache, not DB"),
    ):
        response2 = await async_client.get(f"/sapling_estimation/{farm.id}/grid", headers=officer_auth_headers)

    assert response2.status_code == 200
    assert response2.json() == first_result


async def test_get_planting_grid_returns_geojson(
    async_client,
    async_session,
    setup_farm,
    officer_auth_headers,
):
    farm = setup_farm

    estimate = PlantingEstimate(
        farm_id=farm.id,
        slope=5.0,
        geometry=WKTElement("POINT (125.001 -9.001)", srid=4326),
    )
    async_session.add(estimate)
    await async_session.commit()

    response = await async_client.get(f"/sapling_estimation/{farm.id}/grid", headers=officer_auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 1
    assert data["features"][0]["geometry"]["type"] == "Point"


async def test_get_planting_grid_404_when_no_estimates(
    async_client,
    setup_farm,
    officer_auth_headers,
):
    farm = setup_farm

    response = await async_client.get(f"/sapling_estimation/{farm.id}/grid", headers=officer_auth_headers)

    assert response.status_code == 404


async def test_get_planting_grid_requires_auth(
    async_client,
    setup_farm,
):
    farm = setup_farm

    response = await async_client.get(f"/sapling_estimation/{farm.id}/grid")

    assert response.status_code == 401

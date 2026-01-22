import pytest
import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box
import os

from sapling_estimation.estimate import sapling_estimation


@pytest.fixture
def create_dem(tmp_path):
    # Creates a 10x10 DEM raster with simple gradient
    data = np.linspace(0, 20, 100, dtype=np.float32).reshape(10, 10)

    # Creates a path for the DEM file inside pytest's temporary directory
    dem_path = tmp_path / "DEM.tif"

    # Defines a georeferencing transform for rasterio
    transform = from_origin(
        0, 100, 10, 10
    )  # origin_x, origin_y, pixel_width, pixel_height

    # Write data into new raster file
    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(data, 1)

    return tmp_path


def test_sapling_estimation(create_dem):
    # Change working directory so sapling_estimation() loads DEM.tif naturally
    os.chdir(create_dem)

    # Execute the sapling estimation feature
    result = sapling_estimation(
        farm_polygon=box(0, 0, 50, 50),  # 50m × 50m polygon
        spacing_m=3.0,
        farm_boundary_crs="EPSG:4326",
        debug=False,
    )

    # Planting plan/Output check
    assert isinstance(result, dict)  # Validate that the function returns a dictionary
    assert "sapling_count" in result  # Ensure required keys exist in the output
    assert "optimal_angle" in result

    assert (
        result["sapling_count"] > 0
    )  # Ensure the function produced at least one valid planting point
    assert (
        0 <= result["optimal_angle"] <= 360
    )  # Ensure the rotation angle is within the valid range

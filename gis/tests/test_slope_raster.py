import pytest
import numpy as np
import rasterio
from rasterio.transform import from_origin
import geopandas as gpd
from shapely.geometry import box

from sapling_estimation.slope_raster import compute_farm_slope


@pytest.fixture
def create_dem(tmp_path):
    # Creates a 5x5 DEM/array with simple gradient
    data = np.array(
        [
            [1, 2, 3, 4, 5],
            [2, 3, 4, 5, 6],
            [3, 4, 5, 6, 7],
            [4, 5, 6, 7, 8],
            [5, 6, 7, 8, 9],
        ],
        dtype=np.float32,
    )

    # Creates a path for the DEM file inside pytest's temporary directory
    dem_path = tmp_path / "DEM.tif"

    # Defines a georeferencing transform for rasterio
    transform = from_origin(0, 5, 1, 1)  # origin_x, origin_y, pixel_width, pixel_height

    # Write data into new raster file
    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        height=data.shape[0],
        width=data.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(data, 1)

    return dem_path


@pytest.fixture
def create_farm_polygon():
    # Creates a 5x5 square polygon
    poly = box(0, 0, 5, 5)

    # Wrap it in a GeoDataFrame with a CRS
    return gpd.GeoDataFrame(geometry=[poly], crs="EPSG:4326")


def test_compute_farm_slope(create_dem, create_farm_polygon):
    # Open test DEM file to compute slope
    with rasterio.open(create_dem) as dem_src:
        slope, transform, profile = compute_farm_slope(dem_src, create_farm_polygon)

    # Slope raster checks
    assert isinstance(slope, np.ndarray)  # Ensure slope output is a numpy array
    assert slope.shape == (5, 5)  # Ensure slope array has the expected 5x5 shape
    assert np.all(slope >= 0)  # Ensure slope values are not negative
    assert np.all(slope <= 90)  # Ensure slope values are not greater than 90 degrees

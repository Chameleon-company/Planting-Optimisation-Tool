import pytest
import numpy as np
import rasterio
from rasterio.transform import from_origin
import geopandas as gpd
from shapely.geometry import Point

from sapling_estimation.slope_rules import apply_slope_rules, MAX_SLOPE


@pytest.fixture
def create_slope_raster():
    # Creates a 5x5 slope raster containing slope values
    data = np.array(
        [
            [20, 20, 20, 20, 20],
            [20, 5, 5, 5, 20],
            [20, 5, 5, 5, 20],
            [20, 5, 5, 5, 20],
            [20, 20, 20, 20, 20],
        ],
        dtype=np.float32,
    )

    # Defines a georeferencing transform for rasterio
    transform = from_origin(0, 5, 1, 1)  # origin_x, origin_y, pixel_width, pixel_height
    return data, transform


@pytest.fixture
def create_planting_points():
    # Creates 5 planting points for different scenarios
    points = [
        Point(2, 2),  # Inside raster, on low slope
        Point(2, 3),  # Inside raster, on low slope
        Point(3, 2),  # Inside raster, on low slope
        Point(0, 0),  # Inside raster, on high slope
        Point(10, 10),  # Outside raster
    ]

    return gpd.GeoDataFrame(geometry=points, crs="EPSG:4326")


def test_apply_slope_rules_basic(create_slope_raster, create_planting_points):
    # Create the slope raster and apply the slope rules
    slope_array, transform = create_slope_raster
    filtered = apply_slope_rules(slope_array, create_planting_points, transform)

    # Slope rules check
    assert isinstance(
        filtered, gpd.GeoDataFrame
    )  # Ensure the function returns a GeoDataFrame
    assert len(filtered) == 3  # Ensure only the 3 points remains

    # Ensure the 3 remaining points are the ones inside raster and on low slope
    for p in filtered.geometry:
        r, c = rasterio.transform.rowcol(transform, p.x, p.y)
        assert slope_array[r, c] <= MAX_SLOPE

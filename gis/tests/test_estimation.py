import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import Polygon

from sapling_estimation.estimate import sapling_estimation


@pytest.fixture
def create_farm_polygon():
    # Creates a 100m x 100m square polygon
    return Polygon([(0, 0), (0, 100), (100, 100), (100, 0)])


@pytest.fixture
def create_dem_array():
    # Creates a simple DEM (10x10 grid)
    return np.ones((10, 10), dtype=np.float32) * 10


def test_sapling_estimation(create_farm_polygon, create_dem_array):
    result = sapling_estimation(
        farm_polygon=create_farm_polygon,
        spacing_m=10,
        farm_boundary_crs="EPSG:3857",
        dem_array=create_dem_array,
        dem_upper_left_x=0,
        dem_upper_left_y=100,
        pixel_width=10,
        pixel_height=10,
        dem_crs="EPSG:3857",
        debug=False,
    )

    # Ensure result structure
    assert isinstance(result, dict)
    assert "final_grid" in result
    assert "optimal_angle" in result
    assert "slope_values" in result

    final_grid = result["final_grid"]

    # Ensure output type
    assert isinstance(final_grid, gpd.GeoDataFrame)

    # Ensure points generated
    assert len(final_grid) > 0

    # Ensure angle is valid
    assert 0 <= result["optimal_angle"] <= 360

    # Ensure slope values match grid size
    assert len(result["slope_values"]) == len(final_grid)

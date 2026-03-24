import geopandas as gpd
import numpy as np
import pytest
from rasterio.transform import from_origin
from shapely.geometry import Polygon

from sapling_estimation.estimate import sapling_estimation


@pytest.fixture
def create_farm_polygon():
    # Use METERS directly (EPSG:3857)
    poly = Polygon([
        (0, 0),
        (0, 100),
        (100, 100),
        (100, 0)
    ])
    return poly


@pytest.fixture
def create_dem_array():
    # Flat DEM (low slope)
    data = np.ones((10, 10), dtype=np.float32)

    transform = from_origin(0, 100, 10, 10)
    return data, transform


def test_sapling_estimation(create_farm_polygon, create_dem_array):
    dem_array, transform = create_dem_array

    result = sapling_estimation(
        farm_polygon=create_farm_polygon,
        spacing_m=10,                 
        farm_boundary_crs="EPSG:3857",  
        dem_array=dem_array,
        dem_transform=transform,
        debug=False
    )

    assert isinstance(result, dict)

    assert "final_grid" in result
    assert "optimal_angle" in result

    final_grid = result["final_grid"]
    assert isinstance(final_grid, gpd.GeoDataFrame)

    assert len(final_grid) > 0   
    assert result["optimal_angle"] >= 0
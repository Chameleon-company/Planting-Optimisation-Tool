import pytest
import geopandas as gpd
from shapely.geometry import box

from sapling_estimation.planting_points import generate_planting_points


@pytest.fixture
def create_farm_polygon():
    # Creates a 10x10 square polygon
    poly = box(0, 0, 10, 10)  # xmin, ymin, xmax, ymax
    return poly


def test_generate_planting_points(create_farm_polygon):
    spacing = 3.0  # Define 3x3 spacing rule
    crs = "EPSG:4326"  # Define CRS

    # Define the bounds of the polygon (xmin, ymin, xmax, ymax)
    slope_bounds = (0, 0, 10, 10)

    # Run the planting point generator
    planting_grid = generate_planting_points(
        farm_polygon=create_farm_polygon,
        target_crs=crs,
        slope_bounds=slope_bounds,
        spacing_m=spacing,
    )

    # Planting grid checks
    assert isinstance(
        planting_grid, gpd.GeoDataFrame
    )  # Ensure the output is a GeoDataFrame
    assert len(planting_grid) > 0  # Ensure at least one planting point was generated
    assert planting_grid.within(
        create_farm_polygon
    ).all()  # Ensure all points lie within the polygon

    # Expected number of grid points inside the 10x10 square with spacing 3
    # Grid coordinates: 3, 6, 9  >  3 x 3 = 9
    assert len(planting_grid) == 9

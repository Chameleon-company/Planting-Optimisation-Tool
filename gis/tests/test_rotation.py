import pytest
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.affinity import rotate

from sapling_estimation.planting_points import generate_planting_points
from sapling_estimation.rotation import rotate_grid


@pytest.fixture
def farm_polygon_45():
    """
    Creates a 1:3 rectangle (10m x 30m) rotated 45 degrees.
    """
    # Create the base unrotated rectangle (Width 10, Height 30)
    # Vertices: (0,0) -> (10,0) -> (10,30) -> (0,30)
    base_rect = Polygon([(0, 0), (10, 0), (10, 30), (0, 30), (0, 0)])

    # Rotate it 45 degrees
    # origin='center' ensures it spins in place rather than swinging around (0,0)
    rotated_rect = rotate(base_rect, 45, origin="center")

    return rotated_rect


def test_rotate_grid_basic(farm_polygon_45):
    # Use a small polygon and large spacing
    spacing = 4.0

    initial_grid = generate_planting_points(
        farm_polygon_45, "EPSG:4326", farm_polygon_45.bounds, spacing
    )

    final_grid, angle = rotate_grid(farm_polygon_45, initial_grid, spacing)

    assert isinstance(final_grid, gpd.GeoDataFrame)
    assert 0 <= angle <= 360
    assert len(final_grid) > 0
    assert len(final_grid) >= len(initial_grid)

import time

import geopandas as gpd
import pytest
from shapely.affinity import rotate
from shapely.geometry import Polygon

from sapling_estimation.planting_points import generate_planting_points
from sapling_estimation.rotation import old_rotate_grid, rotate_grid


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
    spacing_x = 4.0
    spacing_y = 4.0

    initial_grid = generate_planting_points(farm_polygon_45, "EPSG:4326", farm_polygon_45.bounds, spacing_x, spacing_y)

    final_grid, angle = rotate_grid(farm_polygon_45, initial_grid, spacing_x, spacing_y)

    assert isinstance(final_grid, gpd.GeoDataFrame)
    assert 0 <= angle <= 360
    assert len(final_grid) > 0
    assert len(final_grid) >= len(initial_grid)


def test_rotation_speed(farm_polygon_45):
    spacing_x = 3.0
    spacing_y = 3.0
    planting_grid = generate_planting_points(farm_polygon_45, "EPSG:4326", farm_polygon_45.bounds, spacing_x, spacing_y)

    start = time.perf_counter()
    old_grid, _ = old_rotate_grid(farm_polygon_45, planting_grid, spacing_x)
    old_time = time.perf_counter() - start

    start = time.perf_counter()
    new_grid, _ = rotate_grid(farm_polygon_45, planting_grid, spacing_x, spacing_y)
    new_time = time.perf_counter() - start

    print(f"Rotation completed in {new_time:.4f} seconds.")
    print(f"Time saved: {(old_time - new_time):.4f} seconds. Speedup: {(old_time / new_time):.2f}x faster")
    assert new_time < old_time


def test_rotation_correctness(farm_polygon_45):
    spacing_x = 3.0
    spacing_y = 3.0
    planting_grid = generate_planting_points(farm_polygon_45, "EPSG:4326", farm_polygon_45.bounds, spacing_x, spacing_y)

    old_grid, old_angle = old_rotate_grid(farm_polygon_45, planting_grid, spacing_x)
    new_grid, new_angle = rotate_grid(farm_polygon_45, planting_grid, spacing_x, spacing_y)

    assert len(old_grid) == len(new_grid)
    assert old_angle == new_angle

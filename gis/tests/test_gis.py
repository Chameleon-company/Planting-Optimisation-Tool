from unittest.mock import patch, MagicMock
import builtins


from core.gee_client import init_gee
from core.extract_data import (
    get_ph,
    get_rainfall,
    get_elevation,
    get_landcover,
    get_temperature,
    get_NDVI,
)

from core.geometry_parser import (
    parse_point,
    parse_multipoint,
    parse_polygon,
    parse_geometry,
)


# Helper to create fake ee module for mocking
def make_fake_ee():
    fake = MagicMock()
    fake.Geometry = MagicMock()
    fake.ServiceAccountCredentials = MagicMock()
    fake.Initialize = MagicMock()
    return fake


# init_gee test
@patch("core.gee_client.SERVICE_ACCOUNT", "sa@example.com")
@patch("core.gee_client.KEY_PATH", "/tmp/key.json")
def test_init_gee():
    fake_ee = make_fake_ee()

    # Patch import ee inside the function
    with patch.object(builtins, "__import__", return_value=fake_ee):
        result = init_gee()

    assert result is True
    fake_ee.ServiceAccountCredentials.assert_called_once_with(
        "sa@example.com", "/tmp/key.json"
    )
    fake_ee.Initialize.assert_called_once()


# parse_point test
def test_parse_point():
    fake_ee = make_fake_ee()

    with patch.object(builtins, "__import__", return_value=fake_ee):
        g = parse_point(-8.55, 125.57)

    fake_ee.Geometry.Point.assert_called_once_with([125.57, -8.55])
    assert g == fake_ee.Geometry.Point.return_value


# parse_multipoint test


def test_parse_multipoint():
    fake_ee = make_fake_ee()

    coords = [(-8.55, 125.57), (-8.56, 125.58)]

    with patch.object(builtins, "__import__", return_value=fake_ee):
        g = parse_multipoint(coords)

    fake_ee.Geometry.MultiPoint.assert_called_once_with(
        [[125.57, -8.55], [125.58, -8.56]]
    )
    assert g == fake_ee.Geometry.MultiPoint.return_value


# parse_polygon test


def test_parse_polygon():
    fake_ee = make_fake_ee()

    coords = [
        [
            (-8.55, 125.57),
            (-8.56, 125.57),
            (-8.56, 125.58),
            (-8.55, 125.58),
            (-8.55, 125.57),
        ]
    ]

    with patch.object(builtins, "__import__", return_value=fake_ee):
        g = parse_polygon(coords)

    fake_ee.Geometry.Polygon.assert_called_once_with(
        [
            [
                [125.57, -8.55],
                [125.57, -8.56],
                [125.58, -8.56],
                [125.58, -8.55],
                [125.57, -8.55],
            ]
        ]
    )
    assert g == fake_ee.Geometry.Polygon.return_value


# ph test
def test_get_ph():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake feature
    fake_feature = MagicMock()
    fake_feature.get.return_value.getInfo.return_value = 5.8

    fake_fc = MagicMock()
    fake_fc.filterBounds.return_value.first.return_value = fake_feature

    fake_ee.FeatureCollection.return_value = fake_fc

    with patch.object(builtins, "__import__", return_value=fake_ee):
        ph_value = get_ph(-8.6, 125.6)

    assert isinstance(ph_value, (int, float))
    assert 0 <= ph_value <= 14
    assert ph_value == 5.8

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([125.6, -8.6])
    fake_ee.FeatureCollection.assert_called_once_with(
        "projects/scenic-block-466510-c5/assets/soil_ph_timor"
    )
    fake_fc.filterBounds.assert_called_once_with(fake_point)
    fake_fc.filterBounds.return_value.first.assert_called_once()
    fake_feature.get.assert_called_once_with("ph")


# rainfall test
def test_get_rainfall():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake Image pipeline
    fake_img = MagicMock()
    fake_img.select.return_value = fake_img
    fake_img.reduceRegion.return_value = {"b1": 978.5366590315607}

    fake_ee.Image.return_value = fake_img

    with patch.object(builtins, "__import__", return_value=fake_ee):
        rain_value = get_rainfall(-8.6, 125.6)

    # Check the return value
    assert isinstance(rain_value, (int, float))
    assert rain_value == 978.5366590315607

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([125.6, -8.6])
    fake_ee.Image.assert_called_once_with(
        "projects/scenic-block-466510-c5/assets/CHIRPS_5yr_Avg_Annual_Rainfall_2020_2024_30m"
    )
    fake_img.select.assert_called_once_with("b1")
    fake_img.reduceRegion.assert_called_once()


# temperature test
def test_get_temperature():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake Image pipeline
    fake_img = MagicMock()
    fake_img.select.return_value = fake_img
    fake_img.reduceRegion.return_value = {"b1": 24.318966087873864}

    fake_ee.Image.return_value = fake_img

    with patch.object(builtins, "__import__", return_value=fake_ee):
        temp_value = get_temperature(-8.6, 125.6)

    # Check the return value
    assert isinstance(temp_value, (int, float))
    assert temp_value == 24.318966087873864

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([125.6, -8.6])
    fake_ee.Image.assert_called_once_with(
        "projects/scenic-block-466510-c5/assets/MOD11A2_5yr_Avg_Annual_temperature_2020_2024_30m"
    )
    fake_img.select.assert_called_once_with("b1")
    fake_img.reduceRegion.assert_called_once()


# elevation test
def test_get_elevation():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake Image pipeline
    fake_img = MagicMock()
    fake_img.select.return_value = fake_img
    fake_img.reduceRegion.return_value = {"b1": 692.0}

    fake_ee.Image.return_value = fake_img

    with patch.object(builtins, "__import__", return_value=fake_ee):
        elev_value = get_elevation(-8.6, 125.6)

    # Check the return value
    assert isinstance(elev_value, (int, float))
    assert elev_value == 692.0

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([125.6, -8.6])
    fake_ee.Image.assert_called_once_with("projects/scenic-block-466510-c5/assets/DEM")
    fake_img.select.assert_called_once_with("b1")
    fake_img.reduceRegion.assert_called_once()


# landcover test
def test_get_landcover():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake feature
    fake_feature = MagicMock()
    fake_feature.get.return_value.getInfo.return_value = "forest"

    fake_fc = MagicMock()
    fake_fc.filterBounds.return_value.first.return_value = fake_feature

    fake_ee.FeatureCollection.return_value = fake_fc

    with patch.object(builtins, "__import__", return_value=fake_ee):
        landcover_value = get_landcover(-8.6, 125.6)

    assert landcover_value == "forest"

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([125.6, -8.6])
    fake_ee.FeatureCollection.assert_called_once_with(
        "projects/scenic-block-466510-c5/assets/farm_with_landcover"
    )
    fake_fc.filterBounds.assert_called_once_with(fake_point)
    fake_fc.filterBounds.return_value.first.assert_called_once()
    fake_feature.get.assert_called_once_with("lc_class")


def test_get_NDVI():
    fake_ee = make_fake_ee()

    # Fake Geometry Point
    fake_point = MagicMock()
    fake_ee.Geometry = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake Image
    fake_img = MagicMock()

    # Fake Dict
    fake_dict = MagicMock()
    fake_dict.get.return_value.getInfo.return_value = 7815

    fake_img.reduceRegion.return_value = fake_dict

    # Fake Image Collection
    fake_ic = MagicMock()
    fake_ic.filterDate.return_value = fake_ic
    fake_ic.select.return_value = fake_ic
    fake_ic.mean.return_value = fake_img

    fake_ee.ImageCollection.return_value = fake_ic

    with patch.object(builtins, "__import__", return_value=fake_ee):
        ndvi_value = get_NDVI(-8.6, 125.6)

    assert isinstance(ndvi_value, (int, float))
    assert abs(ndvi_value - 0.7815) < 1e-6

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([125.6, -8.6])
    fake_ee.ImageCollection.assert_called_once_with("MODIS/061/MOD13Q1")
    fake_ic.filterDate.assert_called_once_with("2025-01-01", "2025-12-31")
    fake_ic.select.assert_called_once_with("NDVI")
    fake_ic.mean.assert_called_once()
    fake_img.reduceRegion.assert_called_once()


# parse_geometry auto-detection


def test_parse_geometry_dispatch():
    fake_ee = make_fake_ee()

    # ---- Point ----
    with patch.object(builtins, "__import__", return_value=fake_ee):
        parse_geometry((-8.55, 125.57))  # no variable assigned

    fake_ee.Geometry.Point.assert_called_once_with([125.57, -8.55])
    fake_ee.Geometry.Point.reset_mock()

    # ---- MultiPoint ----
    with patch.object(builtins, "__import__", return_value=fake_ee):
        parse_geometry([(-8.55, 125.57), (-8.56, 125.58)])  # no variable assigned

    fake_ee.Geometry.MultiPoint.assert_called_once_with(
        [[125.57, -8.55], [125.58, -8.56]]
    )
    fake_ee.Geometry.MultiPoint.reset_mock()

    # ---- Polygon ----
    polygon_raw = [
        [
            (-8.55, 125.57),
            (-8.56, 125.57),
            (-8.56, 125.58),
            (-8.55, 125.58),
            (-8.55, 125.57),
        ]
    ]

    with patch.object(builtins, "__import__", return_value=fake_ee):
        g_polygon = parse_geometry(polygon_raw)

    fake_ee.Geometry.Polygon.assert_called_once()
    assert g_polygon == fake_ee.Geometry.Polygon.return_value

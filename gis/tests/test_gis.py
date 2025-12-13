from unittest.mock import patch, MagicMock
import builtins
from config.settings import (
    RAINFALL_ASSET_ID,
    RAINFALL_BAND,
    TEMP_ASSET_ID,
    TEMP_BAND,
    SOIL_PH_ASSET_ID,
    SOIL_PH_FIELD,
    DEM_ASSET_ID,
    DEM_BAND,
    SLOPE_BAND,
    SOIL_TEXTURE_ASSET_ID,
    SOIL_TEXTURE_FIELD,
    BOUNDARY_TIMOR_ASSET_ID,
)


from core.gee_client import init_gee
from core.extract_data import (
    get_rainfall,
    get_temperature,
    get_ph,
    get_area_ha,
    get_dist_to_coast,
    get_elevation,
    get_slope,
    get_texture,
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

    coords = (-8.569, 126.676)

    with patch.object(builtins, "__import__", return_value=fake_ee):
        ph_value = get_ph(coords)

    assert isinstance(ph_value, (int, float))
    assert 0 <= ph_value <= 14
    assert ph_value == 5.8

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([126.676, -8.569])
    fake_ee.FeatureCollection.assert_called_once_with(SOIL_PH_ASSET_ID)
    fake_fc.filterBounds.assert_called_once_with(fake_point)
    fake_fc.filterBounds.return_value.first.assert_called_once()
    fake_feature.get.assert_called_once_with(SOIL_PH_FIELD)


# rainfall test
def test_get_rainfall():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake Image pipeline
    fake_img = MagicMock()
    fake_img.select.return_value = fake_img
    fake_img.reduceRegion.return_value = {RAINFALL_BAND: 978.5366590315607}
    fake_ee.Image.return_value = fake_img

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "ee":
            return fake_ee
        return real_import(name, *args, **kwargs)

    coords = (-8.569, 126.676)

    with patch.object(builtins, "__import__", side_effect=fake_import):
        value = get_rainfall(coords)

    # Check the return value
    assert isinstance(value, (int, float))
    assert value == int(round(978.5366590315607))

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([126.676, -8.569])
    fake_ee.Image.assert_called_once_with(RAINFALL_ASSET_ID)
    fake_img.select.assert_called_once_with(RAINFALL_BAND)
    fake_img.reduceRegion.assert_called_once()


# temperature test
def test_get_temperature():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake Image pipeline
    fake_img = MagicMock()
    fake_img.select.return_value = fake_img
    fake_img.reduceRegion.return_value = {TEMP_BAND: 25.251091954023018}
    fake_ee.Image.return_value = fake_img

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "ee":
            return fake_ee
        return real_import(name, *args, **kwargs)

    coords = (-8.569, 126.676)

    with patch.object(builtins, "__import__", side_effect=fake_import):
        value = get_temperature(coords)

    # Check the return value
    assert isinstance(value, (int, float))
    assert value == int(round(25.251091954023018))

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([126.676, -8.569])
    fake_ee.Image.assert_called_once_with(TEMP_ASSET_ID)
    fake_img.select.assert_called_once_with(TEMP_BAND)
    fake_img.reduceRegion.assert_called_once()


# elevation test
def test_get_elevation():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake Image pipeline
    fake_img = MagicMock()
    fake_img.select.return_value = fake_img
    fake_img.reduceRegion.return_value = {DEM_BAND: 1867.647706320975}
    fake_ee.Image.return_value = fake_img

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "ee":
            return fake_ee
        return real_import(name, *args, **kwargs)

    coords = (-8.569, 126.676)

    with patch.object(builtins, "__import__", side_effect=fake_import):
        value = get_elevation(coords)

    # Check the return value
    assert isinstance(value, (int, float))
    assert value == int(round(1867.647706320975))

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([126.676, -8.569])
    fake_ee.Image.assert_called_once_with(DEM_ASSET_ID)
    fake_img.select.assert_called_once_with(DEM_BAND)
    fake_img.reduceRegion.assert_called_once()


# slope test
def test_get_slope():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake DEM image
    fake_dem = MagicMock()
    fake_dem.select.return_value = fake_dem
    fake_ee.Image.return_value = fake_dem

    # Fake slope image
    fake_slope_img = MagicMock()
    fake_slope_img.reduceRegion.return_value = {SLOPE_BAND: 11.488}
    fake_ee.Terrain.slope.return_value = fake_slope_img

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "ee":
            return fake_ee
        return real_import(name, *args, **kwargs)

    coords = (-8.569, 126.676)

    with patch.object(builtins, "__import__", side_effect=fake_import):
        value = get_slope(coords)

    # Check the return value
    assert isinstance(value, (int, float))
    assert value == round(11.488, 3)

    # Check Geometry + Image calls
    fake_ee.Geometry.Point.assert_called_once_with([126.676, -8.569])
    fake_ee.Image.assert_called_once_with(DEM_ASSET_ID)
    fake_dem.select.assert_called_once_with(DEM_BAND)
    fake_ee.Terrain.slope.assert_called_once_with(fake_dem)


# texture test
def test_get_texture():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake feature
    fake_feature = MagicMock()
    fake_feature.get.return_value.getInfo.return_value = ["Clay"]

    fake_fc = MagicMock()
    fake_fc.filterBounds.return_value.first.return_value = fake_feature

    fake_ee.FeatureCollection.return_value = fake_fc

    coords = (-8.569, 126.676)

    with patch.object(builtins, "__import__", return_value=fake_ee):
        value = get_texture(coords)

    assert value == ["Clay"]

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([126.676, -8.569])
    fake_ee.FeatureCollection.assert_called_once_with(SOIL_TEXTURE_ASSET_ID)
    fake_fc.filterBounds.assert_called_once_with(fake_point)
    fake_fc.filterBounds.return_value.first.assert_called_once()
    fake_feature.get.assert_called_once_with(SOIL_TEXTURE_FIELD)


# area_ha test
def test_get_area():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()

    # Fake area hectar
    fake_area_number = MagicMock()
    fake_area_number.getInfo.return_value = 49_320.0
    fake_point.area.return_value = fake_area_number

    fake_ee.Geometry.Point.return_value = fake_point

    coords = (-8.569, 126.676)

    with patch.object(builtins, "__import__", return_value=fake_ee):
        value = get_area_ha(coords)

    assert isinstance(value, (int, float))
    assert value == 4.932

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([126.676, -8.569])
    fake_point.area.assert_called_once_with(maxError=1)


# dist_to_coast test
def test_get_dist_to_coast():
    fake_ee = make_fake_ee()

    # Fake Geometry.Point
    fake_point = MagicMock()
    fake_ee.Geometry.Point.return_value = fake_point

    # Fake centroid point hectar
    fake_centroid = MagicMock()
    fake_point.centroid.return_value = fake_centroid

    # Fake Feature Collection and country geom
    fake_country_geom = MagicMock()
    fake_feature = MagicMock()
    fake_ee.FeatureCollection.return_value = fake_feature
    fake_feature.geometry.return_value = fake_country_geom

    # Fake distance values
    fake_dist_value = MagicMock()
    fake_dist_value.getInfo.return_value = 4_932.9
    fake_centroid.distance.return_value = fake_dist_value

    coords = (-8.569, 126.676)

    with patch.object(builtins, "__import__", return_value=fake_ee):
        value = get_dist_to_coast(coords)

    assert isinstance(value, (int, float))
    assert value == 4.933

    # Check that the EE API was called as expected
    fake_ee.Geometry.Point.assert_called_once_with([126.676, -8.569])
    fake_point.centroid.assert_called_once_with(maxError=1)
    fake_ee.FeatureCollection.assert_called_once_with(BOUNDARY_TIMOR_ASSET_ID)
    fake_feature.geometry.assert_called_once_with()
    fake_centroid.distance.assert_called_once_with(fake_country_geom, 100)


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

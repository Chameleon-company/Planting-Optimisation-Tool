import io
from unittest.mock import MagicMock

import pytest
from PIL import Image
from staticmap import Polygon, StaticMap

from src.services.farm_map_image import (
    DEFAULT_IMAGE_HEIGHT,
    DEFAULT_IMAGE_WIDTH,
    FETCH_MAX_ZOOM,
    TILE_REQUEST_TIMEOUT_SECONDS,
    _apply_digital_zoom,
    _choose_zoom,
    _extract_exterior_rings,
    render_farm_boundary_image,
)

POLYGON_FEATURE = {
    "type": "Feature",
    "geometry": {
        "type": "Polygon",
        "coordinates": [[[125.0, -9.0], [125.0, -9.002], [125.002, -9.002], [125.002, -9.0], [125.0, -9.0]]],
    },
    "properties": {"farm_id": 1},
}

MULTIPOLYGON_FEATURE = {
    "type": "Feature",
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [
            [[[125.0, -9.0], [125.0, -9.002], [125.002, -9.002], [125.002, -9.0], [125.0, -9.0]]],
            [[[126.0, -8.0], [126.0, -8.001], [126.001, -8.001], [126.001, -8.0], [126.0, -8.0]]],
        ],
    },
    "properties": {"farm_id": 2},
}


def _fake_tile_response(status_code: int = 200) -> MagicMock:
    """A fake requests.Response carrying a real 256x256 PNG tile so staticmap can open it."""
    tile = Image.new("RGB", (256, 256), color=(34, 139, 34))
    buffer = io.BytesIO()
    tile.save(buffer, format="PNG")

    response = MagicMock()
    response.status_code = status_code
    response.content = buffer.getvalue()
    return response


async def test_render_farm_boundary_image_returns_png_bytes_for_polygon(mocker):
    mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())

    result = await render_farm_boundary_image(POLYGON_FEATURE)

    assert result is not None
    image = Image.open(io.BytesIO(result))
    assert image.format == "PNG"
    assert image.size == (DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT)


async def test_render_farm_boundary_image_returns_png_bytes_for_multipolygon(mocker):
    mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())

    result = await render_farm_boundary_image(MULTIPOLYGON_FEATURE)

    assert result is not None
    image = Image.open(io.BytesIO(result))
    assert image.format == "PNG"


async def test_render_farm_boundary_image_uses_custom_width_and_height(mocker):
    mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())

    result = await render_farm_boundary_image(POLYGON_FEATURE, width=300, height=200)

    assert result is not None
    image = Image.open(io.BytesIO(result))
    assert image.size == (300, 200)


async def test_render_farm_boundary_image_requests_correct_esri_tile_urls(mocker):
    mock_get = mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())

    await render_farm_boundary_image(POLYGON_FEATURE)

    assert mock_get.called
    requested_urls = [call.args[0] for call in mock_get.call_args_list]
    assert all("server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/" in url for url in requested_urls)


async def test_render_farm_boundary_image_uses_a_tighter_zoom_than_staticmaps_own_cap(mocker):
    # staticmap's own zoom search hard-codes a maximum of 17, which leaves a
    # small farm's boundary looking tiny within the frame. POLYGON_FEATURE's
    # ~0.002 degree extent needs a zoom above 17 to actually fill a 600x400
    # canvas. Regression test for the fix that recomputes zoom without that cap.
    mock_get = mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())

    await render_farm_boundary_image(POLYGON_FEATURE)

    requested_urls = [call.args[0] for call in mock_get.call_args_list]
    requested_zooms = {int(url.split("/tile/")[1].split("/")[0]) for url in requested_urls}
    assert max(requested_zooms) > 17


async def test_render_farm_boundary_image_never_requests_tiles_above_fetch_max_zoom(mocker):
    # Esri returns HTTP 200 above zoom 18 too, but the content is a generic
    # placeholder graphic there, not real imagery (confirmed manually: z18
    # tiles are ~14KB of real detail, z19+ are a ~2.5KB placeholder). Extra
    # zoom beyond 18 must come from digitally cropping/upscaling the rendered
    # image, never from requesting tiles the server can't really provide.
    mock_get = mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())

    await render_farm_boundary_image(POLYGON_FEATURE)

    requested_urls = [call.args[0] for call in mock_get.call_args_list]
    requested_zooms = {int(url.split("/tile/")[1].split("/")[0]) for url in requested_urls}
    assert max(requested_zooms) == 18


async def test_render_farm_boundary_image_sets_a_tile_request_timeout(mocker):
    # staticmap defaults to no timeout at all (waits forever on a hung request),
    # so this must be set explicitly. Regression test for that gap.
    mock_get = mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())

    await render_farm_boundary_image(POLYGON_FEATURE)

    assert mock_get.called
    for call in mock_get.call_args_list:
        assert call.kwargs["timeout"] == TILE_REQUEST_TIMEOUT_SECONDS
        assert call.kwargs["timeout"] is not None


async def test_render_farm_boundary_image_returns_none_when_tiles_never_succeed(mocker):
    mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response(status_code=500))

    result = await render_farm_boundary_image(POLYGON_FEATURE)

    assert result is None


async def test_render_farm_boundary_image_returns_none_for_empty_multipolygon(mocker):
    mock_get = mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())
    empty_feature = {
        "type": "Feature",
        "geometry": {"type": "MultiPolygon", "coordinates": []},
        "properties": {"farm_id": 3},
    }

    result = await render_farm_boundary_image(empty_feature)

    assert result is None
    # No shapes were added, so no tiles should have been requested at all.
    assert not mock_get.called


async def test_render_farm_boundary_image_actually_draws_the_boundary_onto_the_tiles(mocker):
    background_color = (34, 139, 34)
    mocker.patch("staticmap.staticmap.requests.get", return_value=_fake_tile_response())

    result = await render_farm_boundary_image(POLYGON_FEATURE, width=300, height=300)

    assert result is not None
    image = Image.open(io.BytesIO(result)).convert("RGB")
    pixels = image.get_flattened_data()
    # If the polygon/line were never actually drawn, every pixel would still be
    # the plain background tile colour. At least some pixels must differ from
    # it, proving the boundary overlay was really composited onto the image.
    assert any(pixel != background_color for pixel in pixels)


def test_choose_zoom_picks_a_zoom_above_staticmaps_own_cap_for_a_tiny_shape():
    static_map = StaticMap(DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT)
    ring = POLYGON_FEATURE["geometry"]["coordinates"][0]
    static_map.add_polygon(Polygon([(lon, lat) for lon, lat in ring], (255, 0, 0, 50), None))

    zoom = _choose_zoom(static_map, max_zoom=20)

    assert zoom > 17


def test_apply_digital_zoom_upscales_when_shape_needs_more_zoom_than_fetch_max():
    static_map = StaticMap(DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT)
    # A tiny (~0.0003 degree) polygon, smaller than POLYGON_FEATURE, whose tight
    # fit needs a zoom above FETCH_MAX_ZOOM (18), the only fixture size that
    # actually exercises the digital-zoom path.
    coords = [(125.0, -9.0), (125.0, -9.0003), (125.0003, -9.0003), (125.0003, -9.0), (125.0, -9.0)]
    static_map.add_polygon(Polygon(coords, (255, 0, 0, 50), None))
    image = Image.new("RGB", (DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT), color=(34, 139, 34))

    result = _apply_digital_zoom(image, FETCH_MAX_ZOOM, static_map)

    assert result.size == (DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT)
    assert result is not image


def test_apply_digital_zoom_is_a_noop_when_fetch_zoom_already_fits():
    static_map = StaticMap(DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT)
    # A large shape that already needs a low zoom to fit: no extra digital
    # zoom should be applied on top of it.
    coords = [(120.0, -9.0), (120.0, -7.0), (122.0, -7.0), (122.0, -9.0), (120.0, -9.0)]
    static_map.add_polygon(Polygon(coords, (255, 0, 0, 50), None))
    image = Image.new("RGB", (DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT), color=(34, 139, 34))

    result = _apply_digital_zoom(image, fetch_zoom=8, static_map=static_map)

    assert result is image


def test_choose_zoom_never_exceeds_max_zoom():
    static_map = StaticMap(DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT)
    # A single point has zero extent, so the tightest possible fit is always
    # available: this should hit the max_zoom ceiling rather than search past it.
    static_map.add_polygon(Polygon([(125.0, -9.0), (125.0, -9.0), (125.0, -9.0)], (255, 0, 0, 50), None))

    zoom = _choose_zoom(static_map, max_zoom=20)

    assert zoom == 20


def test_extract_exterior_rings_for_polygon():
    rings = _extract_exterior_rings(POLYGON_FEATURE["geometry"])

    assert len(rings) == 1
    assert rings[0] == POLYGON_FEATURE["geometry"]["coordinates"][0]


def test_extract_exterior_rings_for_multipolygon():
    rings = _extract_exterior_rings(MULTIPOLYGON_FEATURE["geometry"])

    assert len(rings) == 2


def test_extract_exterior_rings_raises_for_unsupported_geometry_type():
    with pytest.raises(ValueError, match="Unsupported boundary geometry type"):
        _extract_exterior_rings({"type": "LineString", "coordinates": [[125.0, -9.0], [125.001, -9.001]]})

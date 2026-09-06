import io
from unittest.mock import MagicMock

import pytest
from PIL import Image

from src.services.farm_map_image import (
    DEFAULT_IMAGE_HEIGHT,
    DEFAULT_IMAGE_WIDTH,
    TILE_REQUEST_TIMEOUT_SECONDS,
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

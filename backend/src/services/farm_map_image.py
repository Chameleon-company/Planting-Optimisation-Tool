import asyncio
import io

from PIL import Image
from staticmap import Line, Polygon, StaticMap
from staticmap.staticmap import _lat_to_y, _lon_to_x

# Same satellite imagery provider and tile scheme used by the interactive map
# (FarmBoundaryMap.tsx), so the static image in a report looks consistent with
# what a user sees on screen. staticmap fetches individual tiles and picks
# whatever zoom level is needed to fit the given shape, so unlike a single
# "export image for this bbox" API call, there is no minimum area it can render,
# a farm of any size can be zoomed in on properly.
ESRI_TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

DEFAULT_IMAGE_WIDTH = 600
DEFAULT_IMAGE_HEIGHT = 400

# staticmap defaults this to None (no timeout at all), which means a single
# hung tile request could block the thread indefinitely. Set explicitly so a
# slow or unresponsive tile server fails after a bounded wait instead.
TILE_REQUEST_TIMEOUT_SECONDS = 15.0

# Matches the web map's styling (FarmBoundaryMap.tsx: color "#ffffff", fillColor "#ff4444", fillOpacity 0.3).
OUTLINE_COLOR = (255, 255, 255, 255)
FILL_COLOR = (255, 68, 68, 77)
OUTLINE_WIDTH = 3

# staticmap's own zoom search (StaticMap._calculate_zoom) hard-codes a maximum
# zoom of 17, so a small farm that would need a higher zoom to fill the frame
# instead renders zoomed far out, with the boundary lost in a sea of
# surrounding land. _choose_zoom below redoes staticmap's own tight-fit search
# without that cap, but only up to FETCH_MAX_ZOOM: Esri's tile server returns
# HTTP 200 above zoom 18 too, but the *content* is a generic "Map data not yet
# available" placeholder there, not real imagery (confirmed: z18 tiles are
# ~14KB of real detail, z19+ are a ~2.5KB placeholder graphic, matching the
# interactive map's own maxNativeZoom=18). So real tile data is only ever
# fetched up to 18; any additional zoom needed to fill the frame is achieved
# afterwards in _apply_digital_zoom by cropping and upscaling the rendered
# image, the same trick Leaflet performs client-side for its maxZoom=22.
FETCH_MAX_ZOOM = 18
MAX_DIGITAL_ZOOM_LEVELS = 2


def _choose_zoom(static_map: StaticMap, max_zoom: int) -> int:
    """Finds the highest zoom level at which the map's current shapes still fit
    within its canvas. Mirrors staticmap's own StaticMap._calculate_zoom, but
    without that method's hard-coded cap of 17."""
    for zoom in range(max_zoom, -1, -1):
        min_lon, min_lat, max_lon, max_lat = static_map.determine_extent(zoom=zoom)
        width = (_lon_to_x(max_lon, zoom) - _lon_to_x(min_lon, zoom)) * static_map.tile_size
        height = (_lat_to_y(min_lat, zoom) - _lat_to_y(max_lat, zoom)) * static_map.tile_size
        if width <= static_map.width and height <= static_map.height:
            return zoom
    return 0


def _apply_digital_zoom(image: Image.Image, fetch_zoom: int, static_map: StaticMap) -> Image.Image:
    """Crops the rendered image around its center and upscales it back to full
    size, simulating the extra zoom levels real tile data can't provide (see
    FETCH_MAX_ZOOM above). No-op if the shape already fits at fetch_zoom
    without needing it."""
    ideal_zoom = _choose_zoom(static_map, max_zoom=FETCH_MAX_ZOOM + MAX_DIGITAL_ZOOM_LEVELS)
    extra_levels = min(ideal_zoom - fetch_zoom, MAX_DIGITAL_ZOOM_LEVELS)
    if extra_levels <= 0:
        return image

    scale = 2**extra_levels
    width, height = image.size
    crop_w, crop_h = width // scale, height // scale
    left, top = (width - crop_w) // 2, (height - crop_h) // 2
    cropped = image.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((width, height), Image.LANCZOS)


def _extract_exterior_rings(geometry: dict) -> list[list[list[float]]]:
    """Returns just the outer boundary ring of each polygon, ignoring any holes.
    A farm boundary is not expected to have interior holes."""
    geom_type = geometry["type"]
    if geom_type == "Polygon":
        return [geometry["coordinates"][0]]
    if geom_type == "MultiPolygon":
        return [polygon[0] for polygon in geometry["coordinates"]]
    raise ValueError(f"Unsupported boundary geometry type: {geom_type}")


def _render_sync(geometry: dict, width: int, height: int) -> bytes:
    """Builds and renders the static map. Runs staticmap's synchronous,
    network-fetching render() call, so this must be run off the event loop
    (see render_farm_boundary_image)."""
    static_map = StaticMap(width, height, url_template=ESRI_TILE_URL, tile_request_timeout=TILE_REQUEST_TIMEOUT_SECONDS)

    for ring in _extract_exterior_rings(geometry):
        coords = [(lon, lat) for lon, lat in ring]
        static_map.add_polygon(Polygon(coords, FILL_COLOR, None))
        static_map.add_line(Line(coords + [coords[0]], OUTLINE_COLOR, OUTLINE_WIDTH, simplify=False))

    # _choose_zoom needs at least one shape to compute an extent from. An empty
    # map (e.g. a MultiPolygon with no polygons) has none, so leave zoom as
    # None and let render() raise its usual RuntimeError for an empty map,
    # rather than reaching _apply_digital_zoom with nothing to measure.
    has_shapes = bool(static_map.lines or static_map.markers or static_map.polygons)
    zoom = _choose_zoom(static_map, max_zoom=FETCH_MAX_ZOOM) if has_shapes else None
    image = static_map.render(zoom=zoom)
    image = _apply_digital_zoom(image, zoom, static_map)

    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


async def render_farm_boundary_image(
    boundary: dict,
    width: int = DEFAULT_IMAGE_WIDTH,
    height: int = DEFAULT_IMAGE_HEIGHT,
) -> bytes | None:
    """Renders a farm boundary as a static satellite image with the polygon outlined,
    ready to embed in a PDF/DOCX report.

    boundary is the GeoJSON Feature returned by farm_service.get_farm_boundary
    (a dict with a "type": "Feature" and a "geometry" key).

    Returns PNG image bytes, or None if the satellite tiles could not be fetched
    (staticmap retries transient failures itself before giving up).
    """
    geometry = boundary["geometry"]
    try:
        return await asyncio.to_thread(_render_sync, geometry, width, height)
    except RuntimeError:
        return None

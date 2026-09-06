import asyncio
import io

from staticmap import Line, Polygon, StaticMap

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

    image = static_map.render()

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

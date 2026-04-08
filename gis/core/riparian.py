"""
Riparian zone detection using Timor-Leste Waterways dataset via Google Earth Engine.

The waterways dataset (HOT OSM) is uploaded as a GEE FeatureCollection asset,
eliminating the need for any local file. This integrates naturally with the
existing GEE service account setup used by all other extractors.

"""

from __future__ import annotations

import ee

from config.settings import WATERWAYS_ASSET_ID
from core.geometry_parser import parse_geometry

# ============================================================================
# CONSTANTS
# ============================================================================

# Riparian buffer distance confirmed by environmental consultant (US-018).
# 15 metres from the centreline of any mapped waterway.
# Change this value if the regulatory threshold is revised.
RIPARIAN_BUFFER_M: float = 15.0


# ============================================================================
# AC2 + AC3 — GEOSPATIAL INTERSECTION CHECK / PUBLIC API
# ============================================================================


def get_riparian_flags(
    geometry,
    buffer_m: float | None = None,
) -> dict:
    """
    Check if a farm geometry falls within a riparian zone using GEE.

    Loads the waterways FeatureCollection from a GEE asset and computes
    the distance from the farm geometry to the nearest waterway line.

    Works for both existing farms and candidate new farm boundaries.

    Args:
        geometry:  Farm geometry — same formats as geometry_parser.py.
                   (lat/lon tuple, list of tuples, list of rings)
        buffer_m:  Riparian buffer distance in metres.
                   Defaults to RIPARIAN_BUFFER_M (15.0m).

    Returns:
        {
            "is_riparian": bool | None,
            "distance_to_nearest_waterway_m": float | None,
        }

        Returns None values if the GEE call fails, so callers can distinguish
        "not riparian" from "check not performed".
    """
    buffer_m = buffer_m if buffer_m is not None else RIPARIAN_BUFFER_M

    try:
        farm_geom = parse_geometry(geometry)  # ee.Geometry

        waterways = ee.FeatureCollection(WATERWAYS_ASSET_ID)

        # Compute distance from farm geometry to each waterway feature,
        # then get the minimum (nearest waterway).
        # ee.Geometry.distance() returns metres (geodesic).
        def add_distance(feature):
            dist = farm_geom.distance(feature.geometry(), maxError=1)
            return feature.set("distance_m", dist)

        nearest_distance = waterways.map(add_distance).aggregate_min("distance_m")

        distance_m = float(nearest_distance.getInfo())
        is_riparian = distance_m <= buffer_m

        return {
            "is_riparian": bool(is_riparian),
            "distance_to_nearest_waterway_m": round(distance_m, 1),
        }

    except Exception as e:
        import warnings

        warnings.warn(
            f"Riparian check via GEE failed: {e}. Verify asset exists: {WATERWAYS_ASSET_ID}",
            stacklevel=2,
        )
        return {
            "is_riparian": None,
            "distance_to_nearest_waterway_m": None,
        }

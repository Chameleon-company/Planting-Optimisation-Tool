# Overview
This module provides a lightweight interface for extracting geospatial attributes from coordinates.
It is designed to support the Planting Optimisation Tool by converting longitude/latitude inputs into meaningful environmental data such as elevation, rainfall, temperature, soil pH, and landcover.
```
gis/
│
├── assets/
│   └── gadm41_TLS_3.json        # Administrative boundary data for Timor-Leste
│
├── config/
│   └── settings.py              # Environment variable loading (service account, key paths)
│
├── core/
│   ├── extract_data.py          # Functions to fetch rainfall, temp, pH, elevation, landcover
│   ├── farm_profile.py          # Builds a farm profile from coordinates
│   ├── gee_client.py            # Earth Engine initialization + client handling
│   └── geometry_parser.py       # Parsers for point, multipoint, polygon inputs
|___docs/
|   └── README.md                # folder structure, update works
│
├── keys/
│   └── <service-account>.json   # Local service account key (ignored by Git)
│
├── .env                         # GEE_SERVICE_ACCOUNT and GEE_KEY_PATH variables
├── tests/
│   └──test_gis.py               # unit tests for all gis functions
├── utils 
    └──build_farm_table.py       # script to load farm_boundaries.gpkg and generates a CSV for later import into PostgreSQL
```

# Function Documentation

**init_gee()**

Initializes Google Earth Engine using the service account and key path from config/settings.py.
Validates the required environment variables and calls ee.Initialize().

**parse_point(lat, lon)**

Converts a (lat, lon) coordinate into an ee.Geometry.Point.
Earth Engine expects coordinates in [lon, lat] order.

**parse_multipoint(coords)**

Takes a list of (lat, lon) tuples and returns an ee.Geometry.MultiPoint.
Coordinates are converted to [lon, lat].

**parse_polygon(coords)**

Creates an ee.Geometry.Polygon from a list of rings.
Each ring is a list of (lat, lon) tuples; the outer ring must be closed.

**parse_geometry(geom_raw)**

Auto-detects whether the input is a Point, MultiPoint, or Polygon and returns the appropriate Earth Engine geometry.
Raises an error for unsupported formats.

**build_farm_table()**

A one-time script that loads farm_boundaries.gpkg, cleans the geometries, and prepares a farm table for later GIS and database use.
It converts 3D polygons to 2D, computes centroids, calculates area in hectares, generates WKT geometry, and outputs a clean CSV (gis/docs/farm_table.csv) containing all farm attributes and polygon data.

**get_rainfall()**
Returns the 5-year (2020 - 2024) average annual rainfall (mm) for a given geometry (point or polygon), in Timor-Leste from PO's Dataset.

**get_temperature()**
Returns the 5-year (2020 - 2024) average land surface temperature (°C) for a given geometry (point or polygon), in Timor-Leste from PO's Dataset.

**get_ph()**
Returns the soil pH value for a given geometry (point or polygon), based on a soil pH polygon layer from PO's Dataset.

**get_elevation()**
Returns the elevation (m) for a given geometry (point or polygon), from a DEM provided by the PO.

**get_slope()**
Returns the get_slope (degree) for a given geometry (point or polygon), from a DEM provided by the PO.

**get_texture()**
Return soil texture for a given geometry (point or polygon), from a soil_texture provided by the PO.

**get_area_ha()**
Return area of the input geometry in hectares for a given geometry (point or polygon)

**get_dist_to_coast()**
Return distance to coast_boundary by measure the distance of the centroild point to timor boundary for a given geometry (point or polygon)

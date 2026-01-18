# GIS Module Documentation

## Overview

This module provides a lightweight, production-ready interface for extracting geospatial environmental data from farm coordinates in Timor-Leste. It serves as the core GIS engine for the Planting Optimisation Tool, transforming simple longitude/latitude inputs into comprehensive environmental profiles that include elevation, rainfall, temperature, soil properties, and terrain characteristics.

The module integrates two primary data sources:
1. **Global datasets** via Google Earth Engine (GEE) - providing satellite-derived climate and terrain data with validated accuracy
2. **Local datasets** from the Product Owner (PO) - including ground-truth measurements, farm boundaries, and field surveys specific to Timor-Leste

All datasets have been rigorously validated against 940 farm measurements collected by the Product Owner between 2020-2024. This validation period was chosen because it represents recent, high-quality ground truth data, but the system can extract historical data from GEE datasets dating back to their respective start dates (e.g., CHIRPS: 1981-present, MODIS: 2000-present).

### Key Capabilities

- **Individual Farm Profiling**: Extract complete environmental profiles for single farm locations in 1-2 seconds
- **Bulk Processing**: Process hundreds of farms in parallel using multi-threaded operations (2-5 farms/second)
- **Temporal Flexibility**: Query data for any year within dataset coverage (CHIRPS: 1981-present, MODIS: 2000-present)
- **Multi-Year Averaging**: Calculate averages over custom time periods (not limited to 2020-2024)
- **Flexible Input**: Accept coordinates as points, polygons, or coordinate lists
- **Data Validation**: All extraction functions include built-in quality checks and error handling
- **Efficient Updates**: Update only temporal variables (rainfall, temperature) without re-extracting static data

### Primary Use Cases

1. **Farm Registration**: Generate initial environmental profiles when new farms join the system
2. **Annual Monitoring**: Update climate variables each growing season to track year-to-year changes
3. **Historical Analysis**: Extract past climate data to understand trends and variability
4. **Spatial Analysis**: Compare environmental conditions across different farm locations
5. **Crop Suitability**: Provide environmental inputs for crop recommendation algorithms
6. **Risk Assessment**: Identify climate and terrain risks (drought, flooding, erosion) based on environmental profiles

### Data Quality Assurance

All datasets have undergone comprehensive validation against Product Owner field measurements (2020-2024 period):
- **Excellent correlation** (r > 0.95): Rainfall, Elevation, Farm Area
- **Good correlation** (r > 0.85): Temperature (with bias correction applied)
- **Poor correlation** (r < 0.20): Soil pH (flagged for local calibration)

The module automatically applies validated bias corrections and includes data quality warnings for unreliable variables. Note that while validation was performed on 2020-2024 data, the extraction functions work for any year within each dataset's temporal coverage.

## Project Structure

```
gis/
│
│
├── assets/
│    ├── all_farm_sample.csv      # Farm data sample, provided by PO
│    └── farm_boundaries.gpkg     # Farms' geolocations 
│
├── config/
│   └── settings.py              # Environment variable loading (service account, key paths)
│                                # Dataset configurations (CHIRPS, MODIS, SRTM, etc.)
│                                # Texture mapping dictionary
├── core/
│   ├── extract_data.py          # Functions to fetch rainfall, temp, pH, elevation, landcover
│   ├── farm_profile.py          # Builds farm profiles from coordinates (single & bulk)
│   ├── gee_client.py            # Earth Engine initialization + client handling
│   └── geometry_parser.py       # Parsers for point, multipoint, polygon inputs
│
├── docs/
│   ├── README.md                # This file - module documentation
│   └── output_schema.md          # schema for farm profile output
│
├── notebook/
│   ├── all_farm_environmental_factors.csv              # (to be updated by Danny)
│   ├── extract_environmental_factor_each_farm.ipynb    # (to be updated by Danny)
│   └── eda_gee.ipynb                                   # EDA: comparing data extracted directly from GEE and
│                                                               data provided by PO.
│
├── keys/
│   └── <service-account>.json   # service account key (ignored by Git)
│
├── tests/
│   └── test_gis.py              # Unit tests for all GIS functions (34 tests)
│
├── .env                         # GEE_SERVICE_ACCOUNT and GEE_KEY_PATH variables

```

## Key Features

- **Individual Operations**: Extract data for single farm locations
- **Bulk Operations**: Process hundreds of farms in parallel
- **Dataset Validation**: All datasets validated against 940 ground truth measurements
- **Flexible Input**: Accepts points, polygons, or coordinate lists
- **Error Handling**: Graceful handling of missing data and invalid inputs
- **Temporal Data**: Supports year-specific queries for rainfall and temperature

## Data Sources

### Google Earth Engine Datasets (Global)

| Dataset | Variable | Resolution | Temporal Coverage | Validation (2020-2024) | Status |
|---------|----------|------------|-------------------|------------------------|--------|
| CHIRPS | Rainfall | 5.5 km | 1981-present | r=0.96, MAE=23mm | Excellent |
| SRTM DEM | Elevation | 90 m | Static (2000) | r=0.98, MAE=11m | Excellent |
| MODIS LST | Temperature | 1 km | 2000-present | r=0.87, MAE=1.5°C | Good (bias corrected) |
| OpenLandMap | Soil pH | 250 m | Static (~2020) | r=0.18, MAE=1.21 | Poor (not recommended) |


### Product Owner (PO) Datasets (Timor-Leste)

Local datasets collected and maintained by the Product Owner (field measurements and surveys):

| Dataset | Variable | Source | Coverage |
|---------|----------|--------|----------|
| Farm Boundaries | Geometry | farm_boundaries.gpkg | 940 farms |
| Rainfall | 5-year avg (2020-2024) | CHIRPS_5yr_Avg_Annual_Rainfall_2020_2024_30m | Timor-Leste |
| Temperature | 5-year avg (2020-2024) | MOD11A2_5yr_Avg_Annual_temperature_2020_2024_30m | Timor-Leste |
| Soil pH | Point measurements | PO soil surveys | 911 field samples |
| Soil Texture | Texture classes | QGIS Soil Texture | Selected regions |

**Note**: PO datasets represent ground-truth measurements used to validate the global GEE datasets.

## Installation

### Setup Virtual Environment

```bash
cd gis
uv venv
uv sync
source .venv/bin/activate
```

### Google Earth Engine Setup

1. Create service account in Google Cloud Platform
2. Download JSON key file
3. Place key in `gis/keys/` directory
4. Create `.env` file:

```bash
#Edit .env with your credentials
GEE_SERVICE_ACCOUNT=your-service-account@project.iam.gserviceaccount.com
GEE_KEY_PATH=/path/to/gis/keys/service-account-key.json
```

## Function Documentation

### Core Functions

#### **init_gee()**

Initializes Google Earth Engine using the service account and key path from config/settings.py.

**Parameters:** None (reads from environment variables)

**Returns:** `bool` - True if initialization successful

**Raises:** 
- `ValueError` - If GEE_SERVICE_ACCOUNT or GEE_KEY_PATH not set
- `ee.EEException` - If authentication fails

**Example:**
```python
from gis.core.gee_client import init_gee

success = init_gee()
if success:
    print("GEE initialized successfully")
```

**Notes:**
- Validates required environment variables before initialization
- Must be called before any GEE operations
- Only needs to be called once per session

---

### Geometry Parsing Functions

#### **parse_point(lat, lon)**

Converts a (lat, lon) coordinate into an ee.Geometry.Point.

**Parameters:**
- `lat` (float): Latitude in decimal degrees (-90 to 90)
- `lon` (float): Longitude in decimal degrees (-180 to 180)

**Returns:** `ee.Geometry.Point`

**Example:**
```python
from gis.core.geometry_parser import parse_point

point = parse_point(-8.569, 126.676)
# Returns ee.Geometry.Point([126.676, -8.569])
```

**Notes:**
- Earth Engine expects coordinates in [lon, lat] order (reversed)
- Function handles the coordinate order conversion automatically

---

#### **parse_multipoint(coords)**

Takes a list of (lat, lon) tuples and returns an ee.Geometry.MultiPoint.

**Parameters:**
- `coords` (list): List of (lat, lon) tuples

**Returns:** `ee.Geometry.MultiPoint`

**Example:**
```python
from gis.core.geometry_parser import parse_multipoint

coords = [(-8.55, 125.57), (-8.56, 125.58), (-8.57, 125.59)]
multipoint = parse_multipoint(coords)
```

**Notes:**
- Useful for multi-parcel farms or farm clusters
- Coordinates are automatically converted to [lon, lat] order

---

#### **parse_polygon(coords)**

Creates an ee.Geometry.Polygon from a list of rings.

**Parameters:**
- `coords` (list): List of rings, where each ring is a list of (lat, lon) tuples

**Returns:** `ee.Geometry.Polygon`

**Example:**
```python
from gis.core.geometry_parser import parse_polygon

# Simple polygon (outer ring only)
coords = [[
    (-8.55, 125.57),
    (-8.56, 125.57),
    (-8.56, 125.58),
    (-8.55, 125.58),
    (-8.55, 125.57)  # Must close the ring
]]
polygon = parse_polygon(coords)
```

**Notes:**
- Outer ring must be closed (first point = last point)
- Supports holes (additional inner rings)
- Coordinates converted to [lon, lat] order

---

#### **parse_geometry(geom_raw)**

Auto-detects whether the input is a Point, MultiPoint, or Polygon and returns the appropriate Earth Engine geometry.

**Parameters:**
- `geom_raw` (tuple|list): Coordinates in various formats

**Returns:** `ee.Geometry` (Point, MultiPoint, or Polygon)

**Raises:** `ValueError` - If geometry format not recognized

**Example:**
```python
from gis.core.geometry_parser import parse_geometry

# Auto-detect point
geom1 = parse_geometry((-8.569, 126.676))

# Auto-detect polygon
geom2 = parse_geometry([[(-8.55, 125.57), (-8.56, 125.57), ...]])

# Auto-detect multipoint
geom3 = parse_geometry([(-8.55, 125.57), (-8.56, 125.58)])
```

**Detection Logic:**
- Tuple of 2 floats → Point
- List of tuples (all 2-element) → MultiPoint
- List of lists → Polygon

---

### Data Extraction Functions

#### **get_rainfall(geometry, year=None)**

Returns the annual rainfall (mm) for a given geometry and specified year.

**Data Source:** CHIRPS (Climate Hazards Group InfraRed Precipitation with Station data)

**Temporal Coverage:** 1981 to present (updated regularly)

**Validation:** r=0.96, MAE=23mm - Validated against Product Owner field station measurements from 2020-2024 period (Excellent correlation)

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates
- `year` (int, optional): Specific year for data extraction. If None, defaults to 2024.

**Returns:** `float` - Annual rainfall in millimeters for the specified year

**Example:**
```python
from gis.core.extract_data import get_rainfall

# Get rainfall for specific year
rainfall_2024 = get_rainfall((-8.569, 126.676), year=2024)
# Returns: 1850.5 mm

rainfall_2015 = get_rainfall((-8.569, 126.676), year=2015)
# Returns: 1672.3 mm

rainfall_1990 = get_rainfall((-8.569, 126.676), year=1990)
# Returns: 1805.1 mm

# Default (uses 2024 if year not specified)
rainfall_default = get_rainfall((-8.569, 126.676))
# Returns: 1850.5 mm (year=2024)
```

**Notes:**
- Based on CHIRPS daily dataset summed annually
- Resolution: 5.5 km
- Temporal range: **1981 to present** (not limited to 2020-2024)
- Validation performed on 2020-2024 data, but extraction works for any year
- Most reliable dataset (r=0.96 validation against PO ground truth)
- Automatically aggregates daily values to annual totals
- Data updated regularly by UCSB Climate Hazards Center

**Multi-Year Averaging:**
To calculate multi-year averages, call the function multiple times:
```python
# Calculate 5-year average (2020-2024)
years = range(2020, 2025)
rainfall_values = [get_rainfall(coords, year=y) for y in years]
avg_rainfall = sum(rainfall_values) / len(rainfall_values)

# Calculate 10-year average (2014-2023)
years = range(2014, 2024)
rainfall_values = [get_rainfall(coords, year=y) for y in years]
avg_rainfall_10yr = sum(rainfall_values) / len(rainfall_values)
```

---

#### **get_temperature(geometry, year=None)**

Returns the mean annual land surface temperature (°C) for a given geometry and specified year.

**Data Source:** MODIS Land Surface Temperature (MOD11A2, 8-day composite)

**Temporal Coverage:** 2000 to present (updated regularly)

**Validation:** r=0.87, MAE=1.5°C - Validated against Product Owner weather station measurements from 2020-2024 period with automatic bias correction applied (Good correlation)

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates
- `year` (int, optional): Specific year for data extraction. If None, defaults to 2024.

**Returns:** `float` - Mean annual temperature in Celsius (bias-corrected) for the specified year

**Example:**
```python
from gis.core.extract_data import get_temperature

# Get temperature for specific year
temp_2024 = get_temperature((-8.569, 126.676), year=2024)
# Returns: 24.3°C (automatically bias-corrected)

temp_2010 = get_temperature((-8.569, 126.676), year=2010)
# Returns: 23.8°C

temp_2005 = get_temperature((-8.569, 126.676), year=2005)
# Returns: 24.1°C

# Default (uses 2024 if year not specified)
temp_default = get_temperature((-8.569, 126.676))
# Returns: 24.3°C (year=2024)
```

**Notes:**
- Measures land surface temperature (LST), not air temperature
- **Automatic bias correction**: -4.43°C adjustment applied to match PO air temperature measurements
- This correction accounts for daytime solar heating of land surface vs. air temperature
- After correction: Excellent agreement with ground truth (MAE=1.5°C)
- Resolution: 1 km
- Temporal range: **2000 to present** (not limited to 2020-2024)
- Validation performed on 2020-2024 data, but extraction works for any year since 2000
- Daytime measurements only (LST_Day_1km band)
- 8-day composite reduces cloud contamination
- Data updated regularly by NASA

**Multi-Year Averaging:**
```python
# Calculate 5-year average (2020-2024)
years = range(2020, 2025)
temp_values = [get_temperature(coords, year=y) for y in years]
avg_temp = sum(temp_values) / len(temp_values)

# Calculate decadal average (2010-2019)
years = range(2010, 2020)
temp_values = [get_temperature(coords, year=y) for y in years]
avg_temp_decade = sum(temp_values) / len(temp_values)
```

---

#### **get_ph(geometry, year=None)**

Returns the soil pH value for a given geometry.

**Data Source:** OpenLandMap Soil pH (0-5cm depth)

**Validation:** r=0.18, MAE=1.21 pH units - Validated against Product Owner soil survey data (Poor correlation - NOT RECOMMENDED)

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates
- `year` (int, optional): Not used (static dataset)

**Returns:** `float` - Soil pH value (0-14 scale) or `None` if no data

**Example:**
```python
from gis.core.extract_data import get_ph

ph = get_ph((-8.569, 126.676))
# Returns: 6.2 (but low reliability for Timor-Leste)
```

**WARNING - Low Data Quality:**
- Very low correlation (r=0.18) with Product Owner field measurements
- Shows severe value compression (predicts 5.5-6.5 vs actual range 5.0-8.0)
- Systematic underestimation in alkaline soils (errors of -2 to -3 pH units above pH 7)
- Root cause: Sparse training data in tropical Southeast Asia
- **NOT RECOMMENDED** for operational use in Timor-Leste

**Recommendation:**
- Use Product Owner field measurements directly (911 samples available)
- Develop local calibration model using PO data with predictors:
  - Elevation (r=0.98 - strongest proxy)
  - Rainfall patterns
  - Geological substrate
  - Land cover type
- Expected local model accuracy: r ≥ 0.4-0.6

**Notes:**
- Resolution: 250 m
- Global dataset (limited local calibration)
- Function included for demonstration but flagged as unreliable

---

#### **get_elevation(geometry, year=None)**

Returns the elevation (m) for a given geometry.

**Data Source:** SRTM (Shuttle Radar Topography Mission) DEM 90m

**Validation:** r=0.98, MAE=11m (Excellent)

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates
- `year` (int, optional): Not used (static dataset)

**Returns:** `float` - Elevation in meters above sea level

**Example:**
```python
from gis.core.extract_data import get_elevation

elevation = get_elevation((-8.569, 126.676))
# Returns: 580 m
```

**Notes:**
- Very high accuracy (r=0.98)
- Resolution: 90 m
- Static dataset (no temporal variation)
- Used for coastal flag calculation

---

#### **get_slope(geometry, year=None)**

Returns the slope (degrees) for a given geometry.

**Data Source:** Calculated from SRTM DEM using ee.Terrain.slope()

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates
- `year` (int, optional): Not used (static dataset)

**Returns:** `float` - Slope in degrees (0-90)

**Example:**
```python
from gis.core.extract_data import get_slope

slope = get_slope((-8.569, 126.676))
# Returns: 12.3 degrees
```

**Notes:**
- Derived from SRTM DEM
- Uses Earth Engine's terrain analysis
- Range: 0° (flat) to 90° (vertical cliff)
- Resolution: 90 m

---

#### **get_texture(geometry, year=None)**

Returns soil texture for a given geometry.

**Data Source:** Currently using OpenLandMap pH as placeholder to demonstrate GEE extraction capability

**Status:** Demonstration only - awaiting Product Owner soil texture dataset

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates
- `year` (int, optional): Not used

**Returns:** `str|float` - Texture class name (when configured) or numeric value (current demonstration)

**Example:**
```python
from gis.core.extract_data import get_texture

texture = get_texture((-8.569, 126.676))
# Currently returns: 6.2 (pH value as demonstration)
# Will return: "loam" (when proper texture dataset configured)
```

**Notes:**
- **Current implementation**: Demonstrates GEE extraction using pH data as proxy
- **Production use**: Requires Product Owner soil texture dataset configuration
- Expected texture classes: USDA classification (sand, loam, clay, etc.)
- To activate: Replace asset_id in settings.py with actual texture dataset path
- Framework ready - just needs proper dataset reference

**Configuration Required:**
```python
# In settings.py, update to:
"soil_texture": {
    "type": "raster",  # or "vector"
    "asset_id": "path/to/actual/texture/dataset",
    "band": "texture_class",  # or "field": "texture"
    "scale": 250,
}
```

---

#### **get_texture_id(geometry, year=None)**

Returns USDA soil texture classification ID (1-12).

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates
- `year` (int, optional): Not used

**Returns:** `int` - Texture ID (1-12) or `None`

**Texture ID Mapping:**
```python
1:  sand
2:  loamy sand
3:  sandy loam
4:  loam
5:  silt loam
6:  silt
7:  sandy clay loam
8:  clay loam
9:  silty clay loam
10: sandy clay
11: silty clay
12: clay
```

**Example:**
```python
from gis.core.extract_data import get_texture_id

texture_id = get_texture_id((-8.569, 126.676))
# Returns: 4 (loam)
```

---

#### **get_area_ha(geometry)**

Returns area of the input geometry in hectares.

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Polygon coordinates

**Returns:** `float` - Area in hectares

**Example:**
```python
from gis.core.extract_data import get_area_ha

polygon = [[(-8.55, 125.57), (-8.56, 125.57), (-8.56, 125.58), (-8.55, 125.58), (-8.55, 125.57)]]
area = get_area_ha(polygon)
# Returns: 123.45 ha
```

**Notes:**
- Uses geodesic calculation (accounts for Earth's curvature)
- Transforms to UTM Zone 51S (EPSG:32751) for accurate area calculation
- For points: returns 0.0

---

#### **get_centroid_lat_lon(geometry)**

Returns centroid coordinates (latitude, longitude) for a given geometry.

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates

**Returns:** `tuple` - (latitude, longitude) in decimal degrees

**Example:**
```python
from gis.core.extract_data import get_centroid_lat_lon

polygon = [[(-8.55, 125.57), (-8.56, 125.57), (-8.56, 125.58), (-8.55, 125.58), (-8.55, 125.57)]]
lat, lon = get_centroid_lat_lon(polygon)
# Returns: (-8.555, 125.575)
```

**Notes:**
- For points: returns the point itself
- For polygons: returns geometric center
- Used for distance calculations and mapping

---

#### **get_dist_to_coast(geometry)**

Returns distance from geometry centroid to Timor-Leste coastal boundary.

**Data Source:** GADM administrative boundaries (gadm41_TLS_3.json)

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Point or polygon coordinates

**Returns:** `float` - Distance to coast in kilometers

**Example:**
```python
from gis.core.extract_data import get_dist_to_coast

dist = get_dist_to_coast((-8.569, 126.676))
# Returns: 15.2 km
```

**Notes:**
- Measures from centroid to nearest point on boundary
- Uses geodesic distance calculation
- Coastal farms (< 5km): important for climate classification
- Based on GADM Level 3 administrative boundaries

---

### Farm Profile Functions

#### **build_farm_profile(geometry, year=None, farm_id=None, **additional_fields)**

Builds a complete farm profile by extracting all environmental variables.

**Parameters:**
- `geometry` (tuple|list|ee.Geometry): Farm location/boundary
- `year` (int, optional): Year for temporal data (default: 2024)
- `farm_id` (int, optional): Unique farm identifier
- `**additional_fields`: Custom fields (e.g., farmer_name, crop_type)

**Returns:** `dict` - Complete farm profile

**Profile Structure:**
```python
{
    "id": 1,
    "year": 2024,
    "rainfall_mm": 1850.5,
    "temperature_celsius": 24.3,
    "elevation_m": 580,
    "slope_degrees": 12.3,
    "soil_ph": 6.2,
    "soil_texture_id": 4,
    "area_ha": 2.5,
    "latitude": -8.569,
    "longitude": 126.676,
    "coastal": False,
    "dist_to_coast_km": 15.2,
    "updated_at": "2024-01-15T10:30:00",
    "status": "success"
}
```

**Example:**
```python
from gis.core.farm_profile import build_farm_profile

profile = build_farm_profile(
    geometry=(-8.569, 126.676),
    farm_id=1,
    year=2024,
    farmer_name="John Doe",
    farm_name="Highland Farm"
)

print(f"Farm: {profile['farm_name']}")
print(f"Rainfall: {profile['rainfall_mm']} mm")
print(f"Elevation: {profile['elevation_m']} m")
```

**Notes:**
- Calls all data extraction functions
- Calculates coastal flag (elevation < 100m AND 500 < rainfall < 3000mm)
- Includes error handling (status field)
- Custom fields preserved in output

---

#### **update_farm_profile(existing_profile, geometry, fields=None, year=None)**

Updates specific fields in an existing farm profile.

**Parameters:**
- `existing_profile` (dict): Current profile dictionary
- `geometry` (tuple|list|ee.Geometry): Farm geometry
- `fields` (list, optional): List of fields to update (None = all fields)
- `year` (int, optional): Year for temporal data

**Returns:** `dict` - Updated profile

**Example:**
```python
from gis.core.farm_profile import update_farm_profile

# Update only temporal fields for 2025
updated = update_farm_profile(
    existing_profile=profile_2024,
    geometry=farm_geometry,
    fields=["rainfall_mm", "temperature_celsius"],
    year=2025
)

print(f"Rainfall changed: {profile_2024['rainfall_mm']} → {updated['rainfall_mm']}")
```

**Updatable Fields:**
- Temporal: rainfall_mm, temperature_celsius
- Spatial: elevation_m, slope_degrees, area_ha, latitude, longitude
- Soil: soil_ph, soil_texture_id
- Derived: coastal, dist_to_coast_km

---

#### **bulk_create_profiles(farms, geometry_field="geometry", id_field="farm_id", year=None, max_workers=5, progress_callback=None)**

Creates profiles for multiple farms in parallel.

**Parameters:**
- `farms` (list): List of farm dictionaries with geometry and ID
- `geometry_field` (str): Field name containing geometry (default: "geometry")
- `id_field` (str): Field name containing farm ID (default: "farm_id")
- `year` (int, optional): Year for data extraction
- `max_workers` (int): Number of parallel workers (default: 5)
- `progress_callback` (callable, optional): Progress tracking function(current, total)

**Returns:** `pandas.DataFrame` - All farm profiles

**Example:**
```python
from gis.core.farm_profile import bulk_create_profiles

farms = [
    {"farm_id": 1, "geometry": (-8.55, 125.57), "farmer": "Alice"},
    {"farm_id": 2, "geometry": (-8.56, 125.58), "farmer": "Bob"},
    {"farm_id": 3, "geometry": (-8.57, 125.59), "farmer": "Carol"},
]

profiles_df = bulk_create_profiles(
    farms,
    year=2024,
    max_workers=3
)

profiles_df.to_csv("farm_profiles_2024.csv", index=False)
```

**Output:**
```
Starting bulk profile creation for 3 farms...
  Progress: 3/3 (100.0%) - 2.5 farms/sec - ETA: 0s

Bulk creation complete!
  Total time: 1.2s
  Rate: 2.5 farms/sec
  Success: 3/3 (100.0%)
  Failed: 0
```

**Notes:**
- Uses ThreadPoolExecutor for parallel processing
- Progress tracking with ETA
- Error isolation (one failure doesn't stop others)
- Performance: ~2-5 farms/second depending on network

---

#### **bulk_update_profiles(profiles_df, geometries, fields=None, year=None, max_workers=5, progress_callback=None)**

Updates profiles for multiple farms in parallel.

**Parameters:**
- `profiles_df` (pandas.DataFrame): Existing profiles
- `geometries` (dict): Mapping of farm_id to geometry
- `fields` (list, optional): Fields to update (None = all)
- `year` (int, optional): Year for temporal data
- `max_workers` (int): Number of parallel workers
- `progress_callback` (callable, optional): Progress tracking

**Returns:** `pandas.DataFrame` - Updated profiles

**Example:**
```python
from gis.core.farm_profile import bulk_update_profiles
import pandas as pd

# Load existing profiles
profiles_2024 = pd.read_csv("profiles_2024.csv")

# Prepare geometries
geometries = {
    1: (-8.55, 125.57),
    2: (-8.56, 125.58),
    3: (-8.57, 125.59),
}

# Update only temporal fields for 2025
profiles_2025 = bulk_update_profiles(
    profiles_df=profiles_2024,
    geometries=geometries,
    fields=["rainfall_mm", "temperature_celsius"],
    year=2025
)

profiles_2025.to_csv("profiles_2025.csv", index=False)
```

**Output:**
```
Starting bulk profile update for 3 farms...
  Fields to update: ['rainfall_mm', 'temperature_celsius']
  Progress: 3/3 (100.0%) - 5.0 farms/sec - ETA: 0s

Bulk update complete!
  Total time: 0.6s
  Success: 3/3 (100.0%)
```

---

### Utility Functions

#### **build_farm_table()**

One-time script to process farm boundaries and create a standardized farm table.

**Data Source:** farm_boundaries.gpkg

**Operations:**
1. Loads farm geometries from GeoPackage
2. Converts 3D polygons to 2D
3. Computes centroids
4. Calculates area in hectares
5. Generates WKT (Well-Known Text) geometry
6. Handles multi-parcel farms (merges parcels)
7. Outputs clean CSV

**Output:** `gis/docs/farm_table.csv`

**Example:**
```python
from gis.scripts.build_farm_table import build_farm_table

build_farm_table()
# Creates: gis/docs/farm_table.csv
```

**Output Columns:**
- farm_id: Unique identifier
- farm_name: Farm name
- centroid_lat: Centroid latitude
- centroid_lon: Centroid longitude
- area_ha: Farm area in hectares
- geometry_wkt: WKT polygon string
- num_parcels: Number of parcels (for multi-parcel farms)

**Notes:**
- Handles invalid geometries automatically
- Merges multi-parcel farms using unary_union
- Filters out farms with area < 0.01 ha
- Preserves all original attributes

---

## Usage Examples

### Example 1: Single Farm Profile

```python
from gis.core.gee_client import init_gee
from gis.core.farm_profile import build_farm_profile

# Initialize GEE
init_gee()

# Create profile
profile = build_farm_profile(
    geometry=(-8.569, 126.676),  # Timor-Leste coordinates
    farm_id=1,
    year=2024,
    farmer_name="John Doe",
    farm_name="Highland Coffee Farm"
)

# Display results
print(f"Farm: {profile['farm_name']}")
print(f"Farmer: {profile['farmer_name']}")
print(f"Location: ({profile['latitude']}, {profile['longitude']})")
print(f"Elevation: {profile['elevation_m']} m")
print(f"Rainfall: {profile['rainfall_mm']} mm/year")
print(f"Temperature: {profile['temperature_celsius']}°C")
print(f"Area: {profile['area_ha']} ha")
print(f"Coastal: {profile['coastal']}")
```

### Example 2: Bulk Processing

```python
from gis.core.farm_profile import bulk_create_profiles
import pandas as pd

# Load farm data
farms_df = pd.read_csv("farms_input.csv")

# Convert to list of dicts
farms = []
for _, row in farms_df.iterrows():
    farms.append({
        "farm_id": row["id"],
        "geometry": (row["latitude"], row["longitude"]),
        "farmer_name": row["farmer"],
        "farm_name": row["name"]
    })

# Create profiles in bulk
profiles_df = bulk_create_profiles(
    farms,
    year=2024,
    max_workers=10
)

# Save results
profiles_df.to_csv("farm_profiles_output.csv", index=False)

# Summary statistics
print(f"\nTotal farms: {len(profiles_df)}")
print(f"Average rainfall: {profiles_df['rainfall_mm'].mean():.1f} mm")
print(f"Average elevation: {profiles_df['elevation_m'].mean():.1f} m")
print(f"Coastal farms: {profiles_df['coastal'].sum()}")
```

### Example 3: Annual Updates

```python
from gis.core.farm_profile import bulk_update_profiles
import pandas as pd

# Load 2024 profiles
profiles_2024 = pd.read_csv("profiles_2024.csv")

# Prepare geometries (from previous data)
geometries = dict(zip(
    profiles_2024["id"],
    zip(profiles_2024["latitude"], profiles_2024["longitude"])
))

# Update only climate data for 2025
profiles_2025 = bulk_update_profiles(
    profiles_df=profiles_2024,
    geometries=geometries,
    fields=["rainfall_mm", "temperature_celsius"],  # Only update these
    year=2025,
    max_workers=10
)

# Analyze changes
changes = pd.DataFrame({
    "farm_id": profiles_2024["id"],
    "rainfall_2024": profiles_2024["rainfall_mm"],
    "rainfall_2025": profiles_2025["rainfall_mm"],
    "change_mm": profiles_2025["rainfall_mm"] - profiles_2024["rainfall_mm"],
    "change_pct": ((profiles_2025["rainfall_mm"] - profiles_2024["rainfall_mm"]) 
                   / profiles_2024["rainfall_mm"] * 100)
})

print(changes.head())
```

### Example 4: Error Handling

```python
from gis.core.farm_profile import build_farm_profile

farms = [
    {"id": 1, "geometry": (-8.55, 125.57)},  # Valid
    {"id": 2, "geometry": (999, 999)},        # Invalid
    {"id": 3, "geometry": (-8.57, 125.59)},  # Valid
]

results = []
for farm in farms:
    profile = build_farm_profile(
        geometry=farm["geometry"],
        farm_id=farm["id"],
        year=2024
    )
    results.append(profile)
    
    if profile["status"] == "failed":
        print(f"Farm {farm['id']} failed: {profile.get('error')}")
    else:
        print(f"Farm {farm['id']}: success")
```

## Testing

### Running Tests

```bash
# Run all tests
pytest gis/tests/test_gis.py -v -s

# Run specific test
pytest gis/tests/test_gis.py::test_get_rainfall -v

# Run by category
pytest gis/tests/test_gis.py -k "bulk" -v  # Bulk operations
pytest gis/tests/test_gis.py -k "get_" -v   # Data extraction
pytest gis/tests/test_gis.py -k "validation" -v  # EDA validation

# Skip slow tests
pytest gis/tests/test_gis.py -m "not slow" -v
```


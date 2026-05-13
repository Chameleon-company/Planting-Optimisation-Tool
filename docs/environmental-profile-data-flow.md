# Environmental Profile Data Flow

## Purpose

This document explains how environmental attributes are derived for a farm - from raw boundary data through to the final profile response returned by the API.

It covers the full data flow across four pipeline stages: local PostGIS queries, Google Earth Engine (GEE) extraction, imputation, and normalisation. Reading this document should give a developer enough context to understand, debug, or extend the environmental profiling system without needing to read across multiple files.

This implementation is defined across:

- `backend/src/routers/environmental_profile.py`
- `backend/src/services/environmental_profile.py`
- `backend/src/schemas/environmental_profile.py`
- `gis/core/farm_profile.py`
- `gis/core/extract_data.py`

---

# Table of Contents

- [Pipeline Overview](#pipeline-overview)
- [Data Sources](#data-sources)
- [Data Source Priority](#data-source-priority)
- [End-to-End Pipeline](#end-to-end-pipeline)
- [Imputation](#imputation)
- [Error Handling](#error-handling)
- [Output Schema](#output-schema)
- [Example Output](#example-output)
- [Test Coverage](#test-coverage)
- [Limitations](#limitations)

---

# Pipeline Overview

A farm profile is built on demand when the `GET /profile/{farm_id}` endpoint is called. The pipeline runs inside `EnvironmentalProfileService.run_environmental_profile()`.

```text
Client Request
      ↓
environmental_profile router
 - Requires OFFICER role or higher (403 if not met)
 - Checks if farm is accessible to the requesting user (404 if not found or not owned)
 - Checks cache: if profile:{farm_id} exists → return cached JSON immediately
      ↓ (cache miss only)
EnvironmentalProfileService.run_environmental_profile()
      ↓
Local PostGIS queries (soil pH, soil texture, riparian flag)
      ↓
build_farm_profile() - GEE extraction
      ↓
GEE failed? → Fallback to stored Farm DB values
      ↓
impute_missing() - Fills missing fields
      ↓
Normalisation and range validation
      ↓
Write to cache under key profile:{farm_id}
      ↓
FarmProfileResponse returned
```

The `data_source` field in the response indicates which path was taken:

- `"hybrid"` - GEE extraction succeeded. Local overrides may still apply for soil pH and texture.
- `"fallback"` - GEE failed. Values were read from the stored Farm DB record instead.

## Endpoint

```http
GET /profile/{farm_id}
```

**Path parameter:**
- `farm_id` - integer ID of the farm to profile

**Request body:** None. This endpoint takes no request body.

**Required headers:**
```http
Authorization: Bearer <JWT>
```

## Authentication & Authorisation

The endpoint requires a valid JWT. The authenticated user's identity is read from `current_user` via the `require_role` dependency.

- **Admin** - Can profile any farm
- **Supervisor** - Can profile any farm
- **Officer** - Can profile own farms only

Officers are filtered by `user_id` - a valid `farm_id` belonging to a different officer returns 404, not 403. The endpoint is limited to 10 requests per minute per user.


---

# Data Sources

## Global Datasets (Google Earth Engine)

The following attributes are extracted via GEE. All datasets were validated against 3201 farm measurements collected by the Product Owner.

- **Rainfall** - CHIRPS dataset at 5.5 km resolution. Validated at r=0.97, MAE=24mm.
- **Temperature** - MODIS LST (MOD11A2) at 1 km resolution. Validated at r=0.88, MAE=3.82°C. A bias correction of −3.82°C is applied automatically to convert land surface temperature to air temperature.
- **Elevation** - SRTM DEM at 90 m resolution. Validated at r=0.998, MAE=8m.
- **Slope** - Derived from the SRTM DEM using `ee.Terrain.slope()` at 90 m resolution.
- **Soil pH** - OpenLandMap at 250 m resolution. Validated at r=0.19, MAE=1.27. Low confidence.

## Local Datasets (PostGIS)

The following attributes are resolved from local spatial datasets before GEE is called:

- **Soil pH** - Point query against the Product Owner soil survey raster (911 field samples). Preferred over the GEE OpenLandMap dataset.
- **Soil texture** - Point query against the QGIS soil texture raster. Falls back to the Farm DB `soil_texture_id` record if no raster value is found.
- **Riparian flag** - Boolean result of a polygon intersection between the farm boundary and the waterway dataset, executed in PostGIS.

---

# Data Source Priority

Several attributes have multiple possible sources. The pipeline resolves them in priority order:

**Soil pH:**
Local PostGIS raster → GEE OpenLandMap (low confidence) → (Fallback) Farm DB record → Imputation

**Soil texture:**
Local PostGIS raster → Farm DB `soil_texture_id` → Imputation

**Rainfall:**
GEE CHIRPS → Farm DB record → Imputation

**Temperature:**
GEE MODIS → Farm DB record → Imputation

**Elevation:**
GEE SRTM → Farm DB record → Imputation

**Slope:**
GEE SRTM-derived → Imputation

**Riparian:**
PostGIS intersection → Farm DB record

GEE's OpenLandMap soil pH has very poor accuracy for Timor-Leste (r=0.18). Out-of-range pH values (outside 5.0–8.5) are explicitly nulled before imputation so they are treated as missing rather than passed through silently.

---

# End-to-End Pipeline

## 1. Fetch Boundary and Farm Record

The service fetches the `FarmBoundary` and `Farm` records from the database using the `farm_id`. If either record is missing, `None` is returned and the API raises a 404.

The boundary geometry (`MultiPolygon` or `Polygon`) is parsed into a Shapely object. The first polygon ring is extracted and reformatted as `[(lat, lon), ...]` for the GEE geometry parser. The centroid is also computed at this step for use in local raster point queries.

### Importance

The boundary geometry drives all downstream spatial queries. The centroid is used for local raster lookups (soil pH, soil texture), while the full polygon is used for riparian intersection.

---

## 2. Local PostGIS Queries

Three attributes are resolved locally before GEE is called:

**Riparian flag** - a spatial intersection between the farm boundary polygon and a buffered waterway dataset, executed via `get_riparian_flags()`.

**Soil pH** - a point query against the local soil pH raster using `get_soil_ph_for_point(db, lat, lon)`. Values outside the dataset's valid range (5.0–8.5) are rejected and treated as missing.

**Soil texture** - a point query via `get_soil_texture_for_point(db, lat, lon)`. If no raster value is found and the Farm record has a `soil_texture_id`, the texture name is resolved from the `SoilTexture` table.

---

## 3. GEE Extraction

`build_farm_profile()` (in `gis/core/farm_profile.py`) is called with the formatted geometry, farm ID, riparian flag, and any locally-resolved pH and texture values.

Internally it calls:

- `get_rainfall()` - CHIRPS annual total for the default year 
- `get_temperature()` - MODIS LST mean with −4.43°C bias correction applied
- `get_elevation()` - SRTM mean elevation
- `get_slope()` - SRTM-derived slope in degrees
- `get_area_ha()` - geodesic area calculation
- `get_centroid_lat_lon()` - centroid coordinates
- `get_ph()` - only called if local pH was not provided
- `get_texture_id()` - only called if local texture was not provided

The coastal flag is derived from the extracted values using the condition `elevation < 100m AND 500 ≤ rainfall ≤ 3000mm`.

If GEE extraction raises an exception, `build_farm_profile()` returns `{"status": "failed", ...}` rather than raising. If extraction succeeds, `data_source` is set to `"hybrid"`.

### Importance

GEE is a network call and can fail due to credential issues, quota limits, or connectivity problems. The `status` field allows the pipeline to detect failure and fall through to the fallback path rather than returning corrupt data.

---

## 4. Fallback to Farm DB Values

If `build_farm_profile()` returns `status: "failed"`, the pipeline assembles a profile using: locally‑resolved raster values for soil pH and soil texture (if available), the Farm database record for all other attributes (rainfall, temperature, elevation, slope, area, etc.).

`data_source` is set to `"fallback"` in this case.

---

## 5. Imputation

After the profile is assembled from either GEE or fallback, out-of-range values are nulled before imputation runs:

- Rainfall values outside `RAINFALL_MIN` / `RAINFALL_MAX` are set to `None`
- Temperature values outside `TEMPERATURE_MIN` / `TEMPERATURE_MAX` are set to `None`

The imputer then checks which target fields are `None`. If any are missing, `impute_missing()` is called to fill them. The fields that can be imputed are `slope_degrees` (imputer key: `slope`), `soil_ph` (imputer key: `ph`), `rainfall_mm`, `temperature_celsius`, and `elevation_m`.

When a field is imputed, a corresponding flag is set on the profile (e.g. `ph_imputed: true`) and persisted to the `Farm` DB record.

After assembling the profile (`hybrid` or `fallback`), any missing numeric fields are imputed. The only case where imputation is skipped is when the profile is completely empty, but in practice the fallback path should always supply the required base features.

---

## 6. Normalisation

The final profile is normalised before being returned:

- `temperature_celsius` - rounded to nearest integer
- `rainfall_mm` - rounded to nearest integer
- `soil_ph` - rounded to 1 decimal place
- `slope_degrees` - rounded to 2 decimal places

The response is also written to cache under the key `profile:{farm_id}` to avoid redundant GEE calls on repeat requests.

---

# Imputation

The imputation package fills missing numeric fields using available profile features as inputs.

Key behaviours:

- Only runs if one or more target fields are `None` after GEE extraction or fallback
- Sets `{field}_imputed: True` flags on both the profile dict and the `Farm` DB record
- Raises `ImputationError` (returned as HTTP 503) if imputation fails or produces unrealistic values 

---

# Error Handling

 - Missing or invalid JWT - 401 returned
 - Insufficient role - 403 returned
 - Farm not accessible to requesting user - 404 returned - `"Farm with ID {farm_id} not found."` 
 - Farm boundary record missing - 404 returned - `"Farm boundary not found for farm_id: {farm_id}"` 
 - Imputation model failure - 503 returned - `ImputationError` message

GEE extraction failure does not produce an error response - the pipeline falls through to the fallback path automatically and returns a valid profile with `"data_source": "fallback"`.

# Output Schema

The response is validated and serialised by `FarmProfileResponse`. Fields that are `None` are excluded from the response (`response_model_exclude_none=True`), so imputation flags only appear in the output when they are `True`.

Response fields:

- `id` - Farm ID
- `status` - Always `"success"` in a valid response
- `data_source` - `"hybrid"` or `"fallback"`
- `rainfall_mm` - Integer; nulled if outside valid range
- `temperature_celsius` - Integer; nulled if outside valid range
- `elevation_m` - Integer
- `ph` - Decimal (aliased from `soil_ph`); 1 decimal place
- `slope` - Decimal (aliased from `slope_degrees`); 2 decimal places
- `soil_texture` - USDA texture class name
- `soil_texture_id` - Integer 1–12 (USDA classification)
- `area_ha` - Decimal
- `latitude` - Decimal
- `longitude` - Decimal

- `coastal` - Boolean; derived flag
- `riparian` - Boolean
- `nitrogen_fixing` - Boolean; from Farm record
- `shade_tolerant` - Boolean; from Farm record
- `bank_stabilising` - Boolean; from Farm record

- `elevation_m_imputed` - Boolean; present only if imputed
- `slope_imputed` - Boolean; present only if imputed
- `temperature_celsius_imputed` - Boolean; present only if imputed
- `rainfall_mm_imputed` - Boolean; present only if imputed
- `ph_imputed` - Boolean; present only if imputed

The internal profile dictionary (produced by the service and GEE layer) uses `soil_ph` and `slope_degrees` as keys. The API response renames these; `soil_ph` becomes `ph` and `slope_degrees` becomes `slope`. If you are reading service logs or debugging the raw profile dict, expect the internal names. The API response uses the aliased names.

---

# Example Output

A hybrid profile where GEE succeeded and local soil data was available:

```json
{
  "id": 42,
  "status": "success",
  "data_source": "hybrid",
  "rainfall_mm": 1851,
  "temperature_celsius": 24,
  "elevation_m": 580,
  "ph": 6.3,
  "slope": 12.34,
  "soil_texture": "loam",
  "soil_texture_id": 4,
  "area_ha": 2.450,
  "latitude": -8.569,
  "longitude": 126.676,
  "coastal": false,
  "riparian": true,
  "nitrogen_fixing": false,
  "shade_tolerant": true,
  "bank_stabilising": false
}
```

A fallback profile where GEE failed and rainfall was filled by imputation:

```json
{
  "id": 43,
  "status": "success",
  "data_source": "fallback",
  "rainfall_mm": 1851,
  "temperature_celsius": 24,
  "elevation_m": 580,
  "ph": 6.3,
  "slope": 12.34,
  "soil_texture": "clay loam",
  "soil_texture_id": 8,
  "area_ha": 2.450,
  "latitude": -8.612,
  "longitude": 126.643,
  "coastal": false,
  "riparian": false,
  "nitrogen_fixing": false,
  "shade_tolerant": false,
  "bank_stabilising": false,
  "rainfall_mm_imputed": true
}
```

---

# Test Coverage

Test files:
- `backend/tests/test_environmental_profile_router.py`
- `backend/tests/test_environmental_profile_service.py`
- `backend/tests/test_environmental_profile.py`

The tests verify:

- Cache miss - service is called and result returned on first request
- Cache hit - service is not called on repeat request; cached response returned
- Imputation not triggered when all fields are present
- Imputation values and flags correctly set when fields are missing
- Non-imputed fields have no imputation flag in the response
- Imputation model unavailability raises `ImputationError` (HTTP 503)
- `None` returned when `build_farm_profile()` returns `None`
- Profile returns valid `soil_ph` from local raster or fallback
- Profile handles invalid/missing pH (e.g. `ph=0.0`) without failing
- Profile returns valid `soil_texture` from local raster or Farm DB fallback

# Limitations

## Farm Must Exist Before Profile Can Be Generated

The pipeline requires both a `Farm` record and a `FarmBoundary` record to exist in the database before it can run. This means the endpoint cannot be used to profile a candidate farm boundary before the farm has been saved.

In the intended UI workflow where a user draws a boundary, reviews the derived environmental profile, then confirms or adjusts values before saving a default Farm record and boundary must be written to the database first before this endpoint can be called. The profile can not generated be from a boundary alone.
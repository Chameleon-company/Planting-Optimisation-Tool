# Output Schema for build_farm_profile

This document explains the internal output schema returned by the `build_farm_profile()` function in `gis/core/farm_profile.py`.

The profile combines environmental attributes extracted from Google Earth Engine (GEE), locally resolved spatial data, and derived environmental indicators.

---

## Output Fields

| Field | Type | Description |
|---|---|---|
| `id` | int/null | Farm ID passed into the profile builder. |
| `year` | int | Year used for environmental data extraction. |
| `rainfall_mm` | int | Average annual rainfall extracted from configured datasets. |
| `temperature_celsius` | int | Average land surface temperature extracted from configured datasets. |
| `elevation_m` | int | Mean elevation of the farm in metres. |
| `slope_degrees` | float | Mean terrain slope in degrees. |
| `soil_ph` | float | Soil pH value at the farm location. |
| `soil_texture_id` | int/null | USDA soil texture classification ID (1–12). |
| `soil_texture` | string/null | Local soil texture name if available. |
| `area_ha` | float | Farm area in hectares. |
| `latitude` | float | Geographic centroid latitude. |
| `longitude` | float | Geographic centroid longitude. |
| `coastal` | bool | Derived environmental flag indicating coastal-like conditions. |
| `riparian` | bool/null | Riparian flag passed from backend service. |
| `updated_at` | string | ISO timestamp when the profile was generated. |
| `status` | string | Profile generation status (`success` or `failed`). |

---

## JSON Example

```json
{
  "id": 1,
  "year": 2024,
  "rainfall_mm": 1843,
  "temperature_celsius": 24,
  "elevation_m": 950,
  "slope_degrees": 11.5,
  "soil_ph": 6.2,
  "soil_texture_id": 8,
  "soil_texture": "clay loam",
  "area_ha": 3.742,
  "latitude": -8.57,
  "longitude": 126.676,
  "coastal": true,
  "riparian": false,
  "updated_at": "2026-05-12T10:30:00",
  "status": "success"
}
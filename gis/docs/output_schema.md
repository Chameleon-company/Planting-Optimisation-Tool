# Outout schema for build_farm_profile
This document explains the output schema from the build_farm_profile function. The output from the recommender system needs to include the exclusions handling output plus this output.

## Minimal Output Schema
*  `id` *(int, required)* - ID from farms.
*  `temperature_celsius` *(int)* - 5-year average land surface temperature (°C).
*  `rainfall_mm` *(int)* - 5-year average annual rainfall at the farm location (mm).
*  `elevation_m` *(int)* - Mean elevation of the farm (m)
*  `ph` *(float)* - Soil pH at the farm location.
*  `soil_textures)ud` *(int)* - Dominant soil texture.
*  `area_ha` *(float)* - Farm area in hectares.
*  `latitude` *(float)* - Geographic latitude.
*  `longitude` *(float)* - Geographic longitude 
*  `coastal` *(bool)* - true if farm is within 30 km of coast, false otherwise, null if distance is missing.
*  `slope` *(float)* - Mean slope of the farm (degrees).

**JSON example**

```json
{
  "id": 1,
  "rainfall_mm": 1843,
  "temperature_celsius": 24,
  "elevation_m": 950,
  "ph": 6.2,
  "soil_texture_id": 8,
  "area_ha": 3.742,
  "latitude": -8.57,
  "longitude": 126.676,
  "coastal": true,
  "slope": 11.5,
}
```
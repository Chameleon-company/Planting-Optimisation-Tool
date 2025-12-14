# Outout schema for build_farm_profile
This document explains the output schema from the build_farm_profile function. The output from the recommender system needs to include the exclusions handling output plus this output.

## Minimal Output Schema
*  `id` *(int, required)* - ID from farms.
*  `geometry` *(list [tuple])* - Input geometry in [lon, lat] format (point or polygon ring).
*  `temperature_celsius` *(int)* - 5-year average land surface temperature (°C).
*  `rainfall_mm` *(int)* - 5-year average annual rainfall at the farm location (mm).
*  `ph` *(float)* - Soil pH at the farm location.
*  `area_ha` *(float)* - Farm area in hectares.
*  `soil_textures` *(string)* - Dominant soil texture.
*  `elevation_m` *(int)* - Mean elevation of the farm (m)
*  `slope` *(float)* - Mean slope of the farm (degrees).
*  `dist_to_coast_km` *(float)* - Distance from farm centroid to coast (km). 
*  `coastal region` *(bool)* - true if farm is within 30 km of coast, false otherwise, null if distance is missing.

**JSON example**

```json
{
  "farm_id": 1,
  "geometry": [(-8.569, 126.676),(-8.570, 126.676),(-8.570, 126.677)],
  "rainfall_mm": 1843,
  "temperature_celsius": 24,
  "ph": 6.2,
  "area_ha": 3.742,
  "soil_textures": "clay loam",
  "elevation_m": 950,
  "slope": 11.5,
  "dist_to_coast_km": 12.384,
  "coastal_flag": true
}
```

# **Data Dictionary**
These data dictionaries contains all variables for the recommendation system (suitability scoring and exclusions) and farm profile extraction and aligns with the database schema.

## **Farms Dataset**

| Column Name          | Type        | Unit     | Description                     | Constraints                        |
| -------------------- | ----------- | -------- | ------------------------------- | ---------------------------------- |
| `id`            | Integer      | —        | Unique identifier for each farm | Required, unique                   |
| `rainfall_mm`    | Float       | `mm` | Annual average rainfall         | Required, Range: `1000`–`3000`             |
| `temperature_celsius` | Float       | `celsius` | Annual average temperature      | Required, Range: `15`–`30`             |
| `elevation_m`    | Float       | `m` | Elevation above sea level       | Required, Range: `0`–`2963`             |
| `ph`                 | Float       | pH units | Soil acidity/alkalinity         | Required, Range: `4.0`–`8.5`             |
| `soil_texture_id`          | Integer | —        | Dominant soil texture type id    | Required, Allowed: See Soil Textures table  |
| `area_ha`          | Float       | `ha`  | Farm area            | Range: 0 to 100                 |
| `slope`          | Float       | `degree`  | Indicates how steep the farm terrain is, based on elevation gradients.            | Range: 0 to 90                 |
| `latitude`           | Float       | `degree`  | Geographic latitude             | Range: -90 to 90                   |
| `longitude`          | Float       | `degree`  | Geographic longitude            | Range: -180 to 180                 |
| `coastal`    | Boolean   | —        | Is a coastal environment   | Required, Allowed: True/False    |
| `riparian`    | Boolean   | —        | Is a riparian environment   | Required, Allowed: True/False    |
| `nitrogen_fixing`    | Boolean   | —        | Needs Nitrogen-fixing species  | Required, Allowed: True/False    |
| `shade_tolerant`    | Boolean   | —        | Needs shade tolerant species  | Required, Allowed: True/False    |
| `bank_stabilising`    | Boolean   | —        | Needs erosion control species  | Required, Allowed: True/False    |
| `agroforestry_type_id`    | List (integers)   | —        | Required agroforestry types          | Required, Allowed: See Agroforestry Types table |

***

## **Species Dataset**

| Column Name               | Type   | Unit     | Description                              | Constraints                        |
| ------------------------- | ------ | -------- | ---------------------------------------- | ---------------------------------- |
| `id`              | Integer | —        | Unique identifier for each species       | Required, unique                   |
| `name`            | String | —        | Scientific name of the species | Required                           |
| `common_name`            | String | —        | Common name of the species | Required                           |
| `rainfall_mm_min`            | Float  | `mm` | Minimum preferred annual rainfall        | Required, Range: `200`–`5000`             |
| `rainfall_mm_max`            | Float  | `mm` | Maximum preferred annual rainfall        | Required, Range: `200`–`5000`             |
| `temperature_celsius_min`         | Float  | `celsius` | Minimum preferred temperature            | Required, Range: `10`–`40`             |
| `temperature_celsius_max`         | Float  | `celsius` | Maximum preferred temperature            | Required, Range: `10`–`40`             |
| `elevation_m_min`            | Float  | `m` | Minimum preferred altitude               | Required, Range: `0`–`3000`             |
| `elevation_m_max`            | Float  | `m` | Maximum preferred altitude               | Required, Range: `0`–`3000`             |
| `ph_min`                  | Float  | pH units | Minimum preferred soil pH                | Required, Range: `4.0`–`7.0`             |
| `ph_max`                  | Float  | pH units | Maximum preferred soil pH                | Required, Range: `7.0`–`8.5`             |
| `preferred_soil_texture_id`    | List (integers)   | —        | List of compatible soil texture ids            | Required, See Soil Textures table    |
| `coastal`    | Boolean   | —        | Suitable for costal environment   | Required, Allowed: True/False    |
| `riparian`    | Boolean   | —        | Suitable for wetlands adjacent to rivers and streams   | Required, Allowed: True/False    |
| `nitrogen_fixing`    | Boolean   | —        | Provides Nitrogen-fixing function  | Required, Allowed: True/False    |
| `shade_tolerant`    | Boolean   | —        | Is tolerant to shade  | Required, Allowed: True/False    |
| `bank_stabilising`    | Boolean   | —        | Can be used for erosion control  | Required, Allowed: True/False    |
| `agroforestry_type_ids`    | List   | —        | List of compatible agroforestry uses          | Required, Allowed: See Agroforestry Types table  |

## **Soil Textures**

| Name               | ID   | 
| -------------------|------ | 
| `sand`             | 1    |
| `loamy sand`       | 2    |
| `sandy loam`       | 3    |
| `loam`             | 4    |
| `silt loam`        | 5    |
| `silt`             | 6    |
| `sandy clay loam`  | 7    |
| `clay loam`        | 8    |
| `silty clay loam`  | 9    |
| `sandy clay`       | 10   |
| `silty clay`       | 11   |
| `clay`             | 12   |


## **Agroforestry Types**

| Name             | ID  |
| -----------------|----- |
| `block`            | 1   |
| `boundary`         | 2   |
| `intercropping`    | 3   |
| `mosaic`           | 4   |

***

## **Notes**

*   **Ranges must be ordered**: For species, `*_min` ≤ `*_max`.
*   **Units normalization**: All numeric values should be converted to standard units (e.g., mm/year for rainfall, °C for temperature).
*   **Categorical normalization**: Use canonical names (e.g., "Loam" not "loamy soil").
*   **Missing values**: TBD if any missing values are allowed.

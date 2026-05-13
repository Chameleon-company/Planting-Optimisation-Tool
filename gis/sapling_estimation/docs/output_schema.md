# Output schema for Sapling Estimation Feature
This document outlines the response schema returned by the sapling estimation feature.

## Response Fields

| Field | Type | Description |
|---|---|---|
| `status` | string | Response status |
| `id` | integer/null | Optional estimation identifier |
| `pre_slope_count` | integer | Planting point count before slope filtering |
| `aligned_count` | integer | Final planting point count after slope filtering |
| `optimal_angle` | integer | Rotation angle that maximizes planting capacity |
| `rotation_average` | float | Average planting count across tested rotations |
| `rotation_std_dev` | float | Standard deviation of rotation counts |

### JSON Example

```json
{
  "status": "success",
  "id": 1,
  "pre_slope_count": 320,
  "aligned_count": 250,
  "optimal_angle": 45,
  "rotation_average": 298.4,
  "rotation_std_dev": 12.7
}
```

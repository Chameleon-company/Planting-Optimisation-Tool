# Output schema for Sapling Estimation Feature
This document outlines the output schema from the feature/estimate.py.

## Minimal Output Schema

*  Planting plan *(dict, required)* - Final planting plan.
    *  `sapling_count` *(int, required)* - Final sapling count.
    *  `optimal_angle` *(int, required)* - Optimal rotation angle.

### JSON example

```json
{
  "sapling_count": 250,
  "optimal_angle": 45
}
```

# Overview
This document outlines the structure of the Sapling Estimator Feature.
It is designed to support the Planting Optimisation Tool by estimating the maximum number of saplings that can be planted on a farm, while considering terrain features such as slope and rotation.

```

gis/
│
├── sapling_estimation/
│   │
│   ├── docs/
│   │   │
│   │   ├── images/
│   │   │   └── flowchart.png   # Sapling Estimator flowchart
│   │   │
│   │   ├── feature_summary.md  # Sapling Estimator overview
│   │   ├── output_schema.md    # Sapling Estimator output schema
│   │   └── README.md           # Sapling Estimator structure
│   │
│   ├── data/
│   │   └── DEM.tif         # DEM file containing elevation data
│   │
│   ├── __init__.py
│   ├── slope_raster.py     # Computes slope raster
│   ├── planting_points.py  # Generates planting points grid
│   ├── rotation.py         # Determines best rotation angle that maximizes planting points and rotates grid
│   ├── slope_rules.py      # Apply slope rules and returns adjusted (final) sapling count
│   └── estimate.py         # Calls all module functions and returns final results (Sapling count, Optimal rotation angle)
│
├── tests/
│   ├── test_slope_raster.py     # pyTest for slope_raster.py
│   ├── test_planting_points.py  # pyTest for planting_points.py
│   ├── test_rotation.py         # pyTest for rotation.py
│   └── test_slope_rules.py      # pyTest for slope_rules.py
│
├── pyproject.toml  # Configuration file
├── uv.lock         # Freezes installed dependencies
│

```

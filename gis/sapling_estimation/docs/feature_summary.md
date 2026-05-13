# Sapling Estimation Feature

## Introduction
This document outlines the estimation algorithm used to estimate the maximum number of saplings that can be planted on a farm, while considering terrain features such as slope and rotation.

The sapling estimation feature accepts `farm_id`, `spacing_x`, `spacing_y`, and `max_slope` as inputs. The system retrieves the farm boundary from the database and matches it against the Digital Elevation Model (DEM) raster to generate slope data for terrain analysis.

A planting grid is generated using the configured spacing values (`spacing_x`, `spacing_y`) to define planting area dimensions. The grid is then rotated through angles between 0–90 degrees to identify the orientation that produces the maximum planting count.

A configurable slope threshold (`max_slope`) is applied to remove planting points located on terrain that exceeds the allowed slope. The algorithm returns the optimised planting count, optimal rotation angle, and rotation statistics for the input farm.

The computational cost increases with the number of generated planting points and terrain sampling operations. Factors such as planting density, farm boundary complexity, and rotation analysis can affect processing time.

## Inputs and Outputs

### Inputs
#### DEM Raster (DEM.tif)
Provides farm elevation data, used for computing slope.

#### Farm Boundary Polygon (Shapely file passed by API)
Defines the input farm's boundaries/polygons, used for generating planting points.

#### Spacing and Slope Parameters
- `spacing_x` – Horizontal spacing between saplings
- `spacing_y` – Vertical spacing between saplings
- `max_slope` – Maximum allowed terrain slope for planting

### Outputs

#### Pre-Slope Count
Number of planting points before slope filtering.

#### Final Aligned Count
Final planting point count after applying slope filtering.

#### Optimal Rotation Angle
Rotation angle that maximizes planting capacity.

#### Rotation Statistics
- Rotation average
- Rotation standard deviation

Used to analyse planting density consistency across tested rotations.

#### Planting Points Grid (final_grid.shp)
Defines the planting areas of the farm, adjusted after applying slope rules.
*This file is saved/output only in debug mode

## Core Modules

### slope_raster.py
Purpose: Compute farm slope values.

Output: slope array, raster transform object, raster profile

Logic:
* Accepts DEM.tif and farm polygon.
* Clips DEM data to the farm polygon.
* Computes x and y gradient, then magnitude.
* Converts magnitude to angle then degrees.
* Contains a test function to validate slope values.

### planting_points.py
Purpose: Generates a grid of planting points that defines the farm's planting areas.

Output: Initial planting grid

Logic:
* Accepts farm polygon.
* Generates a regular grid by applying user-defined spacing rules (`spacing_x`, `spacing_y`) and farm polygon bounds.
* Creates points within the farm polygon boundary.

### rotation.py
Purpose: Determines the optimal rotation angle for the planting points grid, and rotates the grid.

Output: Optimal rotation angle, Rotated planting grid

Logic:
* Accepts initial planting grid.
* Generates a base grid covering the farm polygon.
* Tests rotation angles from 0 to 90 degrees by rotating the polygon around the farm centroid.
* For each tested angle, counts the number of rotated points that fall within the farm polygon.
* Selects the angle with the highest planting point count.
* Applies the optimal angle to the base grid to produce the final rotated grid.
* Contains a test function to validate that rotation does not reduce planting points.

### slope_rules.py
Purpose: Apply slope rules to adjust planting points based on terrain steepness.

Output: Adjusted/Final planting grid

Logic:
* Accepts slope array rotated planting grid.
* Converts planting point coordinates into raster row/column indices.
* Samples slope values from the slope raster.
* Removes points with slope values above the user-provided `max_slope` threshold.

### estimate.py
Purpose: Orchestrator module that calls all core modules to produce the final planting plan.

Output: Pre-slope count, final aligned count, optimal rotation angle, rotation statistics, and final planting grid

Logic:
* Accepts farm polygon, spacing parameters (`spacing_x`, `spacing_y`), and slope threshold (`max_slope`) from the API.
* Load DEM.tif file to pass to the first function.
* Executes all functions in slope_raster.py, planting_points.py, rotation.py and slope_rules.py in order.
* Contains a debug feature for inspecting final planting grid.
* Returns estimation metrics including pre_slope_count, aligned_count, optimal_angle, rotation_average, rotation_std_dev.

## Feature Flowchart
The Back-end API calls the sapling_estimation function in the estimate.py module, and passes the farm polygon, spacing parameters, and slope threshold. The estimate.py module then calls the functions in all modules in order, by first passing DEM.tif data and farm polygon into slope_raster.py. Through the function calling process, the module receives the optimal rotation angle from `rotation.py` and the final aligned planting count from `slope_rules.py`. Finally, the `estimate.py` module returns the estimation metrics as a dictionary back to the API.

![Sapling Estimation Flowchart](images/flowchart.png)

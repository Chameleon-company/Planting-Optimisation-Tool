# Sapling Estimation Feature

## Introduction
This document outlines the estimation algorithm used to estimate the maximum number of saplings that can be planted on a farm, while considering terrain features such as slope and rotation.

The feature begins with a farm boundary/polygon for the input farm that is passed by the API, it matches the polygon with the Digital Elevation Model (DEM) raster, which is converted into a slope raster to identify terrain steepness. A square grid of planting points is generated using the default 3m spacing to define the planting areas (Each planting area would be a 3x3m square); the gird is then rotated by potential angles to determine the orientation that maximizes sapling count. Finally, a slope rule of 15 degrees is applied to remove planting points on the terrain that is too steep, and the estimator/main algorithm outputs the final sapling count and optimal rotation angle of the input farm, which is passed back to the API.

The algorithm scales with the number of planting points. Larger farms produce more points, which increases computation time for grid generation, rotation mechanism, and slope sampling.

## Inputs and Outputs

### Inputs
#### DEM Raster (DEM.tif)
Provides farm elevation data, used for computing slope.

#### Farm Boundary Polygon (Shapely file passed by API)
Defines the input farm's boundaries/polygons, used for generating planting points.

### Outputs
#### Optimal Rotation Angle
Defines the orientation of the planting points grid that maximizes sapling count.

#### Final Sapling Count
An estimate of the maximum number of saplings that can be planted on the farm, after applying slope rules and grid rotation.

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
* Generates a regular grid by applying spacing rules (3m) and farm polygon bounds.
* Creates points within the farm polygon boundary.

### rotation.py
Purpose: Determines the optimal rotation angle for the planting points grid, and rotates the grid.

Output: Optimal rotation angle, Rotated planting grid

Logic:
* Accepts initial planting grid.
* Generates a base grid covering the farm polygon.
* Tests rotation angles from 0 to 90 degrees by rotating the grid around the farm centroid.
* For each tested angle, count the number of rotated points that fall within the farms.
* Select the angle with the highest planting point count.
* Applies the optimal angle to produce the final rotated grid.
* Contains a test function to validate that rotation does not reduce planting points.

### slope_rules.py
Purpose: Apply slope rules to adjust planting points based on terrain steepness.

Output: Adjusted/Final planting grid

Logic:
* Accepts slope array rotated planting grid.
* Converts planting point coordinates into raster row/column indices.
* Samples slope values from the slope raster.
* Removes points with slope values above the maximum threshold (15 degrees).

### estimate.py
Purpose: Orchestrator module that calls all core modules to produce the final planting plan.

Output: Final sapling count, Optimal rotation angle, Final planting grid

Logic:
* Accepts farm polygon and spacing from API.
* Load DEM.tif file to pass to the first function.
* Executes all functions in slope_raster.py, planting_points.py, rotation.py and slope_rules.py in order.
* Contains a debug feature for inspecting final planting grid.
* Returns a dictionary containing sapling count and optimal angle.

## Feature Flowchart
The Back-end API calls the sapling_estimation function in the estimate.py module, and passes the farm polygon and spacing rule. The estimate.py module then calls the functions in all modules in order, by first passing DEM.tif data and farm polygon into slope_raster.py. Through the function calling process, it will receive the optimal rotation angle from rotation.py, and the final sapling count from slope_rules.py through the output. Finally, the estimate.py module passes both outputs as a dictionary back to the API.

![Sapling Estimation Flowchart](images/flowchart.png)

## Additional Information
* The 15 degrees threshold for the slope rule has been choosen just for demonstration and is not based on any evidence.
* The slope rule is hardcoded and cannot be changed via input.

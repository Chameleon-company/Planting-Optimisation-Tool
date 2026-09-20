# Planting Optimisation Tool
[![POT frontend infrastructure](https://github.com/Chameleon-company/Planting-Optimisation-Tool/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Chameleon-company/Planting-Optimisation-Tool/actions/workflows/frontend-ci.yml)
[![POT Back-end Testing](https://github.com/Chameleon-company/Planting-Optimisation-Tool/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Chameleon-company/Planting-Optimisation-Tool/actions/workflows/backend-ci.yml)

[![POT Data Science Testing](https://github.com/Chameleon-company/Planting-Optimisation-Tool/actions/workflows/ds-ci.yml/badge.svg)](https://github.com/Chameleon-company/Planting-Optimisation-Tool/actions/workflows/ds-ci.yml)
[![POT GIS Testing](https://github.com/Chameleon-company/Planting-Optimisation-Tool/actions/workflows/gis-ci.yml/badge.svg)](https://github.com/Chameleon-company/Planting-Optimisation-Tool/actions/workflows/gis-ci.yml)

A data-driven recommendation system designed to support sustainable reforestation and agroforestry planning in Timor-Leste. The tool identifies the most suitable tree species for a given farm by analysing environmental conditions, species requirements, and geospatial datasets.

This project is developed in collaboration with the xPand Foundation under the Rai Matak Program.

For contribution guidelines and to get started working on the project, see [CONTRIBUTING.md](CONTRIBUTING.md)

## Purpose

Smallholder farmers in Timor-Leste face low tree-survival rates due to poor environmental matching and limited access to ecological data. The Planting Optimisation Tool addresses this challenge by:

- Analysing farm-level conditions (rainfall, soil pH, elevation, temperature, slope, area);
- Matching farms with optimal, cautionary, and unsuitable tree species;
- Explaining limiting factors that may affect survival;
- Generating simple, accessible reports for field officers and supervisors.

## Core Features

### Species Recommendation
- Suitability scoring based on rainfall, pH, temperature, elevation, soil class, and other variables.  
- Expert-driven weighting using AHP.
- Data-driven and hybrid weight calculation.
- Species-specific exclusion rules.
- Exclusion rule and dependency management.
- Biological dependency enforcement.
- Ecological function integration.
- Species management through the API and user interface.

### Environmental Profiling 
- Extraction of environmental variables from geospatial datasets and hybrid GIS/GEE data sources (e.g., rainfall, elevation, slope, and soil). 
- Integration with national datasets such as Seeds of Life.   
- Farm-level environmental profiles for decision support.
- DEM data integration and result storage.
- GEE baseline analysis.
- Farm spatial visualisation.
- Riparian zone identification.
- Environmental data imputation and data flagging.


### Sapling Estimation
- Calculates recommended sapling count based on farm area, terrain, planting profile (e.g. 3m × 3m spacing).
- Calculates recommended sapling counts using configurable planting spacing, terrain slope limits, and farm geometry.
- Interactive single-farm sapling estimator.
- Sapling estimation algorithm performance optimisation.
- Riparian calculation improvements.

### User-Facing Web Interface

- Input forms for farm conditions and environmental parameters.
- Species recommendation and environmental profile pages.
- Interactive frontend built with React and Vite.
- Visualization of environmental profile and sapling estimation outputs.
- Farm record management UI.
- Farm spatial visualisation.
- Species management UI.
- Compatibility matrix editor UI.
- Exclusion rules and dependencies UI.
- Admin dashboard foundation and core settings.
- Confirmation dialog before deleting a farm.

## Technology Stack

### Backend
- **FastAPI**, **Python**
- **PostgreSQL / PostGIS**
- **Docker**

### Frontend
- **React** (Vite)

### Data Science / ML
- **NumPy**, **Pandas**, **scikit-learn**

### GIS / Remote Sensing
- **Rasterio**, **GeoPandas** 

## Key Features

### User-Facing Web Interface
- Responsive UI, dashboards, forms, PDF report generation
- Farm record management.
- Farm spatial visualisation.
- Species management.
- Compatibility matrix management.
- Exclusion rules and dependency management.
- Admin dashboard and core settings.

### Data Science / ML Features
- Suitability scoring models
- Farm archetypes and plant functional types
- Exploratory and predictive modelling
- Expert-driven weight calculation using AHP.
- Data-driven and hybrid weight calculation.
- ML-based environmental data imputation.
- Survivability model data remediation and baseline retraining.
- Survivability model training logic improvements.
- Survivability model feature engineering.
- Growth model development.

### GIS / Remote Sensing
- Extraction of rainfall, soil, elevation, slope, and temperature layers from raster and geospatial datasets
- Spatial aggregation for farm-level profile generation
- DEM data integration and results storing.
- GEE baseline analysis.
- Riparian zone identification.
- Farm spatial visualisation.
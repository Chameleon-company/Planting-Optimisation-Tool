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
- Automatic exclusion of species that cannot survive under the farm’s limiting conditions.  
- Identification of key limiting factors for each species.

### Environmental Profiling 
- Extraction of environmental variables from geospatial datasets and hybrid GIS/GEE data sources (e.g., rainfall, elevation, slope, and soil). 
- Integration with national datasets such as Seeds of Life.  
- Farm-level environmental profiles for decision support.

### Sapling Estimation
- Calculates recommended sapling count based on farm area, terrain, planting profile (e.g. 3m × 3m spacing).
- Calculates recommended sapling counts using configurable planting spacing, terrain slope limits, and farm geometry.

### User-Facing Web Interface

- Input forms for farm conditions and environmental parameters.
- Species recommendation and environmental profile pages.
- Interactive frontend built with React and Vite.
- Visualization of environmental profile and sapling estimation outputs.

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

### Data Science / ML Features
- Suitability scoring models
- Farm archetypes and plant functional types
- Exploratory and predictive modelling

### GIS / Remote Sensing
- Extraction of rainfall, soil, elevation, slope, and temperature layers from raster and geospatial datasets
- Spatial aggregation for farm-level profile generation
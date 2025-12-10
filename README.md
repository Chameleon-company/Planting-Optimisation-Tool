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
- Extraction of environmental variables from geospatial datasets (e.g., rainfall, elevation, soil).  
- Integration with national datasets such as Seeds of Life.  
- Farm-level environmental profiles for decision support.

### Sapling Estimation
- Calculates recommended sapling count based on farm area, terrain, planting profile (e.g. 3m × 3m spacing).

### User-Facing Web Interface
- Input forms for farm conditions.  
- Dashboards showing suitable, cautionary, and excluded species.  
- Visual indicators highlighting limiting environmental factors.  
- PDF report generation with species images and charts.  
- Mobile-friendly layout for field use.

## Technology Stack

### Backend
- **FastAPI**, **Python**
- **PostgreSQL / PostGIS**
- **Docker**

### Frontend
- **React** (Vite)
- Responsive UI, dashboards, forms, PDF report generation

### Data Science / ML
- **NumPy**, **Pandas**, **scikit-learn**
- Suitability scoring models  
- Farm archetypes and plant functional types  
- Exploratory and predictive modelling

### GIS / Remote Sensing
- **QGIS**, **GDAL**, **Rasterio**, **GeoPandas**
- Extraction of rainfall, soil, elevation, and temperature layers  
- Spatial aggregation for farm-level profile generation

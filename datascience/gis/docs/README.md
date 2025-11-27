# Overview
This module provides a lightweight interface for extracting geospatial attributes from coordinates.
It is designed to support the Planting Optimisation Tool by converting longitude/latitude inputs into meaningful environmental data such as elevation, rainfall, temperature, soil pH, and landcover.
```
gis/
│
├── assets/
│   └── gadm41_TLS_3.json        # Administrative boundary data for Timor-Leste
│
├── config/
│   └── settings.py              # Environment variable loading (service account, key paths)
│
├── core/
│   ├── extract_data.py          # Functions to fetch rainfall, temp, pH, elevation, landcover
│   ├── farm_profile.py          # Builds a farm profile from coordinates
│   ├── gee_client.py            # Earth Engine initialization + client handling
│   └── geometry_parser.py       # Parsers for point, multipoint, polygon inputs
|___docs/
|   └── README.md                # folder structure, update works
│
├── keys/
│   └── <service-account>.json   # Local service account key (ignored by Git)
│
└── .env                         # GEE_SERVICE_ACCOUNT and GEE_KEY_PATH variables

```
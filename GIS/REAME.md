## Google Earth Engine (GEE)

This feature branch introduces the initial setup and testing of Google Earth Engine (GEE) integration for the Planting Optimisation Tool. The current work focuses on authentication and the base module layout.

### Service Account Authentication

- Loads credentials from `.env`:
  - `GEE_SERVICE_ACCOUNT` — service account email  
  - `GEE_KEY_PATH` — path to the JSON key file  
- Initializes Earth Engine using a service account via `ee.ServiceAccountCredentials`.

### GIS Module Structure


-- DEM ingestion instructions

-- This table stores DEM raster data
CREATE TABLE IF NOT EXISTS dem_table (
    rid SERIAL PRIMARY KEY,
    rast RASTER
);

-- NOTE:
-- DEM data must be loaded using raster2pgsql command:

-- Example:
-- raster2pgsql -s 4326 -I -C /path/to/DEM.tif dem_table | psql -U postgres -d POT_db

-- This step must be executed before running the sapling estimation service.
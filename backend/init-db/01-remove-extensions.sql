-- This runs during the very first container boot
-- It enables the postgis extension and removes other redundant extensions that come packaged with the image
CREATE EXTENSION IF NOT EXISTS postgis;

DROP EXTENSION IF EXISTS postgis_tiger_geocoder CASCADE;
DROP EXTENSION IF EXISTS postgis_topology CASCADE;
DROP EXTENSION IF EXISTS fuzzystrmatch CASCADE;
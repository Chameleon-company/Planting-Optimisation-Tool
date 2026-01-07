import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import Point

spacing = 3.0
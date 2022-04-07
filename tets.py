from osgeo.gdalconst import *
from osgeo import gdal, osr
import numpy as np
from main import *

datasource = gdal.Open('tests/test_dgms/test_dgm.tif')
databand = datasource.GetRasterBand(1)

elevation_model_array = databand.ReadAsArray().astype('float32')
print(elevation_model_array.shape)

print(calculate_tile_dimensions(databand, (534, 1341), 500))
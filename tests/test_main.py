from osgeo.gdalconst import *
from osgeo import gdal, osr
import numpy as np
from main import *


def test_load_elevation_model():
    datasource = gdal.Open('test_dgms/test_dgm.tif')
    databand = datasource.GetRasterBand(1)

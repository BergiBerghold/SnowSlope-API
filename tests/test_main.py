import sys
sys.path.append('../SkiSlope')

from osgeo.gdalconst import *
from osgeo import gdal, osr
import numpy as np
from main import *


def test_load_elevation_model():
    datasource = gdal.Open('tests/test_dgms/test_dgm.tif')
    databand = datasource.GetRasterBand(1)

from osgeo import gdal, osr
from osgeo.gdalconst import *
import numpy as np

datasource = gdal.Open("/media/bergi/Drive/DGM/50607/dgm_50607.tif")
band = datasource.GetRasterBand(1)
A = band.ReadAsArray()

A = (A < -9999)*(-9999) + (A > -9999)*A

print(np.min(A))
print(np.max(A))

size_x, size_y = A.shape

driver = datasource.GetDriver()
out_ds = driver.Create("/media/bergi/Drive/DGM/50607/output.tif", size_y, size_x, 1, GDT_Byte)

out_band = datasource.GetRasterBand(1)
out_band.WriteArray(A, 0, 0)

out_band.SetNoDataValue(0)
out_band.FlushCache()

out_ds.SetGeoTransform(datasource.GetGeoTransform())
out_ds.SetProjection(datasource.GetProjection())

# print(int(elevation_model_array[int(7*x/10), 0]))
# print(-float(elevation_model_array[int(7*x/10), 0])-9999)

# A = np.array(-340282346638528859811704183484516925440).astype(np.float32)
#
# print((A < -9999)*(-9999) + (A > -9999)*A)
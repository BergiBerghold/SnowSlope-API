import gdal
import glob
import time
import cv2
import numpy as np

a = np.array([0,1,0])
b = np.array([[1],[0],[0]])



print(np.any(a) or np.any(b))

# path = '/media/bergi/Drive/DGM/'
# list_of_input_files = glob.glob(path + '*/*.tif')
#
# print(len(list_of_input_files))
#
# options = gdal.BuildVRTOptions(allowProjectionDifference=True)
# gdal.BuildVRT('out.vrt', list_of_input_files, options=options)

# start = time.time()
#
# gdal.Translate('DGM_Salzburg.tif', 'out.vrt')
#
# print(f"Took {time.time()-start}")

import numpy as np
import scipy.ndimage
from matplotlib import pyplot as plt
from skimage import feature


array = np.loadtxt('out.txt')

edges = feature.canny(array)

idx = np.transpose(np.nonzero(edges))


import numpy as np
import scipy.ndimage
from matplotlib import pyplot as plt
from skimage import feature


array = np.loadtxt('out.txt')

edges = feature.canny(array)

idx = np.transpose(np.nonzero(edges))

print(idx)

idx = [(x[0], x[1]) for x in idx]

print(idx)

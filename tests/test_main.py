import tests.test_parameters as test_parameters
from snowslope_api.main import *
import pytest
import os

if os.path.exists('tests/test_dgms/test_dgm.tif'):
    test_dgm_path = 'tests/test_dgms/test_dgm.tif'

elif os.path.exists('test_dgms/test_dgm.tif'):
    test_dgm_path = 'test_dgms/test_dgm.tif'

'''
Test for function calculate_tile_dimensions
'''

parameters = test_parameters.calculate_tile_dimensions


@pytest.mark.parametrize('endpoint_in, tilesize, tile_dimensions, endpoint_out, warning_code', parameters)
def test_calculate_tile_dimensions(endpoint_in, tilesize, tile_dimensions, endpoint_out, warning_code):
    datasource = gdal.Open(test_dgm_path)
    databand = datasource.GetRasterBand(1)

    assert (tile_dimensions, endpoint_out, warning_code) == calculate_tile_dimensions(databand, endpoint_in, tilesize)


'''
Test for function load_elevation_model
'''

parameters = test_parameters.load_elevation_model


@pytest.mark.parametrize('tile_dimensions, elevation_model_array', parameters)
def test_load_elevation_model(tile_dimensions, elevation_model_array):
    datasource = gdal.Open(test_dgm_path)
    databand = datasource.GetRasterBand(1)

    assert elevation_model_array == load_elevation_model(databand, tile_dimensions).tolist()


'''
Test for function transform_wgs84_to_pixel
'''

parameters = test_parameters.transform_wgs84_to_pixel


@pytest.mark.parametrize('lat, long, x, y', parameters)
def test_transform_wgs84_to_pixel(lat, long, x, y):
    datasource = gdal.Open(test_dgm_path)

    assert (x, y) == transform_wgs84_to_pixel(datasource, lat, long)


'''
Test for function check_if_tile_too_small
'''

parameters = test_parameters.check_if_tile_too_small


@pytest.mark.parametrize('array, output', parameters)
def test_check_if_tile_too_small(array, output):
    assert output == check_if_tile_too_small(np.asarray(array))


'''
Test for function crop_to_smallest_size
'''

parameters = test_parameters.crop_to_smallest_size


@pytest.mark.parametrize('array_in, array_out, y_min, x_min', parameters)
def test_crop_to_smallest_size(array_in, array_out, y_min, x_min):
    output_array, output_y_min, output_x_min = crop_to_smallest_size(np.asarray(array_in))

    assert output_array.tolist() == array_out
    assert (output_x_min, output_y_min) == (x_min, y_min)



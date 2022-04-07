from skislope_api.main import *
import random


def generate_test_data_calculate_tile_dimensions():
    datasource = gdal.Open('tests/test_dgms/test_dgm.tif')
    databand = datasource.GetRasterBand(1)

    elevation_model_array = databand.ReadAsArray().astype('float32')

    parameter_array = []

    for i in range(10):
        x = random.randrange(1600)
        y = random.randrange(2500)
        endpoint_in = x, y

        tilesize = random.randrange(1, 1400)

        tile_dimensions, endpoint_out, warning_code = calculate_tile_dimensions(databand, (x, y), tilesize)

        parameter_array.append((endpoint_in, tilesize, tile_dimensions, endpoint_out, warning_code))

    print(parameter_array)


def generate_test_data_load_elevation_model():
    datasource = gdal.Open('tests/test_dgms/test_dgm.tif')
    databand = datasource.GetRasterBand(1)

    parameter_array = []

    while len(parameter_array) < 10:
        x = random.randrange(1600)
        y = random.randrange(2500)
        endpoint_in = x, y

        tilesize = random.randrange(1, 5)

        tile_dimensions, endpoint_out, warning_code = calculate_tile_dimensions(databand, (x, y), tilesize)

        if tile_dimensions:
            array = load_elevation_model(databand, tile_dimensions)
            parameter_array.append((tile_dimensions, array.tolist()))

    print(parameter_array)


def generate_test_data_transform_wgs84_to_pixel():
    datasource = gdal.Open('tests/test_dgms/test_dgm.tif')
    databand = datasource.GetRasterBand(1)

    parameter_array = []

    for i in range(10):
        lat = random.randrange(47155517, 47168500) / 10**6
        long = random.randrange(12774348, 12805801) / 10**6

        x, y = transform_wgs84_to_pixel(datasource, lat, long)

        parameter_array.append((lat, long, x, y))

    print(parameter_array)


def generate_test_data_check_if_tile_too_small():
    parameter_array = []

    while len(parameter_array) < 5:
        array = np.random.randint(0, 2, (10, 10))

        array[0, :] = 0
        array[:, 0] = 0
        array[:, -1] = 0

        if check_if_tile_too_small(array):
            parameter_array.append(array.tolist())

    print(parameter_array)


generate_test_data_check_if_tile_too_small()


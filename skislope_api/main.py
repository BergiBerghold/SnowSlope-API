from osgeo.gdalconst import *
from osgeo import gdal, osr
from PIL import Image
import numpy as np
import hashlib
import time
import cv2
import os


def load_elevation_model(databand, tile_dimensions):
    elevation_model_array = databand.ReadAsArray(tile_dimensions['x_offset'],
                                                 tile_dimensions['y_offset'],
                                                 tile_dimensions['x_size'],
                                                 tile_dimensions['y_size']).astype('float32')

    return elevation_model_array


def calculate_tile_dimensions(databand, endpoint, tile_size):
    endpoint_x, endpoint_y = endpoint
    datasize_x, datasize_y = databand.XSize, databand.YSize

    if not ((0 <= endpoint_x <= datasize_x) and (0 <= endpoint_y <= datasize_y)):
        '''
        Return tiling function as false and set the error code to 1 in case the endpoint is outside of the map
        '''
        error_code = 1
        return False, False, error_code

    x_offset = max(int(endpoint_x - tile_size / 2), 0)
    y_offset = max(int(endpoint_y - tile_size / 2), 0)

    x_size = min(tile_size, datasize_x - x_offset)
    y_size = min(tile_size, datasize_y - y_offset)

    endpoint = endpoint_x - x_offset, endpoint_y - y_offset

    tile_dimensions = {'x_offset': x_offset,
                       'y_offset': y_offset,
                       'x_size': x_size,
                       'y_size': y_size}

    if x_size < tile_size or y_size < tile_size:
        '''
        Warning code 11 in case the endpoint is close to the edge of the map and the tile becomes smaller
        '''
        warning_code = 11

    else:
        warning_code = 0

    return tile_dimensions, endpoint, warning_code


def transform_wgs84_to_pixel(datasource, wgs84_coords):
    wgs84_system = osr.SpatialReference()
    wgs84_system.SetWellKnownGeogCS('WGS84')

    pixel_system = osr.SpatialReference()
    #pixel_system.ImportFromWkt(datasource.GetProjection())
    pixel_system.ImportFromProj4('+proj=tmerc +lat_0=0 +lon_0=13.3333333333333 +k=1 +x_0=450048.038 +y_0=-4999945.657 +ellps=bessel +units=m +no_defs +type=crs')

    try:
        wgs84_system.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        pixel_system.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    except AttributeError as error:
        print(f'Caught Attribute Error: {error} This is not a problem')

    transform = osr.CoordinateTransformation(wgs84_system, pixel_system)
    geo_matrix = datasource.GetGeoTransform()

    wgs84_lat, wgs84_long = wgs84_coords
    x_pixel_sys, y_pixel_sys, z_pixel_sys = transform.TransformPoint(wgs84_long, wgs84_lat)

    ul_x = geo_matrix[0]
    ul_y = geo_matrix[3]
    x_dist = geo_matrix[1]
    y_dist = geo_matrix[5]
    pixel = int((x_pixel_sys - ul_x) / x_dist)
    line = int((y_pixel_sys - ul_y) / y_dist)

    '''pixel, line is x, y in pixel coordinates'''

    return pixel, line


def transform_pixel_to_wgs84(datasource, pixel_coords):
    wgs84_system = osr.SpatialReference()
    wgs84_system.SetWellKnownGeogCS('WGS84')

    pixel_system = osr.SpatialReference()
    #pixel_system.ImportFromWkt(datasource.GetProjection())
    pixel_system.ImportFromProj4('+proj=tmerc +lat_0=0 +lon_0=13.3333333333333 +k=1 +x_0=450048.038 +y_0=-4999945.657 +ellps=bessel +units=m +no_defs +type=crs')

    try:
        wgs84_system.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        pixel_system.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    except AttributeError as error:
        print(f'Caught Attribute Error: {error} This is not a problem')

    transform = osr.CoordinateTransformation(pixel_system, wgs84_system)
    geo_matrix = datasource.GetGeoTransform()

    pixel, line = pixel_coords

    ul_x = geo_matrix[0]
    ul_y = geo_matrix[3]
    x_dist = geo_matrix[1]
    y_dist = geo_matrix[5]
    x_pixel_sys = pixel * x_dist + ul_x
    y_pixel_sys = line * y_dist + ul_y

    x_wgs84_sys, y_wgs84_sys, z_wgs84_sys = transform.TransformPoint(x_pixel_sys, y_pixel_sys)

    lat = y_wgs84_sys
    long = x_wgs84_sys

    return lat, long


def check_if_tile_too_small(array):
    '''
    The function checks the edges of the array for non Zero values.
    If True this means the tile was too small.
    '''

    a = array[0, :] + array[-1, :]
    b = array[:, 0] + array[:, -1]

    return np.any(a) or np.any(b)


def crop_to_smallest_size(array):
    '''
    Crops an array to its smallest size of non Zero values
    '''
    coords = np.argwhere(array != 0)
    x_min, y_min = coords.min(axis=0)
    x_max, y_max = coords.max(axis=0)

    return array[x_min:x_max + 1, y_min:y_max + 1], y_min, x_min


def do_flood_fill(lat, long, min_slope, max_slope, tile_size, datasource):
    databand = datasource.GetRasterBand(1)
    nodata_value = databand.GetNoDataValue()  # TODO -e28 nodata value?

    endpoint = transform_wgs84_to_pixel(datasource, (lat, long))

    tile_dimensions, endpoint, warning_code = calculate_tile_dimensions(databand, endpoint, tile_size)

    if not tile_dimensions:
        '''
        Return flood fill function as false if endpoint is outside of map.
        Outside of map => Error code 1
        '''
        error_code = 1
        return False, error_code

    elevation_model_array = load_elevation_model(databand, tile_dimensions)

    if elevation_model_array[endpoint] == nodata_value:
        '''
        Return flood fill function as false in case the endpoint is in Nodata region.
        In Nodata region => Error code 2
        '''
        error_code = 2
        return False, error_code

    if nodata_value in elevation_model_array:
        '''
        Warning code 12 in case part of the tile is a Nodata region
 
        Warning code 13 in case part of the tile is a Nodata region AND
        the endpoint is close to the edge of the map and the tile becomes smaller
        
        Tile becomes smaller                => Warning code 11
        Nodata in Tile                      => Warning code 12
        Tile smaller AND nodata in Tile     => Warning code 13
        '''
        if warning_code == 0:
            warning_code = 12

        elif warning_code == 11:
            warning_code = 13

    x, y = tile_dimensions['x_size'], tile_dimensions['y_size']
    mask_array = np.zeros((x + 2, y + 2), dtype=np.uint8)

    cv2.floodFill(elevation_model_array,
                  newVal=0,
                  mask=mask_array,
                  seedPoint=endpoint,
                  flags=8 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY,
                  loDiff=-np.tan(np.deg2rad(min_slope)),
                  upDiff=np.tan(np.deg2rad(max_slope)))

    mask_array = mask_array[1:-1, 1:-1]

    if check_if_tile_too_small(mask_array):
        '''
        Return flood fill function as false if tile size was too small.
        Tile too small => Error code 4
        '''
        error_code = 4
        return False, error_code

    mask_array, x_crop_offset, y_crop_offset = crop_to_smallest_size(mask_array)
    total_offset = tile_dimensions['x_offset'] + x_crop_offset, tile_dimensions['y_offset'] + y_crop_offset

    upper_left_image_bound = transform_pixel_to_wgs84(datasource, total_offset)

    image_size_y, image_size_x = mask_array.shape
    lower_right_image_bound = total_offset[0] + image_size_x, total_offset[1] + image_size_y
    lower_right_image_bound = transform_pixel_to_wgs84(datasource, lower_right_image_bound)

    hash_input = f"{lat}{long}{min_slope}{max_slope}"
    filename = hashlib.sha1(hash_input.encode("UTF-8")).hexdigest()
    filename = f'{filename}.png'

    if not os.path.exists('tiles_output'):
        os.mkdir('tiles_output')

    img = Image.fromarray(mask_array, 'P')
    img.putpalette([0,0,0,0, 255,0,0,180], rawmode='RGBA')
    img.save(f'tiles_output/{filename}')

    return_data = {'filename': filename, 'image_bounds': [upper_left_image_bound, lower_right_image_bound]}

    return return_data, warning_code


def calculate_slope(lat, long, min_slope, max_slope):
    if os.path.exists('DGM_Salzburg.tif'):
        model_file = 'DGM_Salzburg.tif'

    elif os.path.exists('../DGM_Salzburg.tif'):
        model_file = '../DGM_Salzburg.tif'

    datasource = gdal.Open(model_file)
    tile_size = 10

    while True:
        filename, return_code = do_flood_fill(lat, long, min_slope, max_slope, tile_size, datasource)

        if return_code == 4:
            '''
            Code 4 means the tile size was too small. Doubling Tile size and rerunning
            '''
            tile_size *= 4
            print(f"Initial Tile size was too small, rerunning with tile size {tile_size}")

        else:
            return filename, return_code


if __name__ == "__main__":
    #start = time.perf_counter()
    # print("Took %s" % (time.perf_counter() - start))

    lng, lat = 13.0459,47.2613

    print(calculate_slope(lat, lng, 0, 45))

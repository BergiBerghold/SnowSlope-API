from subprocess import Popen, PIPE
from osgeo.gdalconst import *
from osgeo import gdal, osr
import numpy as np
import hashlib
import time
import cv2


def load_elevation_model(wgs84_lat, wgs84_long, tile_size):
    datasource = gdal.Open("DGM_Salzburg.tif")
    band = datasource.GetRasterBand(1)
    nodata_value = band.GetNoDataValue() #TODO -e28 nodata value?

    endpoint = transform_wgs84_to_pixel(wgs84_lat, wgs84_long, datasource)

    valid_point = calculate_tile_offsets(band, endpoint, tile_size)

    if valid_point:
        x_offset, y_offset, x_tilesize, y_tilesize, warning_code = valid_point
    else:
        '''
        Return loading function as false in case the endpoint is outside of the map
        Error code = 1
        '''
        return False, 1

    elevation_model_array = band.ReadAsArray(x_offset, y_offset, x_tilesize, y_tilesize).astype('float32')

    endpoint = endpoint[0] - x_offset, endpoint[1] - y_offset

    if elevation_model_array[endpoint] == nodata_value:
        '''
        Return loading function as false in case the endpoint is in Nodata region
        Error code = 2
        '''
        return False, 2

    if nodata_value in elevation_model_array:
        '''
        Warning code 11 in case part of the tile is a Nodata region
        '''
        warning_code = 11

    return datasource, elevation_model_array, endpoint, (x_offset, y_offset), warning_code


def calculate_tile_offsets(databand, endpoint, tile_size):
    point_x, point_y = endpoint
    size_x, size_y = databand.XSize, databand.YSize

    if not ( (0 <= point_x <= size_x) and (0 <= point_y <= size_y) ):
        '''Return tiling function as false in case the endpoint is outside of the map'''
        return False

    x_offset = max( int(point_x - tile_size/2), 0 )
    y_offset = max( int(point_y - tile_size/2), 0 )

    x_tilesize = min(tile_size, size_x - x_offset)
    y_tilesize = min(tile_size, size_y - y_offset)

    warning_code = 0

    if x_tilesize < tile_size or y_tilesize < tile_size:
        warning_code = 11
        '''Warning code 11 in case the endpoint is close to the edge of the map and the tile becomes smaller'''

    return x_offset, y_offset, x_tilesize, y_tilesize, warning_code


def write_output_raster(out_data, datasource, filename, tile_offset):
    if check_if_tile_too_small(out_data):
        '''
        If True then the calculated area borders on the edge of the tile. That means the program
        has to be run again with a bigger tile size.
        '''
        tile_too_small = True
        return 0, tile_too_small

    out_data, x_crop_offset, y_crop_offset = crop_to_smallest_size(out_data)
    x_tile_offset, y_tile_offset = tile_offset
    size_x, size_y = out_data.shape

    driver = datasource.GetDriver()
    out_ds = driver.Create("temp.tif", size_y, size_x, 3, GDT_Byte) #TODO find a better solution for coloring, edit gdal2tiles maybe

    out_band = out_ds.GetRasterBand(1)
    out_band.WriteArray(out_data, 0, 0)

    out_band.SetNoDataValue(0)
    out_band.FlushCache()

    (GT_0, GT_1, GT_2, GT_3, GT_4, GT_5) = datasource.GetGeoTransform()

    out_ds.SetGeoTransform((GT_0 + x_crop_offset + x_tile_offset, GT_1, GT_2, GT_3 - y_crop_offset - y_tile_offset, GT_4, GT_5))
    out_ds.SetProjection(datasource.GetProjection())

    out_ds = None

    process = Popen(["python3", "gdal2tiles_custom.py", "--webviewer=none", "--zoom=13-18", "--processes=8", "temp.tif", f"Kaprun_output/{filename}"], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    print(stderr, stdout)

    while process.poll() is None:
        time.sleep(0.5)

    tile_too_small = False
    return process.returncode, tile_too_small


def crop_to_smallest_size(array):
    coords = np.argwhere(array != 0)
    x_min, y_min = coords.min(axis=0)
    x_max, y_max = coords.max(axis=0)

    return array[x_min:x_max + 1, y_min:y_max + 1], y_min, x_min


def check_if_tile_too_small(array):
    a = array[0, :] + array[-1, :]
    b = array[:, 0] + array[:, -1]

    return np.any(a) or np.any(b)


def transform_wgs84_to_pixel(wgs84_lat, wgs84_long, datasource):
    source_system = osr.SpatialReference()
    source_system.SetWellKnownGeogCS('WGS84')

    target_system = osr.SpatialReference()
    #target_system.ImportFromWkt(datasource.GetProjection())
    target_system.ImportFromProj4('+proj=tmerc +lat_0=0 +lon_0=13.3333333333333 +k=1 +x_0=450048.038 +y_0=-4999945.657 +ellps=bessel +units=m +no_defs +type=crs')

    try:
        source_system.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        target_system.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

    except:
        pass

    transform = osr.CoordinateTransformation(source_system, target_system)
    x_target_sys, y_target_sys, z_target_sys = transform.TransformPoint(wgs84_long, wgs84_lat)

    geo_matrix = datasource.GetGeoTransform()

    ul_x = geo_matrix[0]
    ul_y = geo_matrix[3]
    x_dist = geo_matrix[1]
    y_dist = geo_matrix[5]
    pixel = int((x_target_sys - ul_x) / x_dist)
    line = -int((ul_y - y_target_sys) / y_dist)

    return pixel, line


def do_flood_fill(lat, long, min_slope, max_slope, tile_size):
    successfully_loaded = load_elevation_model(lat, long, tile_size)

    if successfully_loaded[0]:
        datasource, elevation_model_array, endpoint, tile_offset, warning_code = successfully_loaded
    else:
        '''
        Return calculation function as false if endpoint is outside of map or in Nodata region.
        Outside of map => Error code 1
        In Nodata region => Error code 2
        '''
        error_code = successfully_loaded[1]
        return False, error_code

    x, y = elevation_model_array.shape
    output_array = np.zeros((x+2, y+2), dtype=np.uint8)

    cv2.floodFill(elevation_model_array, mask=output_array, seedPoint=endpoint,
                  flags=8 | (255 << 8) | cv2.FLOODFILL_MASK_ONLY, newVal=255,
                  loDiff=-np.tan(np.deg2rad(min_slope)),
                  upDiff=np.tan(np.deg2rad(max_slope)))

    output_array = output_array[1:-1, 1:-1]

    hash_input = f"{lat}{long}{min_slope}{max_slope}"
    filename = hashlib.sha1(hash_input.encode("UTF-8")).hexdigest()

    return_code, tile_too_small = write_output_raster(output_array, datasource, filename, tile_offset)

    if return_code != 0:
        '''
        Return calculation function as false if tile generation has gone wrong.
        Error code = 3
        '''
        return False, 3

    if tile_too_small:
        '''
        Return calculation function as false if tile size was too small.
        Error code = 4
        '''
        return False, 4

    return filename, warning_code


def calculate_slope(lat, long, min_slope, max_slope):
    tile_size = 2048

    while True:
        filename, return_code = do_flood_fill(lat, long, min_slope, max_slope, tile_size)

        if return_code == 4:
            '''
            Code 4 means the tile size was too small. Doubling Tile size and rerunning
            '''
            tile_size *= 2
            print(f"Initial Tile size was too small, rerunning with tile size {tile_size}")

        else:
            return filename, return_code


if __name__ == "__main__":
    #start = time.perf_counter()
    # print("Took %s" % (time.perf_counter() - start))

    lng, lat = 12.82268,47.20402

    print(calculate_slope(lat, lng, 0, 45))



from osgeo import gdal, osr

source_system = osr.SpatialReference()
source_system.ImportFromProj4('+proj=tmerc +lat_0=0 +lon_0=13.3333333333333 +k=1 +x_0=450048.038 +y_0=-4999945.657 +ellps=bessel +units=m +no_defs +type=crs')

target_system = osr.SpatialReference()
target_system.SetWellKnownGeogCS('WGS84')

transform = osr.CoordinateTransformation(source_system, target_system)


def transform_pixel_to_wgs84(x, y, transform):
    x_target_sys, y_target_sys, z_target_sys = transform.TransformPoint(x, y)

    return x_target_sys, y_target_sys


with open('outline_coords.txt') as input:
    in_line = input.readline()
    out_array = []

    a = in_line[1:-2].split("], [")

    for coord in a:
        [x, y] = coord.split(",")
        x = float(x)
        y = float(y)

        lat, lng = transform_pixel_to_wgs84(x, y, transform)

        out_array.append([lat, lng])

print(out_array)



#with open('outline_coords_wgs84.txt', 'w') as output:

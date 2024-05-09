import os
import zipfile

from osgeo import gdal, gdal_array

from math import floor, ceil

import files
import re


def getFilesHashes(continent):
    if continent == "Australia":
        files_hashes = files.Australia
    if continent == "Eurasia":
        files_hashes = files.Eurasia
    if continent == "Africa":
        files_hashes = files.Africa
    if continent == "Islands":
        files_hashes = files.Islands
    if continent == "North_America":
        files_hashes = files.North_America
    if continent == "South_America":
        files_hashes = files.South_America
    return files_hashes


def getNumberOfFiles(file_list, north, south, west, east):
    i = 0

    for file in file_list:
        file = file[1][0:-8]

        [lat, lon] = getLatLonFromFileName(file)

        if inBoundingBox(lat, lon, north, south, west, east):
            i = i + 1

    return i


def getBoundingBox(sysargv, offset):
    try:
        north = int(sysargv[offset])
        south = int(sysargv[offset + 1])
        west = int(sysargv[offset + 2])
        east = int(sysargv[offset + 3])

        print(f"Bounding box {south} <= lat <= {north} and {west} <= lon <= {east}.")

    except:
        north = 90
        south = -90
        west = -180
        east = 180

    return [north, south, west, east]


def inBoundingBox(lat, lon, north, south, west, east):
    return lat <= north and lat >= south and lon >= west and lon <= east


def getLatLonFromFileName(name):
    p = re.compile("[NSEW]\\d*")

    [lat_str, lon_str] = p.findall(name)

    if lat_str[0] == "N":
        lat = int(lat_str[1:])
    else:
        lat = -int(lat_str[1:])

    if lon_str[0] == "E":
        lon = int(lon_str[1:])
    else:
        lon = -int(lon_str[1:])

    return [lat, lon]


def verifyIsContinent(continent):
    if not continent in [
        "Africa",
        "Australia",
        "Eurasia",
        "Islands",
        "North_America",
        "South_America",
    ]:
        print(
            "First argument should be Africa, Australia, Eurasia, Islands, North_America or South_America."
        )

        exit()


def posFromLatLon(lat, lon):
    return floor((lat * 360 + lon) * 1200 * 1200)


def loadTile(continent, filename):
    datapath = os.path.join("data", continent)

    name_hgt = filename + ".hgt"
    name_zip = name_hgt + ".zip"

    filepath_hgt = os.path.join(datapath, name_hgt)
    filepath_zip = os.path.join(datapath, name_zip)

    if not os.path.exists(filepath_zip):
        return None

    print("read file {}".format(filepath_zip))

    zf = zipfile.ZipFile(filepath_zip)

    outfile = open(filepath_hgt, "wb")
    outfile.write(zf.read(name_hgt))
    outfile.flush()
    outfile.close()

    with gdal.Open(filepath_hgt) as srtm:
        if srtm is None:
            print(f"Error: can't open {filepath_hgt}.")
            exit(1)

        result = gdal_array.DatasetReadAsArray(srtm)

    os.remove(filepath_hgt)

    return result


def verify(
    database, number_of_tiles, files_hashes, continent, north, south, west, east
):
    for file in files_hashes:
        file = file[1][0:-8]

        [lat, lon] = getLatLonFromFileName(file)

        if inBoundingBox(lat, lon, north, south, west, east):
            print(f"Verify {file}")

            coordinate_file = loadTile(continent, file)

            if coordinate_file is None:
                print(f"File {file} not exists.")
                continue

            coordinate_db = database.fetchTopLeftAltitude(lat, lon)

            print(coordinate_db)

            if coordinate_db != coordinate_file[1][0]:
                print(f"Mismatch tile {file[1]}")
                continue

    print("Check the total number of points in the database.")

    total = database.getCountAltitude()

    if not total == number_of_tiles * 1200 * 1200:
        print("Not all tiles have been (completely) inserted.")
        exit()

    print("All tiles seem to have made it into the database.")

    exit()


def boundsFromLatLon(latitude, longitude):
    lat0 = floor(latitude)
    lon0 = floor(longitude)
    pos0 = (lat0 * 360 + lon0) * 1200 * 1200

    latPos = (1199.0 / 1200 - (latitude - lat0)) * 1200 * 1200
    lonPos = (longitude - lon0) * 1200

    latPosTop = floor(latPos / 1200) * 1200
    latPosBottom = ceil(latPos / 1200) * 1200
    lonPosLeft = floor(lonPos)
    lonPosRight = ceil(lonPos)

    a = (latPos - latPosTop) / 1200
    b = lonPos - lonPosLeft

    t1 = pos0 + latPosTop + lonPosLeft
    tr = pos0 + latPosTop + lonPosRight
    b1 = pos0 + latPosBottom + lonPosLeft
    br = pos0 + latPosBottom + lonPosRight

    return t1, tr, b1, br, a, b


def bilinearInterpolation(tl, tr, bl, br, a, b):
    b1 = tl
    b2 = bl - tl
    b3 = tr - tl
    b4 = tl - bl - tr + br

    return b1 + b2 * a + b3 * b + b4 * a * b

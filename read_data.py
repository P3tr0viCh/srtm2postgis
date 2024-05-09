from osgeo import gdal

import re
import sys

from database import *
import database_connection
from utils import *


def main():
    gdal.UseExceptions()

    if len(sys.argv) == 1:
        print(
            "Specify the continent: Africa, Australia, Eurasia, Islands, North_America or South_America,\n"
            "or 'clear' to deleting tables from database."
        )
        exit()

    database = Database(
        database_connection.db, database_connection.db_user, database_connection.db_pass
    )

    if "clear" in sys.argv:
        print("Deleting tables from database.")

        database.dropAllTables()

        print("Done.")

        exit()

    database.createTableAltitude()

    if "pos" in sys.argv:
        if len(sys.argv) != 4:
            print("Use: pos latitude longitude.")
            exit()

        lat = float(sys.argv[2])
        lon = float(sys.argv[3])

        print("{0}:{1}".format(lat, lon))

        pos = posFromLatLon(lat, lon)

        print(pos)

        print("Done.")

        exit()

    if "tile" in sys.argv:
        if len(sys.argv) != 4:
            print("Use: tile latitude longitude.")
            exit()

        lat = float(sys.argv[2])
        lon = float(sys.argv[3])

        print("{0}:{1}".format(lat, lon))

        tile = database.readTile(lat, lon)

        print(tile)

        print("Done.")

        exit()

    if "alt" in sys.argv:
        if len(sys.argv) != 4:
            print("Use: alt latitude longitude.")
            exit()

        lat = float(sys.argv[2])
        lon = float(sys.argv[3])

        print("{0}:{1}".format(lat, lon))

        alt = database.altitude(lat, lon)

        print(alt)

        print("Done.")

        exit()

    continent = sys.argv[1]

    verifyIsContinent(continent)

    [north, south, west, east] = getBoundingBox(sys.argv, 3)

    files_hashes = getFilesHashes(continent)

    number_of_tiles = getNumberOfFiles(files_hashes, north, south, west, east)

    if "verify" in sys.argv:
        verify(
            database, number_of_tiles, files_hashes, continent, north, south, west, east
        )

        print("Done.")

        exit()

    p = re.compile("[NSEW]\\d*")
    resume_from = ""
    try:
        if p.find(sys.argv[2]):
            resume_from = sys.argv[2]

    except:
        None

    i = 0

    for file in files_hashes:
        file = file[1][0:-8]

        [lat, lon] = getLatLonFromFileName(file)

        if inBoundingBox(lat, lon, north, south, west, east):
            i = i + 1

            if resume_from == file:
                resume_from = ""

            if resume_from == "":
                tile = loadTile(continent, file)

                if tile is None:
                    print(
                        f"Skipping file (not exists) {file} ({i} of {number_of_tiles})."
                    )
                    continue

                exists = database.fetchTopLeftAltitude(lat, lon)

                if exists is None:
                    print(f"Insert data for tile {file} ({i} of {number_of_tiles}).")

                    database.insertTile(tile, lat, lon)
                else:
                    print(f"Skipping tile {file} ({i} of {number_of_tiles}).")

    print("All tiles inserted. Verify the result with python read_data.py verify.")


if __name__ == "__main__":
    main()

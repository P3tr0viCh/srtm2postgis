import gpxpy
import gpxpy.gpx

import os
import sys

from database import *
import database_connection


def main():
    if len(sys.argv) == 1:
        print("Specify the gpx track file. Add showpoints for show point")
        exit()

    gpx_filename = sys.argv[1]
    show_ponts = "show_ponts" in sys.argv
     
    if not os.path.exists(gpx_filename):
        print("File not exists.")
        exit()

    gpx_file = open(gpx_filename, "r")

    gpx = gpxpy.parse(gpx_file)

    database = Database(
        database_connection.db, database_connection.db_user, database_connection.db_pass
    )

    ascentElevation = 0
    ascentAltitude = 0

    for track in gpx.tracks:
        for segment in track.segments:
            point1 = segment.points[0]

            elevation1 = point1.elevation
            altitude1 = database.altitude(point1.latitude, point1.longitude)

            for point in segment.points:
                elevation = point.elevation
                altitude = database.altitude(point.latitude, point.longitude)

                if show_ponts:
                    print(
                        f"Point at ({point.latitude}, {point.longitude}) – {point.elevation:.2f} : {altitude:.2f}"
                    )
                
                if elevation > elevation1:
                    ascentElevation += elevation - elevation1

                if altitude > altitude1:
                    ascentAltitude += altitude - altitude1

                elevation1 = point.elevation
                altitude1 = altitude
    
    print (f"Ascent by Elevation is {ascentElevation:.2f}, by Altitude is {ascentAltitude:.2f}")

if __name__ == "__main__":
    main()

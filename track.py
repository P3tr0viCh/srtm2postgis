import gpxpy
import gpxpy.gpx

import time

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

    useSrtm = True
    
    gpx_file = open(gpx_filename, "r")

    gpx = gpxpy.parse(gpx_file)

    if useSrtm:
        database = Database(
            database_connection.db, database_connection.db_user, database_connection.db_pass
        )

    ascentElevation = 0
    ascentAltitude = 0
    ascentTrack = 0

    length = 0
    lengthByTrack = 0

    duration = 0
    durationByTrack = 0
    durationInMove = 0
    
    maxSpeed = 0

    for track in gpx.tracks:
        for segment in track.segments:
            point1 = segment.points[0]

            elevation1 = point1.elevation
            
            if useSrtm:
                altitude1 = database.altitude(point1.latitude, point1.longitude)

            for point in segment.points:
                elevation = point.elevation
    
                if useSrtm:
                    altitude = database.altitude(point.latitude, point.longitude)
                else:
                    altitude = 0

                pointDistance = point.distance_2d(point1)

                pointTimeDiff = point.time_difference(point1)

                length += pointDistance

                duration += pointTimeDiff

                speed = 0

                if pointDistance > 0 and pointTimeDiff > 0:
                    speed = pointDistance / pointTimeDiff

                if speed > maxSpeed:
                    maxSpeed = speed
                    
                # print(f"{pointTimeDiff:.0f}, {speed:.2f}")

                if speed > 0.1 and pointTimeDiff < 60:
                    durationInMove += pointTimeDiff

                point1 = point

                if show_ponts:
                    print(
                        f"Point at ({point.latitude}, {point.longitude}) – {point.elevation:.2f} : {altitude:.2f}"
                    )

                if speed > 0.1 and elevation > elevation1:
                    ascentElevation += elevation - elevation1

                if useSrtm:
                    if not altitude is None and not altitude1 is None:
                        if altitude > altitude1:
                            ascentAltitude += altitude - altitude1

                elevation1 = point.elevation
                
                if useSrtm:
                    altitude1 = altitude

        lengthByTrack += track.length_2d()
        
        ascentTrack += track.get_uphill_downhill().uphill

        durationByTrack  += track.get_duration()


    print(f"Max Speed is {maxSpeed}")

    print(f"Length is {lengthByTrack:.2f}, by distance is {length:.2f}")

    print(
        f"Duration is {time.strftime('%H:%M:%S', time.gmtime(durationByTrack))}, by points is {time.strftime('%H:%M:%S', time.gmtime(duration))}"
    )

    print(
        f"Duration in Move is {time.strftime('%H:%M:%S', time.gmtime(durationInMove))}"
    )

    print(
        f"Ascent by Elevation is {ascentElevation:.2f}, by Altitude is {ascentAltitude:.2f}, by track is {ascentTrack:.2f}"
    )


if __name__ == "__main__":
    main()

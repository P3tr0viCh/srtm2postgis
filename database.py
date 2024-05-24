import psycopg2
from psycopg2.extras import execute_values

from math import sqrt

from utils import posFromLatLon, boundsFromLatLon, bilinearInterpolation


class Database:

    def __init__(self, db_name, db_user, db_pass):
        self.conn = psycopg2.connect(
            f"dbname={db_name} user={db_user} password={db_pass}"
        )

        self.cursor = self.conn.cursor()

    def dropAllTables(self):
        self.cursor.execute("DROP TABLE IF EXISTS altitude;")
        self.conn.commit()

    def createTableAltitude(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS altitude (\
                pos bigint NOT NULL, \
                alt int NULL , \
                PRIMARY KEY (pos) \
            );"
        )
        self.conn.commit()

    def fetchAltitude(self, pos):
        self.cursor.execute(f"SELECT alt FROM altitude WHERE pos = {pos};")

        record = self.cursor.fetchone()

        if record == None:
            return None

        return int(record[0])

    def fetchTopLeftAltitude(self, lat, lon):
        pos = posFromLatLon(lat, lon)

        return self.fetchAltitude(pos)

    def getCountAltitude(self):

        self.cursor.execute("SELECT COUNT(alt) FROM altitude;")

        record = self.cursor.fetchone()

        if record == None:
            return None

        return int(record[0])

    def insertTile(self, tile, lat0, lon0):
        begin = posFromLatLon(lat0, lon0)

        data = []

        for row in range(1, len(tile)):
            for col in range(0, len(tile) - 1):
                data += [(begin + (row - 1) * 1200 + col, int(tile[row][col]))]

        query = "INSERT INTO altitude VALUES %s;"

        execute_values(self.cursor, query, data)

        self.conn.commit()

    def readTile(self, lat0, lon0):
        begin = posFromLatLon(lat0, lon0)
        end = posFromLatLon(lat0 + 1, lon0 + 1)

        self.cursor.execute(
            f"SELECT alt FROM altitude \
              WHERE pos >= {begin} AND pos < {end} \
              ORDER BY pos ASC"
        )

        record = self.cursor.fetchall()

        if record is None:
            return None

        tile = []

        tile_width = int(sqrt(len(record)))

        i = 0

        for x in range(tile_width):
            row = []
            for y in range(tile_width):
                row.append(int(record[i][0]))
                i = i + 1

            tile.append(row)

        return tile

    def altitude(self, latitude, longitude):
        tl, tr, bl, br, a, b = boundsFromLatLon(latitude, longitude)

        # print (tl, tr, bl, br, a, b)

        atl = self.fetchAltitude(tl)
        atr = self.fetchAltitude(tr)
        abl = self.fetchAltitude(bl)
        abr = self.fetchAltitude(br)

        if atl is None or atr is None or abl is None or abr is None: return None

        return bilinearInterpolation(atl, atr, abl, abr, a, b)

import pg, psycopg2
from psycopg2.extras import execute_values

from math import sqrt

from utils import posFromLatLon


class DatabasePg:
    def __init__(self, db_name, db_user, db_pass):
        self.db = pg.DB(dbname=db_name, host="localhost", user=db_user, passwd=db_pass)

    def checkDatabaseEmpty(self):
        return self.db.get_tables() == [
            "information_schema.sql_features",
            "information_schema.sql_implementation_info",
            "information_schema.sql_languages",
            "information_schema.sql_packages",
            "information_schema.sql_parts",
            "information_schema.sql_sizing",
            "information_schema.sql_sizing_profiles",
            "public.geometry_columns",
            "public.spatial_ref_sys",
        ]

    def readTile(self, lat0, lon0):
        # Calculate begin and end position
        begin = posFromLatLon(lat0, lon0)
        end = posFromLatLon(lat0 + 1, lon0 + 1)
        sql = self.db.query(
            " \
      SELECT \
        alt \
      FROM altitude \
      WHERE \
        pos >= "
            + str(begin)
            + "\
        AND pos < "
            + str(end)
            + "\
      ORDER BY pos ASC \
    "
        )
        res = sql.getresult()

        # Now turn the result into a 2D array

        tile = []

        # Calculate tile width (should be 1200, or 10 for test tiles)
        tile_width = int(sqrt(len(res)))
        i = 0
        for x in range(tile_width):
            row = []
            for y in range(tile_width):
                row.append(int(res[i][0]))
                i = i + 1

            tile.append(row)

        return tile

    def getTables(self):
        return self.db.get_tables()


class Database:

    def __init__(self, db_name, db_user, db_pass):
        self.db_name = db_name

        self.conn = psycopg2.connect(
            f"dbname={db_name} host=localhost user={db_user} password={db_pass}"
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

    def fetchTopLeftAltitude(self, lat, lon):
        pos = posFromLatLon(lat, lon)

        self.cursor.execute(f"SELECT alt FROM altitude WHERE pos = {pos};")

        record = self.cursor.fetchone()

        if record == None:
            return None

        return int(record[0])

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

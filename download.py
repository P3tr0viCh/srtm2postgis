import requests
import sys

from utils import *


def main():
    # First we make a list of all files that need to be download. This depends
    # on the arguments given to the program.
    # The first argument should be the continent:
    # * Africa
    # * Australia
    # * Eurasia
    # * Islands
    # * North_America
    # * South_America

    if len(sys.argv) > 1:
        continent = sys.argv[1]
        verifyIsContinent(continent)
    else:
        print(
            "Provide arguments\n",
            "First argument should be Africa, Australia, Eurasia, Islands, North_America or South_America.\n",
            "Second argument (optional) specifies from which tile to resume. Use full file name e.g. \n",
            "'N36W004.hgt.zip'. Set to 0 start at the first file. \n",
            "Argument 3-6 optionally specify a bounding box: north, south, west, east",
        )

        exit()

    site = "https://www.okmap.org/srtm/version2_1/SRTM3/"

    print(f"Downloading from {site}.")

    files_hashes = getFilesHashes(continent)

    files = []

    for file_hash in files_hashes:
        files += [file_hash[1]]

    if len(sys.argv) > 2:
        resume = sys.argv[2]
        if not (resume == "0"):
            skip = True
            print(f"Resume from {resume}.")
        else:
            skip = False
    else:
        skip = False

    [north, south, west, east] = getBoundingBox(sys.argv, 3)

    for i in range(len(files)):
        if skip:
            if files[i] == resume:
                skip = False

        if not (skip):
            [lat, lon] = getLatLonFromFileName(files[i])

            if inBoundingBox(lat, lon, north, south, west, east):
                url = f"{site}/{continent}/{files[i]}"

                filename = f"data/{continent}/{files[i]}"

                if os.path.exists(filename):
                    file_size = os.path.getsize(filename)
                else:
                    file_size = 0

                response = requests.get(url, stream=True)

                try:
                    response.raise_for_status()
                except requests.exceptions.HTTPError as error:
                    print(f"Error occurred: {error}")
                    exit()

                size = int(response.headers["Content-length"])

                if size != file_size:
                    print(
                        f"Downloading {files[i]} (lat = {lat}, lon = {lon} [{i + 1} of {len(files)}])."
                    )

                    response = requests.get(url)

                    try:
                        response.raise_for_status()
                    except requests.exceptions.HTTPError as error:
                        print(f"Error occurred: {error}")
                        exit()

                    with open(filename, "wb") as file:
                        file.write(response.content)
                else:
                    print(
                        f"Skip {files[i]} (lat = {lat}, lon = {lon} [{i + 1} of {len(files)}])."
                    )


if __name__ == "__main__":
    main()

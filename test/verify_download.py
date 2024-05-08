# Script verifies that the MD5 checksum of all files is correct

# Usage:
# You must specify the continent and you can optionally specify a bounding box.
# python test/verify_download.py Continent [north] [south] [west] [east]
# e.g.:
# python test/verify_download.py Australia
# python test/verify_download.py Eurasia 54 47 0 16

# I could not find the 'official' MD5 checksums for the data so I created them
# myself. So if you get an error message, that could also mean the MD5
# checksum in this script is wrong. In that case: please let me know.

import hashlib
import sys
import os

sys.path += [os.path.abspath(".")]

import utils

continent = sys.argv[1]

[north, south, west, east] = utils.getBoundingBox(sys.argv, 2)

files_hashes = utils.getFilesHashes(continent)


def md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


if __name__ == "__main__":
    for file_hash in files_hashes:
        [lat, lon] = utils.getLatLonFromFileName(file_hash[1])

        if utils.inBoundingBox(lat, lon, north, south, west, east):
            filename = f"data/{continent}/{file_hash[1]}"

            file_md5 = md5(filename)

            if not file_md5 == file_hash[0]:
                print(
                    f"Error in file {file_hash[1]}. md5 = {file_md5}, hash = {file_hash[0]}."
                )
                exit()

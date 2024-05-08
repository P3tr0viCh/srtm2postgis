import unittest

import requests


class TestDownloadScript(unittest.TestCase):

    def testUrl(self):
        site = "https://www.okmap.org"

        print("Does the server still exists and is it online?")
        response = requests.get(site, stream=True)
        self.assertEqual(response.status_code, 200)
        print("OK")

        url = f"{site}/srtm/version2_1/SRTM3/Eurasia/N00E072.hgt.zip"

        print("Is the data in the right folder?")
        response = requests.get(url, stream=True)
        self.assertEqual(response.status_code, 200)
        size = int(response.headers["Content-length"])
        self.assertEqual(size, 4320)
        print("OK")


if __name__ == "__main__":
    unittest.main()

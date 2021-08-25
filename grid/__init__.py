__author__ = "Chunpeng James Chen"
__version__ = "1.2.16"
__update__ = "Aug 25, 2021"

# imports
import subprocess
import json
import sys
from urllib import request
from pkg_resources import parse_version

if "__main__" not in sys.argv[0]:
    # prevent from re-show welcome message in gridGUI
    # welcome message
    print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
    print("                 Welcome to GRID Ver.%s    " % __version__)
    print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
    print("Author      : James Chen <chun-peng.chen@wsu.edu>    ")
    print("Last update : %s              " % __update__)
    print("User manual : https://poissonfish.github.io/GRID/")

    if "-m" not in sys.argv[0]:
        # if in the command-line environment
        print("    Try 'python -m grid' in Terminel to launch GRID GUI,")
        print("         as command-line version is not ready yet.")
    print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
    print("Recent update ")
    print("    - Support images with huge dimensions (>32767)")
    print("    - Add CRS to shapefiles (.prj) ")
    print("    - Support ESRI shapefile compatible in QGIS    ")
    print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")

# self update
try:
    url = 'https://pypi.python.org/pypi/photo_grid/json'
    releases = json.loads(request.urlopen(url).read())['releases']
    new_version = sorted(releases, key=parse_version, reverse=True)[0]
    if __version__ != new_version:
        # Dialog
        ans = None
        bol_ans = None
        possible_pos_ans = ["y", "Y", "yes"]
        possible_neg_ans = ["n", "N", "no"]

        while bol_ans is None:
            ans = input(
                "A newer version of GRID (ver. %s) is now available, upgrade? (y/n) " % new_version)
            if ans in possible_pos_ans:
                bol_ans = True
            elif ans in possible_neg_ans:
                bol_ans = False

        if bol_ans:
            subprocess.check_call([sys.executable,
                                   '-m', 'pip', 'install',
                                   'photo_grid==%s' % new_version, '--upgrade'])
            print("\n")
            print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
            print("          Please re-launch GRID to finish the update")
            print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
            print("\n")
            quit()
except Exception:
    print("\n")
    print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
    print("     Sorry, we currently have issue updating your GRID.")
    print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
    print("\n")


# self imports
from .grid import *

"""
Update Log

- Aug 25, 2021 (1.2.16)
    * Handle large images (pixel dimension > 32767)

- Sep 28, 2020 (1.2.13)
    * Impore handling of floating-encoded images

- Aug 27, 2020 (1.1.99)
    * Bug fixes of showing tabular information

- Jul 27, 2020 (1.1.96)
    * Fix the shapefile with imprecise coordinates
    * Add Coordinate reference system (CRS) to the shapefile (.prj)

- Jul 6, 2020 (1.1.9)
    * Fix crash when add/delete anchors

- Jul 1, 2020 (1.1.6)
    * Add a output image "Seg_ID.png" to show plot's ID
    * Improve the stability and flexibility in the step to segmentation
    * Bug fixes in the searching centroids step

- Jun 17, 2020 (1.1)
    * The shapefile can be used for the same field taken from different season

- Jun 10, 2020 (1.0.2)
    * The shapefile can match the coordinate system in GeoTiff now

- May 29, 2020 (1.0.1)
    * Minor bug fixes (visualization of layout detection)

- Apr 28, 2020 (0.3.5)
    * Support exporting ESRI shapefile

- Apr 16, 2020 (0.3.4)
    * New interface for angle detection

- Feb 20, 2020 (0.3.0)
    * Support different display modes in the center detection step
    * Support auto-update feature
    * Bug fixes

- Dec 19, 2019 (0.2.46)
    * Add plot variation in the output file
    * Support saving segmentated images as H5 file
    * Now it's possible to display RGB in the plot searching panel.
    * Other minor bug fixes

- Dec 9, 2019 (0.2.45)
    * Bug fixes for image rotating issue
    * Support map with duplicated names

- Oct 29, 2019 (0.2.0)
    * Add progress bars
    * Enhance the support for low resolution monitors
    * Improve UI

- Oct 22, 2019 (0.1.3)
    * Optimize default setting of refining parameters
    * Fix wrong angle detection
    * Minor bug fixes

- Oct 19, 2019 (0.1.2)
    * Support rhombus field layout
    * Bug fixes

- Sep 17, 2019 (0.0.16)
    * Improve memory efficiency on Windows OS

- Sep 12, 2019 (0.0.15)
    * Fix problems wiht fixed segmentation
    * Organize file structure
    * Add dark mode
"""

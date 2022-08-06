__author__ = "Chun-Peng James Chen"
__version__ = "1.2.23"
__update__ = "Aug 5, 2022"

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
    print("Author      : James Chen <niche@vt.edu>    ")
    print("Last update : %s              " % __update__)
    print("User manual : https://poissonfish.github.io/GRID/")

    if "-m" not in sys.argv[0]:
        # if in the command-line environment
        print("    Try 'python -m grid' in Terminel to launch GRID GUI,")
        print("         as command-line version is not ready yet.")
    print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
    print("Recent update ")
    print("    - Upgrade the GUI framework from PyQt5 to PyQt6")
    print("    - Support images with huge dimensions (> 32767)")
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
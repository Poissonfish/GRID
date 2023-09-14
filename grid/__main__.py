# imports
import subprocess
import json
import sys
from urllib import request
from pkg_resources import parse_version

# basic imports
import sys
import os

# 3rd party imports
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import qdarkstyle


# self imports
from grid.gridGUI import *
from grid.__init__ import __version__, __update__


def main():
    if "__main__" not in sys.argv[0]:
        # prevent from re-show welcome message in gridGUI
        # welcome message
        print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
        print("                 Welcome to GRID Ver.%s    " % __version__)
        print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
        print("Author      : James Chen <niche@vt.edu>    ")
        print("Last update : %s              " % __update__)
        print("User manual : https://poissonfish.github.io/GRID/")
        print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")
        print("Recent update ")
        print("    - Now you can launch GRID by typing 'GRID' in terminal")
        print("~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~*~~~~~~~~~")

    # self update
    try:
        url = "https://pypi.python.org/pypi/photo_grid/json"
        releases = json.loads(request.urlopen(url).read())["releases"]
        new_version = sorted(releases, key=parse_version, reverse=True)[0]
        if __version__ != new_version:
            # Dialog
            ans = None
            bol_ans = None
            possible_pos_ans = ["y", "Y", "yes"]
            possible_neg_ans = ["n", "N", "no"]

            while bol_ans is None:
                ans = input(
                    "A newer version of GRID (ver. %s) is now available, upgrade? (y/n) "
                    % new_version
                )
                if ans in possible_pos_ans:
                    bol_ans = True
                elif ans in possible_neg_ans:
                    bol_ans = False

            if bol_ans:
                subprocess.check_call(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "photo_grid==%s" % new_version,
                        "--upgrade",
                    ]
                )
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

    app = QApplication(sys.argv)
    if "--light" not in sys.argv:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    grid = GRID_GUI()
    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)
    app.exec()


if __name__ == "__main__":
    main()

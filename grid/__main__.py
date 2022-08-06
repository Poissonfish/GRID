# basic imports
import sys
import os

# 3rd party imports
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import qdarkstyle

# self imports
from .gridGUI import *

if "--test" not in sys.argv:
    app = QApplication(sys.argv)
    if '--light' not in sys.argv:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    grid = GRID_GUI()

    timer = QTimer()
    timer.timeout.connect(lambda: None)
    timer.start(100)

    app.exec()

else:
    # TEST MODE
    from .gtest import *

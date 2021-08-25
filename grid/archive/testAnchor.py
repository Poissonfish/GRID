import cv2
import sys
import grid as gd
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D
# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# GUI TEST
grid = gd.GRID()
grid.loadData(
    "/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
grid.binarizeImg(k=3, lsSelect=[0, 1], valShad=0, valSmth=0, outplot=False)
app = QApplication(sys.argv)
grid = PnAnchor(grid)

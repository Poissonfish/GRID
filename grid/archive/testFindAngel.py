import timeit
import math
import cv2
import grid as gd
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D


# find best angle
import numpy as np

grid = gd.GRID()
# grid.loadData(
# "/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
grid.binarizeImg(k=5, lsSelect=[4], valShad=0, valSmth=0, outplot=False)
grid.findPlots(outplot=False)
grid.cpuSeg(outplot=True)

gd.pltSegPlot(grid.agents, grid.imgs.get("visSeg"), isRect=True)

dt = grid.map.dt
grid.map.nRow
grid.map.nCol

entry = dt[(dt.row == 0) & (dt.col == 1)].iloc[0]
co = (dt.row == 0) & (dt.col == 1)

entry['row']
entry['pt']

grid.cpuSeg(outplot=True)


img = grid.imgs.get("binSeg")


def rotateBinNdArray(img, angel):
    # create border for the image
    img[:, 0] = 1
    img[0, :] = 1
    img[:, -1] = 1
    img[-1, :] = 1

    # padding
    sizePad = max(img.shape)
    imgP = np.pad(img, [sizePad, sizePad], 'constant')

    # rotate
    pivot = tuple((np.array(imgP.shape[:2])/2).astype(np.int))
    matRot = cv2.getRotationMatrix2D(pivot, angel, 1.0)
    imgR = cv2.warpAffine(
        imgP.astype(np.float32), matRot, imgP.shape, flags=cv2.INTER_LINEAR).astype(np.int8)

    # crop
    sigX = np.where(imgR.sum(axis=0) != 0)[0]
    sigY = np.where(imgR.sum(axis=1) != 0)[0]
    imgC = imgR[sigY[0]:sigY[-1], sigX[0]:sigX[-1]]

    # return
    return imgC

def getFourierTransform(sig):
    sigf = abs(np.fft.fft(sig)/len(sig))
    return sigf[2:int(len(sigf)/2)]
    # return sigf[2:25]

def getCardIntercept(lsValues, angel):
    coef = 1 if angel == 0 else (1/np.sin(np.pi/180*angel))
    return lsValues*coef

def getLineABC(slope, intercept):
    if np.isinf(slope):
        A = 1
        B = 0
        C = intercept
    else:
        A = slope
        B = -1
        C = -intercept
    return A, B, C

def solveLines(slope1, intercept1, slope2, intercept2):
    A1, B1, C1 = getLineABC(slope1, intercept1)
    A2, B2, C2 = getLineABC(slope2, intercept2)
    D = A1*B2-A2*B1
    Dx = C1*B2-B1*C2
    Dy = A1*C2-C1*A2
    if D != 0:
        x, y = Dx/D, Dy/D
        return x, y
    else:
        return False


img = grid.imgs.get("binSeg")

degRot = range(0, 90+1, 15)

# find 2 axes
sc = []
for angel in degRot:
    imgR = rotateBinNdArray(img, angel)
    sig = imgR.mean(axis=0)
    sigFour = getFourierTransform(sig)
    sc.append(max(sigFour))


def plotLine(axes, slope, intercept):
    if abs(slope) > 1e+9:
        # vertical line
        y_vals = np.array(axes.get_ylim())
        x_vals = np.repeat(intercept, len(y_vals))
    else:
        # usual line
        x_vals = np.array(axes.get_xlim())
        y_vals = intercept + slope * x_vals
    axes.plot(x_vals, y_vals, '--', color="red")


def pltCross(x, y, size=3, width=1, color="red"):
    pt1X = [x-size, x+size]
    pt1Y = [y-size, y+size]
    line1 = Line2D(pt1X, pt1Y, linewidth=width, color=color)
    pt2X = [x-size, x+size]
    pt2Y = [y+size, y-size]
    line2 = Line2D(pt2X, pt2Y, linewidth=width, color=color)
    return line1, line2

# plotting
fig, ax = plt.subplots()
ax.imshow(img)
for i in range(2):
    for intercept in intercepts[i]:
        plotLine(ax, slopes[i], intercept)
for pt in pts:
    line1, line2 = pltCross(pt[0], pt[1], width=1)
    ax.add_line(line1)
    ax.add_line(line2)

plt.show()




# DEMO
row = 9
col = 3
degs = []
sigs = []
maxs = []
for i in range(row):
    deg = i*15
    degs.append(deg)
    imgr = rotateBinNdArray(img, deg)
    sigr = imgr.mean(axis=0)
    sigrf = getFourierTransform(sigr)
    sigabs = abs(sigrf)
    plt.subplot(row, col, 1+i*col+0)
    plt.imshow(imgr)
    plt.subplot(row, col, 1+i*col+1)
    plt.plot(sigr)
    plt.subplot(row, col, 1+i*col+2)
    plt.ylim(0, 0.15)
    plt.plot(sigabs)
    sigs.append(round(sum(sigabs), 2))
    maxs.append(round(max(sigabs), 2))

print(degs)
print(sigs)
print(maxs)
plt.show()

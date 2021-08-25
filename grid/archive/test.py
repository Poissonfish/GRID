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

from grid.gridGUI import *


grid = gd.GRID()
grid.loadData("/Users/jameschen/Dropbox/UAV/James/Alfalfa/20190505RGB_RDNIR_H.tif")
grid.cropImg()

grid.binarizeImg(k=3, lsSelect=[0])
grid.imgs.get("crop")

# grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
grid.loadData("/Users/jameschen/demo.png", pathMap="/Users/jameschen/demo.csv")
grid.binarizeImg(k=3, lsSelect=[0])
grid.findPlots()
grid.cpuSeg(outplot=False)

grid.save()

dt_TE = grid.getDfIndex(ch_1=3, ch_2=0, isContrast=True, name_index="ttt")
dt_org = grid.map.dt

dt_TE[:10]
dt_org[:10]
dt_TE['var']
dt_org['var']
pd.merge(dt_org, dt_TE, on='var', how='left')


# find best angle
# plot
grid = gd.GRID()
grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Prototype/Rhombus Pumptree.jpg")
grid.binarizeImg(k=5, lsSelect=[3, 4], valShad=0, valSmth=3, outplot=True)
grid.findPlots(nCol=5, nRow=6, nSmooth=0, outplot=True)
grid.map.angles
plt.imshow(grid.map.imgs[1])
plt.plot(grid.map.imgs[1].sum(axis=0))
plt.show()

signal = grid.map.imgs[1].mean(axis=0)
# gaussian smooth
for i in range(3):
    signal = np.convolve(
        np.array([1, 2, 4, 2, 1])/10, signal, mode='same')
peaks, _ = find_peaks(signal)
peaks
plt.plot(signal)
plt.show()


app = QApplication(sys.argv)
grid = PnAnchor(grid)



# TEST code
# cp -r grid/* env/lib/python3.6/site-packages/grid/ | python3 -m grid

# GUI TEST
grid = gd.GRID()
grid.loadData(
    "/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
grid.binarizeImg(k=3, lsSelect=[0, 1], valShad=0, valSmth=0, outplot=False)
app = QApplication(sys.argv)
grid = PnAnchor(grid)


# ZZ FINAL TEST
grid = gd.GRID()
grid.loadData(
    "/Users/jameschen/Dropbox/James Chen/GRID/Prototype/F5SAS_Overview.jpg")
grid.binarizeImg(k=9, lsSelect=[0,1,2,3], valShad=0, valSmth=10, outplot=True)
grid.findPlots(outplot=True)
grid.cpuSeg(outplot=True)



grid = gd.GRID()
grid.loadData(
    "/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
grid.binarizeImg(k=3, lsSelect=[0, 1], valShad=0, valSmth=0, outplot=True)
grid.findPlots(outplot=True)
grid.cpuSeg(outplot=True)

grid = gd.GRID()
grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
grid.binarizeImg(k=5, lsSelect=[4], valShad=0, valSmth=0, outplot=False)
grid.findPlots(outplot=False)


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
    sigX = np.where(imgR.sum(axis=0)!=0)[0]
    sigY = np.where(imgR.sum(axis=1)!=0)[0]
    imgC = imgR[sigY[0]:sigY[-1], sigX[0]:sigX[-1]]

    # return 
    return imgC

angel = 60
imgR = rotateBinNdArray(img, angel)
ictA = gd.findPeaks(imgR, axis=1)[0] * (1/np.sin(np.pi/180*angel))
slpA = -1/np.tan(np.pi/180*angel)





plt.imshow(img)

def 
for intercept in ictA:
    axes = plt.gca()
    x_vals = np.array(axes.get_xlim())
    y_vals = intercept + slpA * x_vals
    plt.plot(x_vals, y_vals, '--')

plt.show()



plt.plot(imgR.mean(axis=0))
plt.show()
plt.imshow(imgR)
plt.show()



def getFourierTransform(sig):
    sigf = np.fft.fft(sig)/len(sig)
    # return sigf[2:int(len(sigf)/2)]
    return sigf[2:25]

import math

math.degrees(np.pi/180)

def getCardY(value, deg):
    return value * (np.cos(np.pi/180*deg))    


getCardY(4, deg=30)



np.tan(np.pi/180*45)


lsPxRow, _ = findPeaks(GImg.get("binSeg"), nPeaks=self.nRow, axis=0, nSmooth=nSmooth)


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



########

pil = Image.fromarray(np.uint8(img*255))

plt.imshow(pil.rotate(45))
plt.show()

npimg = np.asarray(pil.rotate(45), dtype=np.uint8)/255
plt.imshow(npimg)
plt.show()

# rotate
rotation_matrix = cv2.getRotationMatrix2D((num_cols/2, num_rows/2), 30, 1)
img_rotation = cv2.warpAffine(img, rotation_matrix, (num_cols, num_rows))
cv2.imshow('Rotation', img_rotation)
cv2.waitKey()


num_rows, num_cols = img.shape[:2]

translation_matrix = np.float32(
    [[1, 0, int(0.5*num_cols)], [0, 1, int(0.5*num_rows)]])

rotation_matrix=cv2.getRotationMatrix2D((num_cols, num_rows), 30, img_translation=cv2.warpAffine(img, translation_matrix, 1))

img_rotation = cv2.warpAffine(img_translation, rotation_matrix, (2*num_cols, 2*num_rows))

cv2.imshow('Rotation', img_rotation)
cv2.waitKey()





grid = gd.GRID()
grid.run(pathImg="/Users/jameschen/Dropbox/James_Git/FN/data/demo.png",
         lsSelect=[0, 1], valShad=0, valSmth=5,
         nRow=11, nCol=7)
grid.output()

grid = gd.GRID()
grid.run(pathImg="/Users/jameschen/Dropbox/James_Git/FN/data/demo.png",
         preset="/Users/jameschen/GRID.grid", outplot=True)

grid = gd.GRID()






grid.findPlots(nRow=11, nCol=7, plot=True)
grid.cpuSeg(plot=True)

# display seg
# Create figure and axes
fig, ax = plt.subplots(1)
# Display the image
ax.imshow(grid.imgs.get('visSeg'))
for row in range(11):
    for col in range(7):
        recAg = grid.agents.get(row=row, col=col).getQRect()
        rect = patches.Rectangle(
            (recAg.x(), recAg.y()), recAg.width(), recAg.height(),
            linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

plt.show()

# preview for fin
fig, ax = plt.subplots()
ax.imshow(grid.imgs.get('visSeg'))
for row in range(11):
    for col in range(7):
        agent = grid.agents.get(row=row, col=col)
        recAg = agent.getQRect()
        line1, line2 = pltCross(agent.x, agent.y, width=1)
        rect = patches.Rectangle(
            (recAg.x(), recAg.y()), recAg.width(), recAg.height(),
            linewidth=1, edgecolor='r', facecolor='none')
        ax.add_line(line1)
        ax.add_line(line2)
        ax.add_patch(rect)

plt.show()

plt.imshow(grid.imgs.get("raw"))

pltImShow(grid.imgs.get("raw"))

pltSegPlot(grid.agents, grid.imgs.get("visSeg"))


def test(a, b, c=0):
    return a+b+c

parm = {
    "a":1,
    "b":3,
    "c":4,
    "d":5,
}

test(**parm)

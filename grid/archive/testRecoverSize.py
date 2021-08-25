import math
import cv2
import os
import sys
import grid as gd
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D


# seedling   "/Users/jameschen/Dropbox/photo_grid/test/pheno/lsh_20200223.tif"
# [[7931.0036832412525, 6546.418047882136], [6971.510128913444, 8684.02394106814],
#  [2295.497237569061, 6595.0], [3218.5543278084715, 4408.812154696133]]
# matured    "/Users/jameschen/Dropbox/photo_grid/test/pheno/lsh_20200331.tif"
# [[5450.830570902393, 4299.983425414364], [7668.826887661141, 5293.896869244935],
#  [6706.300184162062, 7407.270718232044], [4519.690607734807, 6455.206261510129]]


grid = gd.GRID()
grid.loadData(
    "/Users/jameschen/Dropbox/photo_grid/test/pheno/lsh_20200223.tif")
pts = np.array([[7931.0036832412525, 6546.418047882136, 1], 
                [6971.510128913444, 8684.02394106814, 1],
                [2295.497237569061, 6595.0, 1], 
                [3218.5543278084715, 4408.812154696133, 1]], dtype=np.float32)
grid.cropImg(pts=pts)

grid.binarizeImg(k=3, lsSelect=[0, 1], valShad=0, valSmth=0, outplot=False)

img = grid.imgs.get("crop")

shape = img.shape


pts = np.array([[7931.0036832412525, 6546.418047882136, 1],
                [6971.510128913444, 8684.02394106814, 1],
                [2295.497237569061, 6595.0, 1],
                [3218.5543278084715, 4408.812154696133, 1]], dtype=np.float32)

pts2 = np.float32([[0, 0, 1], 
                  [shape[0], 0, 1], 
                  [0, shape[1], 1], 
                  [shape[0], shape[1], 1]])


pts = np.array([[7931.0036832412525, 6546.418047882136],
                [6971.510128913444, 8684.02394106814],
                [2295.497237569061, 6595.0],
                [3218.5543278084715, 4408.812154696133]], dtype=np.float32)

pts2 = np.float32([[0, 0],
                   [shape[0], 0],
                   [0, shape[1]],
                   [shape[0], shape[1]]])

M = cv2.getPerspectiveTransform(pts2, pts)

np.matmul(M, pts2.transpose()).transpose()
pts

pts.shape
M.shape


st = cv2.warpPerspective(img, M, (shape[0], shape[1]))

dst.shape
dst = np.array(dst).astype(np.uint8)

#######
pts1 = np.float32([[200, 200], [600, 300],
                   [100, 800], [500, 900]])
pts13 = np.float32([[200, 200, 1], [600, 300, 1],
                    [100, 800, 1], [500, 900, 1]])
fix = 123
pts2 = np.float32([[0, 0], [fix, 0], 
                 [0, fix], [fix, fix]])
pts23 = np.float32([[0, 0, 1], [fix, 0, 1], 
                   [0, fix, 1], [fix, fix, 1]])

M = cv2.getPerspectiveTransform(pts1, pts2)

recover_scale(pts2, M)

pts2_f = np.matmul(M, pts13.transpose())
pts2
pts2_f.transpose()

pts1_f = np.matmul(pts23, M)
pts1_f

app = QApplication(sys.argv)
grid = PnAnchor(grid)


pts1_r = np.matmul(np.linalg.inv(M), pts23.transpose()).transpose()
i = 0

ls = [pts1_r[i, :2] for i in range(len(pts1_r))]
np.matrix(ls)

pts1

pts2.shape
[list(pts2[i, :]) + [1] for i in range(4)]
pts23.shape

pts23


M.shape
np.linalg.inv(pts1)

pts1.shape


def recover_scale(mat_in, mat_H):
    """
    recover the cropped shaped into original scale

    parameters
    ----------
    mat_in: 4 x 2 matrix
    mat_H: 3 x 3 matrix
    """

    n_points = len(mat_in)
    # conver mat_in into 4 x 3 matrix
    mat_in = np.array([list(mat_in[i, :]) + [1] for i in range(4)])

    # solve recovered matrix
    mat_recover = np.matmul(np.linalg.inv(mat_H), mat_in.transpose())

    # transpose back to the right dimension (4 x 3)
    mat_recover = mat_recover.transpose()

    # extract the first 2 elements in each point (4 x 2)
    mat_recover = [mat_recover[i, :2] for i in range(n_points)]

    # return
    return np.array(np.matrix(mat_recover))


pts1 = np.float32([[200, 200], [600, 300],
                   [100, 800], [500, 900]])
pts13 = np.float32([[200, 200, 1], [600, 300, 1],
                    [100, 800, 1], [500, 900, 1]])
fix = 123
pts2 = np.float32([[0, 0], [fix, 0],
                   [0, fix], [fix, fix]])
pts23 = np.float32([[0, 0, 1], [fix, 0, 1],
                    [0, fix, 1], [fix, fix, 1]])

M = cv2.getPerspectiveTransform(pts1, pts2)

recover_scale(pts2, M)


np.rot90(pts1, 2)

import math

np.cos(np.pi/180*0)

pts1 = np.float32([[400, 200], [600, 600],
                   [300, 800], [500, 1200]])
pts1 = np.float32([[200, 400], [800, 600],
                   [200, 600], [800, 400]])
origin = np.median(pts1, axis=0)
# ptr1 = np.array([rotatePts((500, 500), pts1[i], 90) for i in range(4)])
ptr1 = rotatePts(pts1, 90, (500, 500))
plt.scatter(pts1.transpose()[0], pts1.transpose()[1])
plt.scatter(ptr1.transpose()[0], ptr1.transpose()[1])
 

M = cv2.getPerspectiveTransform(pts, pts2)
dst = cv2.warpPerspective(img, M, (shape[0], shape[1]))
transformed_points = cv2.warpPerspective(
    p_array, matrix, (2, 1), cv2.WARP_INVERSE_MAP)

def rotatePts(pts, angle, org=(0, 0)):
    """
    ----------
    Parameters
    ----------
    """
    ox, oy = org
    ptx = np.array([pts[i, 0] for i in range(len(pts))])
    pty = np.array([pts[i, 1] for i in range(len(pts))])
    qx = ox + math.cos(math.radians(angle))*(ptx - ox) - \
        math.sin(math.radians(angle))*(pty - oy)
    qy = oy + math.sin(math.radians(angle))*(ptx - ox) + \
        math.cos(math.radians(angle))*(pty - oy)
    qpts = [[qx[i], qy[i]] for i in range(len(pts))]
    return np.array(qpts)

    ox, oy = origin
    px, py = point

    ag = np.pi / 180 * angle
    qx = ox + np.cos(ag) * (px - ox) - np.sin(ag) * (py - oy)
    qy = oy + np.sin(ag) * (px - ox) + np.cos(ag) * (py - oy)
    return qx, qy


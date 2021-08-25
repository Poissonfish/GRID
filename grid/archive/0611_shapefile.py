import matplotlib.pyplot as plt
import cv2
import numpy as np
from io import BytesIO as StringIO
import shapefile
import numpy
import rasterio
import rasterio.mask
import os

os.chdir("..")
sys.path
sys.path.remove("/Users/jameschen/Dropbox/photo_grid/grid")
os.chdir("/Users/jameschen/Dropbox/photo_grid/")
import grid as gd

# 
os.chdir("/Users/jameschen/Dropbox/photo_grid/test/Jacob")
f_tif = rasterio.open('RGB-integer.tif')
f_sf = shapefile.Reader("jacob.shp")

row_max = -1
col_max = -1
pts_crop = [(0, 0), (0, 0), (0, 0), (0, 0)]

rec = f_sf.shapeRecords()
n_rec = len(rec)

for i in range(n_rec):
    # find four corners
    # [[W, N], [E, N], [E, S], [W, S]]
    # (0, 0), (0, m), (m, m), (m, 0)
    pts = rec[i].shape.points
    attr = rec[i].record
    row = attr[1]
    col = attr[2]

    if row == 0 and col == 0:
        # NW
        pts_crop[0] = pts[0]
    elif row == 0 and col > col_max:
        # NE
        pts_crop[1] = pts[1]
    elif row > row_max and col == 0:
        # SW
        pts_crop[3] = pts[3]
    elif row > row_max and col > col_max:
        # SE
        pts_crop[2] = pts[2]

pts_crop = [invAffine(pts_crop[i], f_tif.transform) for i in range(4)]


pts = [invAffine(pts[i], f_tif.transform) for i in range(4)]
ptPlt = np.array(pts_crop).transpose()
ptSm = np.array(pts).transpose()
plt.scatter(ptPlt[0], ptPlt[1])
plt.scatter(ptSm[0], ptSm[1])


def invAffine(pt, affine):
    """
    convert GIS coordinate to (x, y)

    NOTE:
    # a = width of a pixel
    # b = row rotation(typically zero)
    # c = x-coordinate of the center of the upper-left pixel
    # d = column rotation(typically zero)
    # e = height of a pixel(typically negative)
    # f = y-coordinate of the center of the upper-left pixel
    """
    # transformation
    xg = (pt[0] - affine[2]) / affine[0]
    yg = (pt[1] - affine[5]) / affine[4]

    # return 
    return (xg, yg)




pt = (30, 50)
xy = affine * pt
invAffine(xy, affine)





# generate sorted source point




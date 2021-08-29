
# === === === === === run main === === === === ===
# # basic imports
# import sys
# import os

# # 3rd party imports
# from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import QTimer
# import qdarkstyle

# # self imports
# from .gridGUI import *
# app = QApplication(sys.argv)
# if '--light' not in sys.argv:
#     app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

# grid = GRID_GUI()

# timer = QTimer()
# timer.timeout.connect(lambda: None)
# timer.start(100)

# app.exec_()

# === === === === === command-line test === === === === ===

# import os, sys
# os.chdir("/Users/jameschen/Dropbox/photo_grid")
# sys.path.remove("/Users/jameschen/Dropbox/photo_grid/grid")
# from PyQt5.QtWidgets import QApplication
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# import grid as gd

# os.chdir("/Users/jameschen/Dropbox/UAV/James/Chickpea/")
# grid = gd.GRID()
# grid.run(
#     pathImg="temp.png",
#     preset="tttttt.grid")

# ======== 20200827 segmentation ========
# import os
# import sys
# from PyQt5.QtWidgets import QApplication
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# import grid as gd
# from .gridGUI import *
# import shapefile
# import numpy as np
# import pandas as pd
# import rasterio
# import rasterio.mask

# os.getcwd()

# app = QApplication(sys.argv)
# grid = gd.GRID()

# grid.loadData(
#     pathImg="/Users/poissonfish/Dropbox/photo_grid/test/map_match/demo.jpg",
#     pathMap="/Users/poissonfish/Dropbox/photo_grid/test/map_match/demo.csv")
# grid.binarizeImg(k=3, lsSelect=[0, 1], valShad=0, valSmth=0)
# grid.findPlots(nRow=4, nCol=3)

# g = GRID_GUI(grid, 4)  # 0:input, 1:crop, 2:kmean, 3:anchor, 4:output
# app.exec_()

# ========= 20200801 multi seasons =========

import os, sys
sys.path
sys.path.remove("/Users/jchen/Dropbox/projects/photo_grid/grid")
from PyQt5.QtWidgets import QApplication
import numpy as np
import cv2
import matplotlib.pyplot as plt
os.chdir("/Users/jchen/Dropbox/projects/photo_grid/")
import grid as gd

import shapefile
import numpy as np
import pandas as pd
import rasterio


grid = gd.GRID()
grid.loadData()
pts = [[250, 500],
       [250, 1500],
       [750, 1500],
       [750, 500]]
grid.cropImg(pts)
grid.imgs["w"]

pts *= 1000

imgCrop, M = gd.cropImg(img_raw, pts)

img = grid.imgs.imgs["raw"]
resize = 2048

# define input coordinates
pts = np.float32(pts)

# assign sorted pts
pt_NW, pt_NE, pt_SE, pt_SW = gd.sortPts(pts)

# estimate output dimension
img_W = (gd.euclidean(pt_NW, pt_NE) + gd.euclidean(pt_SE, pt_SW))/2
img_H = (gd.euclidean(pt_SE, pt_NE) + gd.euclidean(pt_SW, pt_NW))/2

# resize output dimension
shape = find_small_shape((img_W, img_H), limit=2048)

# generate target point
pts2 = np.float32(
    # NW,    NE,            SE,                   SW
    [[0, 0], [shape[0], 0], [shape[0], shape[1]], [0, shape[1]]])

# transformation
H = cv2.getPerspectiveTransform(pts, pts2)
# dst = cv2.warpPerspective(img, H, shape)
dst = cv2.warpPerspective(np.zeros((100000, 30), dtype=np.int), H, shape)
dst = np.array(dst).astype(np.uint8)

plt.imshow(img)
test = cv2.resize(img, (500, 100))
test.shape
plt.imshow(test)
src[required] source/input image
dsize[required] desired size for the output image


plt.imshow(dst)

rasterio.warp.aligned_target(H, shape[1], shape[0], )


plt.imshow(grid.imgs.imgs["raw"])
plt.imshow(grid.imgs.imgs["crop"])

# grid.cropImg(pts=[[718.3549060542798, 3950.951983298539],
#                   [5798.1503131524005, 2488.5866388308978],
#                   [7722.315240083507, 8799.847599164927],
#                   [2462.9311064718163, 10185.246346555323]])
# grid.binarizeImg(k=5, lsSelect=[0, 1], valShad=0, valSmth=0, outplot=True)

# img = grid.imgs.get("crop")
# raw = grid.imgs.get("raw")

# gimg = grid.imgs

# affine = gimg.tiff_transform
# pts_crop = gimg.pts_crop
# mat_H = gimg.mat_H

# # load agents
# agents = gimg.f_shp.shapeRecords()

# n_agents = len(agents)
# print("Test shp")
# i = 0
# # extract agent info
# pts_ag = agents[i].shape.points
# att_ag = agents[i].record

# # find the remap pts
# pts_xy = [invAffine(pts_ag[i], affine) for i in range(4)]


# # get affine old
# grid_old = gd.GRID()
# grid_old.loadData(pathImg="/Users/jameschen/Dropbox/photo_grid/test/seasons/s1.tif")

# crs1 = grid.imgs.crs
# crs2 = grid_old.imgs.crs
# crs1 == crs2

# def aff(pt, affine, affine2):
#     x = (pt[0] - affine[2]) / affine[0]
#     y = (pt[1] - affine[5]) / affine[4]
#     return (x, y)


# affine2 = grid_old.imgs.tiff_transform
# pts_xy2 = [aff(pts_ag[i], affine, affine2) for i in range(4)]

# dx = (affine[2] - affine2[2]) / affine[0]
# dy = (affine[5] - affine2[5]) / affine[4]
# dx
# dy

# plt.figure(figsize=(10, 10))
# plt.imshow(raw)
# for pt in pts_xy:
#     plt.plot(pt[0], pt[1], "x", color="red")

# plt.figure(figsize=(10, 10))
# plt.imshow(raw)
# for pt in pts_xy2:
#     plt.plot(pt[0], pt[1], "x", color="red")


# # pts_xy2 = [aff(pts_ag[i], affine2, affine2) for i in range(4)]

# # plt.figure(figsize=(10, 10))
# # plt.imshow(grid_old.imgs.get("raw"))
# # for pt in pts_xy2:
# #     plt.plot(pt[0], pt[1], "x", color="red")

# pts_crop_temp = np.matmul(
#     mat_H, np.float32(pts_xy).transpose()).transpose()

# pts_crop = np.array([pts_crop_temp[i, :2] / pts_crop_temp[i, 2]
#                     for i in range(4)], dtype=int)

# plt.figure(figsize=(10, 10))
# plt.imshow(img)
# for pt in pts_crop:
#     plt.plot(pt[0], pt[1], "x", color="red")

# agent = grid.agents.get(3, 10)
# pts_crop = [[agent.border["WEST"], agent.border["NORTH"]],
#             [agent.border["EAST"], agent.border["NORTH"]],
#             [agent.border["EAST"], agent.border["SOUTH"]],
#             [agent.border["WEST"], agent.border["SOUTH"]]]
# pts_crop = [[0, 0], [0, img.shape[0]], [img.shape[1], 0], [img.shape[1], img.shape[0]]]

# plt.imshow(img)
# for pt in pts_crop:
#     plt.plot(pt[0], pt[1], "x", color="red")


# mat_H = grid.imgs.mat_H

# # pts_rec = recover_scale(pts_crop, mat_H)
# n_points = len(pts_crop)
# # conver mat_in into 4 x 3 matrix
# mat_in = np.array([list(pts_crop[i]) + [1] for i in range(4)])

# # solve recovered matrix
# mat_recover = np.matmul(np.linalg.inv(mat_H), mat_in.transpose())

# # transpose back to the right dimension (4 x 3)
# mat_recover = mat_recover.transpose()

# # extract the first 2 elements in each point (4 x 2)
# mat_recover = [mat_recover[i, :2] / mat_recover[i, 2]
#                for i in range(n_points)]

# # return
# pts_rec = np.array(np.matrix(mat_recover)).tolist()


# plt.figure(figsize=(12, 8))
# plt.imshow(raw)
# for pt in pts_rec:
#     plt.plot(pt[0], pt[1], "x", color="red")

# tiff_transform = grid.imgs.tiff_transform
# # try remapping to Tiff coordinate
# pts_rec = [list(tiff_transform * pts_rec[i])
#            for i in range(4)]


# grid.cpuSeg(outplot=True)

# ========= 20200727 recover shapefile =========
# import os, sys
# sys.path
# # sys.path.remove("/Users/jameschen/Dropbox/photo_grid/grid")
# from PyQt5.QtWidgets import QApplication
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# os.chdir("/Users/jameschen/Dropbox/photo_grid/")
# import grid as gd
# import shapefile
# import numpy as np
# import pandas as pd
# import rasterio
# import rasterio.mask

# os.getcwd()

# app = QApplication(sys.argv)
# grid = gd.GRID()
# os.chdir("/Users/jameschen/Dropbox/photo_grid/test/zhou")
# grid.loadData(
#     pathImg="/Users/jameschen/Dropbox/photo_grid/test/Jacob/RGB-integer.tif")

# grid.cropImg(pts=[[1266.6388308977034, 2754.9394572025053],
#                   [3689.0855949895613, 2200.78496868476],
#                   [4385.736951983298, 5430.713987473904],
#                   [1931.6242171189979, 5953.202505219207]], outplot=True)
# grid.binarizeImg(k=3, lsSelect=[0], valShad=0, valSmth=5)
# grid.findPlots(nRow=4, nCol=13, outplot=True)
# grid.cpuSeg(outplot=True)


# img = grid.imgs.get("crop")
# raw = grid.imgs.get("raw")


# agent = grid.agents.get(3, 10)
# pts_crop = [[agent.border["WEST"], agent.border["NORTH"]],
#             [agent.border["EAST"], agent.border["NORTH"]],
#             [agent.border["EAST"], agent.border["SOUTH"]],
#             [agent.border["WEST"], agent.border["SOUTH"]]]
# pts_crop = [[0, 0], [0, img.shape[0]], [img.shape[1], 0], [img.shape[1], img.shape[0]]]

# plt.imshow(img)
# for pt in pts_crop:
#     plt.plot(pt[0], pt[1], "x", color="red")


# mat_H = grid.imgs.mat_H

# # pts_rec = recover_scale(pts_crop, mat_H)
# n_points = len(pts_crop)
# # conver mat_in into 4 x 3 matrix
# mat_in = np.array([list(pts_crop[i]) + [1] for i in range(4)])

# # solve recovered matrix
# mat_recover = np.matmul(np.linalg.inv(mat_H), mat_in.transpose())

# # transpose back to the right dimension (4 x 3)
# mat_recover = mat_recover.transpose()

# # extract the first 2 elements in each point (4 x 2)
# mat_recover = [mat_recover[i, :2] / mat_recover[i, 2]
#                for i in range(n_points)]

# # return
# pts_rec = np.array(np.matrix(mat_recover)).tolist()


# plt.figure(figsize=(12, 8))
# plt.imshow(raw)
# for pt in pts_rec:
#     plt.plot(pt[0], pt[1], "x", color="red")

# tiff_transform = grid.imgs.tiff_transform
# # try remapping to Tiff coordinate
# pts_rec = [list(tiff_transform * pts_rec[i])
#            for i in range(4)]


# ========= 20200706 improve map flexibility =========
# import os, sys
# from PyQt5.QtWidgets import QApplication
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# import grid as gd
# from .gridGUI import *
# import shapefile
# import numpy as np
# import pandas as pd
# import rasterio
# import rasterio.mask

# os.getcwd()

# app = QApplication(sys.argv)
# grid = gd.GRID()
# os.chdir("/Users/jameschen/Dropbox/photo_grid/test/map_match")

# grid.loadData(
#     pathMap="demo2.csv",
#     pathImg="demo3.png")
# grid.binarizeImg()
# grid.findPlots()
# grid.cpuSeg()

# g = GRID_GUI(grid, 4)  # 0:input, 1:crop, 2:kmean, 3:anchor, 4:output
# app.exec_()

# ========= 20200630 improve flexibility of border defining (2 rows)=========
# import os, sys
# from PyQt5.QtWidgets import QApplication
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# import grid as gd
# from .gridGUI import *
# import shapefile
# import numpy as np
# import pandas as pd
# import rasterio
# import rasterio.mask

# os.getcwd()

# app = QApplication(sys.argv)
# grid = gd.GRID()
# os.chdir("/Users/jameschen/Dropbox/UAV/James/Chickpea/")

# grid.loadData(
#     # pathImg="70ft_20200624_5binds.tif")
#     pathImg="temp.png")
# # grid.cropImg(pts=[[704.3102766798419, 4031.569169960474],
# #                   [5925.9209486166, 2428.6561264822135],
# #                   [7674.553359683794, 8767.44861660079],
# #                   [2428.6561264822135, 10176.069169960474]])
# grid.binarizeImg(k=5, lsSelect=[0, 1], valShad=0, valSmth=5)
# grid.findPlots()
# grid.agents.setup(gmap=grid.map,
#                   gimg=grid.imgs)

# g = GRID_GUI(grid, 4)  # 0:input, 1:crop, 2:kmean, 3:anchor, 4:output
# app.exec_()

# === === === === === === Image === === === === === ===
# import os
# from PyQt5.QtWidgets import QApplication
# os.chdir("..")
# sys.path
# sys.path.remove("/Users/jameschen/Dropbox/photo_grid/grid")
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# import grid as gd
# os.getcwd()

# path = "/Users/jameschen/Downloads/drive-download-20200928T202825Z-001/PDK52_18_09_19_AltumTIFF.tif"
# rasObj = rasterio.open(path)
# rasObj.mode

# ls_dtype = rasObj.dtypes
# nCh = rasObj.count


# npImg = np.zeros((rasObj.height, rasObj.width, 3), dtype="uint8")
# for i in range(3):
#     band = rasObj.read(i + 1)
#     if "float" in ls_dtype[i]:
#         band[band < 0] = 0
#         band_int8 = (band - band.min()) * 255 / (np.quantile(band, .999) - band.min())
#         band_int8[band_int8 > 255] = 255
#         npImg[:, :, i] = band_int8
#     else:
#         npImg[:, :, i] = band


# === === === === === === CMD DEBUG === === === === === ===
# import os
# from PyQt5.QtWidgets import QApplication
# os.chdir("..")
# sys.path
# sys.path.remove("/Users/jameschen/Dropbox/photo_grid/grid")
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# import grid as gd
# os.getcwd()

# grid = gd.GRID()
# grid.loadData(
#     pathImg="/Users/jameschen/Downloads/drive-download-20200928T202825Z-001/PDK52_18_09_19_AltumTIFF.tif")
# plt.imshow(grid.imgs.get("raw")[:, :, :3])

# imgs = grid.imgs.get("raw")
# np.min(imgs, axis=(0, 1))
# np.max(imgs, axis=(0, 1))
# np.mean(imgs, axis=(0, 1))

# grid.cropImg(pts=[[4446.843373493975, 5406.265060240964],
#                   [3685.3975903614455, 2192.9638554216867],
#                   [1218.313253012048, 2725.975903614458],
#                   [1949.301204819277, 5984.963855421686]])

# grid.binarizeImg(k=5, lsSelect=[0, 1], features=[0, 1, 2], valShad=0, valSmth=0)
# grid.findPlots(nRow=4, nCol=13)
# grid.cpuSeg()
# grid.save(path="/Users/jameschen/Dropbox/photo_grid/test/Jacob/", prefix="jacob", h5=True)

# === === === === === === DEBUG === === === === === ===

# ### recover scale
# import pandas as pd
# import shapefile

# path = "/Users/jameschen/Dropbox/photo_grid/test/Jacob/"
# prefix = "jacob"
# h5 = True
# pathDT = os.path.join(path, prefix+"_data.csv")
# pathSp = os.path.join(path, prefix)

# # info
# imgH = grid.map.imgH
# dt = pd.read_csv(pathDT)
# mat_H = grid.imgs.mat_H
# tiff_transform = grid.imgs.tiff_transform
# pts_crop = grid.imgs.pts_crop
# n_rot = grid.imgs.n_rot
# org = (int(grid.imgs.widthRs / 2), int(grid.imgs.heightRs / 2))

# f = shapefile.Writer(pathSp)
# # define fields
# cols = dt.columns

# for col in cols:
#     instance = dt[col][0]

#     if isinstance(instance, object):
#         # characters
#         mode = "C"
#         arg1, arg2 = 20, 20
#     else:
#         # integer, floating
#         mode = "N"
#         arg1, arg2 = 10, 10

#     f.field(col, mode, arg1, arg2)

# # for idx, entry in dt.iterrows():
# entry = dt.iloc[0]
# # get agents
# row = entry["row"]
# col = entry["col"]
# agent = grid.agents.get(row, col)

# pts_crop = [[agent.border["WEST"], agent.border["NORTH"]],
#             [agent.border["EAST"], agent.border["NORTH"]],
#             [agent.border["EAST"], agent.border["SOUTH"]],
#             [agent.border["WEST"], agent.border["SOUTH"]]]

# # recover
# pts_rec = recover_scale(pts_crop, mat_H)

# # try remapping to Tiff coordinate if applicable
# try:
#     pts_rec = [list(tiff_transform * pts_rec[i]) for i in range(4)]
# except Exception as e:
#     print(e)

# # input shape file
# f.poly([pts_rec])

# # attributes
# dc = {c: entry[c] for c in dt.columns}
# f.record(**dict(dc))


###### ###### ###### ###### ###### ###### ###### ######

### repeatability
# import os
# os.chdir("/Users/jameschen/Dropbox/photo_grid")
# import grid as gd
# import pandas as pd
# import matplotlib.pyplot as plt
# from  scipy.stats import pearsonr

# grid = gd.GRID()
# pathImg = "/Users/jameschen/Dropbox/James Chen/Projects/GRID/Prototype/GRID_Demo_Croped.jpg"
# grid.loadData(pathImg=pathImg)
# grid.binarizeImg(k=3, lsSelect=[0], valShad=10, valSmth=0)
# grid.findPlots(nRow=23, nCol=12)
# grid.cpuSeg()

# gd.saveDT(grid, "/Users/jameschen/", prefix="g1_2")
# v1 = pd.read_csv("/Users/jameschen/g1_2_data.csv")["area_all"]


# grid = gd.GRID()
# pathImg = "/Users/jameschen/Dropbox/James Chen/Projects/GRID/Prototype/GRID_Demo_Croped.jpg"
# grid.loadData(pathImg=pathImg)
# grid.binarizeImg(k=3, lsSelect=[0], valShad=10, valSmth=0)
# grid.findPlots(nRow=23, nCol=12)
# grid.cpuSeg()

# gd.saveDT(grid, "/Users/jameschen/", prefix="g2_2")
# v2 = pd.read_csv("/Users/jameschen/g2_2_data.csv")["area_all"]

# pearsonr(v1, v2)


# plt.imshow(grid.imgs.get("bin"))
################


# plt.figure(figsize=(24, 24))
# # plt.imshow(grid.imgs.get("crop"))
# plt.imshow(grid.imgs.get("visSeg"))
# grid.findPlots(outplot=True)
# grid.cpuSeg()


# grid.save(pah="/Users/jameschen/", prefix="test")

# g = GRID_GUI(grid, 3)  # 0:input, 1:crop, 2:kmean, 3:anchor, 4:output
# app.exec_()


# ### open cv
# img = grid.imgs.get("crop")
# img.shape
# plt.imshow(img)

# pts1 = np.float32([[200, 200], [600, 300],
#                    [100, 800], [500, 900]])
# pts13 = np.float32([[200, 200, 1], [600, 300, 1],
#                     [100, 800, 1], [500, 900, 1]])
# fix = 123
# pts2 = np.float32([[0, 0], [fix, 0], [0, fix], [fix, fix]])
# pts23 = np.float32([[0, 0, 1], [fix, 0, 1], [0, fix, 1], [fix, fix, 1]])

# M = cv2.getPerspectiveTransform(pts1, pts2)

# pts2_f = np.matmul(M, pts13.transpose())
# pts2
# pts2_f.transpose()


# mat = img[:, :, 0]

# mat2 = img.reshape((-1, 1))
# mat2.shape

# np.multiply(M, img)
# dst = cv2.warpPerspective(img, M, (300, 300))


# plt.imshow(dst)

# return
# ========== peak searching ==========
# , prominence = (0.01, None)

# def findPeaks(img, nPeaks=0, axis=1, nSmooth=100):
#     """
#     ----------
#     Parameters
#     ----------
#     """
#     # compute 1-D signal
#     signal = img.mean(axis=(not axis)*1) # 0:nrow
#     # ignore signals from iamge frame
#     signal[:2] = 0
#     signal[-2:] = 0
#     # gaussian smooth
#     for _ in range(int(len(signal)/30)):
#         signal = np.convolve(
#             np.array([1, 2, 4, 2, 1])/10, signal, mode='same')
#     # find primary peaks
#     peaks, _ = find_peaks(signal)
#     lsDiff = np.diff(peaks)
#     medSig = statistics.median(signal[peaks])
#     stdSig = np.array(signal[peaks]).std()
#     medDiff = statistics.median(lsDiff)
#     stdDiff = np.array(lsDiff).std()
#     print(lsDiff)
#     print(medDiff)
#     print(stdDiff)
#     # get finalized peaks with distance constrain
#     peaks, _ = find_peaks(signal, distance=medDiff-stdDiff*4)
#     if nPeaks != 0:
#         if len(peaks) > nPeaks:
#             while len(peaks) > nPeaks:
#                 ls_diff = np.diff(peaks)
#                 idx_diff = np.argmin(ls_diff)
#                 idx_kick = idx_diff if (
#                     signal[peaks[idx_diff]] < signal[peaks[idx_diff+1]]) else (idx_diff+1)
#                 peaks = np.delete(peaks, idx_kick)
#         elif len(peaks) < nPeaks:
#             while len(peaks) < nPeaks:
#                 ls_diff = np.diff(peaks)
#                 idx_diff = np.argmax(ls_diff)
#                 peak_insert = (peaks[idx_diff]+peaks[idx_diff+1])/2
#                 peaks = np.sort(np.append(peaks, int(peak_insert)))
#     return peaks, signal


# pks, sig = findPeaks(grid.map.imgs[1])
# plt.plot(sig)
# plt.plot(pks, sig[pks], "x")
# plt.show()

# ========== peak searching ==========

# === === === find angles === === === ===
# import os
# os.chdir("..")
# sys.path
# sys.path.remove("/Users/jameschen/Dropbox/photo_grid/grid")
# import numpy as np
# import cv2
# import matplotlib.pyplot as plt
# import grid as gd
# os.getcwd()


# def rotateBinNdArray(img, angel):
#     # create border for the image
#     img[:, 0] = 1
#     img[0, :] = 1
#     img[:, -1] = 1
#     img[-1, :] = 1

#     # padding
#     sizePad = max(img.shape)
#     imgP = np.pad(img, [sizePad, sizePad], 'constant')

#     # rotate
#     pivot = tuple((np.array(imgP.shape[:2])/2).astype(np.int))
#     matRot = cv2.getRotationMatrix2D(pivot, angel, 1.0)
#     imgR = cv2.warpAffine(
#         imgP.astype(np.float32), matRot, imgP.shape, flags=cv2.INTER_LINEAR).astype(np.int8)

#     # crop
#     sigX = np.where(imgR.sum(axis=0) != 0)[0]
#     sigY = np.where(imgR.sum(axis=1) != 0)[0]
#     imgC = imgR[sigY[0]:sigY[-1], sigX[0]:sigX[-1]]

#     # return
#     return imgC

# # fq_sim = 10

# # signal = np.sin(2*np.pi*fq_sim* np.linspace(0, 1, 100))
# # signal = np.array([3,2,1,2,3,4,5,4,3,2,1,2,3,4,5,4,3])
# # fd = np.fft.fft(signal)/len(signal)
# # fd = fd[range(int(len(signal)/2))]

# # plt.subplot(211)
# # plt.plot(signal)
# # plt.subplot(212)
# # plt.plot(abs(fd))

# def getFourierTransform(sig):
#     sigf = abs(np.fft.fft(sig)/len(sig))
#     # sigf = abs(np.fft.fft(sig))
#     # sigf[0] = 0
#     # sigf[1] = 0
#     return sigf
#     # return sigf[2:25]


# grid = gd.GRID()
# grid.loadData(
#     "/Users/jameschen/Dropbox/James Chen/Projects/GRID/Manuscript/Remote Sensing/First Revision/demo/angle detection/ag4.png")
# grid.binarizeImg(k=3, lsSelect=[0], valShad=0, valSmth=60, outplot=False)

# img = grid.imgs.get("bin")
# row = 7
# col = 3
# degs = []
# sigs = []
# maxs = []
# plt.figure(figsize=(18, 15))
# for i in range(row):
#     deg = -i*15
#     degs.append(deg)
#     imgr = rotateBinNdArray(img, deg)
#     sigr = imgr.mean(axis=0)
#     # gaussian smooth
#     for _ in range(60):
#         sigr = np.convolve(
#             np.array([1, 2, 4, 2, 1])/10, sigr, mode='same')
#     sigrf = getFourierTransform(sigr)
#     sigabs = (sigrf)
#     plt.subplot(row, col, 1+i*col+0)
#     plt.axis('off')
#     plt.imshow(imgr)
#     plt.subplot(row, col, 1+i*col+1)
#     plt.plot(sigr)
#     plt.subplot(row, col, 1+i*col+2)
#     plt.ylim(0, 0.12)
#     plt.xticks(range(20), np.arange(1, 21))
#     plt.plot(sigabs[:20])
#     sigs.append(round(sum(sigabs), 4))
#     maxs.append(round(max(sigabs), 4))

# print(degs)
# print(maxs)
# print(sigs)

# === === === find angles === === === ===

# import os, sys
# import matplotlib.pyplot as plt
# import pandas as pd
# import numpy as np
# import h5py as h5

# f = h5.File("/Users/jameschen/Dropbox/James Chen/GRID/Manuscript/Remote Sensing/First Revision/demo/precision/GRID_case1.h5", "r")
# lsKey = np.array(list(f.keys()))
# np.random.shuffle(lsKey)

# row = 5
# col = 5
# plt.figure(0, figsize=(7, 4))
# for i in range(row):
#     for j in range(col):
#         idx = i*col + j
#         img = f[lsKey[idx]][:]
#         img[img.var(axis=(2)) == 0] = 255
#         ax = plt.subplot2grid((row, col), (i, j))
#         ax.set_yticklabels([])
#         ax.set_xticklabels([])
#         plt.tight_layout(pad=0.3)
#         plt.xticks([], [])
#         plt.yticks([], [])
#         ax.imshow(img[:, :, :3])
# plt.show()


# k = 5
# row = k
# col = 4
# i = 0

# grid.binarizeImg(k=k, lsSelect=[0], valShad=0, valSmth=0, outplot=False)

# === === === index value === === ===
# import os
# os.chdir("..")
# sys.path
# sys.path.remove("/Users/jameschen/Dropbox/photo_grid/grid")
# os.getcwd()

# import grid as gd
# import numpy as np
# import matplotlib.pyplot as plt

# grid = gd.GRID()
# # 90 deg
# pathImg = "/Users/jameschen/Dropbox/James Chen/Projects/GRID/Prototype/Alfalfa/GRID_Demo_Croped.jpg"
# grid.loadData(pathImg)
# grid.binarizeImg(k=3, lsSelect=[0], valShad=0, valSmth=0)
# grid.findPlots(nRow=23, nCol=12)
# grid.cpuSeg()

# # progress bar
# nD = grid.imgs.depth
# lsK = grid.imgs.paramKMs["lsSelect"]

# # grab info from GRID obj
# img = grid.imgs.get("crop").copy().astype(np.int)
# ch1Sub = 1 if img.shape[2] == 3 else 3  # replace NIR with Gr if it's RGB


# imgNum = (img[:, :, ch1Sub] - img[:, :, 0])
# imgDet = (img[:, :, ch1Sub] + img[:, :, 0] + 1e-8)
# imgNDVI = imgNum / imgDet

# imgDet.shape
# imgNum[1100:1200, 180:220]
# imgNum[1100:1200, :50]
# imgDet[1100:1200, 180:220]
# imgDet[1100:1200, :50]

# plt.imshow(img)
# plt.imshow(imgNum)
# plt.imshow(imgDet)
# plt.imshow(imgNDVI)

# === === === detect default rank of K === === === ===
# import grid as gd
# import numpy as np
# import matplotlib.pyplot as plt

# grid = gd.GRID()
# grid.loadData("/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
# # grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")

# k = 5
# row = k
# col = 4
# i = 0

# grid.binarizeImg(k=k, lsSelect=[0], valShad=0, valSmth=0, outplot=False)

# for i in range(row):
#     imgB = (np.isin(grid.imgs.get('kmean'), i)*1).astype(np.int)
#     sigs = imgB.mean(axis=0)
#     plt.subplot(row, col, 1+i*col+0)
#     plt.imshow(imgB)
#     plt.subplot(row, col, 1+i*col+1)
#     plt.ylim(0, 1)
#     plt.plot(sigs)
#     plt.subplot(row, col, 1+i*col+2)
#     sigf = gd.getFourierTransform(sigs)
#     plt.plot(sigf)
#     plt.subplot(row, col, 1+i*col+3)
#     # scMaxF = round(max(sigf)*5, 4)  # [0, 1]
#     scMaxF = round((max(sigf)/sigf.mean())/100, 4)  # [0, 1]
#     scMean = round(1-(sigs.mean()), 4) # [0, 1]
#     scPeaks = round(len(gd.find_peaks(sigs, height=(sigs.mean()))
#                   [0])/len(gd.find_peaks(sigs)[0]), 4)
#     # scPeaks = len(gd.find_peaks(sigs)[0])
#     score = scMaxF*.25 + scMean*.25 + scPeaks*.5
#     plt.text(.3, .8, str(score), fontsize=10)
#     plt.text(.3, .6, str(scMaxF), fontsize=10)
#     plt.text(.3, .4, str(scMean), fontsize=10)
#     plt.text(.3, .2, str(scPeaks), fontsize=10)

# plt.show()

# === === === detect default rank of K === === === ===


# max(getFourierTransform(sigs))


# plt.imshow()
# plt.show()

# grid = gd.GRID()
# grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
# grid.binarizeImg(k=5, lsSelect=[0], valShad=0, valSmth=0, outplot=False)
# grid.findPlots(outplot=False)
# grid.map.dt
# # grid.cpuSeg()
# # grid.save(prefix="Pumptree2")

# app = QApplication(sys.argv)
# g = GRID_GUI(grid, 4) # 0:input, 1:crop, 2:kmean, 3:anchor, 4:output
# app.exec_()


# # ========== kmean ==========
# array = numpy.array([4, 2, 7, 1])
# temp = array.argsort()
# ranks = numpy.empty_like(temp)
# ranks[temp] = numpy.arange(len(array))

# def getRank(array):
#     sort = array.argsort()
#     rank = np.zeros(len(sort), dtype=np.int)
#     rank[sort] = np.flip(np.arange(len(array)), axis=0)
#     return rank

# test = np.array([2, 6, 87,1, 3, 6])
# getRank(test)
# temp = test.argsort()
# np.zeros(len(temp))
# rank = np.empty_like(temp)
# rank[temp] = np.flip(np.arange(len(test)), axis=0)
# np.arange(1, 7, 1)
# np.arange(6, 2, 1)

# ========== plotting ==========

# FIXME: Wrong order for the second axis

# ========== peak searching ==========
# pks, sig = gd.findPeaks(grid.map.imgs[1])
# plt.plot(sig)
# plt.plot(pks, sig[pks], "x")
# plt.show()


# grid.save(prefix="Pumptree2")

# grid = gd.GRID()
# grid.loadData("/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg")
# grid.binarizeImg(k=5, lsSelect=[0], valShad=0, valSmth=0, outplot=False)
# grid.findPlots(nRow=7, nCol=6, outplot=False)
# grid.cpuSeg(outplot=True)
# grid.save(prefix="Rhombus")
# # grid.run(pathImg="/Users/jameschen/Dropbox/James Chen/GRID/Modeling/Rhombus.jpg", k=5, lsSelect=[4], path="/Users/jameschen", prefix="letmesleep")

# # with open("/Users/jameschen/Dropbox/photo_grid/Outputter_1018.grid", "wb") as file:
# #     pickle.dump(grid, file, pickle.HIGHEST_PROTOCOL)

# # grid.loadData("/Users/jameschen/Dropbox/James_Git/FN/data/demo.png")
# # grid.binarizeImg(k=3, lsSelect=[0, 1], valShad=0, valSmth=0, outplot=False)


# g = GRID_GUI(grid, 4)
# app.exec_()

#
#
#

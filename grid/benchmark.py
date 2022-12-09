import time
import matplotlib.pyplot as plt
import cv2
import numpy as np
import rasterio
import os
os.chdir("/Users/jameschen/Dropbox/photo_grid")
import grid as gd
os.chdir("/Users/jameschen/Dropbox/James Chen/GRID/Manuscript/Remote Sensing/")
os.chdir("First Revision/demo/")

# load the 1st demo file
img = gd.loadImg("demo_1.tif")


# define output function
def out_diff_size(imgIn, pts, path, size):
    img = gd.cropImg(imgIn, pts, img_W=size, img_H=size).astype(rasterio.uint8)
    bands = img.shape[2]
    with rasterio.open(path, 'w', driver="GTiff",
                       height=img.shape[0], width=img.shape[1],
                       count=bands, dtype=rasterio.uint8) as dst:
        for i in range(bands):
            dst.write(img[:, :, i], i+1)


# crop AOI for demo
pts = [[2879.464480874317, 5707.814207650273],
       [5758.928961748634, 5861.158469945355],
       [5571.508196721311, 8945.081967213115],
       [2709.0819672131147, 8808.775956284153]]

# output different file size of data from the same AOI
out_diff_size(img, pts, "size/size_2_0gb.tif", 18500)
out_diff_size(img, pts, "size/size_1_5gb.tif", 15700)
out_diff_size(img, pts, "size/size_1_0gb.tif", 13000)
out_diff_size(img, pts, "size/size_0_5gb.tif", 9150)
out_diff_size(img, pts, "size/size_0_1gb.tif", 4100)

# output different plot number of data from the same file size 500 MB
# 5*10 = 50
out_diff_size(img,
              [[2860.333586050038, 5697.028051554207],
               [2777.5966641395, 6985.360121304018],
               [4125.02653525398, 5779.764973464746],
               [4065.92873388931, 7044.457922668688]],
              "plot/plot_50.tif", 9150)

# 10*10 = 100
out_diff_size(img,
              [[2860.333586050038, 5697.028051554207],
               [4136.846095526915, 5767.945413191812],
               [3971.3722517058377, 8297.331311599697],
               [2730.3184230477636, 8226.413949962092]],
              "plot/plot_100.tif", 9150)

# 10*15 = 150
out_diff_size(img,
              [[2860.333586050038, 5708.847611827142],
               [2718.4988627748294, 8226.413949962092],
               [4621.44806671721, 8344.609552691432],
               [4763.282789992419, 5815.223654283548]],
              "plot/plot_150.tif", 9150)

# 10*20 = 200
out_diff_size(img,
              [[2848.5140257771036, 5697.028051554207],
               [2718.4988627748294, 8226.413949962092],
               [5236.06520090978, 8380.068233510236],
               [5401.539044730856, 5838.862774829417]],
              "plot/plot_200.tif", 9150)


# output benchmark results for size comparison
with open("benchmark_size.csv", "w") as f:
    f.write("size,elapse,iter\n")

dic_size = {"2_0": 2,
            "1_5": 1.5,
            "1_0": 1.0,
            "0_5": 0.5,
            "0_1": 0.1}

for i in range(100):
    for key, val in dic_size.items():
        # time the loading process
        t_cur = time.time()
        grid = gd.GRID()
        grid.loadData("size/size_%sgb.tif" % key)
        elapse = round(time.time() - t_cur, 4)
        # export results
        with open("benchmark_size.csv", "a") as f:
            f.write("%d,%.4f,%d\n" % (val, elapse, i))


# output benchmark results for plots comparison
with open("benchmark_plot.csv", "w") as f:
    f.write("plot,ep_plots,ep_seg,iter\n")

dic_plot = {"50": (50, 5, 10), 
            "100": (100, 10, 10),
            "150": (150, 10, 15),
            "200": (200, 10, 20)}

for i in range(100):
    for key, val in dic_plot.items():
        nplot, nrow, ncol = val
        grid = gd.GRID()
        grid.loadData("plot/plot_%d.tif" % nplot)
        w, h, d = grid.imgs.get("raw").shape
        grid.cropImg(pts=[[0, 0], [0, w], [h, 0], [h, w]])
        grid.binarizeImg(k=3, lsSelect=[0], valShad=0, valSmth=0)
        # locate center
        t_cur = time.time()
        grid.findPlots(nRow=nrow, nCol=ncol)
        ep_pt = round(time.time() - t_cur, 4)
        # expand boundaries
        t_cur = time.time()
        grid.cpuSeg()
        ep_sg = round(time.time() - t_cur, 4)
        # export results
        with open("benchmark_plot.csv", "a") as f:
            f.write("%d,%.4f,%.4f,%d\n" % (nplot, ep_pt, ep_sg, i))

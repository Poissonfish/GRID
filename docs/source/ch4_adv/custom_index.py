import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
os.chdir("/Users/jameschen/Dropbox/photo_grid/docs/source/res/GRID3")

dt = pd.read_csv("GRID_data.csv")


dt_idx = dt[["area_veg", "NDVI"] + ["ch_%d" % i for i in range(1, 7)]].dropna()
dt_idx


dt_results = pd.DataFrame(columns=["x0", "x1", "form", "r", "r2"])

ls_formula = {"(x0 - x1) / (x0 + x1)": lambda x0, x1: (x0 - x1) / (x0 + x1),
              "x0 / x1":               lambda x0, x1: x0 / x1,
              "(x0 ^ 2) + (x1 ^ 2)":   lambda x0, x1: (x0 ** 2) + (x1 ** 2)}


cols_ignored = 2  # we won't loop over the first 2 columns
p = 6  # number of channels we'd like to loop over
for i in range(p):
    for j in range(p):
        x0 = dt_idx.iloc[:, cols_ignored + i]
        x1 = dt_idx.iloc[:, cols_ignored + j]
        ls_idx = [list(ls_formula.values())[i](x0, x1) for i in range(3)]
        dt_temp = pd.DataFrame({
            "x0":   i,
            "x1":   j,
            "form": list(ls_formula.keys()),
            "r":    [pearsonr(dt_idx["area_veg"], ls_idx[i])[0]
                     for i in range(3)],
            "r2":   [pearsonr(dt_idx["area_veg"], ls_idx[i])[0] ** 2
                     for i in range(3)]
        })
        dt_results = dt_results.append(dt_temp)

dt_results

r2_ndvi = pearsonr(dt_idx["area_veg"], dt_idx["NDVI"])[0] ** 2
r2_ndvi

dt_results.loc[dt_results.r2.isna(), "r2"] = 0


plt.figure(figsize=(30, 10))
fig, axes = plt.subplots(1, 3, constrained_layout=True)
# Heatmap showing how derived indices associate with canopy areas
for i in range(3):
    # get r2 values by each formula
    formula = list(ls_formula.keys())[i]
    ls_r2 = dt_results.loc[dt_results.form == formula, "r2"]
    # reshape the list to a 2D matrix
    M = np.array(ls_r2).reshape((p, p))
    # plot interface
    axes[i].set_title(list(ls_formula.keys())[i])
    axes[i].set_xlabel("x1")
    axes[i].set_ylabel("x0")
    for x0 in range(p):
        for x1 in range(p):
            text = axes[i].text(x0, x1, round(M[x1, x0], 3),
                            ha="center", va="center", color="w", fontsize=4)
    plt.sca(axes[i])
    plt.xticks(ticks=np.arange(p))
    plt.yticks(ticks=np.arange(p))
    axes[i].imshow(M)  # , vmin=r2_ndvi



dt_select = dt_results.loc[dt_results.r2 >r2_ndvi].\
                sort_values(by="r2", ascending=False)
dt_select



def to8bit(img_in):
    img_out = (img_in - img_in.min()) / (img_in.max() - img_in.min()) * 255
    return img_out.astype(np.uint8)



img = np.load("GRID_image.npy")
img_idx = img[:, :, 0] / (img[:, :, 4] + 1e-9)
plt.imshow((img_idx))

plt.imshow(img[:, :, :3])

img_idx_flip = abs(img_idx - img_idx.max())
fig, axes = plt.subplots(1, 2, figsize=(8, 18), constrained_layout=True)
axes[0].imshow(img[:, :, :3])
axes[1].imshow(img_idx_flip)

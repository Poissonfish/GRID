import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
import h5py as h5

os.chdir("/Users/jameschen/Dropbox/photo_grid/docs/source/ch4_adv/res/seasons/")


dt_s1 = pd.read_csv("s1_data.csv").loc[:, ["var", "area_veg", "NDVI"]]
dt_s2 = pd.read_csv("s2_data.csv").loc[:, ["var", "area_veg", "NDVI"]]

dt_s1.columns = ["id", "canopy_s1", "ndvi_s1"]
dt_s2.columns = ["id", "canopy_s2", "ndvi_s2"]
dt = pd.merge(dt_s1, dt_s2)

plt.scatter(dt.ndvi_s1, dt.ndvi_s2)
pearsonr(dt.ndvi_s1, dt.ndvi_s2)[0] ** 2

plt.scatter(dt.canopy_s1, dt.canopy_s2)
pearsonr(dt.canopy_s1, dt.canopy_s2)[0] ** 2

dt.loc[:, "growth_rate"] = (dt.canopy_s2 - dt.canopy_s1) / dt.canopy_s1

_ = plt.hist(dt.growth_rate.values)

cutoff = 1
dt.loc[dt.growth_rate >= cutoff, "isElite"] = True
dt.loc[dt.growth_rate < cutoff, "isElite"] = False

plt.scatter(x=dt[dt.isElite].canopy_s1, 
            y=dt[dt.isElite].canopy_s2, 
            label="elite")
plt.scatter(x=dt[~dt.isElite].canopy_s1, 
            y=dt[~dt.isElite].canopy_s2, 
            label="non-elite")
plt.legend()


dt.sort_values(by="growth_rate", ascending=False, inplace=True)
dt


id_elite = dt[:3].id.values


def extract_imgs_from_h5(filename, ids):
    ls_imgs = []  
    with h5.File(filename, "r") as f:
        for id in ids:
            ls_imgs += [np.swapaxes(f[id+"_raw"][:], 0, 1)]
    return ls_imgs

imgs_s1 = extract_imgs_from_h5("s1.h5", id_elite)
imgs_s2 = extract_imgs_from_h5("s2.h5", id_elite)

fig, axes = plt.subplots(2, 3, figsize=(20, 10))
plt.subplots_adjust(hspace=0, bottom=0, top=.3)
for i in range(3):
    axes[0, i].imshow(imgs_s1[i])
    axes[0, i].set_title(id_elite[i])
    axes[1, i].imshow(imgs_s2[i])

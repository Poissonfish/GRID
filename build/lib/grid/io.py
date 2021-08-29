# Basic imports
import io
import os
import numpy as np
import pandas as pd
from urllib.request import urlopen
from PIL import Image

# 3-rd party imports
from PyQt5.QtCore import QFile, QIODevice
import h5py
import rasterio
import shapefile
import cv2


# self import
from .lib import find_small_shape, initProgress, updateProgress, pltImShow, pltSegPlot, recover_scale
from .dir import Dir


def loadImg(path):
    """
    ----------
    Parameters
    ----------
    path : str
           path to the image file

    -------
    Returns
    -------
    npImg : 3-d ndarray encoded in UINT8

    """

    # rasObj = rasterio.open(path)
    # nCh = rasObj.count
    # obj = initProgress(nCh, "loading channel 1")
    # if nCh < 3:
    #     npImg = np.zeros((rasObj.height, rasObj.width, 3), dtype="uint8")
    #     for i in range(3):
    #         npImg[:, :, i] = rasObj.read(1)
    #         updateProgress(obj, 1, "loading channel %d" %
    #                        (i+2 if i != (nCh-1) else i+1))
    # else:
    #     npImg = np.zeros((rasObj.height, rasObj.width, nCh), dtype="uint8")
    #     for i in range(nCh):
    #         npImg[:, :, i] = rasObj.read(i + 1)
    #         updateProgress(obj, "loading channel %d" % (i+2) if i != (nCh-1)
    # e
    # lse "Done")

    # return npImg
    rasObj = rasterio.open(path)
    ls_dtype = rasObj.dtypes
    nCh = rasObj.count
    prog = initProgress(nCh, name="Loading channel 1")
    if nCh < 3:
        npImg = np.zeros((rasObj.height, rasObj.width, 3), dtype="uint8")
        for i in range(3):
            npImg[:, :, i] = getBandUint8(rasObj.read(1), ls_dtype[1])
            if i != nCh-1:
                updateProgress(prog, name="Loading channel %d" % (i+2))
            else:
                updateProgress(prog, name="Done")
    else:
        npImg = np.zeros((rasObj.height, rasObj.width, nCh), dtype="uint8")
        for i in range(nCh):
            npImg[:, :, i] = getBandUint8(rasObj.read(i + 1), ls_dtype[i])
            if i != nCh-1:
                updateProgress(prog, name="Loading channel %d" % (i+2))
            else:
                updateProgress(prog, name="Done")

    # try to fetch geo info
    transform = rasObj.transform

    # fetch projection info
    try:
        crs = rasObj.crs.wkt
    except Exception:
        crs = False

    rasObj.close()

    # resize to avoid cv2 int16 limit (32767)
    h, w = find_small_shape(npImg.shape[:2])
    npImg = cv2.resize(npImg, (w, h))
    print("")
    print("GRID: Image was reshaped to (%d, %d)" % (h, w))

    # return
    return npImg, transform, crs


def getBandUint8(band, dtype):
    if "float" in dtype:
        band[band < 0] = 0
        band_int8 = (band - band.min()) * 255 / \
                    (np.quantile(band, .999) - band.min())
        band_int8[band_int8 > 255] = 255
        return band_int8
    else:
        return band


def loadImgWeb(URL):
    """
    ----------
    Parameters
    ----------
    URL : str
          URL to the UINT8-encoded image file

    -------
    Returns
    -------
    npImg : 3-d ndarray encoded in UINT8

    """

    with urlopen(URL)as url:
        file = io.BytesIO(url.read())
        npImg = np.array(Image.open(file), dtype="uint8")

    return npImg


def loadMap(path):
    """
    ----------
    Parameters
    ----------
    path : str
           path to the csv file

    -------
    Returns
    -------
    pdMap : Pandas dataframe or None if path is empty

    """

    try:
        pdMap = pd.read_csv(path, header=None)
    except Exception:
        pdMap = None

    return pdMap


def saveQImg(qimg, path):
    """
    ----------
    Parameters
    ----------
    qimg : qimage

    path : str
           path to the destination
    -------
    Returns
    -------
    None

    """

    qfile = QFile(path + ".jpg")
    qfile.open(QIODevice.WriteOnly)
    qimg.save(qfile, "JPG")
    qfile.close()


def saveDT(grid, path, prefix="GRID", simple=True):
    # save npy
    if not simple:
        np.save(os.path.join(path, prefix+"_image.npy"), grid.imgs.get("crop"))

    # get path
    pathDT = os.path.join(path, prefix+"_data.csv")

    # progress bar
    nD = grid.imgs.depth
    lsK = grid.imgs.paramKMs["lsSelect"]

    # grab info from GRID obj
    img = grid.imgs.get("crop").copy().astype(np.int)
    ch1Sub = 1 if img.shape[2] == 3 else 3  # replace NIR with Gr if it's RGB

    # intialize dataframe
    df = pd.DataFrame(columns=['var', 'row', 'col',
                               'area_all', 'area_veg'])

    # calculate index imgs
    dicIdx = dict({
        "NDVI": (img[:, :, ch1Sub] - img[:, :, 0]) /
                (img[:, :, ch1Sub] + img[:, :, 0] + 1e-8),
        "GNDVI": (img[:, :, ch1Sub] - img[:, :, 1]) /
                (img[:, :, ch1Sub] + img[:, :, 1] + 1e-8),
        "CNDVI": (2 * img[:, :, ch1Sub] - img[:, :, 0] - img[:, :, 1]) /
                (img[:, :, ch1Sub] + img[:, :, 0] + img[:, :, 1] + 1e-8),
        "RVI": img[:, :, ch1Sub] / (img[:, :, 0] + 1e-8),
        "GRVI": img[:, :, ch1Sub] / (img[:, :, 1] + 1e-8),
        "NDGI": (img[:, :, 1] - img[:, :, 0]) /
                (img[:, :, 1] + img[:, :, 0] + 1e-8)
    })

    # channel values
    for i in range(nD):
        name = "ch_%d" % (i + 1)
        dicIdx[name] = img[:, :, i]

    # # ratio of each cluster (k)
    # cluster = 0
    # for k in lsK:
    #     name = "cluster_%d" % cluster
    #     dicIdx[name] = (np.isin(grid.imgs.get("kmean"), i))*1
    #     cluster += 1

    # append columns based on the dict
    for key, _ in dicIdx.items():
        df[key] = None
        df[key + "_std"] = None

    # index data frame
    for row in range(grid.agents.nRow):
        for col in range(grid.agents.nCol):
            agent = grid.agents.get(row, col)
            if not agent or agent.isFake():
                continue
            try:
                entry = dict(var=str(agent.name),
                             row=int(row + 1),
                             col=int(col + 1))

                # compute valid ranges
                rg_row, rg_col = get_valid_range(agent, grid.imgs.get('bin'))

                # get selected pixels info
                imgBinAgent = grid.imgs.get('bin')[rg_row, :][:, rg_col]
                n_veg = imgBinAgent.sum()

                # load area info
                entry["area_all"] = len(rg_row)*len(rg_col)
                entry["area_veg"] = n_veg

                # append temp entry
                for key, imgIdx in dicIdx.items():
                    imgIdxAgent = imgIdx[rg_row, :][:, rg_col]
                    img_out = np.multiply(imgBinAgent, imgIdxAgent)
                    vec_out = img_out[img_out != 0].flatten()
                    entry[key] = vec_out.mean()
                    entry[key + "_std"] = vec_out.std()

                df.loc[len(df)] = entry

            except Exception as e:
                print("=====row: %d, col: %d=====" % (row, col))
                print(e)
                print("The plot is out of the borders")

    df = df[~df['var'].isnull()]

    # export
    df.to_csv(pathDT, index=False)


def savePlot(grid, path, prefix="GRID", simple=True):
    # raw-none
    pltSegPlot(grid.agents, grid.imgs.get("crop")[:, :, :3],
               path=path, prefix=prefix, filename="_raw.png")
    if not simple:
        # raw-center
        pltSegPlot(grid.agents, grid.imgs.get("crop")[:, :, :3],
                   isCenter=True,
                   path=path, prefix=prefix, filename="_raw_centroid.png")
        # raw-frame
        pltSegPlot(grid.agents, grid.imgs.get("crop")[:, :, :3],
                   isRect=True,
                   path=path, prefix=prefix, filename="_raw_border.png")
        # raw-both
        pltSegPlot(grid.agents, grid.imgs.get("crop")[:, :, :3],
                   isCenter=True, isRect=True,
                   path=path, prefix=prefix, filename="_raw_both.png")

    # cluster-none
    pltSegPlot(grid.agents, grid.imgs.get("kmean"),
               path=path, prefix=prefix, filename="_kmeans.png")
    if not simple:
        # cluster-center
        pltSegPlot(grid.agents, grid.imgs.get("kmean"),
                   isCenter=True,
                   path=path, prefix=prefix, filename="_kmeans_centroid.png")
        # cluster-frame
        pltSegPlot(grid.agents, grid.imgs.get("kmean"),
                   isRect=True,
                   path=path, prefix=prefix, filename="_kmeans_border.png")
        # cluster-both
        pltSegPlot(grid.agents, grid.imgs.get("kmean"),
                   isCenter=True, isRect=True,
                   path=path, prefix=prefix, filename="_kmeans_both.png")

    # binary-none
    pltSegPlot(grid.agents, grid.imgs.get("bin"),
               path=path, prefix=prefix, filename="_bin.png")
    if not simple:
        # binary-center
        pltSegPlot(grid.agents, grid.imgs.get("bin"),
                   isCenter=True,
                   path=path, prefix=prefix, filename="_bin_centroid.png")
        # binary-frame
        pltSegPlot(grid.agents, grid.imgs.get("bin"),
                   isRect=True,
                   path=path, prefix=prefix, filename="_bin_border.png")
        # binary-both
        pltSegPlot(grid.agents, grid.imgs.get("bin"),
                   isCenter=True, isRect=True,
                   path=path, prefix=prefix, filename="_bin_both.png")

    if not simple:
        # extraction-none
        pltSegPlot(grid.agents, grid.imgs.get("visSeg"),
                   path=path, prefix=prefix, filename="_seg.png")
        # extraction-center
        pltSegPlot(grid.agents, grid.imgs.get("visSeg"),
                   isCenter=True,
                   path=path, prefix=prefix, filename="_seg_centroid.png")
        # extraction-frame
        pltSegPlot(grid.agents, grid.imgs.get("visSeg"),
                   isCenter=True, isRect=True,
                   path=path, prefix=prefix, filename="_seg_both.png")

    # extraction-frame
    pltSegPlot(grid.agents, grid.imgs.get("visSeg"),
               isRect=True,
               path=path, prefix=prefix, filename="_seg_border.png")
    # extraction-ID
    pltSegPlot(grid.agents, grid.imgs.get("visSeg"),
               isName=True, isRect=True,
               path=path, prefix=prefix, filename="_seg_ID.png")


def saveH5(grid, path, prefix="GRID"):
    # get path
    pathH5 = os.path.join(path, prefix+".h5")

    # create file
    with h5py.File(pathH5, "w"):
        None  # create file

    # index data frame
    img = grid.imgs.get("crop").copy()
    for row in range(grid.agents.nRow):
        for col in range(grid.agents.nCol):
            try:
                agent = grid.agents.get(row, col)
                if not agent or agent.isFake():
                    continue
                key = str(agent.name)

                # get ROI region
                rgY, rgX = get_valid_range(agent, grid.imgs.get('bin'))

                # compute kernel
                imgAll = img[:, rgX, :][rgY, :, :]
                imgBin = grid.imgs.get("bin")[:, rgX][rgY, :]
                imgFin = np.multiply(imgAll, np.expand_dims(imgBin, 2))
            except Exception as e:
                print("%s: The plot is out of the borders" % key)
                print(e)

            # export image
            try:
                with h5py.File(pathH5, "a") as f:
                    f.create_dataset(key, data=imgFin, compression="gzip")
                    f.create_dataset(key+"_raw", data=imgAll,
                                     compression="gzip")
            except Exception as e:
                print("Failed to save %s" % key)
                print(e)


def saveShape(grid, path, prefix="GRID"):
    pathDT = os.path.join(path, prefix+"_data.csv")
    pathSp = os.path.join(path, prefix)

    # info
    imgH = grid.map.imgH
    dt = pd.read_csv(pathDT)
    mat_H = grid.imgs.mat_H
    tiff_transform = grid.imgs.tiff_transform
    crs = grid.imgs.crs
    pts_crop = grid.imgs.pts_crop
    n_rot = grid.imgs.n_rot
    org = (int(grid.imgs.widthRs / 2), int(grid.imgs.heightRs / 2))

    with shapefile.Writer(pathSp) as f:
        # define fields
        cols = dt.columns

        for col in cols:
            instance = dt[col][0]

            try:
                float(instance)
                # integer, floating
                mode = "N"
                arg1, arg2 = 50, 50
            except ValueError:
                # characters
                mode = "C"
                arg1, arg2 = 50, 50

            if col == cols[0]:
                mode = "C"
                arg1, arg2 = 50, 50

            f.field(col, mode, arg1, arg2)

        for idx, entry in dt.iterrows():
            try:
                # get agents (the table is 1-index)
                row = entry["row"] - 1
                col = entry["col"] - 1
                agent = grid.agents.get(row, col)

                # polygon
                bn, bs, bw, be = get_valid_range(
                    agent, grid.imgs.get('bin'), is_border=True)
                pts_crop = [[bw, bn],
                            [be, bn],
                            [be, bs],
                            [bw, bs]]

                # recover
                pts_rec = recover_scale(pts_crop, mat_H)

                # try remapping to Tiff coordinate
                pts_rec = [list(tiff_transform * pts_rec[i]) for i in range(4)]

                # input shape file
                f.poly([pts_rec])
            except Exception as e:
                print("%s: The plot is out of the borders" % entry["var"])
                print(e)

            # attributes
            dc = {c: entry[c] for c in dt.columns}
            f.record(**dict(dc))

    try:
        with open(pathSp + ".prj", "w") as f:
            f.write(crs)
    except Exception:
        print("No CRS found to write")


def get_valid_range(agent, img, is_border=False):
    # get border values
    bn = int(agent.getBorder(Dir.NORTH))
    bs = int(agent.getBorder(Dir.SOUTH))
    bw = int(agent.getBorder(Dir.WEST))
    be = int(agent.getBorder(Dir.EAST))

    # get image dimension
    imgH, imgW = img.shape

    # adjust to valid ranges
    if bn < 0:
        bn = 0
    if bw < 0:
        bw = 0
    if bs > imgH:
        # height
        bs = imgH
    if be >= imgW:
        # width
        be = imgW

    # make ranges
    rg_row = range(bn, bs)
    rg_col = range(bw, be)

    # return
    if is_border:
        return bn, bs, bw, be
    else:
        return rg_row, rg_col


# # create the PRJ file
# prj = open("%s.prj" % filename, "w")
# epsg = 'GEOGCS["WGS 84",'
# epsg += 'DATUM["WGS_1984",'
# epsg += 'SPHEROID["WGS 84",6378137,298.257223563]]'
# epsg += ',PRIMEM["Greenwich",0],'
# epsg += 'UNIT["degree",0.0174532925199433]]'
# prj.write(epsg)
# prj.close()
# WGS84-UTM


# PROJCS["WGS 84 / UTM zone 20N",
# GEOGCS["WGS 84",DATUM["WGS_1984",
# SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",-63],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["Easting",EAST],AXIS["Northing",NORTH],AUTHORITY["EPSG","32620"]]'

# PROJCS["WGS 84 / UTM zone 20N",
# GEOGCS["WGS 84",
# DATUM["WGS_1984",
# SPHEROID["WGS 84", 6378137, 298.257223563,
# AUTHORITY["EPSG", "7030"]],
# AUTHORITY["EPSG", "6326"]],
# PRIMEM["Greenwich", 0,
#  AUTHORITY["EPSG", "8901"]],
# UNIT["degree", 0.0174532925199433,
# AUTHORITY["EPSG", "9122"]],
# AUTHORITY["EPSG", "4326"]],
#        PROJECTION["Transverse_Mercator"],
#        PARAMETER["latitude_of_origin", 0],
#        PARAMETER["central_meridian", -63],
#        PARAMETER["scale_factor", 0.9996],
#        PARAMETER["false_easting", 500000],
#        PARAMETER["false_northing", 0],
#        UNIT["metre", 1, AUTHORITY["EPSG", "9001"]],
#        AXIS["Easting", EAST], AXIS["Northing", NORTH], A
#        UTHORITY["EPSG", "32620"]]


# PROJCS["WGS_1984_UTM_Zone_20N",
#        GEOGCS["GCS_WGS_1984",
#               DATUM["D_WGS_1984",
#                     SPHEROID["WGS_1984", 6378137, 298.257223563]],
#               PRIMEM["Greenwich", 0],
#               UNIT["Degree", 0.017453292519943295]],
#        PROJECTION["Transverse_Mercator"],
#        PARAMETER["latitude_of_origin", 0],
#        PARAMETER["central_meridian", -63],
#        PARAMETER["scale_factor", 0.9996],
#        PARAMETER["false_easting", 500000],
#        PARAMETER["false_northing", 0], UNIT["Meter", 1]]

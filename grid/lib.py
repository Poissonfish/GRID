# basic imports
import numpy as np
import sys
import time
import math
import os
import pickle
import statistics

# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from tqdm import tqdm, tqdm_gui
import cv2
from scipy.signal import convolve2d
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.lines import Line2D


def find_small_shape(shape_src, limits=32767, rate=0.95):
    h, w = shape_src
    while max(h, w) > limits:
        h *= rate
        w *= rate
    return int(h), int(w)


def doKMeans(img, k=3, features=[0]):
    """
    ----------
    Parameters
    ----------
    """

    # data type conversion for opencv
    ## select features
    img = img[:, :, features].copy()
    ## standardize
    img_max, img_min = img.max(axis=(0, 1)), img.min(axis=(0, 1))-(1e-8)
    img = (img-img_min)/(img_max-img_min)
    ## convert to float32
    img_z = img.reshape((-1, img.shape[2])).astype(np.float32)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    param_k = dict(data=img_z,
                   K=k,
                   bestLabels=None,
                   criteria=criteria,
                   attempts=10,
                   #    flags=cv2.KMEANS_RANDOM_CENTERS)
                   flags=cv2.KMEANS_PP_CENTERS)

    # KMEANS_RANDOM_CENTERS
    cv2.setRNGSeed(99163)
    _, img_k_temp, center = cv2.kmeans(**param_k)

    # Convert back
    img_k = img_k_temp.astype(np.uint8).reshape((img.shape[0], -1))

    # return
    return img_k, center


def blurImg(image, n, cutoff=0.5):
    image = smoothImg(image=image, n=n)
    return binarizeSmImg(image, cutoff=cutoff)


def smoothImg(image, n):
    """
    ----------
    Parameters
    ----------
    """

    kernel = np.array((
        [1, 4, 1],
        [4, 9, 4],
        [1, 4, 1]), dtype='int') / 29

    for _ in range(n):
        image = convolve2d(image, kernel, mode='same')

    return image


def binarizeSmImg(image, cutoff=0.5):
    """
    ----------
    Parameters
    ----------
    """
    imgOut = image.copy()
    imgOut[image > cutoff] = 1
    imgOut[image <= cutoff] = 0

    return imgOut.astype(np.int)


def find_angle(v1, v2):
    dot_product = np.dot(v1 / np.linalg.norm(v1), v2 / np.linalg.norm(v2))
    # cap dot_product
    if dot_product > 1:
        dot_product = 1
    elif dot_product < -1:
        dot_product = -1
    angle = np.arccos(dot_product) * 180 / np.pi
    if v1[0] * v2[1] - v1[1] * v2[0] > 0:
        return angle
    else:
        return 360 - angle


def sortPts(pts):
    """
    NOTE: qmap has inverse Y! UP has smaller y value
    """
    # get centroid to calculate vector
    pts_center = np.median(pts, axis=0)
    vec = pts - pts_center

    # get order
    vec_ag = [find_angle(vec[i], (-1, 0)) for i in range(4)]
    order = np.flip(np.argsort(vec_ag))
    # return sorted pts
    return np.array(pts)[order]


def cropImg(img, pts, resize=2048):
    """
    Perspectively project assigned area (pts) to a rectangle image
    -----
    param.
    -----
    img: 2-d numpy array
    pts: a vector of xy coordinate, length is 4. Must be in the order as:
         (NW, NE, SE, SW)
    """

    # define input coordinates
    pts = np.float32(pts)

    # assign sorted pts
    pt_NW, pt_NE, pt_SE, pt_SW = sortPts(pts)

    # estimate output dimension
    img_W = (euclidean(pt_NW, pt_NE) + euclidean(pt_SE, pt_SW))/2
    img_H = (euclidean(pt_SE, pt_NE) + euclidean(pt_SW, pt_NW))/2

    # resize output dimension
    shape = find_small_shape((img_W, img_H), limits=resize)

    # generate target point
    pts2 = np.float32(
        # NW,    NE,            SE,                   SW
        [[0, 0], [shape[0], 0], [shape[0], shape[1]], [0, shape[1]]])

    # transformation
    H = cv2.getPerspectiveTransform(pts, pts2)
    dst = cv2.warpPerspective(img, H, (shape[0], shape[1]))
    dst = np.array(dst).astype(np.uint8)

    # return cropped image and H matrix
    return dst, H


def euclidean(p1, p2):
    """
    calculate Euclidean distance betweeen p1 and p2
    input can be either tuple or matrix
    """

    p1, p2 = np.array(p1), np.array(p2)
    return sum((p1 - p2) ** 2) ** (0.5)


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


# def rotate(origin, point, angle):
#     """
#     Rotate a point counterclockwise by a given angle around a given origin.

#     The angle should be given in radians.

#     @ contributed by Mark Dickinson
#     https://stackoverflow.com/users/270986/mark-dickinson
#     source:
#     https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
#     """
#     ox, oy = origin
#     px, py = point

#     ag = np.pi / 180 * angle
#     qx = ox + np.cos(ag) * (px - ox) - np.sin(ag) * (py - oy)
#     qy = oy + np.sin(ag) * (px - ox) + np.cos(ag) * (py - oy)
#     return qx, qy

# === === === === === GRID pickle === === === === ===

def pickleGRID(obj, path):
    with open(path, "wb") as file:
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)


def getPickledGRID(path):
    with open(path, "rb") as file:
        obj = pickle.load(file)

    return obj

# === === === === === rank === === === === ===


def getRank(array):
    """
    ----------
    Results
    ----------
    [1,3,6,2,4] -> [4,2,0,3,1]
    """
    sort = np.array(array).argsort()
    rank = np.zeros(len(sort), dtype=np.int)
    rank[sort] = np.flip(np.arange(len(array)), axis=0)
    return rank


# === === === === === peak searching === === === === ===
def rotateNdArray(img, angle):
    depth = img.shape[2]
    list_img = []

    for i in range(depth):
        imgTemp = img[:, :, i]
        if imgTemp.max() > 1:
            val_max = 255
        else:
            val_max = 1

        # create border for the image
        imgTemp[:, 0:2] = val_max
        imgTemp[0:2, :] = val_max
        imgTemp[:, -2:] = val_max
        imgTemp[-2:, :] = val_max

        # padding
        sizePad = max(imgTemp.shape)
        imgP = np.pad(imgTemp, [sizePad, sizePad], 'constant')

        # rotate
        pivot = tuple((np.array(imgP.shape[:2])/2).astype(np.int))
        matRot = cv2.getRotationMatrix2D(pivot, -angle, 1.0)
        imgR = cv2.warpAffine(
            imgP.astype(np.float32), matRot, imgP.shape, flags=cv2.INTER_LINEAR).astype(np.uint8)

        # crop
        sigX = np.where(imgR.sum(axis=0) != 0)[0]
        sigY = np.where(imgR.sum(axis=1) != 0)[0]
        imgC = imgR[sigY[0]:sigY[-1], sigX[0]:sigX[-1]]

        # store output img
        list_img.append(imgC)

    imgFinal = np.array(list_img)
    imgFinal = np.swapaxes(imgFinal, 0, 1)
    imgFinal = np.swapaxes(imgFinal, 1, 2)

    return imgFinal


def rotateBinNdArray(img, angle):
    # create border for the image
    img[:, 0:2] = 1
    img[0:2, :] = 1
    img[:, -2:] = 1
    img[-2:, :] = 1

    # padding
    sizePad = max(img.shape)
    imgP = np.pad(img, [sizePad, sizePad], 'constant')

    # rotate
    pivot = tuple((np.array(imgP.shape[:2])/2).astype(np.int))
    matRot = cv2.getRotationMatrix2D(pivot, -angle, 1.0)
    imgR = cv2.warpAffine(
        imgP.astype(np.float32), matRot, imgP.shape, flags=cv2.INTER_LINEAR).astype(np.uint8)

    # crop
    sigX = np.where(imgR.sum(axis=0) != 0)[0]
    sigY = np.where(imgR.sum(axis=1) != 0)[0]
    imgC = imgR[sigY[0]:sigY[-1], sigX[0]:sigX[-1]]

    # return
    return imgC


def rotateVec(vec, angle):
    deg = np.pi / 180
    x, y = vec[0], vec[1]
    xp = np.cos(deg * angle) * x - np.sin(deg * angle) * y
    yp = np.sin(deg * angle) * x + np.cos(deg * angle) * y
    return (xp, yp)


def invAffine(pt, affine, is3d=True):
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
    return (xg, yg, 1) if is3d else (xg, yg)


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
    mat_in = np.array([list(mat_in[i]) + [1] for i in range(4)])

    # solve recovered matrix
    mat_recover = np.matmul(np.linalg.inv(mat_H), mat_in.transpose())

    # transpose back to the right dimension (4 x 3)
    mat_recover = mat_recover.transpose()

    # extract the first 2 elements in each point (4 x 2)
    mat_recover = [mat_recover[i, :2] / mat_recover[i, 2]
                   for i in range(n_points)]

    # return
    return np.array(np.matrix(mat_recover)).tolist()


def getFourierTransform(sig):
    sigf = abs(np.fft.fft(sig)/len(sig))
    return sigf[2:int(len(sigf)/2)]
    # return sigf[2:25]


def getCardIntercept(sig, angle, imgH=0):
    """
    transform signal to intercept
    """
    if angle == 0:
        return sig * 1
    else:
        coef = 1 / np.sin(np.pi / 180 * abs(angle))
        if angle < 0:
            return sig * coef
        else:
            return imgH - sig * coef


def getSigFromItc(itc, angle, imgH=0):
    """
    transform intercept to signal
    """
    if angle < 0 or angle > 90:
        sig = itc * np.sin(np.pi / 180 * abs(angle))
    elif angle > 0 and angle <= 90:
        sig = (imgH - itc) * np.sin(np.pi / 180 * abs(angle))
    else:
        # angle = 0
        sig = itc
    return sig


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
        return int(x), int(y)
    else:
        return False, False


def findPeaks(img, nPeaks=0, axis=1, nSmooth=100):
    """
    ----------
    Parameters
    ----------
    """

    # compute 1-D signal
    signal = img.mean(axis=(not axis)*1)  # 0:nrow

    # ignore signals from iamge frame
    signal[:2] = [0, 0]
    signal[-2:] = [0, 0]

    # gaussian smooth
    for _ in range(int(len(signal)/30)):
        signal = np.convolve(
            np.array([1, 2, 4, 2, 1])/10, signal, mode='same')

    # find primary peaks
    peaks, _ = find_peaks(signal)
    lsDiff = np.diff(peaks)
    medSig = statistics.median(signal[peaks])
    stdSig = np.array(signal[peaks]).std()
    medDiff = statistics.median(lsDiff)
    stdDiff = np.array(lsDiff).std()

    # get finalized peaks with distance constrain
    coef = 0.18/(stdDiff/medDiff)  # empirical
    peaks, _ = find_peaks(signal, distance=medDiff-stdDiff*coef)
    # , prominence=(0.01, None))
    if nPeaks != 0:
        if len(peaks) > nPeaks:
            while len(peaks) > nPeaks:
                ls_diff = np.diff(peaks)
                idx_diff = np.argmin(ls_diff)
                idx_kick = idx_diff if (
                    signal[peaks[idx_diff]] < signal[peaks[idx_diff+1]]) else (idx_diff+1)
                peaks = np.delete(peaks, idx_kick)
        elif len(peaks) < nPeaks:
            while len(peaks) < nPeaks:
                ls_diff = np.diff(peaks)
                idx_diff = np.argmax(ls_diff)
                peak_insert = (peaks[idx_diff]+peaks[idx_diff+1])/2
                peaks = np.sort(np.append(peaks, int(peak_insert)))

    return peaks, signal


# === === === === Plotting === === === === ===

def qCross(x, y, painter, size=2):
    l1_st_x, l1_st_y = x-size, y-size
    l1_ed_x, l1_ed_y = x+size, y+size
    l2_st_x, l2_st_y = x-size, y+size
    l2_ed_x, l2_ed_y = x+size, y-size
    painter.drawLine(l1_st_x, l1_st_y, l1_ed_x, l1_ed_y)
    painter.drawLine(l2_st_x, l2_st_y, l2_ed_x, l2_ed_y)


def pltCross(x, y, size=3, width=1, color="red"):
    pt1X = [x-size, x+size]
    pt1Y = [y-size, y+size]
    line1 = Line2D(pt1X, pt1Y, linewidth=width, color=color)
    pt2X = [x-size, x+size]
    pt2Y = [y+size, y-size]
    line2 = Line2D(pt2X, pt2Y, linewidth=width, color=color)
    return line1, line2


def pltImShow(img, path=None, prefix="GRID", filename=".png"):
    if path is None:
        ax = plt.subplot(111)
        ax.imshow(img)
        plt.show()
    else:
        file = os.path.join(path, prefix+filename)
        if img.max() == 1:
            qimg = getBinQImg(img)
        elif img.max() < 100:
            qimg = getIdx8QImg(img, img.max()+1)
        else:
            qimg = getRGBQImg(img)

        qimg.save(file, "PNG")


def pltSegPlot(agents, plotBase, isName=False, isRect=False, isCenter=False, path=None, prefix="GRID", filename=".png"):
    if path is None:
        # CLI
        ax = plt.subplot(111)
        ax.imshow(plotBase)
        for row in range(agents.nRow):
            for col in range(agents.nCol):
                try:
                    agent = agents.get(row=row, col=col)
                    if not agent:
                        continue
                    recAg = agent.getQRect()
                    line1, line2 = pltCross(agent.x, agent.y, width=1)
                    ax.add_line(line1)
                    ax.add_line(line2)
                    if isRect:
                        rect = patches.Rectangle(
                            (recAg.x(), recAg.y()), recAg.width(), recAg.height(),
                            linewidth=1, edgecolor='r', facecolor='none')
                        ax.add_patch(rect)
                except Exception:
                    print("The plot is out of the borders")
        plt.show()
    else:
        # GUI
        file = os.path.join(path, prefix+filename)
        if plotBase.max() == 1:
            qimg = getBinQImg(plotBase)
        elif plotBase.max() < 100:
            qimg = getIdx8QImg(plotBase, plotBase.max()+1)
        else:
            qimg = getRGBQImg(plotBase)

        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter = QPainter(qimg)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        for row in range(agents.nRow):
            for col in range(agents.nCol):
                try:
                    agent = agents.get(row, col)
                    center = agent.getCoordinate()
                    rect = agent.getQRect()
                    if isName:
                        text = "%s\n(%d, %d)" % (agent.name, row+1, col+1)
                        painter.drawText(rect, Qt.AlignCenter, text)
                    if isRect:
                        painter.drawRect(rect)
                    if isCenter:
                        qCross(center[0], center[1], painter, size=3)
                except Exception:
                    print("The plot is out of the borders")
        painter.end()
        qimg.save(file, "PNG")


def pltImShowMulti(imgs, titles=None, vertical=False):
    nImgs = len(imgs)
    idxImg = 100 if vertical else 10
    idxLyt = 20 if vertical else 200

    plt.figure()
    for i in range(nImgs):
        idxPlot = idxImg*round(nImgs/2) + idxLyt + (i+1)
        plt.subplot(idxPlot)
        plt.imshow(imgs[i])
        try:
            plt.title(titles[i])
        except Exception:
            None

    plt.show()


def pltLinesPlot(gmap, agents, img):
    itcs = gmap.itcs
    slps = gmap.slps
    # plotting
    _, ax = plt.subplots()
    ax.imshow(img)
    for i in range(2):
        for intercept in itcs[i]:
            plotLine(ax, slps[i], intercept)
    for cAgents in agents:
        for agent in cAgents:
            line1, line2 = pltCross(agent.x, agent.y, width=2)
            ax.add_line(line1)
            ax.add_line(line2)

    plt.show()


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


def bugmsg(msg, title="DEBUG"):
    if "--test" in sys.argv:
        print("======%s=====" % title)
        print(msg)


# for GUI
def getRGBQImg(img):
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w, h, w*3, QImage.Format_RGB888)
    return QPixmap(qImg)


def getBinQImg(img):
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w,
                  h, w*1, QImage.Format_Indexed8)
    qImg.setColor(0, qRgb(0, 0, 0))
    qImg.setColor(1, qRgb(241, 225, 29))
    return QPixmap(qImg)


def getIdx8QImg(img, k):
    colormap = [qRgb(228, 26, 28),
                qRgb(55, 126, 184),
                qRgb(77, 175, 74),
                qRgb(152, 78, 163),
                qRgb(255, 127, 0),
                qRgb(255, 255, 51),
                qRgb(166, 86, 40),
                qRgb(247, 129, 191),
                qRgb(153, 153, 153)]
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w,
                  h, w*1, QImage.Format_Indexed8)
    for i in range(k):
        qImg.setColor(i, colormap[i])
    return QPixmap(qImg)


def getGrayQImg(img):
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w,
                  h, w*1, QImage.Format_Grayscale8)
    return QPixmap(qImg)


# progress bar
class GProg(QWidget):
    def __init__(self, size, name, widget):
        super().__init__()
        try:
            self._width = widget.width()/5
            self._height = self._width/16*5
            wgW, wgH = widget.width(), widget.height()
            self._pos = widget.pos()
        except Exception:
            self._width, self._height = 1, 1
            wgW, wgH = 1, 1
            self._pos = QPoint(1, 1)

        self.label = QLabel(name)
        font = QFont("Trebuchet MS", 20)
        self.label.setFont(font)
        self.bar = QProgressBar()
        self.bar.setRange(0, size)
        self.bar.setValue(0)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.bar)
        self.setLayout(self.layout)
        self.move(self._pos.x()+(wgW-self._width)/2,
                  self._pos.y()+(wgH-self._height)/2)
        self.resize(self._width, self._height)
        self.show()
        self.repaint()
        QApplication.processEvents()

    def inc(self, n, name=None):
        self.bar.setValue(self.bar.value()+n)
        if name is not None:
            self.label.setText(name)
        self.repaint()
        QApplication.processEvents()

    def set(self, n, name=None):
        self.bar.setValue(n)
        if name is not None:
            self.label.setText(name)
        self.repaint()
        QApplication.processEvents()


def initProgress(size, name=None):
    if "__main__.py" in sys.argv[0]:
        # GUI
        widget = QApplication.activeWindow()
        obj = GProg(size, name, widget)
    else:
        # CLT
        obj = tqdm(total=size, postfix=name)

    return obj


def updateProgress(obj, n=1, name=None, flag=True):
    if (not flag) or (obj is None):
        return 0

    if "__main__.py" in sys.argv[0]:
        # GUI
        obj.inc(n, name)
    else:
        # CLT
        obj.set_postfix_str(name)
        obj.update(n)

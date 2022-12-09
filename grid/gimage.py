# basic imports
import numpy as np
import shapefile

# self imports
from .io import *
from .lib import *


class GImage():
    """
    """

    def __init__(self):
        """
        ----------
        Parameters
        ----------
        """

        # images
        self.imgs = {
            'raw': None,
            'rawRs': None,
            'crop': None,
            'mean': None,
            'kmean': None,
            'binOrg': None,
            'binTemp': None,
            'binSd': None,
            'binSm': None,
            'bin': None,
            'binSeg': None,
            'visSeg': None
        }

        # dimension
        self.width, self.height, self.depth = 0, 0, 0
        self.widthRs, self.heightRs = 0, 0
        self.shape = (self.height, self.width, self.depth)
        self.shapeRs = (self.heightRs, self.widthRs, self.depth)
        self.n_rot = 0

        # crop/ geo-reference
        self.f_shp = None
        self.hasShp = False
        self.tiff_transform = None
        self.crs = False
        self.pts_crop = []
        self.mat_H = None

        # kmean param.
        self.paramKMs = {
            'k': -1,
            'center': None,
            'rank': None,
            'features': [],
            'lsSelect': [],
            'lsKTobin': [],
            'valShad': -1,
            'valSmth': -1
        }

    def get(self, key):
        """
        ----------
        Parameters
        ----------
        """

        return self.imgs[key]

    def set(self, key, value):
        """
        ----------
        Parameters
        ----------
        """

        self.imgs[key] = value

    def load(self, pathImg, pathShp=None):
        """
        ----------
        Parameters
        ----------
        """
        if isinstance(pathImg, str):
            # a path to a file
            isLocalImg = pathImg.find("http://") + \
                pathImg.find("https://") == -2

            # image
            if isLocalImg:
                imgInput, self.tiff_transform, self.crs = loadImg(pathImg)
                try:
                    self.f_shp = shapefile.Reader(pathShp)
                    tmp = self.f_shp.shapeRecords()  # test if it can be read
                    self.hasShp = True
                except Exception:
                    self.f_shp = None
                    self.hasShp = False
            else:
                imgInput = loadImgWeb(pathImg)
        elif isinstance(pathImg, np.ndarray):
            # is a numpy
            imgInput = pathImg

        # assign
        self.set(key='raw', value=imgInput)
        self.setShape(shape=imgInput.shape, isRaw=True)

    def getParam(self, key):
        """
        ----------
        Parameters
        ----------
        """

        return self.paramKMs[key]

    def setParam(self, key, value):
        """
        ----------
        Parameters
        ----------
        """

        self.paramKMs[key] = value

    def resetParam(self):
        """
        ----------
        Parameters
        ----------
        """

        self.paramKMs = {
            'k': -1,
            'center': None,
            'features': [],
            'lsSelect': [],
            'lsKTobin': [],
            'valShad': -1,
            'valSmth': -1
        }

    def crop(self, pts=None):
        """
        ----------
        Parameters
        ----------
        """

        if pts is None:
            # (x, y) = (W, H)
            pts = np.float32([[0, 0],
                             [self.shape[1], 0],
                             [self.shape[1], self.shape[0]],
                             [0, self.shape[0]]])

        imgCrop, M = cropImg(self.imgs['raw'], pts)
        self.set(key='crop',
                 value=imgCrop)
        self.set(key='mean',
                 value=self.get('crop')[:, :, :3].mean(axis=2))
        self.setShape(shape=self.get(key='crop').shape)
        self.mat_H = M
        self.pts_crop = pts.copy()

        self.resetParam()

    def doKMeans(self, k=3, features=[0, 1, 2], colorOnly=False):
        """
        ----------
        Parameters
        ----------
        """

        if len(features) == 0:
            print("no feature is selected")
        elif (k != self.paramKMs['k']) or\
             (features != self.paramKMs['features']):
            # Will skip if no updates on the params
            imgK, center = doKMeans(img=self.get('crop'),
                                    k=k,
                                    features=features)
            self.set(key='kmean', value=imgK)
            # update parameters
            self.paramKMs['center'] = center
            self.paramKMs['rank'] = self.rankCenters(
                k=k, center=center, colorOnly=colorOnly)
            # can't update yet as binarize needs it
            # self.paramKMs['k'] = k
            # self.paramKMs['features'] = features
        else:
            # skip
            bugmsg("skip kmean")

    def binarize(self, k=3, features=[0, 1, 2], lsSelect=[0]):
        """
        ----------
        Parameters
        ----------
        """

        if len(features) == 0:
            print("no feature is selected")
        elif (k != self.paramKMs['k']) or\
             (features != self.paramKMs['features']) or\
             (lsSelect != self.paramKMs['lsSelect']):
            # ratioK = [(self.paramKMs['center'][i, 0]-self.paramKMs['center'][i, 1])/self.paramKMs['center'][i, :].sum()
            #           for i in range(self.paramKMs['center'].shape[0])]
            # # rankK = np.flip(np.argsort(ratioK), 0)
            # rankK = np.argsort(ratioK)
            try:
                clusterSelected = self.paramKMs['rank'][lsSelect]
            except Exception:
                clusterSelected = []
            self.set(key='binOrg', value=(
                (np.isin(self.get('kmean'), clusterSelected))*1).astype(np.int))
            self.set(key='binTemp', value=self.get('binOrg').copy())
            self.set(key='binSm', value=self.get('binOrg').copy())
            # udpate parameters
            self.paramKMs['k'] = k
            self.paramKMs['features'] = features
            self.paramKMs['lsSelect'] = lsSelect
            self.paramKMs['lsKToBin'] = clusterSelected
        else:
            # skip
            bugmsg("skip binarize")

    def smooth(self, value):
        """
        ----------
        Parameters
        ----------
        """

        if value != self.paramKMs['valSmth']:
            valSmthDiff = value - self.paramKMs['valSmth']
            if valSmthDiff > 0:
                valSmthReal = valSmthDiff
            else:
                valSmthReal = value
                self.set(key='binTemp', value=self.get(key='binOrg').copy())
            self.set(key='binTemp', value=smoothImg(
                image=self.get(key='binTemp'), n=valSmthReal))
            self.set(key='binSm',   value=binarizeSmImg(
                self.get(key='binTemp')))
            # update parameters
            self.paramKMs['valSmth'] = value
        else:
            # skip
            bugmsg("skip smoothing")

    def deShadow(self, value):
        """
        ----------
        Parameters
        ----------
        """

        if value != self.paramKMs['valShad']:
            self.set(key='binSd', value=(self.get(key='mean') >= value)*1)
            # update parameter
            self.paramKMs['valShad'] = value
        else:
            # skip
            bugmsg("skip shadow")

    def finalized(self):
        """
        ----------
        Parameters
        ----------
        """

        self.set(key='bin', value=np.multiply(
            self.get('binSm'), self.get('binSd')))

    def readyForSeg(self):
        """
        ----------
        Parameters
        ----------
        """
        nSmt = int(min(self.get('bin').shape[0], self.get('bin').shape[1])/300)
        self.set(key='binSeg', value=blurImg(self.get('bin'),
                                             n=nSmt))
        # compute the vis/seg image
        imgTemp = np.expand_dims(self.get("bin"), axis=2)
        imgSeg = np.multiply(self.get('crop')[:, :, :3], imgTemp).copy()
        imgSeg[(imgSeg.mean(axis=2) == 0), :] = 255
        self.set(key='visSeg', value=imgSeg)

    def rankCenters(self, k, center, colorOnly=False):
        scores = []

        if colorOnly:
            ratioK = [(center[i, 0]-center[i, 1])/center[i, :].sum()
                      for i in range(center.shape[0])]
            rank = np.flip(np.argsort(ratioK), axis=0)
        else:
            for i in range(k):
                imgB = (np.isin(self.get('kmean'), i)*1).astype(np.int)
                sigs = imgB.mean(axis=0)
                sigsF = getFourierTransform(sigs)
                scMaxF = round((max(sigsF)/sigsF.mean())/100, 4)  # [0, 1]
                scMean = round(1-(sigs.mean()), 4)  # [0, 1]
                try:
                    scPeaks = round(len(find_peaks(sigs, height=(sigs.mean()))
                                        [0])/len(find_peaks(sigs)[0]), 4)
                except Exception:
                    scPeaks = 0

                score = scMaxF*.25 + scMean*.25 + scPeaks*.5
                scores.append(score)
            rank = np.flip(np.array(scores).argsort(), axis=0)

        return rank

    def rotate(self, nRot):
        """
        ----------
        Parameters
        ----------
        """

        self.n_rot += nRot

        for key in self.imgs.keys():
            if key == 'raw' or key == 'rawRs':
                # only rotate cropped images
                continue
            try:
                self.set(key=key, value=np.rot90(self.get(key=key), nRot))
            except Exception:
                None
        self.setShape(self.get("crop").shape)

    def setShape(self, shape, isRaw=False):
        """
        ----------
        Parameters
        ----------
        """
        if isRaw:
            try:
                self.height, self.width, self.depth = shape
            except Exception:
                self.height, self.width = shape
                self.depth = 1
            self.shape = (self.height, self.width, self.depth)
        else:
            try:
                self.heightRs, self.widthRs, self.depth = shape
            except Exception:
                self.heightRs, self.widthRs = shape
                self.depth = 1
            self.shapeRs = (self.heightRs, self.widthRs, self.depth)

    def getShape(self, is3D=False, isRaw=False):
        """
        ----------
        Parameters
        ----------
        """
        if is3D:
            return self.shape if isRaw else self.shapeRs
        else:
            return self.shape[:2] if isRaw else self.shapeRs[:2]

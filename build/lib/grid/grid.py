# basic imports
from .lib import *
from .gagent import *
from .gmap import *
from .gimage import *
from .guser import *
import os
import sys
import warnings
warnings.filterwarnings("ignore")

# self imports


class GRID():

    def __init__(self):
        """
        ----------
        Parameters
        ----------
        """
        # self-defined class
        self.user = GUser()
        self.imgs = GImage()
        self.map = GMap()
        self.agents = GAgent()

        # for progressbar
        self.flag = True
        self.subflag = True
        self.window = 1000

    def __user__(self):
        """
        ----------
        Parameters
        ----------
        """

        self.user.printInfo()

    def run(self, pathImg=None, pathMap=None, pts=None,
            k=3, features=[0, 1, 2], lsSelect=[0], valShad=0, valSmth=0,
            nRow=0, nCol=0, nSmooth=100,
            tol=5, coefGrid=.2,
            outplot=False,
            path=None, prefix="GRID",
            preset=None):
        """
        ----------
        Parameters
        ----------
        """

        if preset is not None:
            params = getPickledGRID(preset)
            self.run(pathImg=pathImg, pathMap=pathMap, pts=pts,
                     nSmooth=nSmooth,
                     tol=tol,
                     **params, outplot=outplot)
        else:
            prog = initProgress(6, "loading data")
            self.loadData(pathImg=pathImg, pathMap=pathMap, outplot=outplot)
            prog = updateProgress(prog, 1, "cropping")
            self.cropImg(pts=pts, outplot=outplot)
            prog = updateProgress(prog, 1, "binarizing")
            self.binarizeImg(k=k, features=features,
                             lsSelect=lsSelect,
                             valShad=valShad, valSmth=valSmth, outplot=outplot)
            prog = updateProgress(prog, 1, "locating plots")
            self.findPlots(nRow=nRow, nCol=nCol,
                           nSmooth=nSmooth, outplot=outplot)
            prog = updateProgress(prog, 1, "segmenting")
            self.cpuSeg(tol=tol, coefGrid=coefGrid, outplot=outplot)
            prog = updateProgress(prog, 1, "exporting")
            self.save(path=path, prefix=prefix)
            prog = updateProgress(prog, 1, "done!")

    def save(self, path=None, prefix="GRID", simple=True):
        """
        ----------
        Parameters
        ----------
        """
        if "__main__.py" not in sys.argv[0]:
            app = QApplication(sys.argv)

        # check if the path is valid
        if path is None or not os.path.exists(path):
            path = self.user.dirHome

        # put everything in a folder
        path_f = os.path.join(path, prefix)
        try:
            os.mkdir(path_f)
        except OSError:
            path_f = path
            print("Failed to create a new directory")

        self.savePlotAndDT(path=path_f, prefix=prefix, simple=simple)

        if "__main__.py" not in sys.argv[0]:
            app.quit()

        # params = {
        #     "k": self.imgs.paramKMs["k"],
        #     "features": self.imgs.paramKMs["features"],
        #     "lsSelect": self.imgs.paramKMs["lsSelect"],
        #     "valShad":  self.imgs.paramKMs["valShad"],
        #     "valSmth":  self.imgs.paramKMs["valSmth"],
        #     "nRow": self.agents.nRow,
        #     "nCol": self.agents.nCol,
        #     "coefGrid": self.agents.coef
        # }

        # try:
        #     pathOut = os.path.join(path_f, prefix) + ".grid"
        #     pickleGRID(params, pathOut)
        # except Exception:
        #     None

    # === === === === === === MAJOR WORKFLOW === === === === === ===

    def loadData(self, pathImg=None, pathMap=None, pathShp=None, outplot=False):
        """
        ----------
        Parameters
        ----------
        """
        if pathImg is None:
            self.imgs.load(
                pathImg=os.path.join(self.user.dirGrid, "demo/seg_img.jpg"))
            self.map.load(
                pathMap=os.path.join(self.user.dirGrid, "demo/seg_map.csv"))
            self.path_out = os.path.expanduser("~")
        else:
            self.imgs.load(pathImg=pathImg, pathShp=pathShp)
            self.map.load(pathMap=pathMap)
            self.path_out = os.path.abspath(
                os.path.join(os.path.dirname(pathImg)))

        if outplot:
            pltImShow(self.imgs.get("raw")[:, :, :3])

    def cropImg(self, pts=None, outplot=False):
        """
        ----------
        Parameters
        ----------
        """
        bugmsg("--- cropped ---")
        bugmsg(pts)
        self.imgs.crop(pts)

        if outplot:
            pltImShow(self.imgs.get("crop")[:, :, :3])

    def binarizeImg(self, k=3, features=[0, 1, 2], lsSelect=[0], valShad=0,
                    valSmth=0, colorOnly=False, outplot=False):
        """
        ----------
        Parameters
        ----------
        """
        # from QtCore import QTimer

        if self.imgs.get("crop") is None:
            self.cropImg()

        # KMEAN
        prog = None
        if self.flag:
            self.flag = False
            prog = initProgress(5, name="K-Means Clustering")
        self.imgs.doKMeans(k=k, features=features, colorOnly=colorOnly)

        # BINARIZE
        updateProgress(prog, name="Binarizing", flag=self.subflag)
        self.imgs.binarize(k=k, features=features, lsSelect=lsSelect)

        # SMOOTH
        updateProgress(prog, name="Smoothing", flag=self.subflag)
        self.imgs.smooth(value=valSmth)

        # DESHADOW
        updateProgress(prog, name="DeShade-ing", flag=self.subflag)
        self.imgs.deShadow(value=valShad)

        # FINALIZE
        updateProgress(prog, name="Finalizing", flag=self.subflag)
        self.imgs.finalized()
        updateProgress(prog, name="Done", flag=self.subflag)

        # set progress bar inactive for 300ms
        if self.subflag and "__main__.py" in sys.argv[0]:
            self.subflag = False
            QTimer.singleShot(self.window, lambda: setattr(self, "flag", True))
            QTimer.singleShot(
                self.window, lambda: setattr(self, "subflag", True))

        # Plot
        if outplot:
            pltImShowMulti(
                imgs=[self.imgs.get('crop')[:, :, :3],
                      self.imgs.get('kmean'),
                      self.imgs.get('binOrg'),
                      self.imgs.get('bin')],
                titles=["Original", "K-Means", "Binarized", "Finalized"])

    def findPlots(self, nRow=0, nCol=0, nSmooth=100, outplot=False):
        """
        ----------
        Parameters
        ----------
        """

        # iamge
        self.imgs.readyForSeg()

        self.map.findPlots(imgRGB=self.imgs.get("crop")[:, :, :3],
                           imgBin=self.imgs.get("binSeg"),
                           nRow=nRow, nCol=nCol, nSmooth=nSmooth)

        self.agents.setup(gmap=self.map, gimg=self.imgs)

        if outplot:
            pltLinesPlot(gmap=self.map, agents=self.agents.agents,
                         img=self.imgs.get('binSeg'))

    def cpuSeg(self, tol=5, coefGrid=.2, outplot=False):
        """
        ----------
        Parameters
        ----------
        """

        self.agents.cpuPreDim(tol=tol)
        self.agents.autoSeg(coefGrid=coefGrid)

        if outplot:
            pltSegPlot(self.agents, self.imgs.get("visSeg"), isRect=True)

    # === === === === === === IMAGE === === === === === ===

    def rotateImg(self, nRot):
        """
        ----------
        Parameters
        ----------
        """
        self.imgs.rotate(nRot)

    # === === === === === === MAP === === === === === ===

    def updateCenters(self, idx, angle=-999, nPeaks=0):
        if angle != -999:
            self.map.angles[idx] = angle
        if nPeaks != 0:
            self.map.nAxs[idx] = nPeaks
        self.map.locateCenters()

    # === === === === === === AGENTS === === === === === ===

    def fixSeg(self, width, length):
        """
        ----------
        Parameters
        ----------
        """
        self.agents.fixSeg(width, length)

    # === === === === === === OUTPUT === === === === === ===

    def savePlotAndDT(self, path, prefix="GRID", simple=True):
        """
        ----------
        Parameters
        ----------
        """
        progExtra = 1 if simple else 0
        # progress bar
        prog = initProgress(2 + progExtra, "Exporting Dataframe")

        saveDT(self, path, prefix, simple=simple)
        updateProgress(prog, name="Exporting Figures")
        savePlot(self, path, prefix, simple=simple)
        updateProgress(prog, name="Exporting shapefile")
        saveShape(self, path, prefix)

        if not simple:
            updateProgress(prog, name="Exporting h5 files")
            saveH5(self, path, prefix)

        updateProgress(prog, name="Done")

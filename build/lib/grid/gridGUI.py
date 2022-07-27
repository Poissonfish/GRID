# basic imports 
from enum import Enum

# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from .grid import *
from .gui import *
from .lib import *
from .__init__ import __version__

class GRID_GUI(QMainWindow):
    """
    """

    def __init__(self, gridInput=None, idxPn=None):
        """
        ----------
        Parameters
        ----------
        """
        super().__init__()
        #         QWidget {
        #     font: 16pt Trebuchet MS
        # }
        self.setStyleSheet("""
        QWidget {
            font: 16pt Trebuchet MS
        }
        QGroupBox::title{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 3px 0 3px;
        }
        QGroupBox {
            border: 1px solid gray;
            border-radius: 9px;
            margin-top: 0.5em;
        }
        """)

        # CLI
        self.grid = GRID()

        # GUI
        self.nPanel = -1
        self.pnContent = QWidget()
        self.pnMain = QStackedWidget()

        self.pnNavi = QWidget()
        self.btNext = QPushButton()
        self.btPrev = QPushButton()
        self.prog = GProg(size=5, name="Specify an image to proceed", widget=self.pnContent)
        self.layout = None

        # Shortcut
        self.gridInput = gridInput
        self.idxPn = idxPn

        # UI
        self.initUI()

    def startover(self):
        while self.pnMain.count()!=0:
            widget = self.pnMain.widget(self.pnMain.count()-1)
            self.pnMain.removeWidget(widget)

        self.nPanel = -1
        self.gridInput = None
        self.idxPn = None
        del self.grid
        self.grid = GRID()
        self.initUI()

    def initUI(self):
        """
        ----------
        Parameters
        ----------
        """

        # window setup
        self.setWindowTitle("GRID (%s)" % __version__)
        self.resize(1280, 700)
        self.centerWindow()

        if self.gridInput is None:
            # initialize with first panel
            self.showInputer()
        else:
            # or use shortcut
            self.grid = self.gridInput
            if self.idxPn==0:
                self.showInputer()
            elif self.idxPn==1:
                self.showCropper()
            elif self.idxPn==2:
                self.showKMeaner()
            elif self.idxPn==3:
                self.showAnchor()
            elif self.idxPn==4:
                self.showOutputer()

        # show
        self.show()

    def showInputer(self, isNew=True):
        bugmsg("show input")
        self.prog.set(n=0, name="Specify (or drag & drop) an image to proceed")
        self.assembleNavigation(nameNext="Load Files ->", oneSide=True)
        self.btNext.clicked.connect(
            lambda: self.showCropper())
        self.updateMainPn(panel=Panels.INPUTER, isNew=isNew)

    def showCropper(self, isNew=True):
        bugmsg("crop")
        self.prog.set(n=1, name="Left-click to define AOI. Right-click to change zoom-in rate. After initialing the AOI:\nDrag at AOI's corner/side to adjust the border. Drag at AOI's center to move the whole AOI. Drag at the area further away from AOI to rotate")
        self.assembleNavigation()
        self.btPrev.clicked.connect(
            lambda: self.showInputer(isNew=False))
        self.btNext.clicked.connect(
            lambda: self.showKMeaner())
        self.updateMainPn(panel=Panels.CROPPER, isNew=isNew)

    def showKMeaner(self, isNew=True):
        bugmsg("kmean")
        self.prog.set(
            n=2, name="Define the pixels of interest (POI)")
        self.assembleNavigation()
        self.btPrev.clicked.connect(
            lambda: self.showCropper(isNew=False))
        if self.grid.imgs.hasShp:
            self.btNext.clicked.connect(
                lambda: self.showOutputer())
        else:
            self.btNext.clicked.connect(
                lambda: self.showAnchor())
        self.updateMainPn(panel=Panels.KMEANER, isNew=isNew)

    def showAnchor(self, isNew=True):
        bugmsg("anchor")
        self.prog.set(
            n=3, name="Define the plot centers: LEFT-CLICK to add, RIGHT-CLICK to remove, DRAG to adjust")
        self.assembleNavigation()
        self.btPrev.clicked.connect(
            lambda: self.showKMeaner(isNew=False))
        self.btNext.clicked.connect(
            lambda: self.showOutputer())
        self.updateMainPn(panel=Panels.ANCHOR, isNew=isNew)

    def showOutputer(self, isNew=True):
        bugmsg("show output")
        self.prog.set(
            n=4, name="Finalize the segmentation and export results: Drag to adjust borders")
        self.assembleNavigation(nameNext="Finish")
        if self.grid.imgs.hasShp:
            self.btPrev.clicked.connect(
                lambda: self.showKMeaner(isNew=False))
        else:
            self.btPrev.clicked.connect(
                lambda: self.showAnchor(isNew=False))
        self.btNext.clicked.connect(lambda: self.finalize())
        self.updateMainPn(panel=Panels.OUTPUTER, isNew=isNew)

    def updateMainPn(self, panel, isNew=True):
        token_err = False
        # traverse forward
        if isNew:
            try:
                # run computation from the previous panel
                bugmsg("run")
                self.pnMain.currentWidget().run()
            except Exception:
                token_err = True
                # except the initial one

            if token_err and self.nPanel == 0:
                # missing file handling
                self.showInputer(isNew=False)
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Failed to load files")
                msg.setInformativeText("No such file or directory")
                msg.exec_()
            else:
                self.pnMain.addWidget(panel.value[1](self.grid))
            self.nPanel += 1

            token_err = False
        # traverse backward
        else:
            widget = self.pnMain.widget(panel.value[0]+1)
            self.pnMain.removeWidget(widget)
            self.nPanel -= 1

        # set current widget
        self.pnMain.setCurrentIndex(self.nPanel)

        # show
        self.assembleAndShow()

    def finalize(self):
        """
        ----------
        Parameters
        ----------
        """

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Finished!")
        msgBox.setInformativeText("Save and start another job?")
        msgBox.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No| QMessageBox.Discard)

        msgBox.button(QMessageBox.Yes).setText("Save and stay in current work")
        msgBox.button(QMessageBox.No).setText("Save and start new job")
        msgBox.button(QMessageBox.Discard).setText("Cancel")

        returnValue = msgBox.exec()
        path = self.pnMain.currentWidget().fd_output.text()
        prefix = self.pnMain.currentWidget().fd_project.text()
        isSimple = self.pnMain.currentWidget().ck_simple.isChecked()
        if returnValue == QMessageBox.Yes:
            self.grid.save(path=path, prefix=prefix, simple=isSimple)
        elif returnValue == QMessageBox.No:
            self.grid.save(path=path, prefix=prefix, simple=isSimple)
            self.startover()

    def centerWindow(self):
        """
        ----------
        Parameters
        ----------
        """

        center = QApplication.desktop().availableGeometry().center()
        rect = self.geometry()
        rect.moveCenter(center)
        self.setGeometry(rect)

    def assembleNavigation(self, nameNext="Next ->", namePrev="<- Prev", oneSide=False):
        """
        ----------
        Parameters
        ----------
        """

        self.pnNavi = QWidget()
        self.btNext = QPushButton(nameNext)
        self.btPrev = QPushButton(namePrev)
        loNavi = QHBoxLayout()
        if oneSide:
            loNavi.addStretch(1)
        else:
            loNavi.addWidget(self.btPrev)
        loNavi.addWidget(self.btNext)
        self.pnNavi.setLayout(loNavi)

    def assembleAndShow(self):
        """
        ----------
        Parameters
        ----------
        """

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.addWidget(self.prog)
        self.layout.addWidget(self.pnMain, Qt.AlignCenter)
        self.layout.addWidget(self.pnNavi)
        self.pnContent = QWidget()
        self.pnContent.setLayout(self.layout)
        self.setCentralWidget(self.pnContent)
        self.setMinimumHeight(30)
        self.show()


class Panels(Enum):
    INPUTER = 0, PnInputer
    CROPPER = 1, PnCropper
    KMEANER = 2, PnKmeaner
    ANCHOR = 3, PnAnchor
    OUTPUTER = 4, PnOutputer



# ARCHIVE:
# def test(self):
#     import json
#     with open('anchors', 'w') as fout:
#         json.dump(self.params['anchors'], fout)
#     np.save("img_crop", self.params['crop'])
#     np.save("img_bin", self.params['bin'])
#     np.save("map", self.params['map'])
#     np.save("img_k", self.params['k'])
#     np.save("ls_bin", self.params['ls_bin'])
#     bugmsg("nc:%d" % (self.params['nc']))
#     bugmsg("nr:%d" % (self.params['nr']))


# def updateMainPn(self, panel, isNew=True):
#     # traverse forward
#     if isNew:
#         try:
#             # run computation from the previous panel
#             bugmsg("run")
#             self.pnMain.currentWidget().run()
#         except:
#             # except the initial one
#             None
#         self.pnMain.addWidget(panel.value[1](self.grid))
#     # traverse backward
#     else:
#         self.pnMain.removeWidget(self.pnMain.widget(panel.value[0]+1))

#     # set current widget
#     self.pnMain.setCurrentIndex(panel.value[0])

#     # show
#     self.assembleAndShow()
# 
# def updateMainPn(self, panel, isNew=True):
#     """
#     ----------
#     Parameters
#     ----------
#     """
#     # define events
#     if panel == Panels.INPUTER:
#         bugmsg("panel Input")
#         self.assembleNavigation(nameNext="Load Files ->", oneSide=True)
#         self.btNext.clicked.connect(
#             lambda: self.updateMainPn(Panels.CROPPER))
#     elif panel == Panels.CROPPER:
#         bugmsg("panel cropper")
#         self.assembleNavigation()
#         self.btPrev.clicked.connect(
#             lambda: self.updateMainPn(Panels.INPUTER, isNew=False))
#         self.btNext.clicked.connect(
#             lambda: self.updateMainPn(Panels.KMEANER))
#     elif panel == Panels.KMEANER:
#         bugmsg("panel kmeaner")
#         self.assembleNavigation()
#         self.btPrev.clicked.connect(
#             lambda: self.updateMainPn(Panels.CROPPER, isNew=False))
#         self.btNext.clicked.connect(
#             lambda: self.updateMainPn(Panels.ANCHOR))
#     elif panel == Panels.ANCHOR:
#         self.assembleNavigation()
#         self.btPrev.clicked.connect(
#             lambda: self.updateMainPn(Panels.KMEANER, isNew=False))
#         self.btNext.clicked.connect(
#             lambda: self.updateMainPn(Panels.OUTPUTER))
#     elif panel == Panels.OUTPUTER:
#         self.assembleNavigation(nameNext="Finish")
#         self.btPrev.clicked.connect(
#             lambda: self.updateMainPn(Panels.ANCHOR, isNew=False))
#         self.btNext.clicked.connect(lambda: self.finalize())

#     # traverse forward
#     if isNew:
#         try:
#             # run computation from the previous panel
#             bugmsg("run")
#             self.pnMain.currentWidget().run()
#         except:
#             # except the initial one
#             None
#         self.pnMain.addWidget(panel.value[1](self.grid))
#     # traverse backward
#     else:
#         self.pnMain.removeWidget(self.pnMain.widget(panel.value[0]+1))

#     # set current widget
#     self.pnMain.setCurrentIndex(panel.value[0])

#     # show
#     self.assembleAndShow()
# 

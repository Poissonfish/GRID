# basic imports
import numpy as np

# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from ..grid import *
from .customQt import *


class PnKmeaner(QWidget):
    """
    """

    def __init__(self, grid):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.update()
        '''attr'''
        self.grid = grid
        # # grid params.
        self.nFeatures = min(self.grid.imgs.depth, 9)
        self.features = []
        self.lsSelect = None

        # main/img
        self.layout = QHBoxLayout()
        # img preview (left)
        self.gr_left = QGroupBox()
        self.lo_left = QGridLayout()
        self.wg_img = Widget_Kmeans(grid)
        self.bt_ccw = QPushButton("rotate ccw (Q)")
        self.bt_cw = QPushButton("rorate cw (E)")
        # K mean (right)
        self.kMax = 9
        self.gr_pre = QGroupBox("K-means Algo.")
        self.lo_pre = QGridLayout()

        self.gr_ft = QGroupBox("Channels used for clustering")
        self.lo_ft = QHBoxLayout()
        self.ck_ft = []
        for i in range(self.nFeatures):
            checkbox = QCheckBox(str(i+1))
            # if i < 3:
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.change_k)
            self.ck_ft.extend([checkbox])
            self.lo_ft.addWidget(self.ck_ft[i])

        self.lsSelect = [0]
        self.gr_k = QGroupBox("K = 3")
        self.lo_k = QVBoxLayout()
        self.sl_k = QSlider(Qt.Horizontal)
        # Binarization
        self.gr_bin = QGroupBox("Binarization")
        self.lo_bin = QVBoxLayout()
        # Binarization (auto)
        self.gr_cut = QGroupBox("Auto cutoff = 1")
        self.lo_cut = QVBoxLayout()
        self.sl_cut = QSlider(Qt.Horizontal)
        self.gr_cusb = QGroupBox("Custom")
        self.lo_cusb = QHBoxLayout()
        self.ck_cusb = []
        for i in range(1, self.kMax+1):
            checkbox = QCheckBox(str(i))
            checkbox.stateChanged.connect(self.custom_cut)
            if i>3:
                checkbox.setEnabled(False)
            self.ck_cusb.extend([checkbox])
        self.ls_bin = [0]
        # Display
        self.gr_dis = QGroupBox("Display")
        self.lo_dis = QHBoxLayout()
        self.rb_bin = QRadioButton("Binary (A)")
        self.rb_rgb = QRadioButton("RGB (S)")
        self.rb_k = QRadioButton("K-Means (D)")
        # zoom
        self.gr_zm = QGroupBox(
            "Magnification Levels (Right-click to switch)")
        self.lo_zm = QHBoxLayout()
        self.rb_1x = QRadioButton("1X")
        self.rb_15x = QRadioButton("1.5X")
        self.rb_3x = QRadioButton("3X")

        # refine (right)
        self.gr_pro = QGroupBox("Clusters Refine")
        self.lo_pro = QVBoxLayout()
        self.gr_shad = QGroupBox("De-Shade = 0")
        self.lo_shad = QVBoxLayout()
        self.sl_shad = QSlider(Qt.Horizontal)
        self.gr_gb = QGroupBox("De-Noise = 0")
        self.lo_gb = QVBoxLayout()
        self.sl_gb = QSlider(Qt.Horizontal)

        # panel right
        self.pn_right = QWidget()
        self.lo_right = QVBoxLayout()
        self.sc_right = QScrollArea()
        self.sc_right.setStyleSheet("QScrollBar {width:0px;}")
        self.sc_right.setWidgetResizable(True)

        '''initialize UI'''
        self.initUI()

    def initUI(self):
        '''img preview (left)'''
        # components
        self.bt_ccw.clicked.connect(self.rotateCCW)
        self.bt_cw.clicked.connect(self.rotateCW)
        # layout
        self.lo_left.addWidget(self.wg_img, 0, 0, 1, 2)
        self.lo_left.addWidget(self.bt_ccw, 1, 0)
        self.lo_left.addWidget(self.bt_cw, 1, 1)
        self.gr_left.setLayout(self.lo_left)
        '''pre keans (right)'''
        # components
        self.sl_k.setMinimum(2)
        self.sl_k.setMaximum(self.kMax)
        self.sl_k.setValue(3)
        self.sl_k.setTickInterval(1)
        self.sl_k.setTickPosition(QSlider.TicksBelow)
        self.sl_k.valueChanged.connect(self.change_k)

        # layout
        self.gr_ft.setLayout(self.lo_ft)
        self.lo_k.addWidget(self.sl_k)
        self.gr_k.setLayout(self.lo_k)
        self.lo_pre.addWidget(self.gr_ft)
        self.lo_pre.addWidget(self.gr_k)
        self.gr_pre.setLayout(self.lo_pre)

        '''binarization'''
        # component
        self.gr_cut.setCheckable(True)
        self.gr_cut.setChecked(True)
        self.gr_cut.clicked.connect(self.auto_cut)
        self.sl_cut.setMinimum(1)
        self.sl_cut.setMaximum(3)
        self.sl_cut.setValue(1)
        self.sl_cut.setTickInterval(1)
        self.sl_cut.setTickPosition(QSlider.TicksBelow)
        self.sl_cut.valueChanged.connect(self.auto_cut)
        self.gr_cusb.setCheckable(True)
        self.gr_cusb.setChecked(False)
        self.gr_cusb.clicked.connect(self.custom_cut)
        # layout
        self.lo_cut.addWidget(self.sl_cut)
        self.gr_cut.setLayout(self.lo_cut)
        for i in range(self.kMax):
            self.lo_cusb.addWidget(self.ck_cusb[i])
        self.gr_cusb.setLayout(self.lo_cusb)
        self.lo_bin.addWidget(self.gr_cut)
        self.lo_bin.addWidget(self.gr_cusb)
        self.gr_bin.setLayout(self.lo_bin)

        '''pro keans (right)'''
        # components
        self.sl_shad.setMinimum(0)
        self.sl_shad.setMaximum(255)
        self.sl_shad.setValue(0)
        self.sl_shad.setTickInterval(20)
        self.sl_shad.setTickPosition(QSlider.TicksBelow)
        self.sl_shad.valueChanged.connect(self.change_shad)
        self.sl_gb.setMinimum(0)
        self.sl_gb.setMaximum(50)
        self.sl_gb.setValue(0)
        self.sl_gb.setTickInterval(5)
        self.sl_gb.setTickPosition(QSlider.TicksBelow)
        self.sl_gb.valueChanged.connect(self.change_gb)
        # layout
        self.lo_shad.addWidget(self.sl_shad)
        self.gr_shad.setLayout(self.lo_shad)
        self.lo_gb.addWidget(self.sl_gb)
        self.gr_gb.setLayout(self.lo_gb)
        self.lo_pro.addWidget(self.gr_shad)
        self.lo_pro.addWidget(self.gr_gb)
        self.gr_pro.setLayout(self.lo_pro)

        "Zoom"
        self.rb_1x.toggled.connect(lambda: self.changeZoom(0))
        self.rb_15x.toggled.connect(lambda: self.changeZoom(1))
        self.rb_3x.toggled.connect(lambda: self.changeZoom(2))
        self.lo_zm.addWidget(self.rb_1x)
        self.lo_zm.addWidget(self.rb_15x)
        self.lo_zm.addWidget(self.rb_3x)
        self.gr_zm.setLayout(self.lo_zm)

        '''display'''
        # components
        self.rb_bin.setChecked(True)
        self.rb_bin.toggled.connect(self.wg_img.switch_imgB)
        self.rb_rgb.toggled.connect(self.wg_img.switch_imgVis)
        self.rb_k.toggled.connect(self.wg_img.switch_imgK)
        # layout
        self.lo_dis.addWidget(self.rb_bin)
        self.lo_dis.addWidget(self.rb_rgb)
        self.lo_dis.addWidget(self.rb_k)
        self.gr_dis.setLayout(self.lo_dis)

        '''right'''
        self.lo_right.addWidget(self.gr_pre)
        self.lo_right.addWidget(self.gr_bin)
        self.lo_right.addWidget(self.gr_pro)
        self.lo_right.addWidget(self.gr_dis)
        self.lo_right.addWidget(self.gr_zm)
        self.pn_right.setLayout(self.lo_right)
        self.sc_right.setWidget(self.pn_right)

        '''assemble'''
        policy_right = QSizePolicy(QSizePolicy.Preferred,
                                   QSizePolicy.Preferred)
        policy_right.setHorizontalStretch(2)
        self.sc_right.setSizePolicy(policy_right)
        policy_left = QSizePolicy(QSizePolicy.Preferred,
                                  QSizePolicy.Preferred)
        policy_left.setHorizontalStretch(3)
        self.gr_left.setSizePolicy(policy_left)
        self.layout.addWidget(self.gr_left)
        self.layout.addWidget(self.sc_right)
        self.setLayout(self.layout)
        self.change_k()  # initialize kmeans
        self.show()

        '''collapse'''
    #     self.gr_pre.setCheckable(True)
    #     self.gr_pre.setChecked(True)
    #     self.gr_pre.toggled.connect(self.collapsePre)
    #     # self.collapsePre()

    #     self.gr_bin.setCheckable(True)
    #     self.gr_bin.setChecked(False)
    #     self.gr_bin.toggled.connect(self.collapseBin)
    #     self.collapseBin()

    #     self.gr_pro.setCheckable(True)
    #     self.gr_pro.setChecked(False)
    #     self.gr_pro.toggled.connect(self.collapsePro)
    #     self.collapsePro()

    #     self.gr_dis.setCheckable(True)
    #     self.gr_dis.setChecked(True)
    #     self.gr_dis.toggled.connect(self.collapseDis)
    #     # self.collapseDis()

    #     self.gr_zm.setCheckable(True)
    #     self.gr_zm.setChecked(False)
    #     self.gr_zm.toggled.connect(self.collapseZm)
    #     self.collapseZm()

    # def collapsePre(self):
    #     self.gr_ft.setVisible(not self.gr_ft.isVisible())
    #     self.gr_k.setVisible(not self.gr_k.isVisible())

    # def collapseBin(self):
    #     self.gr_cut.setVisible(not self.gr_cut.isVisible())
    #     self.gr_cusb.setVisible(not self.gr_cusb.isVisible())

    # def collapsePro(self):
    #     self.gr_shad.setVisible(not self.gr_shad.isVisible())
    #     self.gr_gb.setVisible(not self.gr_gb.isVisible())

    # def collapseDis(self):
    #     self.rb_bin.setVisible(not self.rb_bin.isVisible())
    #     self.rb_rgb.setVisible(not self.rb_rgb.isVisible())
    #     self.rb_k.setVisible(not self.rb_k.isVisible())

    # def collapseZm(self):
    #     self.rb_1x.setVisible(not self.rb_1x.isVisible())
    #     self.rb_15x.setVisible(not self.rb_15x.isVisible())
    #     self.rb_3x.setVisible(not self.rb_3x.isVisible())

    def changeZoom(self, index):
        self.wg_img.zoom = index

    def rotateCCW(self):
        self.grid.rotateImg(nRot=1)
        self.refresh()

    def rotateCW(self):
        self.grid.rotateImg(nRot=3)
        self.refresh()

    def binarizeImgGUI(self):
        self.grid.binarizeImg(
            k=self.sl_k.value(),
            features=self.features,
            lsSelect=self.lsSelect, 
            valShad=self.sl_shad.value(),
            valSmth=self.sl_gb.value()
        )
        self.refresh()

    def change_k(self):
        value = self.sl_k.value()
        ls_ft = []
        for i in range(len(self.ck_ft)):
            # if i < self.nFeatures:
            #     self.ck_ft[i].setVisible(True)
            # else:
            #     self.ck_ft[i].setVisible(False)
            if i in range(self.nFeatures) and self.ck_ft[i].isChecked():
                ls_ft.extend([i])

        self.features = ls_ft
        self.sl_cut.setMaximum(value)
        self.gr_k.setTitle("K = %d" % value)
        # will certainly go to either of cut function, no need to do binarize
        if self.gr_cusb.isChecked():
            self.custom_cut()
        else:
            self.auto_cut()

    def auto_cut(self):
        self.gr_cut.setChecked(True)
        self.gr_cusb.setChecked(False)
        value = self.sl_cut.value()
        self.gr_cut.setTitle("Auto cutoff = %d" % value)
        ls_bin = []
        for i in range(self.kMax):
            self.ck_cusb[i].setEnabled(False)
            if i < value:
                ls_bin.extend([i])
        self.lsSelect = ls_bin
        self.binarizeImgGUI()

    def custom_cut(self):
        self.gr_cut.setChecked(False)
        self.gr_cusb.setChecked(True)
        value = self.sl_k.value()
        ls_bin = []
        for i in range(self.kMax):
            if i < value:
                self.ck_cusb[i].setEnabled(True)
                if self.ck_cusb[i].isChecked():
                    ls_bin.extend([i])
            else:
                self.ck_cusb[i].setEnabled(False)
        self.lsSelect = ls_bin
        self.binarizeImgGUI()

    def change_shad(self):
        value = self.sl_shad.value()
        self.gr_shad.setTitle("De-Shade = %d" % value)
        self.binarizeImgGUI()

    def change_gb(self):
        value = self.sl_gb.value()
        self.gr_gb.setTitle("De-Noise = %d" % value)
        self.binarizeImgGUI()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.rb_bin.setChecked(True)
        elif event.key() == Qt.Key_S:
            self.rb_rgb.setChecked(True)
        elif event.key() == Qt.Key_D:
            self.rb_k.setChecked(True)
        elif event.key() == Qt.Key_Q:
            self.rotateCCW()
        elif event.key() == Qt.Key_E:
            self.rotateCW()
    # def keyReleaseEvent(self, event):
        # self.rb_bin.setChecked(True)

    def refresh(self):
        self.rb_bin.setChecked(True)
        self.wg_img.switch_imgB()
        # elif self.rb_rgb.isChecked():
        #     self.wg_img.switch_imgVis()
        # elif self.rb_k.isChecked():
        #     self.wg_img.switch_imgK()

    def run(self):
        # GRID got everything done
        return 0

    def paintEvent(self, paint_event):
        if self.wg_img.zoom == 0:
            self.rb_1x.setChecked(True)
        elif self.wg_img.zoom == 1:
            self.rb_15x.setChecked(True)
        else:
            self.rb_3x.setChecked(True)


class Widget_Kmeans(Widget_Img):
    def __init__(self, grid):
        super().__init__()
        self.setMouseTracking(True)
        self.grid = grid
        self.pos = None
        self.zoom = 1
        #
        self.initUI()

    def initUI(self):
        self.show()

    def paintEvent(self, paint_event):
        painter = QPainter(self)
        super().paintImage(painter)
        painter.end()

    def switch_imgVis(self):
        super().make_rgb_img(self.grid.imgs.get("crop"))
        self.repaint()
        self.updateMag()

    def switch_imgK(self):
        super().make_idx8_img(self.grid.imgs.get("kmean"), self.grid.imgs.getParam('k'))
        self.repaint()
        self.updateMag()

    def switch_imgB(self):
        super().make_bin_img(self.grid.imgs.get("bin"))
        self.repaint()
        self.updateMag()

    def mouseMoveEvent(self, event):
        self.updateMag()
        self.repaint()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.zoom = (self.zoom+1) % 3
            self.mouseMoveEvent(event)

    def updateMag(self):
        pos = self.mapFromGlobal(QCursor().pos())
        if self.zoom != 0:
            magnifying_glass(self, pos, area=int(self.width()/7), zoom=self.zoom*1.5)
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

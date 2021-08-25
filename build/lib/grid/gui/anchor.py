# basic imports
import numpy as np

# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from .customQt import *


class PnAnchor(QWidget):
    """
    """

    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        # compute
        self.grid.findPlots()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # major
        self.layout = QHBoxLayout()
        self.grRight = QWidget()
        self.wgImg = WidgetAnchor(grid)

        self.recImg = QRect(0, 0, 0, 0)
        self.recAxs = QRect(0, 0, 0, 0)
        self.recRight = QRect(0, 0, 0, 0)

        # Right Panel
        self.loRight = QVBoxLayout()
        self.sc_right = QScrollArea()
        self.sc_right.setStyleSheet("QScrollBar {width:0px;}")
        self.sc_right.setWidgetResizable(True)

        # axes
        self.grAxis = [QGroupBox("Major axis"), QGroupBox("Minor axis: ")]
        self.loAxis = [QGridLayout(), QGridLayout()]
        self.lbAg = [QLabel("Angle"), QLabel("Angle")]
        self.rbMajAg = [QRadioButton("0°"), QRadioButton("90°")]
        self.dlMinAg = QDial()
        self.lbTk = [QLabel("# of ticks"), QLabel("# of ticks")]
        self.spbTk = [QSpinBox(), QSpinBox()]

        self.mtp = 1  # for slider

        # Tools
        self.idx_tool = 0 # 0 for major, 1 for minor
        self.gr_tool = QGroupBox("Adjust centeroids")
        self.lo_tool = QHBoxLayout()
        self.rb_maj = QRadioButton("Major axis")
        self.rb_min = QRadioButton("Minor axis")

        # Display
        self.gr_dis = QGroupBox("Display")
        self.lo_dis = QHBoxLayout()
        self.rb_bin = QRadioButton("Binary (A)")
        self.rb_rgb = QRadioButton("RGB (S)")

        # reset
        self.btReset = QPushButton("Reset")

        # mouse event
        self.idxAnc = -1 # which tick
        self.idxMaj = 0 # which majar angle (0 or 90)
        self.ptX = -1
        self.ptY = -1
        self.ptXpress = -1
        self.ptYpress = -1
        self.new_itc = -1

        # UI
        self.switch = True
        self.initUI()

        # show
        self.show()
        self.wgImg.updateDim()

    def initUI(self):
        agMaj, agMin = self.grid.map.angles

        # RIGHT: major axis
        if agMaj == 0:
            self.idxMaj = 0
            self.rbMajAg[0].setChecked(True)
            self.wgImg.isMajV = True
        else:
            self.idxMaj = 1
            self.rbMajAg[1].setChecked(True)
            self.wgImg.isMajV = False

        self.spbTk[0].setValue(len(self.grid.map.itcs[0]))
        self.loAxis[0].addWidget(self.lbAg[0], 0, 0)
        self.loAxis[0].addWidget(self.rbMajAg[0], 0, 1)
        self.loAxis[0].addWidget(self.rbMajAg[1], 0, 2)
        self.loAxis[0].addWidget(self.lbTk[0], 1, 0)
        self.loAxis[0].addWidget(self.spbTk[0], 1, 1, 1, 2)
        self.grAxis[0].setLayout(self.loAxis[0])
        self.loRight.addWidget(self.grAxis[0])

        # RIGHT: minor axis
        self.grAxis[1].setTitle("Minor axis")
        self.lbAg[1].setText("Angle: %d" % agMin)
        self.dlMinAg.setRange(-int(90/self.mtp), int(90/self.mtp))
        self.dlMinAg.setValue(int(agMin/self.mtp))
        self.dlMinAg.setPageStep(3)
        self.dlMinAg.setNotchesVisible(True)
        self.dlMinAg.setNotchTarget(5)
        self.spbTk[1].setValue(len(self.grid.map.itcs[1]))
        self.loAxis[1].addWidget(self.lbAg[1], 0, 0, 1, 1)
        self.loAxis[1].addWidget(self.dlMinAg, 0, 1, 1, 2)
        self.loAxis[1].addWidget(self.lbTk[1], 1, 0, 1, 1)
        self.loAxis[1].addWidget(self.spbTk[1], 1, 1, 1, 2)
        self.grAxis[1].setLayout(self.loAxis[1])
        self.loRight.addWidget(self.grAxis[1])

        # RIGHT: functions
        self.rbMajAg[0].toggled.connect(lambda: self.changeAngle(idx=0))
        self.rbMajAg[1].toggled.connect(lambda: self.changeAngle(idx=0))
        self.dlMinAg.valueChanged.connect(lambda: self.changeAngle(idx=1))
        self.spbTk[0].valueChanged.connect(lambda: self.changePeaks(idx=0))
        self.spbTk[1].valueChanged.connect(lambda: self.changePeaks(idx=1))
        self.rb_maj.toggled.connect(self.switchTool)
        self.rb_min.toggled.connect(self.switchTool)
        self.rb_bin.toggled.connect(self.displayImage)
        self.rb_rgb.toggled.connect(self.displayImage)

        # RIGHT: tool
        self.rb_maj.setChecked(True)
        self.lo_tool.addWidget(self.rb_maj)
        self.lo_tool.addWidget(self.rb_min)
        self.gr_tool.setLayout(self.lo_tool)
        self.loRight.addWidget(self.gr_tool)

        # RIGHT: display
        self.rb_bin.setChecked(True)
        self.lo_dis.addWidget(self.rb_bin)
        self.lo_dis.addWidget(self.rb_rgb)
        self.gr_dis.setLayout(self.lo_dis)
        self.loRight.addWidget(self.gr_dis)

        # RIGHT: comp
        self.loRight.addWidget(self.btReset)
        self.grRight.setLayout(self.loRight)
        self.sc_right.setWidget(self.grRight)

        # LEFT IMG: mouse tracking
        # self.wgImg.setMouseTracking(True)

        # Main
        policyRight = QSizePolicy(QSizePolicy.Preferred,
                                  QSizePolicy.Preferred)
        policyRight.setHorizontalStretch(2)
        self.sc_right.setSizePolicy(policyRight)

        policyLeft = QSizePolicy(QSizePolicy.Preferred,
                                 QSizePolicy.Preferred)
        policyLeft.setHorizontalStretch(3)
        self.wgImg.setSizePolicy(policyLeft)

        self.layout.addWidget(self.wgImg)
        self.layout.addWidget(self.sc_right)

        self.setLayout(self.layout)

    def paintEvent(self, event):
        try:
            self.updatePlots()
        except Exception as e:
            print(e)

        # '''rect'''
        # pen.setWidth(1)
        # pen.setColor(Qt.black)
        # painter.setPen(pen)
        # painter.setBrush(Qt.transparent)
        # painter.drawRect(self.rec_acr_c)
        # painter.drawRect(self.rec_acr_r)

    def updatePlots(self):
        self.updateMajorLines()
        self.updateAgents()

    def changeAngle(self, idx):
        # current angle
        if idx == 0:
            # if major axis
            angle = 0 if self.rbMajAg[0].isChecked() else 90
            # oposite angle
            angleOp = self.dlMinAg.value() * self.mtp
        else:
            # if minor axis     
            angle = self.dlMinAg.value() * self.mtp
            # oposite angle
            angleOp = 0 if self.rbMajAg[0].isChecked() else 90
            # change title
            self.lbAg[1].setText("Angle: %d°" % angle)

        # major angle
        self.wgImg.isMajV = self.rbMajAg[0].isChecked()
        self.idxMaj = 0 if self.wgImg.isMajV else 1  # v -> 0°

        # print("before")
        # print("ops:%2f" % (angleOp))
        # print("self:%2f" % (angle))
        # print("after")
        # angle difference between two axes
        # if difference is greater than 0
            # # if difference is greater than 90 degrees
            # if angleDiff > 90:
            #     print("greater than 90")
            #     if angle > 0:
            #         value = (angle - 90) / self.mtp
            #     else:
            #         value = (angle + 90) / self.mtp
            #     # if idx == 0:
            #     #     value = min(angle + 90, 90) / self.mtp
            #     # else:
            #     #     value = max(-90, angle - 90) / self.mtp
            #     print("ops:%2f" % (value * self.mtp))
            #     print("self:%2f" % (angle))
            #     self.dlAg[1 - idx].setValue(int(value))
            # # if different side
            # elif angle * angleOp < 0:
            #     print("less than 90, different sides")
            #     # force the current one equal to 0
            #     angleOp = (angle - 90) if angle > 0 else (angle + 90)
            #     self.dlAg[1 - idx].setValue(int(angleOp / self.mtp))
            # # same side
            # else:
            #     print("less than 90, same sides")
            #     # current is +-90, push opp
            #     if abs(angle) > abs(angleOp):
            #         angleOp = (angle - 90) if angle > 0 else (angle + 90)
            #         self.dlAg[1 - idx].setValue(int(angleOp / self.mtp))
            #     # opp is +-90
            #     else:
            #         angleOp = 90 if angleOp > 0 else -90
            #         self.dlAg[1 - idx].setValue(int(angleOp / self.mtp))

            # if difference is less than 90 degrees and neither of them is 0
            # elif angle * angleOp > 0:
            #     # force the current one equal to 0
            #     angle = 0
            #     self.dlAg[idx].setValue(0)
        self.grid.updateCenters(idx, angle=angle)
        self.switch = False
        self.spbTk[0].setValue(len(self.grid.map.itcs[0]))
        self.spbTk[1].setValue(len(self.grid.map.itcs[1]))
        self.switch = True
        self.displayImage()
        self.repaint()

    def changePeaks(self, idx):
        if self.switch:
            nPeaks = self.spbTk[idx].value()
            self.grid.updateCenters(idx, nPeaks=nPeaks)
            self.displayImage()
            self.repaint()

    # def switchAngle(self, idx):
    #     self.idxAx = idx
    #     self.displayImage()
    #     self.grAxis[idx].setChecked(True)
    #     self.grAxis[int(not idx)].setChecked(False)
    #     self.repaint()

    def switchTool(self):
        self.idx_tool = 0 if self.rb_maj.isChecked() else 1
        self.wgImg.isMajTool = self.rb_maj.isChecked()
        self.wgImg.repaint()

    def displayImage(self):
        self.idxAx = 0 ###NOTE
        if self.rb_bin.isChecked():
            self.wgImg.make_bin_img(self.grid.map.imgBin)
        else:
            self.wgImg.make_rgb_img(self.grid.map.imgRGB)
        self.wgImg.repaint()

    def updateMajorLines(self):
        ptsRaw = self.grid.map.sigs[0]
        if self.idxMaj == 0: # which major angle (0° or 90°)
            rgSrc = (0, self.grid.map.imgW)
            rgDst = self.wgImg.rgX
        else:
            rgSrc = (0, self.grid.map.imgH)
            rgDst = self.wgImg.rgY

        pts = rescale(ptsRaw, rgSrc, rgDst)
        self.wgImg.ptMajLine = pts

    def updateAgents(self):
        # fetch info
        gmap = self.grid.map
        agCr = gmap.angles[0]
        agOp = gmap.angles[1]
        agDiff = agOp
        agAbs = abs(agDiff)

        imgH, imgW = gmap.imgH, gmap.imgW
        qimgH, qimgW = self.wgImg.sizeImg.height(), self.wgImg.sizeImg.width()
        ratio = sum([qimgW / imgW, qimgH / imgH]) / 2

        # current axis
        # self.wgImg.ptMajLine = self.wgAxs.pts

        # another axis
        self.wgImg.slp = 1 / np.tan(np.pi / 180 * agDiff)
        sigs = gmap.sigs[1]
        itc = getCardIntercept(sigs, agDiff, imgH)

        # if agCr % 90 == 0:
        #     # bugmsg("case 1")
        # elif agOp % 90 == 0:
        #     itc = np.cos(np.pi / 180 * agAbs) * gmap.imgHr[1] + \
        #             sigs / np.sin(np.pi / 180 * agAbs)
        #     if agDiff < 0:
        #         # bugmsg("case 2")
        #         None
        #     else:
        #         # bugmsg("case 3")
        #         itc = gmap.imgHr[idxCr] - itc
        # else:
        #     seg1 = gmap.imgH * np.cos(np.pi / 180 * abs(agCr))
        #     seg2 = (sigs - gmap.imgH * np.sin(np.pi / 180 * abs(agOp))) / \
        #         np.sin(np.pi / 180 * (abs(agOp) + abs(agCr)))
        #     itc = seg1 + seg2
        #     if agCr > 0:
        #         # bugmsg("case 4")
        #         None
        #     else:
        #         # bugmsg("case 5")
        #         itc = gmap.imgHr[idxCr] - itc

        self.wgImg.itcs = itc * ratio

        # slp = -1/np.tan(np.pi/180*agAbs) if agAbs < 0 else 1/np.tan(np.pi/180*agAbs)
        # sigs = self.grid.map.sigs[idxOp]
        # if idxOp==1:
        #     self.wgImg.slp = slp
        #     X = (sigs/np.sin(np.pi/180*agAbs)) + \
        #         np.cos(np.pi/180*agAbs)*self.grid.map.imgHr[idxOp]
        #     self.wgImg.itcs = (qimgH - X*ratio)
        # else:
        #     self.wgImg.slp = -slp
        #     segA = sigs/np.sin(np.pi/180*agAbs)
        #     segB = np.sin(np.pi/180*agAbs)*self.grid.map.imgWr[idxOp]
        #     self.wgImg.itcs = segA*ratio + (qimgW - segB*ratio)

    def updateDim(self):
        self.recImg = self.wgImg.geometry()
        self.recRight = self.grRight.geometry()

    def getPtGui2Map(self, pt, axis=0):
        rgWg = self.wgImg.getImgRange()[axis]
        if axis == 0:
            rgMap = (0, self.grid.map.imgW-1)
            value = rescale(values=pt-self.recImg.x(),
                            scaleSrc=rgWg, scaleDst=rgMap)
        else:
            rgMap = (0, self.grid.map.imgH-1)
            value = rescale(values=pt-self.recImg.y(),
                            scaleSrc=rgWg, scaleDst=rgMap)
        return value

    def mousePressEvent(self, event):
        # ptX, ptY are coordinate in map
        pos = event.pos()
        objMap = self.grid.map
        self.updateDim()
        if self.recImg.contains(pos):
            self.ptX = self.getPtGui2Map(pos.x(), axis=0)
            self.ptY = self.getPtGui2Map(pos.y(), axis=1)
            self.ptXpress, self.ptYpress = self.ptX, self.ptY
            if self.idx_tool == 0:
                # major axis  0° or 90°
                ptPress = self.ptX if self.idxMaj == 0 else self.ptY
                # search index by signals
                self.idxAnc = np.abs(
                    ptPress-objMap.sigs[0]).argmin()
            else:
                # minor axis
                slope = objMap.slps[1]
                intercepts = objMap.itcs[1]
                # search index by intercepts, will be fine for angle < 0
                if objMap.angles[1] == 0:
                    self.idxAnc = np.abs(self.ptX-objMap.sigs[1]).argmin()
                else:
                    ls_y = np.array(intercepts) + self.ptX * slope
                    self.idxAnc = np.abs(self.ptY-ls_y).argmin()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        objMap = self.grid.map
        if self.idxAnc != -1:
            if self.idx_tool == 0:
                # major axis
                ptPos = pos.x() if self.idxMaj == 0 else pos.y()
                rg_wgImg = self.wgImg.rgX if self.idxMaj == 0 else self.wgImg.rgY
                size_img = objMap.imgW - 1 if self.idxMaj == 0 else objMap.imgH - 1
                if ptPos > rg_wgImg[0] and ptPos < rg_wgImg[1]:
                    pt = self.getPtGui2Map(ptPos, self.idxMaj)
                elif ptPos <= rg_wgImg[0]:
                    pt = 0
                elif ptPos >= rg_wgImg[1]:
                    pt = size_img - 1
                try:
                    objMap.modMajAnchor(self.idxAnc, pt)  # self.ptX
                except Exception:
                    None
            else:
                # minor axis
                if pos.y() > self.wgImg.rgY[0] and pos.y() < self.wgImg.rgY[1]:
                    ptY = self.getPtGui2Map(pos.y(), axis=1)
                elif pos.y() <= self.wgImg.rgY[0]:
                    ptY = 0
                elif pos.y() >= self.wgImg.rgY[1]:
                    ptY = objMap.imgH - 1

                ptX = self.getPtGui2Map(pos.x(), axis=0)

                if objMap.angles[1] == 0:
                    self.itc_new = ptX
                else:
                    self.itc_new = ptY - ptX * objMap.slps[1]
                try:
                    objMap.modMinAnchor(self.idxAnc, self.itc_new)  # self.ptY
                except Exception:
                    None
            self.update()

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        objMap = self.grid.map
        ptX = self.getPtGui2Map(pos.x(), axis=0)
        ptY = self.getPtGui2Map(pos.y(), axis=1)
        sig = np.array(objMap.sigs[self.idx_tool])
        itc = np.array(objMap.itcs[self.idx_tool])
        if (self.idxAnc != -1 and
           event.button() == Qt.RightButton and
           self.spbTk[self.idx_tool].value() > 1):
            # remove tick
            objMap.delAnchor(self.idx_tool, self.idxAnc)
            value = self.spbTk[self.idx_tool].value() - 1
            self.switch = False
            self.spbTk[self.idx_tool].setValue(value)
            self.switch = True
        elif event.button() == Qt.LeftButton:
            if self.idx_tool == 0:
                # add tick major
                pt = ptX if self.idxMaj == 0 else ptY
                ptPress = self.ptXpress if self.idxMaj == 0 else self.ptYpress
                if ptPress == pt and abs(sig-pt).min() > sig.std() / 20:
                    objMap.addMajAnchor(pt)
                    value = self.spbTk[self.idx_tool].value() + 1
                    self.switch = False
                    self.spbTk[self.idx_tool].setValue(value)
                    self.switch = True
            else:
                # add tick minor
                # check if angle is 0 or not:
                if objMap.angles[1] == 0:
                    new_itc = ptX
                else:
                    new_itc = ptY - ptX * objMap.slps[1]
                # pass itc
                if self.ptYpress == ptY and abs(itc-new_itc).min() > itc.std() / 20:
                    objMap.addMinAnchor(new_itc)
                    value = self.spbTk[self.idx_tool].value() + 1
                    self.switch = False
                    self.spbTk[self.idx_tool].setValue(value)
                    self.switch = True

        self.update()
        self.ptX = -1
        self.ptY = -1
        self.ptXpress = -1
        self.ptYpress = -1
        self.idxAnc = -1
        self.new_itc = -1

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.rb_bin.setChecked(True)
        elif event.key() == Qt.Key_S:
            self.rb_rgb.setChecked(True)

    def run(self):
        self.grid.agents.setup(gmap=self.grid.map,
                               gimg=self.grid.imgs)


class WidgetAnchor(Widget_Img):
    def __init__(self, grid):
        super().__init__()
        self.grid = grid
        self.isMajV = True
        self.isMajTool = True
        self.ptMajLine = []
        self.itcs = []
        self.slp = 0
        super().make_bin_img(grid.map.imgBin)
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        super().paintImage(painter)
        pen = QPen()

        ## Major axis
        # tool switch (major)
        pen_width = 3 if self.isMajTool else 1
        pen.setWidth(pen_width)
        if not self.isMajTool:
            pen.setStyle(Qt.DotLine)
        else:
            pen.setStyle(Qt.SolidLine)
        pen.setColor(Qt.red)
        painter.setPen(pen)

        # major lines
        for pt in self.ptMajLine:
            if self.isMajV:
                painter.drawLine(pt, self.rgY[0], pt, self.rgY[1])
            else:
                painter.drawLine(self.rgX[0], pt, self.rgX[1], pt)

        ## Minor axis
        for itc in self.itcs:
            if self.grid.map.angles[1] != 0:
                # if minor axis angle is not equal to 0
                x1, x2 = self.rgX 
                y1 = self.rgY[0] + itc
                y2 = y1 + (x2-x1)*self.slp
            else:
                # if minor axis angle is equal to 0
                y1, y2 = self.rgY
                x1 = self.rgX[0] + itc
                x2 = x1

            # tool switch (minor)
            pen_width = 1 if self.isMajTool else 3
            pen.setWidth(pen_width)
            if self.isMajTool:
                pen.setStyle(Qt.DotLine)
            else:
                pen.setStyle(Qt.SolidLine)
            painter.setPen(pen)
                    
            try:
                painter.drawLine(x1, y1, x2, y2)
                pen.setWidth(3)
                pen.setStyle(Qt.SolidLine)
                painter.setPen(pen)
                if self.isMajV:
                    for x in self.ptMajLine:
                        ptX = x
                        ptY = y1 + (x - x1) * self.slp
                        if self.isInRange(ptX, ptY):
                            drawCross(ptX, ptY, painter, size=4)
                else:
                    for y in self.ptMajLine:
                        ptX = x1 + ((y - y1) / self.slp)
                        ptY = y
                        if self.isInRange(ptX, ptY):
                            drawCross(ptX, ptY, painter, size=4)
            except Exception as e:
                print(e)

        painter.end()


# class WidgetAxis(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setMouseTracking(True)
#         self.pts = []

#     def setPoints(self, pts):
#         self.pts = pts

#     def paintEvent(self, event):
#         painter = QPainter(self)
#         pen = QPen()
#         pen.setWidth(3)
#         pen.setColor(Qt.red)
#         painter.setPen(pen)
#         painter.setBrush(Qt.red)
#         # plot triangle
#         ptY = int(self.height()/2)
#         for ptX in self.pts:
#             drawTriangle(ptX, ptY, "North", painter)

#         painter.end()


def rescale(values, scaleSrc=(0, 1), scaleDst=(0, 256)):
    values = np.array(values)
    return (values-scaleSrc[0])*(scaleDst[1]-scaleDst[0])/(scaleSrc[1]-scaleSrc[0])+scaleDst[0]

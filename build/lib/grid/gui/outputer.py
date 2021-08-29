# basic imports
import numpy as np
import pandas as pd
import os

# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from ..grid import *
from ..io import *
from .customQt import *


class PnOutputer(QWidget):
    def __init__(self, grid):
        '''
        '''
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.update()
        self.grid = grid
        self.runDefaultSeg()

        self.layout = QHBoxLayout()
        '''left side'''
        self.wg_img = Widget_Seg(grid)
        '''right side'''
        self.pn_right = QWidget()
        self.lo_right = QVBoxLayout()
        self.sc_right = QScrollArea()
        self.sc_right.setWidgetResizable(True)
        # Boundary
        self.gr_seg = QGroupBox("Segmentation")
        self.lo_seg = QGridLayout()
        # Boundary (auto)
        self.gr_auto = QGroupBox("Dynamic")
        self.lo_auto = QVBoxLayout()
        self.gr_grid = QGroupBox("Grid Coef. = 0.0")
        self.lo_grid = QVBoxLayout()
        self.sl_grid = QSlider(Qt.Horizontal)
        # Boundary (fix)
        self.gr_fix = QGroupBox("Fixed")
        self.lo_fix = QVBoxLayout()
        self.gr_width = QGroupBox("Width = 50 units")
        self.lo_width = QVBoxLayout()
        self.sl_width = QSlider(Qt.Horizontal)
        self.gr_length = QGroupBox("Length = 50 units")
        self.lo_length = QVBoxLayout()
        self.sl_length = QSlider(Qt.Horizontal)
        self.lb_alignX = QLabel("Align Columns (beta)")
        self.cb_alignX = QComboBox()
        self.lb_alignY = QLabel("Align Rows (beta)")
        self.cb_alignY = QComboBox()
        self.ck_evenH = QCheckBox("Evenly Distribute Columns (beta)")
        self.ck_evenV = QCheckBox("Evenly Distribute Rows (beta)")
        self.bt_reset = QPushButton("Reset")
        # Tool
        self.gr_tol = QGroupBox("Tools (Right-click to switch)")
        self.lo_tol = QGridLayout()
        self.rb_ct = QRadioButton("Adjust Centroid")
        self.rb_adj = QRadioButton("Adjust Border")
        self.rb_vp = QRadioButton("Pan (Vertical)")
        self.rb_hp = QRadioButton("Pan (Horizontal)")
        # Display
        self.gr_dis = QGroupBox("Display")
        self.lo_dis = QHBoxLayout()
        self.rb_srgb = QRadioButton("Selected RGB (A)")
        self.rb_rgb = QRadioButton("RGB (S)")
        # Output
        self.gr_out = QGroupBox("Output")
        self.lo_out = QGridLayout()
        self.lb_project = QLabel("Prefix")
        self.fd_project = QLineEdit("GRID")
        self.lb_output = QLabel("Output Path")
        self.fd_output = QLineEdit(self.grid.path_out)
        self.bt_output = QPushButton("Browse")
        self.ck_simple = QCheckBox("Simple output")
        '''ui'''
        self.initUI()

    def initUI(self):
        '''seg-auto (right)'''
        # components
        self.sl_grid.setMinimum(0)
        self.sl_grid.setMaximum(10)
        self.sl_grid.setValue(0)
        self.sl_grid.setTickInterval(2)
        self.sl_grid.setTickPosition(QSlider.TicksBelow)
        self.sl_grid.valueChanged.connect(self.change_grid)
        self.gr_auto.setCheckable(True)
        self.gr_auto.setChecked(True)
        self.gr_auto.clicked.connect(self.auto_seg)
        # layout
        self.lo_grid.addWidget(self.sl_grid)
        self.gr_grid.setLayout(self.lo_grid)
        self.lo_auto.addWidget(self.gr_grid)
        self.gr_auto.setLayout(self.lo_auto)
        '''seg-fix (right)'''
        # components
        self.sl_width.setMinimum(0)
        self.sl_width.setMaximum(100)
        self.sl_width.setValue(50)
        self.sl_width.setTickInterval(2)
        self.sl_width.setTickPosition(QSlider.TicksBelow)
        self.sl_width.valueChanged.connect(self.change_width)
        self.sl_length.setMinimum(0)
        self.sl_length.setMaximum(100)
        self.sl_length.setValue(50)
        self.sl_length.setTickInterval(2)
        self.sl_length.setTickPosition(QSlider.TicksBelow)
        self.sl_length.valueChanged.connect(self.change_length)
        self.cb_alignX.addItem("None")
        self.cb_alignX.addItem("Left")
        self.cb_alignX.addItem("Center")
        self.cb_alignX.addItem("Right")
        self.cb_alignY.addItem("None")
        self.cb_alignY.addItem("Top")
        self.cb_alignY.addItem("Middle")
        self.cb_alignY.addItem("Bottom")
        self.cb_alignX.currentIndexChanged.connect(self.alignX)
        self.cb_alignY.currentIndexChanged.connect(self.alignY)
        self.ck_evenH.clicked.connect(self.evenH)
        self.ck_evenV.clicked.connect(self.evenV)
        self.bt_reset.clicked.connect(self.reset)
        self.gr_fix.setCheckable(True)
        self.gr_fix.setChecked(False)
        self.gr_fix.clicked.connect(self.fix_seg)
        # layout
        self.lo_width.addWidget(self.sl_width)
        self.gr_width.setLayout(self.lo_width)
        self.lo_length.addWidget(self.sl_length)
        self.gr_length.setLayout(self.lo_length)
        # self.gr_aln.setLayout(self.lo_aln)
        self.lo_fix.addWidget(self.gr_width)
        self.lo_fix.addWidget(self.gr_length)
        self.lo_fix.addWidget(self.lb_alignX)
        self.lo_fix.addWidget(self.cb_alignX)
        self.lo_fix.addWidget(self.lb_alignY)
        self.lo_fix.addWidget(self.cb_alignY)
        self.lo_fix.addWidget(self.ck_evenH)
        self.lo_fix.addWidget(self.ck_evenV)
        self.gr_fix.setLayout(self.lo_fix)
        '''seg (right)'''
        # layout
        self.lo_seg.addWidget(self.gr_auto)
        self.lo_seg.addWidget(self.gr_fix)
        self.gr_seg.setLayout(self.lo_seg)
        '''tool'''
        self.rb_adj.setChecked(True)
        self.rb_ct.toggled.connect(lambda: self.changeTool(index=0))
        self.rb_adj.toggled.connect(lambda: self.changeTool(index=1))
        self.rb_vp.toggled.connect(lambda: self.changeTool(index=2))
        self.rb_hp.toggled.connect(lambda: self.changeTool(index=3))
        self.lo_tol.addWidget(self.rb_ct, 0, 0)
        self.lo_tol.addWidget(self.rb_adj, 0, 1)
        self.lo_tol.addWidget(self.rb_vp, 1, 0)
        self.lo_tol.addWidget(self.rb_hp, 1, 1)
        self.gr_tol.setLayout(self.lo_tol)
        '''display (right)'''
        # components
        self.rb_srgb.setChecked(True)
        self.rb_srgb.toggled.connect(self.wg_img.switch_imgSVis)
        self.rb_rgb.toggled.connect(self.wg_img.switch_imgVis)
        # layout
        self.lo_dis.addWidget(self.rb_srgb)
        self.lo_dis.addWidget(self.rb_rgb)
        self.gr_dis.setLayout(self.lo_dis)
        '''output (right)'''
        # components
        font = self.fd_project.font()
        font.setPointSize(25)
        fm = QFontMetrics(font)
        self.fd_project.setFixedHeight(fm.height())
        self.fd_output.setFixedHeight(fm.height())
        self.bt_output.clicked.connect(self.assign_PathOut)
        self.ck_simple.setChecked(True)
        # layout
        self.lo_out.addWidget(self.lb_project, 0, 0)
        self.lo_out.addWidget(self.fd_project, 0, 1)
        self.lo_out.addWidget(self.lb_output, 1, 0)
        self.lo_out.addWidget(self.fd_output, 1, 1)
        self.lo_out.addWidget(self.bt_output, 1, 2)
        self.lo_out.addWidget(self.ck_simple, 2, 0, 1, 3)
        self.gr_out.setLayout(self.lo_out)
        '''layout'''
        # left
        # NONE
        # right
        self.lo_right.addWidget(self.gr_seg)
        self.lo_right.addWidget(self.gr_tol)
        self.lo_right.addWidget(self.bt_reset)
        self.lo_right.addWidget(self.gr_dis)
        self.lo_right.addWidget(self.gr_out)
        self.pn_right.setLayout(self.lo_right)
        self.sc_right.setWidget(self.pn_right)
        # policy
        policy_right = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy_right.setHorizontalStretch(2)
        self.sc_right.setSizePolicy(policy_right)
        policy_left = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy_left.setHorizontalStretch(3)
        self.wg_img.setSizePolicy(policy_left)
        # assemble
        self.layout.addWidget(self.wg_img)
        self.layout.addWidget(self.sc_right)
        self.setLayout(self.layout)
        # collapsable
        self.collapse(isAuto=True)
        # show
        self.show()

    def collapse(self, isAuto=True):
        self.gr_grid.setVisible(isAuto)
        self.gr_width.setVisible(not isAuto)
        self.gr_length.setVisible(not isAuto)
        self.lb_alignX.setVisible(not isAuto)
        self.cb_alignX.setVisible(not isAuto)
        self.lb_alignY.setVisible(not isAuto)
        self.cb_alignY.setVisible(not isAuto)
        self.ck_evenH.setVisible(not isAuto)
        self.ck_evenV.setVisible(not isAuto)

    def auto_seg(self):
        '''
        '''
        self.gr_auto.setChecked(True)
        self.gr_fix.setChecked(False)
        self.collapse(isAuto=True)
        val_grid = 1-(self.sl_grid.value()/10)
        self.wg_img.auto_seg(coefGrid=val_grid)

    def fix_seg(self):
        '''
        '''
        self.gr_auto.setChecked(False)
        self.gr_fix.setChecked(True)
        self.collapse(isAuto=False)
        value_width = self.sl_width.value()
        value_length = self.sl_length.value()
        self.wg_img.fix_seg(value_width, value_length)

    def changeTool(self, index):
        self.wg_img.task = index

    def change_grid(self):
        '''
        '''
        value = self.sl_grid.value()
        self.gr_grid.setTitle("Grid Coef. = %.2f" % (value/10))
        self.auto_seg()

    def change_width(self):
        '''
        '''
        value = self.sl_width.value()
        self.gr_width.setTitle("Width = %d units" % (value))
        self.fix_seg()

    def change_length(self):
        '''
        '''
        value = self.sl_length.value()
        self.gr_length.setTitle("Length = %d units" % (value))
        self.fix_seg()

    def alignX(self):
        '''
        '''
        index = self.cb_alignX.currentIndex()
        self.wg_img.align(method=index, axis=1)

    def alignY(self):
        '''
        '''
        index = self.cb_alignY.currentIndex()
        self.wg_img.align(method=index, axis=0)

    def evenH(self):
        '''
        '''
        self.wg_img.distributed(axis=1, isEven=self.ck_evenH.isChecked())

    def evenV(self):
        '''
        '''
        self.wg_img.distributed(axis=0, isEven=self.ck_evenV.isChecked())

    def reset(self):
        '''
        '''
        self.sl_width.setValue(50)
        self.sl_length.setValue(50)
        self.cb_alignX.setCurrentIndex(0)
        self.cb_alignY.setCurrentIndex(0)
        self.grid.agents.resetCoordinate()
        self.runDefaultSeg()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.rb_srgb.setChecked(True)
        elif event.key() == Qt.Key_S:
            self.rb_rgb.setChecked(True)

    def assign_PathOut(self):
        path = QFileDialog().getExistingDirectory(self, "", "", QFileDialog.ShowDirsOnly)
        self.fd_output.setText(path)

    def paintEvent(self, paint_event):
        if self.wg_img.task == 0:
            self.rb_ct.setChecked(True)
        elif self.wg_img.task == 1:
            self.rb_adj.setChecked(True)
        elif self.wg_img.task == 2:
            self.rb_vp.setChecked(True)
        else:
            self.rb_hp.setChecked(True)

    def runDefaultSeg(self):
        if self.grid.imgs.hasShp:
            self.grid.imgs.readyForSeg()
            self.grid.agents.setup(gmap=self.grid.map, gimg=self.grid.imgs)
        else:
            self.grid.cpuSeg()


class Widget_Seg(Widget_Img):
    def __init__(self, grid):
        '''
        '''
        super().__init__()
        self.setMouseTracking(True)
        self.grid = grid
        self.img_raw = grid.imgs.get('visSeg')
        self.task = 0  # 0 centroid, 1 zoom, 2 panV, 3 panH
        '''attr'''
        # painter
        self.ratio = 0
        # mouse
        self.agent_click = False
        self.dir = None
        # seg
        imgBin = self.grid.imgs.get("bin")
        imgBinTemp = imgBin.reshape(imgBin.shape[0], imgBin.shape[1], 1)
        self.img_seg = np.multiply(self.grid.imgs.get("crop")[:, :, :3],
                                   imgBinTemp).copy()

        # ui
        self.initUI()

    def initUI(self):
        self.make_rgb_img(self.img_raw)
        self.show()

    def mouseReleaseEvent(self, event):
        self.agent_click = False

    def mousePressEvent(self, event):
        self.pos_press = (event.pos().x(), event.pos().y())
        self.pos_move_prev = self.pos_press

        # to figure out what border has benn selected
        for row in range(self.grid.map.nRow):
            for col in range(self.grid.map.nCol):
                # compute rect of agent
                agent = self.grid.agents.get(row, col)
                if not agent or agent.isFake():
                    continue
                rect = agent.getQRect()
                if self.isFitWidth:
                    self.ratio = self.width() / self.qimg.width()
                else:
                    self.ratio = self.height() / self.qimg.height()

                rec_agent = QRect(rect.x() * self.ratio + self.rgX[0],
                                  rect.y() * self.ratio + self.rgY[0],
                                  rect.width() * self.ratio,
                                  rect.height() * self.ratio)
                # if contain cursor
                if rec_agent.contains(event.pos()):
                    self.agent_click = agent
                    if self.task == 1:
                        # zoom and mod border
                        bd_W = rec_agent.x()
                        bd_N = rec_agent.y()
                        bd_E = bd_W + rec_agent.width()
                        bd_S = bd_N + rec_agent.height()
                        dis_W = abs(self.pos_press[0] - bd_W)
                        dis_N = abs(self.pos_press[1] - bd_N)
                        dis_E = abs(self.pos_press[0] - bd_E)
                        dis_S = abs(self.pos_press[1] - bd_S)
                        dir_idx = np.argmin(np.array([dis_N, dis_W, dis_S, dis_E]))
                        if dir_idx == 0:
                            self.dir = Dir.NORTH
                        elif dir_idx == 1:
                            self.dir = Dir.WEST
                        elif dir_idx == 2:
                            self.dir = Dir.SOUTH
                        elif dir_idx == 3:
                            self.dir = Dir.EAST
                    break

        # mag module
        if event.button() == Qt.RightButton:
            self.task = (self.task + 1) % 4
            self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        self.pos_move = (event.pos().x(), event.pos().y())

        # change cursor
        if self.task == 0:
            # moving centroid
            self.setCursor(QCursor(Qt.SizeAllCursor))
        elif self.task == 1:
            # adjust borders
            magnifying_glass(self, event.pos(), area=int(
                self.width() / 7), zoom=1.5)
        elif self.task == 2:
            self.setCursor(QCursor(Qt.SizeVerCursor))
        elif self.task == 3:
            self.setCursor(QCursor(Qt.SizeHorCursor))

        # pan
        if (event.buttons() == Qt.LeftButton) & (self.agent_click != False):
            # convert GUI to image coordinate
            x_move, y_move = self.convertGUI2XY(self.pos_move)
            x_move_prev, y_move_prev = self.convertGUI2XY(self.pos_move_prev)
            dx = x_move - x_move_prev
            dy = y_move - y_move_prev

            if self.task == 0:
                # adjust centroid
                self.agent_click.updateCoordinate(value=dy, axis=0)
                self.agent_click.updateCoordinate(value=dx, axis=1)
            elif self.task == 1:
                # adjust border
                if self.dir == Dir.NORTH or self.dir == Dir.SOUTH:
                    value = y_move
                elif self.dir == Dir.WEST or self.dir == Dir.EAST:
                    value = x_move
                self.grid.agents.setBorder(self.agent_click, self.dir, value)
            elif self.task == 2:
                # V pan
                row = self.agent_click.row
                self.grid.agents.pan(axis=0, target=row, value=dy)
            elif self.task == 3:
                # H pan
                col = self.agent_click.col
                self.grid.agents.pan(axis=1, target=col, value=dx)

        self.pos_move_prev = self.pos_move
        self.repaint()

    def convertGUI2XY(self, pt):
        posX = (pt[0] - self.rgX[0]) / self.ratio
        posY = (pt[1] - self.rgY[0]) / self.ratio
        return (posX, posY)

    def paintEvent(self, paint_event):
        painter = QPainter(self)
        super().paintImage(painter)
        pen = QPen()        
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        for row in range(self.grid.agents.nRow):
            for col in range(self.grid.agents.nCol):
                agent = self.grid.agents.get(row, col)
                if not agent or agent.isFake():
                    continue
                rect = agent.getQRect()
                pt_x, pt_y = agent.getCoordinate()
                self.ratio = self.width()/self.qimg.width() if self.isFitWidth else self.height()/self.qimg.height()
                rec_agent = QRect(rect.x()*self.ratio+self.rgX[0],
                                  rect.y()*self.ratio+self.rgY[0],
                                  rect.width()*self.ratio,
                                  rect.height()*self.ratio)
                drawCross(pt_x*self.ratio + self.rgX[0], 
                          pt_y*self.ratio + self.rgY[0], painter)
                painter.drawRect(rec_agent)
        painter.end()

    def switch_imgVis(self):
        super().make_rgb_img(self.grid.imgs.get('crop'))
        self.repaint()

    def switch_imgSVis(self):
        super().make_rgb_img(self.grid.imgs.get('visSeg'))
        self.repaint()

    def auto_seg(self, coefGrid=0):
        self.grid.cpuSeg(coefGrid=coefGrid)
        self.repaint()

    def fix_seg(self, width, length):
        self.grid.fixSeg(width=width, length=length)
        self.repaint()

    def align(self, method, axis=0):
        self.grid.agents.align(method=method, axis=axis)
        self.repaint()

    def distributed(self, axis=0, isEven=False):
        self.grid.agents.distributed(axis=axis, isEven=isEven)
        self.repaint()

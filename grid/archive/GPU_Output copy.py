import numpy as np
import pandas as pd
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .CPU_Field import *
from .Misc import *

class Panel_Output(QWidget):
    def __init__(self, **params):
        '''
        '''
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        self.update()
        self.layout = QHBoxLayout()
        '''dimension'''
        self.dim = params['bin'].shape
        self.imgH = self.dim[0]
        self.imgW = self.dim[1]
        '''left side'''
        self.wg_img = Widget_Seg(**params)
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
        self.fd_output = QLineEdit(os.path.expanduser("~"))
        self.bt_output = QPushButton("Browse")
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
        self.lo_fix.addWidget(self.bt_reset)
        self.gr_fix.setLayout(self.lo_fix)
        '''seg (right)'''
        # layout
        self.lo_seg.addWidget(self.gr_auto)
        self.lo_seg.addWidget(self.gr_fix)
        self.gr_seg.setLayout(self.lo_seg)
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
        # layout
        self.lo_out.addWidget(self.lb_project, 0, 0)
        self.lo_out.addWidget(self.fd_project, 0, 1)
        self.lo_out.addWidget(self.lb_output, 1, 0)
        self.lo_out.addWidget(self.fd_output, 1, 1)
        self.lo_out.addWidget(self.bt_output, 1, 2)
        self.gr_out.setLayout(self.lo_out)
        '''layout'''
        # left
        # NONE
        # right
        self.lo_right.addWidget(self.gr_seg)
        self.lo_right.addWidget(self.gr_dis)
        self.lo_right.addWidget(self.gr_out)
        self.pn_right.setLayout(self.lo_right)
        self.sc_right.setWidget(self.pn_right)
        # policy
        policy_right = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy_right.setHorizontalStretch(1)
        self.sc_right.setSizePolicy(policy_right)
        policy_left = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        policy_left.setHorizontalStretch(2)
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
        self.bt_reset.setVisible(not isAuto)
    def auto_seg(self):
        '''
        '''
        self.gr_auto.setChecked(True)
        self.gr_fix.setChecked(False)
        self.collapse(isAuto=True)
        val_grid = 1-(self.sl_grid.value()/10)
        self.wg_img.auto_seg(coef_grid=val_grid)
    def fix_seg(self):
        '''
        '''
        self.gr_auto.setChecked(False)
        self.gr_fix.setChecked(True)
        self.collapse(isAuto=False)
        value_width = self.sl_width.value()
        value_length = self.sl_length.value()
        self.wg_img.fix_seg(value_width, value_length)
    def change_grid(self):
        '''
        '''
        value = self.sl_grid.value()
        self.gr_grid.setTitle("Grid Coef. = %.2f" %(value/10))
        self.auto_seg()
    def change_width(self):
        '''
        '''
        value = self.sl_width.value()
        self.gr_width.setTitle("Width = %d units" %(value))
        self.fix_seg()
    def change_length(self):
        '''
        '''
        value = self.sl_length.value()
        self.gr_length.setTitle("Length = %d units" %(value))
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
        self.wg_img.field.reset_coordinate()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A:
            self.rb_srgb.setChecked(True)
        elif event.key() == Qt.Key_S:
            self.rb_rgb.setChecked(True)
    def assign_PathOut(self):
        path = QFileDialog().getExistingDirectory(self, "", "", QFileDialog.ShowDirsOnly)
        self.fd_output.setText(path)
    def paint_grid(self, qimg):
        """
        """
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter = QPainter(qimg)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        for row in range(self.wg_img.field.nrow):
            for col in range(self.wg_img.field.ncol):
                agent = self.wg_img.field.get_agent(row, col)
                rect = agent.get_rect()
                painter.drawRect(rect)
        painter.end()
    def out_raw(self, path):
        """
        """
        img = self.wg_img.img_raw[:,:,:3].copy()
        self.wg_img.make_rgb_img(img)
        qimg = self.wg_img.qimg
        # self.paint_grid(qimg)
        save_img(qimg, path+"_raw")
        self.wg_img.switch_imgSVis()
    def out_rgb(self, path):
        """
        """
        img = self.wg_img.img_raw[:,:,:3].copy()
        self.wg_img.make_rgb_img(img)
        qimg = self.wg_img.qimg
        self.paint_grid(qimg)
        save_img(qimg, path+"_rgb")
        self.wg_img.switch_imgSVis()
    def out_k(self, path):
        """
        """
        img = self.wg_img.img_k.copy()
        self.wg_img.make_idx8_img(img, img.max()+1)
        qimg = self.wg_img.qimg
        self.paint_grid(qimg)
        save_img(qimg, path+"_kmeans")
        self.wg_img.switch_imgSVis()
    def out_idx(self, path):
        img = self.wg_img.img_idx.copy()
        self.wg_img.make_gray_img(img)
        qimg = self.wg_img.qimg
        self.paint_grid(qimg)
        save_img(qimg, path+"_index")
        self.wg_img.switch_imgSVis()
    def out_seg(self, path):
        """
        """
        self.wg_img.make_rgb_img(self.wg_img.img_seg)
        qimg = self.wg_img.qimg
        self.paint_grid(qimg)
        save_img(qimg, path+"_seg")
        self.wg_img.switch_imgSVis()
    def out_bin(self, path):
        """
        """
        self.wg_img.make_bin_img(self.wg_img.img_bin)
        qimg = self.wg_img.qimg
        self.paint_grid(qimg)
        save_img(qimg, path+"_kmean")
        self.wg_img.switch_imgSVis()
    def output(self):
        """
        """
        field = self.wg_img.field
        path_out = self.fd_output.text()+"/"+self.fd_project.text()
        '''figure'''
        self.out_raw(path=path_out)
        self.out_rgb(path=path_out)
        self.out_k(path=path_out)
        self.out_idx(path=path_out)
        self.out_seg(path=path_out)
        self.out_bin(path=path_out)
        '''dataframe'''
        df = field.get_DF()
        # NDVI
        idx = field.get_index(ch_1=3, ch_2=0, isContrast=True, name_index="NDVI")
        df = pd.merge(df, idx, on='var', how='left')
        # GNDVI
        idx = field.get_index(ch_1=3, ch_2=1, isContrast=True, name_index="GNDVI")
        df = pd.merge(df, idx, on='var', how='left')
        # NDGI
        idx = field.get_index(ch_1=1, ch_2=0, isContrast=True, name_index="NDGI")
        df = pd.merge(df, idx, on='var', how='left')
        # CNDVI
        idx = field.get_index(ch_1=3, ch_2=0, ch_3=1, isThree=True, name_index="CNDVI")
        df = pd.merge(df, idx, on='var', how='left')
        # RVI
        idx = field.get_index(ch_1=3, ch_2=0, isRatio=True, name_index="RVI")
        df = pd.merge(df, idx, on='var', how='left')
        # GRVI
        idx = field.get_index(ch_1=3, ch_2=1, isRatio=True, name_index="GRVI")
        df = pd.merge(df, idx, on='var', how='left')
        # channels
        for i in range(field.n_ch):
            idx = field.get_index(ch_1=i, isSingle=True, name_index="ch_%d"%i)
            df = pd.merge(df, idx, on='var', how='left')
        # clusters
        idx = field.get_index(ch_1=field.ch_nir, ch_2=field.ch_red, isContrast=True, name_index="CLUSTER_INDEX")
        df = pd.merge(df, idx, on='var', how='left')
        idx = field.get_cluster()
        df = pd.merge(df, idx, on='var', how='left')
        # export
        df.to_csv(path_out+"_data.csv", index=False)

class Widget_Seg(Widget_Img):
    def __init__(self, **params):
        '''
        '''
        super().__init__(params['crop'])
        self.setMouseTracking(True)
        self.task = 1 # 0 none, 1 zoom, 2 panV, 3 panH
        '''attr'''
        # basic
        self.field = Field(**params)
        self.img_raw = self.field.img_raw
        self.img_bin = self.field.img_bin
        self.img_k = self.field.img_k
        # painter
        self.is_fit_width = False
        self.pt_st_img = 0
        self.ratio = 0
        # mouse
        self.agent_click = False
        self.dir = None
        # calculate index image
        ch_1 = self.field.ch_nir
        ch_2 = self.field.ch_red
        self.img_idx = (self.img_raw[:,:,ch_1]-self.img_raw[:,:,ch_2])/(self.img_raw[:,:,ch_1]+self.img_raw[:,:,ch_2]+1e-8).copy()
        self.img_idx = ((self.img_idx)*255).astype(np.uint8)
        # ui
        self.initUI()
    def initUI(self):
        '''generate seg image'''
        img_temp = self.img_bin.reshape(self.img_bin.shape[0], self.img_bin.shape[1], 1)
        self.img_seg = np.multiply(self.img_raw[:,:,:3], img_temp).copy()
        # self.img_seg[(self.img_seg.mean(axis=2)==0), :] = self.img_seg.max()
        self.img_seg[(self.img_seg.mean(axis=2)==0), :] = 255
        self.switch_imgSVis()
        self.show()
    def mouseReleaseEvent(self, event):
        self.agent_click = False
    def mousePressEvent(self, event):
        pos = event.pos()
        for row in range(self.field.nrow):
            for col in range(self.field.ncol):
                agent = self.field.get_agent(row, col)
                rect = agent.get_rect()
                if self.is_fit_width:
                    self.ratio = self.width()/self.qimg.width()
                    rec_agent = QRect(rect.x()*self.ratio, rect.y()*self.ratio+self.pt_st_img, rect.width()*self.ratio, rect.height()*self.ratio)
                else:
                    self.ratio = self.height()/self.qimg.height()
                    rec_agent = QRect(rect.x()*self.ratio+self.pt_st_img, rect.y()*self.ratio, rect.width()*self.ratio, rect.height()*self.ratio)
                if rec_agent.contains(pos):
                    self.agent_click = agent
                    if self.task==1:
                        # zoom and mod border
                        bd_W = rec_agent.x()
                        bd_N = rec_agent.y()
                        bd_E = bd_W + rec_agent.width()
                        bd_S = bd_N + rec_agent.height()
                        dis_W = abs(pos.x()-bd_W)
                        dis_N = abs(pos.y()-bd_N)
                        dis_E = abs(pos.x()-bd_E)
                        dis_S = abs(pos.y()-bd_S)
                        # print("W:%.2f, N:%.2f, E:%.2f, S:%.2f" %(dis_W, dis_N, dis_E, dis_S))
                        dir_idx = np.argmin(np.array([dis_N, dis_W, dis_S, dis_E]))
                        if dir_idx==0:
                            self.dir = Dir.NORTH
                        elif dir_idx==1:
                            self.dir = Dir.WEST
                        elif dir_idx==2:
                            self.dir = Dir.SOUTH
                        elif dir_idx==3:
                            self.dir = Dir.EAST
                    break
        # mag module
        if event.button() == Qt.RightButton:
            self.task = (self.task+1)%4
            print(self.task)
            self.mouseMoveEvent(event)
    def mouseMoveEvent(self, event):
        pos = event.pos()
        # change cursor
        if self.task==0:
            self.setCursor(QCursor(Qt.ArrowCursor))
        elif self.task==1:
            magnifying_glass(self, pos, area=200, zoom=1.5)
        elif self.task==2:
            self.setCursor(QCursor(Qt.SizeVerCursor))
        elif self.task==3:
            self.setCursor(QCursor(Qt.SizeHorCursor))
        # pan
        if (event.button()==Qt.LeftButton)&(self.task>0)&(self.agent_click!=False):
            if self.is_fit_width:
                posX = pos.x()/self.ratio
                posY = (pos.y()-self.pt_st_img)/self.ratio
            else:
                posX = (pos.x()-self.pt_st_img)/self.ratio
                posY = pos.y()/self.ratio
            # adjust border
            if self.task==1:
                if self.dir==Dir.NORTH or self.dir==Dir.SOUTH:
                    value = posY
                elif self.dir==Dir.WEST or self.dir==Dir.EAST:
                    value = posX
                self.agent_click.set_border(self.dir, value)
            # V pan
            elif self.task==2:
                value = posY
                row = self.agent_click.row
                self.field.pan(axis=0, target=row, value=value)
            # H pan
            elif self.task==3:
                value = posX
                col = self.agent_click.col
                self.field.pan(axis=1, target=col, value=value)
        self.repaint()
    def paintEvent(self, paint_event):
        painter = QPainter(self)
        super().paintImage(painter)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        for row in range(self.field.nrow):
            for col in range(self.field.ncol):
                agent = self.field.get_agent(row, col)
                rect = agent.get_rect()
                pt_x, pt_y = agent.get_coordinate()
                if self.is_fit_width:
                    self.ratio = self.width()/self.qimg.width()
                    rec_agent = QRect(rect.x()*self.ratio, rect.y()*self.ratio+self.pt_st_img, rect.width()*self.ratio, rect.height()*self.ratio)
                    draw_cross(pt_x*self.ratio, pt_y*self.ratio+self.pt_st_img, painter)
                else:
                    self.ratio = self.height()/self.qimg.height()
                    rec_agent = QRect(rect.x()*self.ratio+self.pt_st_img, rect.y()*self.ratio, rect.width()*self.ratio, rect.height()*self.ratio)
                    draw_cross(pt_x*self.ratio+self.pt_st_img, pt_y*self.ratio, painter)
                painter.drawRect(rec_agent)
        painter.end()
    def switch_imgVis(self):
        super().make_rgb_img(self.img_vis)
        self.repaint()
    def switch_imgSVis(self):
        super().make_rgb_img(self.img_seg)
        self.repaint()
    def auto_seg(self, coef_grid=0):
        self.field.cpu_bound(coef_grid=coef_grid)
        self.repaint()
    def fix_seg(self, width, length):
        self.field.fix_bound(width=width, length=length)
        self.repaint()
    def align(self, method, axis=0):
        self.field.align(method=method, axis=axis)
        self.repaint()
    def distributed(self, axis=0, isEven=False):
        self.field.distributed(axis=axis, isEven=isEven)
        self.repaint()

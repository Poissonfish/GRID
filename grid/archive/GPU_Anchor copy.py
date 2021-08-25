import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .Misc import *

class Panel_Anchor(QWidget):
    def __init__(self, img, map):
        super().__init__()
        self.setMouseTracking(True)
        self.zoom = 1
        '''attr'''
        # mouse
        self.idx_click = -1
        self.pos_temp = QPoint(0, 0)
        self.state_hand = False
        self.cursor = QCursor(Qt.ArrowCursor)
        # size/rec
        self.size_self = QSize(0, 0)
        self.size_imgPan = QSize(0, 0)
        self.size_img = QSize(0, 0)
        # anchor
        self.acr_c, self.acr_c_raw = 0, 0 # ratio
        self.acr_r, self.acr_r_raw = 0, 0 # ratio 
        self.rec_acr_c = QRect(0, 0, 0, 0)
        self.rec_acr_r = QRect(0, 0, 0, 0)
        self.x_acr_c, self.y_acr_c = 0, 0 # px in the plot
        self.x_acr_r, self.y_acr_r = 0, 0 # px in the plot
        # image
        self.img = img
        self.map = map
        self.imgH = self.img.shape[0]
        self.imgW = self.img.shape[1]
        self.margin = 70
        self.space = 5
        self.rec_img = QRect(QPoint(0, 0), QSize(0, 0))
        # button
        self.gr_button = QGroupBox("Options")
        self.lo_button = QGridLayout()
        self.bt_evenH = QCheckBox("Evenly Distributed (X)")
        self.bt_evenV = QCheckBox("Evenly Distributed (Y)")
        self.bt_reset = QPushButton("Reset")
        '''get peaks'''
        acr_r_temp, _ = get_peak(img=self.img, map=self.map, axis=0)
        acr_c_temp, _ = get_peak(img=self.img, map=self.map, axis=1)
        self.acr_r = scaleTo0and1(acr_r_temp, self.imgH)
        self.acr_c = scaleTo0and1(acr_c_temp, self.imgW)
        self.acr_r_raw = self.acr_r.copy()
        self.acr_c_raw = self.acr_c.copy()
        '''UI'''
        self.initUI()

    def initUI(self):
        '''mouse'''
        '''image'''
        qImg = QImage(self.img, self.imgW, self.imgH, self.imgW*1, QImage.Format_Indexed8)
        qImg.setColor(0, qRgb(0, 0, 0))
        qImg.setColor(1, qRgb(241, 225, 29))
        self.qimg = QPixmap(qImg)
        '''button'''
        self.bt_reset.clicked.connect(self.reset_Anchors)
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.bt_reset)
        box_bt = QHBoxLayout()
        box_bt.addStretch(1)
        box_bt.addLayout(vbox)
        self.setLayout(box_bt)
        self.show()

    def mousePressEvent(self, event):
        pos = event.pos()
        self.pos_temp = QPoint(pos.x(), pos.y())
        if self.rec_acr_c.contains(pos):
            self.idx_click = (np.abs(self.x_acr_c-pos.x())).argmin()
            if event.button() == Qt.RightButton:
                self.acr_c = np.delete(self.acr_c, self.idx_click)
        elif self.rec_acr_r.contains(pos):
            self.idx_click = (np.abs(self.y_acr_r-pos.y())).argmin()
            if event.button() == Qt.RightButton:
                self.acr_r = np.delete(self.acr_r, self.idx_click)
        elif event.button() == Qt.RightButton:
            # mag module
            self.zoom = (self.zoom+1)%3
            self.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        # add new anchors
        if (pos.x()==self.pos_temp.x())&(pos.y()==self.pos_temp.y())&(event.button()==Qt.LeftButton):
            if self.rec_acr_c.contains(pos):
                correct = 0 if self.is_fit_width else self.pt_st_img
                new_acr_c = (pos.x()-correct)/(self.size_img.width())
                self.acr_c = np.append(self.acr_c, new_acr_c)
            elif self.rec_acr_r.contains(pos):
                correct = self.pt_st_img if self.is_fit_width else 0
                new_acr_r = (pos.y()-correct)/(self.size_img.height())
                self.acr_r = np.append(self.acr_r, new_acr_r)
        self.repaint()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        correctX = 0 if self.is_fit_width else self.pt_st_img
        correctY = self.pt_st_img if self.is_fit_width else 0
        if event.buttons() == Qt.LeftButton:
            if self.rec_acr_c.contains(pos):
                self.acr_c[self.idx_click] = (pos.x()-correctX)/self.size_img.width()
            elif self.rec_acr_r.contains(pos):
                self.acr_r[self.idx_click] = (pos.y()-correctY)/self.size_img.height()
            self.repaint()
        if (self.rec_acr_c.contains(pos)) or (self.rec_acr_r.contains(pos)):
            self.cursor = QCursor(Qt.PointingHandCursor)
            self.setCursor(self.cursor)
        elif self.rec_img.contains(pos):
            # mag module
            if self.zoom!=0:
                magnifying_glass(self, pos, area=200, zoom=self.zoom*1.5)
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def evenH(self):
        if self.bt_evenH.isChecked():
            size = len(self.acr_c)
            space = 0.02
            length = 1-(space*2)
            self.acr_c = np.arange(space, 1-space, length/size)
        else:
            self.acr_c = self.acr_c_raw
        self.repaint()

    def evenV(self):
        if self.bt_evenV.isChecked():
            size = len(self.acr_r)
            space = 0.02
            length = 1-(space*2)
            self.acr_r = np.arange(space, 1-space, length/size)
        else:
            self.acr_r = self.acr_r_raw
        self.repaint()

    def reset_Anchors(self):
        self.acr_c = self.acr_c_raw
        self.acr_r = self.acr_r_raw
        self.repaint()

    def paintEvent(self, paint_event):
        '''painter'''
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.red)
        '''sort array'''
        self.acr_c = np.sort(self.acr_c)
        self.acr_r = np.sort(self.acr_r)
        '''size info'''
        self.size_self = self.rect().size()
        self.size_imgPan = QSize(self.size_self.width()-self.margin, self.size_self.height()-self.margin)
        self.size_img = self.qimg.size().scaled(self.size_imgPan, Qt.KeepAspectRatio)
        '''Check the image side'''
        if self.size_img.width()==self.size_imgPan.width():
            '''image'''
            self.is_fit_width = True
            self.pt_st_img = int((self.size_imgPan.height()-self.size_img.height())/2)
            painter.drawPixmap(0, self.pt_st_img, self.size_img.width(), self.size_img.height(), self.qimg)
            '''anchor X'''
            self.x_acr_c = (self.acr_c*self.size_img.width()).astype(np.int)
            self.y_acr_c = self.pt_st_img+self.size_img.height()+(self.margin/5)
            '''anchor Y'''
            self.x_acr_r = self.size_self.width()-(self.margin*4/5)
            self.y_acr_r = (self.acr_r*self.size_img.height()+self.pt_st_img).astype(np.int)
            '''rect'''
            self.rec_acr_c = QRect(0, self.pt_st_img+self.size_img.height()+self.space, self.size_img.width(), self.margin)
            self.rec_acr_r = QRect(self.size_img.width()+self.space, self.pt_st_img, self.margin, self.size_img.height())
            self.rec_img = QRect(QPoint(0, self.pt_st_img), self.size_img)
        elif self.size_img.height()==self.size_imgPan.height():
            '''image'''
            self.is_fit_width = False
            self.pt_st_img = int((self.size_imgPan.width()-self.size_img.width())/2)
            painter.drawPixmap(self.pt_st_img, 0, self.size_img.width(), self.size_img.height(), self.qimg)
            '''anchor X'''
            self.x_acr_c = (self.acr_c*self.size_img.width()+self.pt_st_img).astype(np.int)
            self.y_acr_c = self.size_self.height()-(self.margin*4/5)
            '''anchor Y'''
            self.x_acr_r = self.pt_st_img+self.size_img.width()+(self.margin/5)
            self.y_acr_r = (self.acr_r*self.size_img.height()).astype(np.int)
            '''rect'''
            self.rec_acr_c = QRect(self.pt_st_img, self.size_img.height()+self.space, self.size_img.width(), self.margin-5)
            self.rec_acr_r = QRect(self.pt_st_img+self.size_img.width()+self.space, 0, self.margin-5, self.size_img.height())
            self.rec_img = QRect(QPoint(self.pt_st_img, 0), self.size_img)
        '''anchor'''
        # side
        for posX in self.x_acr_c:
            draw_triangle(posX, self.y_acr_c+self.space, "North", painter)
        for posY in self.y_acr_r:
            draw_triangle(self.x_acr_r+self.space, posY, "West", painter)
        # image
        pen.setWidth(3)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        painter.setBrush(Qt.white)
        for posX in self.x_acr_c:
            for posY in self.y_acr_r:
                draw_cross(posX, posY, painter)
        '''rect'''
        pen.setWidth(1)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(Qt.transparent)
        painter.drawRect(self.rec_acr_c)
        painter.drawRect(self.rec_acr_r)
        '''test'''
        # print("========")
        # print(self.is_fit_width)
        # print(self.x_acr_c)
        # print(self.y_acr_c)
        # print(self.x_acr_r)
        # print(self.y_acr_r)
        # print("========")
        
    def get_anchors(self):
        imgW = self.qimg.size().width()
        imgH = self.qimg.size().height()
        anchor_x_org = scaleToOrig(self.acr_c, imgW)
        anchor_y_org = scaleToOrig(self.acr_r, imgH)
        list = []
        for posY in anchor_y_org:
            for posX in anchor_x_org:
                list.append(dict(x=posX, y=posY))
        return list, len(self.acr_c), len(self.acr_r)


def scaleTo0and1(array, length):
    array = np.array(array)
    return (array-0)/(length-0)

def scaleToOrig(array, length):
    array = np.array(array)
    return array*(length-0)+0

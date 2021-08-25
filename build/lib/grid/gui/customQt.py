# basic imports
import numpy as np
import sys

# 3-rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self import
from ..lib import *


class Widget_Img(QWidget):
    '''
    Will keep imgRaw, imgVis and imgQmap
    '''

    def __init__(self):
        super().__init__()
        '''attr'''
        # self.img_raw = img
        # self.img_vis = img[:, :, :3].copy()
        self.qimg = None
        self.isFitWidth = None
        self.rgX, self.rgY = (0, 0), (0, 0)
        self.sizeImg = (0, 0)

    def make_rgb_img(self, img):
        self.qimg = getRGBQImg(img[:, :, :3])
        self.updateDim()

    def make_bin_img(self, img):
        self.qimg = getBinQImg(img)
        self.updateDim()

    def make_idx8_img(self, img, k):
        self.qimg = getIdx8QImg(img, k)
        self.updateDim()

    def make_gray_img(self, img):
        self.qimg = getGrayQImg(img)
        self.updateDim()

    def updateDim(self):
        self.sizeImg = self.qimg.size().scaled(self.rect().size(),
                                               Qt.KeepAspectRatio)
        if self.sizeImg.width() == self.width():
            self.isFitWidth = True
            marginY = int((self.height()-self.sizeImg.height())/2)
            self.rgX = (0, self.sizeImg.width())
            self.rgY = (marginY, marginY+self.sizeImg.height())
        elif self.sizeImg.height() == self.height():
            self.isFitWidth = False
            marginX = int((self.width()-self.sizeImg.width())/2)
            self.rgX = (marginX, marginX+self.sizeImg.width())
            self.rgY = (0, self.sizeImg.height())

    def isInRange(self, x, y):
        if x >= self.rgX[0] and x <= self.rgX[1] and\
           y >= self.rgY[0] and y <= self.rgY[1]:
            return True
        else:
            return False

    def getImgRange(self):
        return self.rgX, self.rgY

    def paintImage(self, painter):
        painter.setRenderHint(QPainter.Antialiasing, True)
        self.updateDim()
        painter.drawPixmap(self.rgX[0], self.rgY[0], self.sizeImg.width(),
                           self.sizeImg.height(), self.qimg)


def getRGBQImg(img):
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w, h, w*3, QImage.Format_RGB888)
    return QPixmap(qImg)


def getBinQImg(img):
     h, w = img.shape[0], img.shape[1]
     qImg = QImage(img.astype(np.uint8).copy(), w, h, w*1, QImage.Format_Indexed8)
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
    qImg = QImage(img.astype(np.uint8).copy(), w, h, w*1, QImage.Format_Indexed8)
    for i in range(k):
        qImg.setColor(i, colormap[i])
    return QPixmap(qImg)


def getGrayQImg(img):
    h, w = img.shape[0], img.shape[1]
    qImg = QImage(img.astype(np.uint8).copy(), w, h, w*1, QImage.Format_Grayscale8)
    return QPixmap(qImg)


def magnifying_glass(widget, pos, area=200, zoom=4):
    size = int(area/zoom)
    pixmap = widget.grab(
        QRect(QPoint(pos.x()-int(size/2), pos.y()-int(size/2)), QSize(size, size)))
    try:
        rate_screen = size / pixmap.width()
        pixmap = pixmap.scaled(int(area/rate_screen), int(area/rate_screen))
        painter = QPainter(pixmap)
        'Rect'
        pen = QPen()
        pen.setWidth(2)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        # define rect
        rect = QRect(QPoint(0, 0), pixmap.size()*rate_screen)
        # draw rect
        painter.drawRect(rect)
        '''Cursor'''
        pen.setWidth(2)
        pen.setColor(Qt.red)
        painter.setPen(pen)
        size_m = 10
        space = 4
        # define lines
        line1 = QLine(QPoint(size_m, 0), QPoint(space, 0))
        line2 = QLine(QPoint(0, size_m), QPoint(0, space))
        line3 = QLine(QPoint(0, -space), QPoint(0, -size_m))
        line4 = QLine(QPoint(-size_m, 0), QPoint(-space, 0))
        line1.translate(pixmap.rect().center() * rate_screen - QPoint(0, 0))
        line2.translate(pixmap.rect().center() * rate_screen - QPoint(0, 0))
        line3.translate(pixmap.rect().center() * rate_screen - QPoint(0, 0))
        line4.translate(pixmap.rect().center() * rate_screen - QPoint(0, 0))
        # draw lines
        painter.drawLine(line1)
        painter.drawLine(line2)
        painter.drawLine(line3)
        painter.drawLine(line4)

        # # remove central
        # pt_center = pixmap.rect().center() * rate_screen
        # x, y = pt_center.x(), pt_center.y()
        # painter.eraseRect(QRect(x-2, y-2, 4, 4))
        '''finish'''
        painter.end()
        cursor = QCursor(pixmap)
        widget.setCursor(cursor)
    except Exception:
        '''not in a valid region'''


def drawCross(x, y, painter, size=2):
    l1_st_x, l1_st_y = x-size, y-size
    l1_ed_x, l1_ed_y = x+size, y+size
    l2_st_x, l2_st_y = x-size, y+size
    l2_ed_x, l2_ed_y = x+size, y-size
    painter.drawLine(l1_st_x, l1_st_y, l1_ed_x, l1_ed_y)
    painter.drawLine(l2_st_x, l2_st_y, l2_ed_x, l2_ed_y)


def drawTriangle(x, y, dir, painter, range=7, peak=30):
    path = QPainterPath()
    path.moveTo(x, y)
    if dir == 'North':
        path.lineTo(x-range, y+peak)
        path.lineTo(x+range, y+peak)
    elif dir == 'South':
        path.lineTo(x-range, y-peak)
        path.lineTo(x+range, y-peak)
    elif dir == 'West':
        path.lineTo(x+peak, y-range)
        path.lineTo(x+peak, y+range)
    elif dir == 'East':
        path.lineTo(x-peak, y-range)
        path.lineTo(x-peak, y+range)
    path.lineTo(x, y)
    painter.drawPath(path)

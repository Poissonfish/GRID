# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from ..lib import *
from ..grid import *
from .customQt import * 


class PnCropper(QGroupBox):
    """
    """

    def __init__(self, grid):
        """
        """

        super().__init__()
        self.setStyleSheet("""
        QGroupBox::title{
            subcontrol-origin: margin;
            subcontrol-position: top center;
        }
        """)

        # attr.
        self.grid = grid
        self.layout = QVBoxLayout()
        self.wgImg = Widget_ViewCrop(grid, self.grid.imgs.get('raw'))
        self.initUI()

    def initUI(self):
        """
        """

        self.layout.addWidget(self.wgImg)
        self.setLayout(self.layout)
        self.show()

    def run(self):
        """
        """
        self.grid.cropImg(pts=self.wgImg.getPinnedPoints())


class Widget_ViewCrop(Widget_Img):

    def __init__(self, grid, img):
        super().__init__()
        self.setMouseTracking(True)
        self.grid = grid
        self.img_vis = img
        self.pos_move_prev = None
        self.pos_move = None
        self.pos_press = None
        self.pos_release = None
        self.zoom = 1
        self.ratio = 1
        self.pts = []
        self.pts_prev = [] # for rotation
        self.n_marks = 0
        self.imgH, self.imgW = img.shape[0], img.shape[1]

        # mouse event
        self.hasDrag = 0
        self.isDragDefine = 0 # is dragging to define rectangle
        self.isDragSize = 0 # is resizing?
        self.sen_resize = 30
        self.sen_rotate = 150
        self.whichState = -1
        '''
        0   4   1
           ___
        7 | 8 | 5
          |___|
        3   6   2

        9 : rotate
        '''
        #

        self.initUI()

    def initUI(self):
        super().make_rgb_img(self.img_vis)
        self.show()

    def paintEvent(self, paint_event):
        painter = QPainter(self)
        super().paintImage(painter)

        painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        # painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
        painter.setBrush(QBrush(Qt.red, Qt.Dense7Pattern))

        if self.hasDrag:
            # has drawn points
            points = QPolygon([QPoint(self.pts[i][0], self.pts[i][1])
                              for i in range(4)])
            painter.drawPolygon(points)
        else:
            if len(self.pts) == 1:
                painter.drawLine(QPoint(self.pts[0][0], self.pts[0][1]),
                                 QPoint(self.pos_move[0], self.pos_move[1]))
            elif len(self.pts) == 2:
                points = QPolygon([QPoint(self.pts[0][0], self.pts[0][1]),
                                   QPoint(self.pts[1][0], self.pts[1][1]), 
                                   QPoint(self.pos_move[0], self.pos_move[1])])
                painter.drawPolygon(points)
            elif len(self.pts) == 3:
                points = QPolygon([QPoint(self.pts[0][0], self.pts[0][1]),
                                   QPoint(self.pts[1][0], self.pts[1][1]),
                                   QPoint(self.pts[2][0], self.pts[2][1]),
                                   QPoint(self.pos_move[0], self.pos_move[1])])
                painter.drawPolygon(points)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Drag to define area
            self.pos_press = (event.pos().x(), event.pos().y())
            self.pos_move_prev = self.pos_press

            if self.whichState == -1:
                # define AOI
                if len(self.pts) < 4:
                    # insert point to incomplete AOI
                    self.pts.append(self.pos_press)
                else:
                    # create new AOI
                    self.pts = [self.pos_press]
                self.hasDrag = 1 if len(self.pts) == 4 else 0
            else:
                self.isDragSize = 1
        elif event.button() == Qt.RightButton:
            # magnifier
            self.zoom = (self.zoom + 1) % 3
            self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        self.pos_move = (event.pos().x(), event.pos().y())

        if not self.isDragSize and self.hasDrag and len(self.pts) == 4:
            '''
            hover around when the rectangle exists
            '''

            # check distance of each corner
            dist_corner = [euclidean(self.pos_move, self.pts[i])
                           for i in range(4)]

            # check distance for each side
            len_n = euclidean(self.pts[0], self.pts[1])
            len_e = euclidean(self.pts[1], self.pts[2])
            len_s = euclidean(self.pts[2], self.pts[3])
            len_w = euclidean(self.pts[3], self.pts[0])

            dist_side_n = sum(np.array(dist_corner)[[0, 1]]) - len_n
            dist_side_e = sum(np.array(dist_corner)[[1, 2]]) - len_e
            dist_side_s = sum(np.array(dist_corner)[[2, 3]]) - len_s
            dist_side_w = sum(np.array(dist_corner)[[3, 0]]) - len_w

            dist_side = [dist_side_n, dist_side_e,
                         dist_side_s, dist_side_w]

            # concatenate the distances
            dist_all = dist_corner + dist_side

            # find the minimum distance
            idx_corner = np.argmin(dist_corner)
            idx_side = np.argmin(dist_side)
            min_all = dist_all[np.argmin(dist_all)]
            min_cor = dist_corner[idx_corner]
            min_sid = dist_side[idx_side]

            # check conditions
            if min_cor <= self.sen_resize:
                # move corner
                self.whichState = idx_corner
            elif min_sid <= self.sen_resize:
                # move side
                self.whichState = idx_side + 4
            elif cv2.pointPolygonTest(self.pts, self.pos_move, True) > 0:
                # move whole
                self.whichState = 8
            elif min_all > self.sen_resize and min_all <= self.sen_rotate:
                # roate
                self.whichState = 9
            else:
                # do nothing
                self.whichState = -1

        elif self.isDragSize:
            '''
            Draging to resize
            '''

            # capture delta
            dx = self.pos_move[0] - self.pos_move_prev[0]
            dy = self.pos_move[1] - self.pos_move_prev[1]

            # check each status
            if self.whichState <= 3:
                # update corner
                self.pts[self.whichState][0] += dx
                self.pts[self.whichState][1] += dy
            elif self.whichState > 3 and self.whichState < 8:
                if self.whichState == 4:
                    # update side N
                    idx1, idx2 = 0, 1
                elif self.whichState == 5:
                    # update side E
                    idx1, idx2 = 1, 2
                elif self.whichState == 6:
                    # update side S
                    idx1, idx2 = 2, 3
                elif self.whichState == 7:
                    # update side W
                    idx1, idx2 = 3, 0
                for i in [idx1, idx2]:
                    self.pts[i][0] += dx
                    self.pts[i][1] += dy
            elif self.whichState == 8:
                # update whole
                for i in range(4):
                    self.pts[i][0] += dx
                    self.pts[i][1] += dy
            elif self.whichState == 9:
                # rotate
                org = np.mean(self.pts_prev, axis=0)
                v_prev = self.pos_press - org
                v_cur = self.pos_move - org
                angle = find_angle(v_prev, v_cur)
                self.pts = np.array(
                    rotatePts(self.pts_prev, angle, org), dtype=int).copy()

        # cursor
        magArea = int(min(self.rgX[1] - self.rgX[0], self.rgY[1] - self.rgY[0]) / 5)
        if self.whichState < 8:
            if self.zoom != 0:
                magnifying_glass(self, event.pos(),
                                area=magArea, zoom=self.zoom * 2.5)
            else:
                self.setCursor(QCursor(Qt.ClosedHandCursor))
        elif self.whichState == 8:
            self.setCursor(QCursor(Qt.SizeAllCursor))
        elif self.whichState == 9:
            size = 32
            pixmap = QPixmap(os.path.join(
                self.grid.user.dirGrid, "res/rotate.png")).scaled(size, size)
            self.setCursor(QCursor(pixmap))

        self.pos_move_prev = self.pos_move
        self.repaint()

    def mouseReleaseEvent(self, event):
        # pt_mouse = event.pos()

        # update points order while moving
        if self.hasDrag:
            self.pts = sortPts(self.pts)
            self.pts_prev = self.pts.copy()

        self.resetStatus()

    def getPinnedPoints(self):
        self.ratio = (self.imgW) / (self.width()) if self.isFitWidth else (self.imgH) / (self.height())
        pts = [[(pt[0] - self.rgX[0]) * (self.ratio),
                (pt[1] - self.rgY[0]) * (self.ratio)] for pt in self.pts]
        if len(pts) < 4:
            pts = [[0, 0], [self.imgW, 0],
                   [self.imgW, self.imgH], [0, self.imgH]]
        return pts

    def resetStatus(self):
        self.isDragDefine = 0
        self.isDragSize = 0


# def getPerpDist(pt1, pt2, pt0):
#     """
#     Find the perpendicular distance from a point (pt0) to aline (pt1, pt2)
#     """
#     slp = (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])

#     if not np.isinf(slp):
#         itc = pt1[1] - (slp * pt1[0])
#         # ax + by + c = 0
#         a = slp
#         b = -1
#         c = itc

#         # numerator
#         num = abs(a * pt0[0] + b * pt0[1] + c)
#         # denominator
#         den = np.sqrt(a ** 2 + b ** 2)

#         # return
#         return num / den
#     else:
#         # if is a vertical line
#         return abs(pt0[0] - pt1[0])


# def getShiftPts(pt1, pt2, pt0):
#     """
#     Find the updated point (pt1*, pt2*) from a new line defined by point (pt0)
#     eq: ax + by = c
#     """
#     slp = (pt1[1] - pt2[1]) / (pt1[0] - pt2[0])
    
#     if slp == 0:
#         # horizon line
#         return [pt1[0], pt0[1]], [pt2[0], pt0[1]]
#     elif np.isinf(slp):
#         # vertical line
#         return [pt0[0], pt1[1]], [pt0[0], pt2[1]]

#     else:
#         itc = pt0[1] - slp * pt0[0]
#         eq = (slp, -1, -itc)  # ax + by = c

#         # find the perpendicular slope
#         slp_perp = - 1 / slp

#         # find the interaction
#         # solve via
#         # a1x + b1y = c1
#         # a2x + b2y = c2
#         itc_1 = pt1[1] - slp_perp * pt1[0]
#         eq_1 = (slp_perp, -1, -itc_1)
#         pt1_new = np.linalg.solve(np.array([[eq[0], eq[1]],  # a
#                                             [eq_1[0], eq_1[1]]]),  # b
#                                 np.array([eq[2], eq_1[2]]))  # c

#         itc_2 = pt2[1] - slp_perp * pt2[0]
#         eq_2 = (slp_perp, -1, -itc_2)
#         pt2_new = np.linalg.solve(np.array([[eq[0], eq[1]],  # a
#                                             [eq_2[0], eq_2[1]]]),  # b
#                                 np.array([eq[2], eq_2[2]]))  # c

#         # return
#         return pt1_new, pt2_new

# getShiftPts([0, 6], [4, 9], [0, 9])
# getShiftPts([1, 3], [5, 3], [4, 6])
# np.linalg.solve(np.array([[3, 2], [5, 2]]),
#                 np.array([1, 3]))

        

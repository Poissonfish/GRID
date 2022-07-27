# 3rd party imports
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# self imports
from ..grid import *

class PnInputer(QWidget):
    """
    """
    def __init__(self, grid):
        """
        """

        super().__init__()
        self.grid = grid
        # user define
        self.gr_user = QGroupBox("User's Input (You can drag and drop files)")
        self.lo_user = QGridLayout()
        self.lb_img = QLabel()
        self.lb_map = QLabel()
        self.lb_shp = QLabel()
        self.fd_img = DnDLineEdit()
        self.fd_map = DnDLineEdit()
        self.fd_shp = DnDLineEdit()
        self.bt_img = QPushButton()
        self.bt_map = QPushButton()
        self.bt_shp = QPushButton()
        # demo
        self.gr_demo = QGroupBox("Demo")
        self.lo_demo = QVBoxLayout()
        self.lb_demo = QLabel(
            "Will use sample files to demo the program. Or go to <a href='https://poissonfish.github.io/GRID/index.html'> User Manual </a>")
        self.lb_demo.setOpenExternalLinks(True)

        # self
        self.layout = QVBoxLayout()

        self.initUI()

    def initUI(self):
        """
        """

        # USER
        ## GUI components
        self.gr_user.setCheckable(True)
        self.gr_user.setChecked(False)
        self.gr_user.clicked.connect(lambda: self.toggle(self.gr_user))
        self.lb_img.setText("Image (.tif, .jpg, .png):")
        self.lb_map.setText("Map (.csv) (OPTIONAL):")
        self.lb_shp.setText("Shape (.shp) (OPTIONAL):")
        font = self.fd_img.font()
        font.setPointSize(25)
        fm = QFontMetrics(font)
        self.fd_img.setFixedHeight(fm.height())
        self.fd_map.setFixedHeight(fm.height())
        self.fd_shp.setFixedHeight(fm.height())
        self.bt_img.setText("Browse")
        self.bt_img.clicked.connect(self.assign_PathImg)
        self.bt_map.setText("Browse")
        self.bt_map.clicked.connect(self.assign_PathMap)
        self.bt_shp.setText("Browse")
        self.bt_shp.clicked.connect(self.assign_PathShp)
        ## layout
        self.lo_user.addWidget(self.lb_img, 0, 0)
        self.lo_user.addWidget(self.fd_img, 0, 1)
        self.lo_user.addWidget(self.bt_img, 0, 2)
        self.lo_user.addWidget(self.lb_map, 1, 0)
        self.lo_user.addWidget(self.fd_map, 1, 1)
        self.lo_user.addWidget(self.bt_map, 1, 2)
        self.lo_user.addWidget(self.lb_shp, 2, 0)
        self.lo_user.addWidget(self.fd_shp, 2, 1)
        self.lo_user.addWidget(self.bt_shp, 2, 2)
        self.gr_user.setLayout(self.lo_user)

        # DEMO
        ## GUI components
        self.gr_demo.setCheckable(True)
        self.gr_demo.setChecked(True)
        self.gr_demo.clicked.connect(lambda: self.toggle(self.gr_demo))
        ## layout
        self.lo_demo.addWidget(self.lb_demo)
        self.gr_demo.setLayout(self.lo_demo)

        # LAYOUT
        self.layout.setContentsMargins(200, 50, 200, 50)
        self.layout.addWidget(self.gr_user)
        self.layout.addWidget(self.gr_demo)

        # FINALIZE
        self.setLayout(self.layout)
        self.show()

    def toggle(self, groupbox):
        """
        """

        if (groupbox.title() == "Demo"):
            self.gr_user.setChecked(not self.gr_user.isChecked())
        elif (groupbox.title() != "Demo"):
            self.gr_demo.setChecked(not self.gr_demo.isChecked())

    def assign_PathImg(self):
        """
        """

        fileter = "Images (*.tif *.jpg *.jpeg *.png)"
        path = QFileDialog().getOpenFileName(self, "", "", fileter)[0]
        self.fd_img.setText(path)

    def assign_PathMap(self):
        """
        """

        fileter = "Map (*.csv *.txt)"
        path = QFileDialog().getOpenFileName(self, "", "", fileter)[0]
        self.fd_map.setText(path)

    def assign_PathShp(self):
        """
        """

        fileter = "Shape (*.shp)"
        path = QFileDialog().getOpenFileName(self, "", "", fileter)[0]
        self.fd_shp.setText(path)

    def run(self):
        """
        """
        if self.gr_user.isChecked():
            self.grid.loadData(pathImg=self.fd_img.text(),
                               pathMap=self.fd_map.text(),
                               pathShp=self.fd_shp.text())
        else:
            self.grid.loadData()  # load demo files


class DnDLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
            text = ""
            for url in event.mimeData().urls():
                text = str(url.toLocalFile())
            self.setText(text)
        else:
            event.ignore()

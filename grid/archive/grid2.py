import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from .CPU_Agent import *
from .CPU_Field import *
from .GPU_Input import *
from .GPU_Cropper import *
from .GPU_Kmeaner import *
from .GPU_Anchor import *
from .GPU_Output import *

class GRID(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
        QWidget {\
            font: 20pt Trebuchet MS
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
        '''attr'''
        # GUI components
        self.pn_content = QWidget()
        self.pn_main = QStackedWidget()
        self.pn_navi = QWidget()
        self.bt_next = QPushButton()
        self.bt_back = QPushButton()
        self.Layout = None
        # params
        self.params = dict()
        # image-related
        self.img_raw = None
        self.img_crop = None
        self.img_bin = None
        self.k_center = None
        # info-=-
        self.title = "GRID"
        self.width = 1440
        self.height = 900
        '''initialize UI'''
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setMinimumSize(self.width, self.height)
        '''first input'''
        self.show_input()
        '''set up windows'''
        center = QApplication.desktop().availableGeometry().center()
        rect = self.geometry()
        rect.moveCenter(center)
        self.setGeometry(rect)
    def show_input(self, isNewImg=True):
        '''input panel'''
        if isNewImg:
            self.pn_main.addWidget(Panel_Input())
        else:
            self.pn_main.removeWidget(self.pn_main.widget(Panels.CROPPER.value))
        self.pn_main.setCurrentIndex(Panels.INPUT.value)
        '''navigation bar'''
        self.assemble_navigation(name_next="Load Files ->", oneSide=True)
        self.bt_next.clicked.connect(lambda: self.show_cropper(isNewImg=True))
        '''finalize'''
        self.assemble_and_show()
    def show_cropper(self, isNewImg=True):
        '''input panel'''
        if isNewImg:
            self.params['raw'], self.params['map'] = self.pn_main.widget(Panels.INPUT.value).get_img()
            self.pn_main.addWidget(Panel_Cropper(np_img=self.params['raw']))
        else:
            self.pn_main.removeWidget(self.pn_main.widget(Panels.KMEANER.value))
        self.pn_main.setCurrentIndex(Panels.CROPPER.value)
        '''navigation bar'''
        self.assemble_navigation()
        self.bt_back.clicked.connect(lambda: self.show_input(isNewImg=False))
        self.bt_next.clicked.connect(lambda: self.show_kmeaner(isNewImg=True))
        '''finalize'''
        self.assemble_and_show()
    def show_kmeaner(self, isNewImg=True):
        '''input panel'''
        if isNewImg:
            self.params['crop'] = self.pn_main.widget(Panels.CROPPER.value).get_img()
            self.pn_main.addWidget(Panel_Kmeaner(np_img=self.params['crop']))
        else:
            self.pn_main.removeWidget(self.pn_main.widget(Panels.ANCHOR.value))
        self.pn_main.setCurrentIndex(Panels.KMEANER.value)
        '''navigation bar'''
        self.assemble_navigation()
        self.bt_back.clicked.connect(lambda: self.show_cropper(isNewImg=False))
        self.bt_next.clicked.connect(lambda: self.show_anchor(isNewImg=True))
        '''finalize'''
        self.assemble_and_show()
    def show_anchor(self, isNewImg=True):
        '''input panel'''
        if isNewImg:
            self.params['crop'], self.params['k'], self.params['bin'], self.params['ch_nir'], self.params['ch_red'], self.params['ls_bin'] = self.pn_main.widget(Panels.KMEANER.value).get_img()
            self.pn_main.addWidget(Panel_Anchor(img=self.params['bin'], map=self.params['map']))
        else:
            self.pn_main.removeWidget(self.pn_main.widget(Panels.OUTPUT.value))
        self.pn_main.setCurrentIndex(Panels.ANCHOR.value)
        '''navigation bar'''
        self.assemble_navigation()
        self.bt_back.clicked.connect(lambda: self.show_kmeaner(isNewImg=False))
        self.bt_next.clicked.connect(lambda: self.show_output(isNewImg=True))
        '''finalize'''
        self.assemble_and_show()
    def show_output(self, isNewImg=True):
        '''input panel'''
        if isNewImg:
            self.params['anchors'], self.params['nc'], self.params['nr'] = self.pn_main.widget(Panels.ANCHOR.value).get_anchors()
            self.pn_main.addWidget(Panel_Output(**self.params))
        self.pn_main.setCurrentIndex(Panels.OUTPUT.value)
        # test
        self.test()
        # test
        '''navigation bar'''
        self.assemble_navigation(name_next="Finish")
        self.bt_back.clicked.connect(lambda: self.show_anchor(isNewImg=False))
        self.bt_next.clicked.connect(self.finish)
        '''finalize'''
        self.assemble_and_show()
    def finish(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText("Start another job?")
        msgBox.setWindowTitle("Finish")
        msgBox.setStandardButtons(QMessageBox.Cancel | QMessageBox.Yes | QMessageBox.Save)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Yes:
            self.pn_main.widget(Panels.OUTPUT.value).output()
            self.show_input()
        elif returnValue == QMessageBox.Save:
            self.pn_main.widget(Panels.OUTPUT.value).output()
            self.show_output(isNewImg=False)
    def assemble_navigation(self, name_next="Next ->", name_back="<- Back", oneSide=False):
        self.pn_navi = QWidget()
        self.bt_next = QPushButton(name_next)
        self.bt_back = QPushButton(name_back)
        layout_navi = QHBoxLayout()
        if oneSide:
            layout_navi.addStretch(1)
        else:
            layout_navi.addWidget(self.bt_back)
        layout_navi.addWidget(self.bt_next)
        self.pn_navi.setLayout(layout_navi)
    def assemble_and_show(self):
        self.Layout = QVBoxLayout()
        self.Layout.addWidget(self.pn_main, Qt.AlignCenter)
        self.Layout.addWidget(self.pn_navi)
        self.pn_content = QWidget()
        self.pn_content.setLayout(self.Layout)
        self.setCentralWidget(self.pn_content)
        self.show()
    def test(self):
        import json
        with open('anchors', 'w') as fout:
            json.dump(self.params['anchors'], fout)
        np.save("img_crop", self.params['crop'])
        np.save("img_bin", self.params['bin'])
        np.save("map", self.params['map'])
        np.save("img_k", self.params['k'])
        np.save("ls_bin", self.params['ls_bin'])
        print("nc:%d"%(self.params['nc']))
        print("nr:%d"%(self.params['nr']))

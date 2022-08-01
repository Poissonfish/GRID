# 3rd party imports
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sys
import qdarkstyle
import os

app = QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

msgBox = QMessageBox()
msgBox.setIcon(QMessageBox.Icon.Information)
msgBox.setText("Finished!")
msgBox.setInformativeText("Save and start another job?")
msgBox.setStandardButtons(
    QMessageBox.StandardButton.Yes|
    QMessageBox.StandardButton.No|
    QMessageBox.StandardButton.Discard)

msgBox.button(QMessageBox.StandardButton.Yes).setText("Save and stay in current work")
msgBox.button(QMessageBox.StandardButton.No).setText("Save and start new job")
msgBox.button(QMessageBox.StandardButton.Discard).setText("Cancel")
# layout = msgBox.layout()
msgBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

msgBox.show()
app.exec()



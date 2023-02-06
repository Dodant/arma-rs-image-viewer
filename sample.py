import sys

import numpy
import pandas
from PyQt5.QtWidgets import QApplication, QWidget


class ArmaViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ARMA3 RS Image Viewer')
        self.move(300, 300)
        self.resize(1000, 800)
        self.show()


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = ArmaViewer()
    sys.exit(viewer.exec_())

import sys

import numpy
import pandas
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, \
    QGroupBox, QHBoxLayout, QGridLayout, QVBoxLayout, QFileDialog, QLabel, QPushButton


class ArmaViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        folderlabel = QLabel('폴더명 : ' + folderpath)

        imageMixBtn = QPushButton('&이미지 순서 섞기', self)
        imageSortBtn = QPushButton('&이미지 순서 정렬하기', self)

        imageMixSortBox = QHBoxLayout()
        imageMixSortBox.addStretch(1)
        imageMixSortBox.addWidget(imageMixBtn)
        imageMixSortBox.addWidget(imageSortBtn)
        imageMixSortBox.addStretch(1)

        fhbox = QHBoxLayout()
        fhbox.addStretch(1)
        fhbox.addWidget(folderlabel)
        fhbox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.createImageGroup())
        hbox.addWidget(self.createLabelGroup())
        hbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(fhbox)
        vbox.addLayout(imageMixSortBox)
        vbox.addLayout(hbox)
        vbox.addStretch(1)

        self.setLayout(vbox)
        self.setWindowTitle('ARMA3 RS Image Viewer')
        self.resize(1000, 800)
        self.center()
        self.show()

    def createImageGroup(self):
        groupbox = QGroupBox('Image Setting')

        eo_radiobtn = QRadioButton('EO', self)
        ir_radiobtn = QRadioButton('IR', self)
        eoir_radiobtn = QRadioButton('EO+IR', self)

        hbox = QHBoxLayout()
        hbox.addWidget(eo_radiobtn)
        hbox.addWidget(ir_radiobtn)
        hbox.addWidget(eoir_radiobtn)
        groupbox.setLayout(hbox)

        return groupbox

    def createLabelGroup(self):
        groupbox = QGroupBox('Label Setting')

        centerpoint_radiobtn = QRadioButton('Center Point', self)
        bbox_radiobtn = QRadioButton('BBOX', self)
        label_radiobtn = QRadioButton('Label', self)

        hbox = QHBoxLayout()
        hbox.addWidget(centerpoint_radiobtn)
        hbox.addWidget(bbox_radiobtn)
        hbox.addWidget(label_radiobtn)
        groupbox.setLayout(hbox)

        return groupbox

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = ArmaViewer()
    sys.exit(viewer.exec_())

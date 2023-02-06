import sys

import numpy
import pandas
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, \
    QGroupBox, QHBoxLayout, QGridLayout, QVBoxLayout, QFileDialog, QLabel, QPushButton, \
    QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class ArmaViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # Horizontal 폴더 열기 & 폴더명
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        folderlabel = QLabel('폴더명 : ' + folderpath)

        fhbox = QHBoxLayout()
        fhbox.addStretch(1)
        fhbox.addWidget(folderlabel)
        fhbox.addStretch(1)

        # Horizontal 이미지 mix & sort
        imageMixBtn = QPushButton('&이미지 순서 섞기', self)
        imageSortBtn = QPushButton('&이미지 순서 정렬하기', self)

        imageMixSortBox = QHBoxLayout()
        imageMixSortBox.addStretch(1)
        imageMixSortBox.addWidget(imageMixBtn)
        imageMixSortBox.addWidget(imageSortBtn)
        imageMixSortBox.addStretch(1)


        # Horizontal << file name >>
        previousBtn = QPushButton('&<<<', self)
        fileNumName = QLabel(f'번째 파일 | 현재 파일명: {folderlabel}')
        nextBtn = QPushButton('&>>>', self)

        prenextBox = QHBoxLayout()
        prenextBox.addStretch(1)
        prenextBox.addWidget(previousBtn)
        prenextBox.addWidget(fileNumName)
        prenextBox.addWidget(nextBtn)
        prenextBox.addStretch(1)


        # Horizontal image & label group
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.createImageGroup())
        hbox.addWidget(self.createLabelGroup())
        hbox.addStretch(1)

        # image window
        pixmap = QPixmap(folderpath)
        lbl_img = QLabel()
        lbl_img.setPixmap(pixmap)

        # Report Button
        reportBtn = QPushButton('&문제 신고하기', self)

        # Total Layout
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(fhbox)
        vbox.addLayout(imageMixSortBox)
        vbox.addLayout(prenextBox)
        vbox.addLayout(hbox)
        vbox.addWidget(lbl_img)
        vbox.addWidget(reportBtn)
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

        centerpoint_checkbtn = QCheckBox('Center Point', self)
        bbox_checkbtn= QCheckBox('BBOX', self)
        label_checkbtn = QCheckBox('Label', self)

        hbox = QHBoxLayout()
        hbox.addWidget(centerpoint_checkbtn)
        hbox.addWidget(bbox_checkbtn)
        hbox.addWidget(label_checkbtn)
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

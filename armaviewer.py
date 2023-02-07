import os
import sys
import time
import random

import numpy
import pandas
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, \
    QGroupBox, QHBoxLayout, QGridLayout, QVBoxLayout, QFileDialog, QLabel, QPushButton, \
    QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


def getAbsoluteFilePath(directory):
    dirlist = []
    for filenames in os.listdir(directory):
        dirlist.append(os.path.abspath(os.path.join(directory, filenames)))
    return sorted(dirlist)


class ArmaViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.fname = 'None'
        self.foldername = 'None'
        self.fileLists = None
        self.folderlabel = QLabel(f'폴더명 : {self.fname}', self)
        self.folderImagePairNumLabel = QLabel('조회된 이미지 쌍 개수: {}')
        self.fileNumName = QLabel(f'번째 파일 | 현재 파일명: {self.fname}')
        self.folderImagePairNumLabel.setAlignment(Qt.AlignHCenter)
        self.pixmap = QPixmap(self.fname)
        self.lbl_img = QLabel()
        self.eo_radiobtn = QRadioButton('EO', self)
        self.ir_radiobtn = QRadioButton('IR', self)
        self.eoir_radiobtn = QRadioButton('EO+IR', self)
        self.initUI()

    def fileDialogOpen(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fname = QFileDialog.getOpenFileName(self, 'Open File', options=options)[0]
        self.foldername = '/'.join(self.fname.split('/')[:-3])
        self.fileLists = getAbsoluteFilePath(self.foldername)

        self.folderlabel.setText(f'폴더명 : {self.foldername}')
        self.folderImagePairNumLabel.setText(f'조회된 이미지 쌍 개수: {len(self.fileLists)}')
        self.fileNumName.setText(f'{self.fileLists.index("/".join(self.fname.split("/")[:-2]))}번째 파일 | 현재 파일명: {str(self.fname.split("/")[-3:-2])}')
        self.pixmap = QPixmap(self.fname)
        self.lbl_img.setPixmap(self.pixmap)
        self.eo_radiobtn.setChecked(True)

    def imageMix(self):
        random.shuffle(self.fileLists)

    def imageSorted(self):
        self.fileLists.sort()

    def initUI(self):
        # Horizontal 폴더 열기 & 폴더명
        folderSelectBtn = QPushButton('&폴더 열기', self)
        folderSelectBtn.clicked.connect(self.fileDialogOpen)

        fhbox = QHBoxLayout()
        fhbox.addStretch(1)
        fhbox.addWidget(folderSelectBtn)
        fhbox.addWidget(self.folderlabel)
        fhbox.addStretch(1)

        # Horizontal 이미지 mix & sort
        imageMixBtn = QPushButton('&이미지 순서 섞기', self)
        imageSortBtn = QPushButton('&이미지 순서 정렬하기', self)
        imageMixBtn.clicked.connect(self.imageMix)
        imageSortBtn.clicked.connect(self.imageSorted)

        imageMixSortBox = QHBoxLayout()
        imageMixSortBox.addStretch(1)
        imageMixSortBox.addWidget(imageMixBtn)
        imageMixSortBox.addWidget(imageSortBtn)
        imageMixSortBox.addStretch(1)


        # Horizontal << file name >>
        previousBtn = QPushButton('&<<<', self)
        nextBtn = QPushButton('&>>>', self)

        prenextBox = QHBoxLayout()
        prenextBox.addStretch(1)
        prenextBox.addWidget(previousBtn)
        prenextBox.addWidget(self.fileNumName)
        prenextBox.addWidget(nextBtn)
        prenextBox.addStretch(1)


        # Horizontal image & label group
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.createImageGroup())
        hbox.addWidget(self.createLabelGroup())
        hbox.addStretch(1)

        # image window
        # pixmap = QPixmap(self.fname)
        # lbl_img = QLabel()
        # lbl_img.setPixmap(self.pixmap)

        # Report Button
        reportBtn = QPushButton('&문제 신고하기', self)

        # Total Vertical Layout
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(fhbox)
        vbox.addWidget(self.folderImagePairNumLabel)
        vbox.addLayout(imageMixSortBox)
        vbox.addLayout(prenextBox)
        vbox.addLayout(hbox)
        vbox.addWidget(self.lbl_img)
        vbox.addWidget(reportBtn)
        vbox.addStretch(1)

        self.setLayout(vbox)
        self.setWindowTitle('ARMA3 RS Image Viewer')
        self.resize(1000, 800)
        self.center()
        self.show()

    def createImageGroup(self):
        groupbox = QGroupBox('Image Setting')

        hbox = QHBoxLayout()
        hbox.addWidget(self.eo_radiobtn)
        hbox.addWidget(self.ir_radiobtn)
        hbox.addWidget(self.eoir_radiobtn)
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

import os
import sys
import time
import random

import numpy
import pandas
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, \
    QGroupBox, QHBoxLayout, QGridLayout, QVBoxLayout, QFileDialog, QLabel, QPushButton, \
    QCheckBox, QButtonGroup
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
        self.nowIndex = 0
        self.imgType = ''
        self.folderlabel = QLabel(f'폴더명 : {self.fname}', self)
        self.folderImagePairNumLabel = QLabel('조회된 이미지 쌍 개수: None')
        self.folderImagePairNumLabel.setAlignment(Qt.AlignHCenter)
        self.fileNumName = QLabel(f'번째 파일 | 현재 파일명: {self.fname}')

        self.pixmap = QPixmap(self.fname)
        self.lbl_img = QLabel()

        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(True)
        self.eo_radiobtn = QRadioButton('EO', self)
        self.ir_radiobtn = QRadioButton('IR', self)
        self.eoir_radiobtn = QRadioButton('EO+IR', self)
        self.btnGroup.addButton(self.eo_radiobtn, 1)
        self.btnGroup.addButton(self.ir_radiobtn, 2)
        self.btnGroup.addButton(self.eoir_radiobtn, 3)
        self.btnGroup.buttonClicked[int].connect(self.btnClicked)

        self.initUI()

    def fileDialogOpen(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fname = QFileDialog.getOpenFileName(self, 'Open File', options=options)[0]
        self.foldername = '/'.join(self.fname.split('/')[:-3])
        self.fileLists = getAbsoluteFilePath(self.foldername)

        self.folderlabel.setText(f'폴더명 : {self.foldername}')
        self.folderImagePairNumLabel.setText(f'조회된 이미지 쌍 개수: {len(self.fileLists)}')
        self.imgType = self.fname[-6:-4]
        self.changeImage()
        self.changeImageInfo()

        if self.imgType == "EO":
            self.eo_radiobtn.setChecked(True)
        elif self.imgType == "IR":
            self.ir_radiobtn.setChecked(True)

    def btnClicked(self, id):
        for button in self.btnGroup.buttons():
            if button is self.btnGroup.button(id):
                selected = button.text()  # EO, IR, EO+IR
                if selected in {'EO', 'IR'}:
                    self.imgType = selected
                    self.fname = self.fname[:-6] + f'{self.imgType}.png'
                    self.changeImage()
                if selected == 'EO+IR':
                    # todo : get EO+IR image
                    pass

    def changeImageInfo(self):
        self.nowIndex = self.fileLists.index("/".join(self.fname.split("/")[:-2]))
        self.fileNumName.setText(f'{self.nowIndex}번째 파일 | 현재 파일명: {str(self.fname.split("/")[-3:-2])}')

    def changeImage(self):
        self.pixmap = QPixmap(self.fname)
        self.lbl_img.setPixmap(self.pixmap)

    def imageMix(self):
        random.shuffle(self.fileLists)

    def imageSorted(self):
        self.fileLists.sort()

    def goToPrevImage(self):
        self.nowIndex -= 1
        if self.nowIndex < 0:
            self.nowIndex = len(self.fileLists) - 1
        self.fname = self.fileLists[self.nowIndex] + f'/IMG/{self.imgType}.png'
        self.changeImage()
        self.changeImageInfo()

    def goToNextImage(self):
        self.nowIndex += 1
        if self.nowIndex >= len(self.fileLists):
            self.nowIndex = 0
        self.fname = self.fileLists[self.nowIndex] + f'/IMG/{self.imgType}.png'
        self.changeImage()
        self.changeImageInfo()

    def initUI(self):
        # Horizontal 폴더 열기 & 폴더명
        folderSelectBtn = QPushButton('폴더 열기', self)
        folderSelectBtn.clicked.connect(self.fileDialogOpen)

        fhbox = QHBoxLayout()
        fhbox.addStretch(1)
        fhbox.addWidget(folderSelectBtn)
        fhbox.addWidget(self.folderlabel)
        fhbox.addStretch(1)

        # Horizontal 이미지 mix & sort
        imageMixBtn = QPushButton('이미지 순서 섞기', self)
        imageSortBtn = QPushButton('이미지 순서 정렬하기', self)
        imageMixBtn.clicked.connect(self.imageMix)
        imageSortBtn.clicked.connect(self.imageSorted)

        imageMixSortBox = QHBoxLayout()
        imageMixSortBox.addStretch(1)
        imageMixSortBox.addWidget(self.folderImagePairNumLabel)
        imageMixSortBox.addWidget(imageMixBtn)
        imageMixSortBox.addWidget(imageSortBtn)
        imageMixSortBox.addStretch(1)

        # Horizontal << file name >>
        prevBtn = QPushButton('<<<', self)
        nextBtn = QPushButton('>>>', self)
        prevBtn.clicked.connect(self.goToPrevImage)
        nextBtn.clicked.connect(self.goToNextImage)

        prenextBox = QHBoxLayout()
        prenextBox.addStretch(1)
        prenextBox.addWidget(prevBtn)
        prenextBox.addWidget(self.fileNumName)
        prenextBox.addWidget(nextBtn)
        prenextBox.addStretch(1)

        # Horizontal image & label group
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.createImageGroup())
        hbox.addWidget(self.createLabelGroup())
        hbox.addStretch(1)

        # Report Button
        # todo : report system
        reportBtn = QPushButton('문제 신고하기', self)

        # Total Vertical Layout
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addLayout(fhbox)
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
        hbox = QHBoxLayout()
        hbox.addWidget(self.eo_radiobtn)
        hbox.addWidget(self.ir_radiobtn)
        hbox.addWidget(self.eoir_radiobtn)
        groupbox = QGroupBox('Image Setting')
        groupbox.setLayout(hbox)

        return groupbox

    def createLabelGroup(self):
        centerpoint_checkbtn = QCheckBox('Center Point', self)
        bbox_checkbtn= QCheckBox('BBOX', self)
        label_checkbtn = QCheckBox('Label', self)
        # todo : center point plot
        # todo : bbox plot
        # todo : label plot

        hbox = QHBoxLayout()
        hbox.addWidget(centerpoint_checkbtn)
        hbox.addWidget(bbox_checkbtn)
        hbox.addWidget(label_checkbtn)
        groupbox = QGroupBox('Label Setting')
        groupbox.setLayout(hbox)

        return groupbox

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_A:
            self.goToPrevImage()
        elif e.key() == Qt.Key_D:
            self.goToNextImage()
        elif e.key() == Qt.Key_W:
            self.imgType = 'EO'
            self.fname = self.fname[:-6] + f'{self.imgType}.png'
            self.changeImage()
            self.eo_radiobtn.setChecked(True)
        elif e.key() == Qt.Key_S:
            self.imgType = 'IR'
            self.fname = self.fname[:-6] + f'{self.imgType}.png'
            self.changeImage()
            self.ir_radiobtn.setChecked(True)


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = ArmaViewer()
    sys.exit(viewer.exec_())

import os
import sys
import time
import random

import numpy as np
import cv2
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, \
    QGroupBox, QHBoxLayout, QGridLayout, QVBoxLayout, QFileDialog, QLabel, QPushButton, \
    QCheckBox, QButtonGroup
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import qimage2ndarray



def getAbsoluteFilePath(directory):
    dirlist = []
    for filenames in os.listdir(directory):
        dirlist.append(os.path.abspath(os.path.join(directory, filenames)))
    return sorted(dirlist)


class ArmaViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.fname = 'None'
        self.oppositefname = 'None'
        self.folderPath = 'None'
        self.fileLists = None
        self.nowIndex = 0
        self.imgType = ''
        self.selected = ''
        self.checked = []
        self.folderlabel = QLabel(f'폴더명 : {self.fname}', self)
        self.folderImagePairNumLabel = QLabel('조회된 이미지 쌍 개수: None')
        self.folderImagePairNumLabel.setAlignment(Qt.AlignHCenter)
        self.fileNumName = QLabel(f'n번째 파일 | 현재 파일명: {self.fname}')

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

        self.center_checkbtn = QCheckBox('Center Point', self)
        self.bbox_checkbtn= QCheckBox('BBOX', self)
        self.label_checkbtn = QCheckBox('Label', self)
        self.center_checkbtn.toggled.connect(self.checkboxToggle)
        self.bbox_checkbtn.toggled.connect(self.checkboxToggle)
        self.label_checkbtn.toggled.connect(self.checkboxToggle)
        self.initUI()

    def checkboxToggle(self):
        self.checked = []
        if self.center_checkbtn.isChecked():
            self.checked.append(0)
        if self.center_checkbtn.isChecked():
            self.checked.append(1)
        if self.center_checkbtn.isChecked():
            self.checked.append(2)

        if self.selected == 'EO+IR':
            eo_canvas = cv2.imread(self.fileTextExtractor('eo_full_path'))
            ir_canvas = cv2.imread(self.fileTextExtractor('ir_full_path'))
            canvas = cv2.addWeighted(eo_canvas, 0.7, ir_canvas, 0.5, 0)
            canvas = self.plotCanvas(canvas)
            self.pixmap = QPixmap(qimage2ndarray.array2qimage(canvas, normalize=False))
            self.lbl_img.setPixmap(self.pixmap)
            return
        if self.imgType == 'EO':
            canvas = cv2.imread(self.fileTextExtractor('eo_full_path'))
            canvas = self.plotCanvas(canvas)
            self.pixmap = QPixmap(qimage2ndarray.array2qimage(canvas, normalize=False))
            self.lbl_img.setPixmap(self.pixmap)
            return
        if self.imgType == 'IR':
            canvas = cv2.imread(self.fileTextExtractor('ir_full_path'))
            canvas = self.plotCanvas(canvas)
            self.pixmap = QPixmap(qimage2ndarray.array2qimage(canvas, normalize=False))
            self.lbl_img.setPixmap(self.pixmap)
            return

    def plotCanvas(self, canvas):
        if 0 in self.checked:
            canvas = self.plotCenteredPtsImage(canvas)
        if 1 in self.checked:
            canvas = self.plotBboxImage(canvas)
        if 2 in self.checked:
            canvas = self.plotBboxImage(canvas)
        return canvas

    def eoirFile(self):
        eo_canvas = cv2.imread(self.fileTextExtractor('eo_full_path'))
        ir_canvas = cv2.imread(self.fileTextExtractor('ir_full_path'))
        blendedCanvas = cv2.addWeighted(eo_canvas, 0.7, ir_canvas, 0.5, 0)
        self.pixmap = QPixmap(qimage2ndarray.array2qimage(blendedCanvas, normalize=False))
        self.lbl_img.setPixmap(self.pixmap)

    def plotCenteredPtsImage(self, canvas):
        anno_file = pd.read_csv(self.fileTextExtractor('annotation_path'))
        for _, row in anno_file.iterrows():
            center_x, center_y = int(row['center_x']), int(row['center_y'])
            cv2.circle(canvas, (center_x, center_y), 1, (0, 0, 255), 2)
        return canvas

    def plotBboxImage(self, canvas):
        anno_file = pd.read_csv(self.fileTextExtractor('annotation_path'))
        for _, row in anno_file.iterrows():
            pts = list(map(list, [row['x1':'y1'], row['x2':'y2'], row['x3':'y3'], row['x4':'y4']]))
            polygon = np.array([pts], dtype=np.int32)
            cv2.polylines(canvas, [polygon], True, (0, 0, 255), 1)
        return canvas

    def plotLabelImage(self, canvas):
        anno_file = pd.read_csv(self.fileTextExtractor('annotation_path'))
        for _, row in anno_file.iterrows():
            center_x, center_y = int(row['center_x']), int(row['center_y'])
            cv2.putText(canvas, row['sub_class'], (center_x + 5, center_y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        return canvas

    def fileTextExtractor(self, case):
        # /home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/EO.png
        if case == 'pick_full_path':
            return self.fname
        # /home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/EO.png
        if case == 'eo_full_path':
            return self.fname[:-6] + 'EO.png'
        # /home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/IR.png
        if case == 'ir_full_path':
            return self.fname[:-6] + 'IR.png'
        # /home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/annotation.csv
        if case == 'annotation_path':
            return '/'.join(self.fname.split('/')[:-2]) + '/annotations.csv'
        # malden-sunny-10-08
        if case == 'folder_name':
            return '/'.join(self.fname.split('/')[-4:-3])
        # /home/dodant/Downloads/malden-sunny-10-08
        if case == 'folder_path':
            return '/'.join(self.fname.split('/')[:-3])
        # 00000.classes_W.csv.result
        if case == 'image_name':
            return self.fname.split('/')[-3:-2][0]
        # EO
        if case == 'img_type':
            return self.fname[-6:-4]
        if case == 'opposite_type':
            if self.fname[-6:-4] == 'EO':
                return 'IR'
            if self.fname[-6:-4] == 'IR':
                return 'EO'
        if case == 'opposite_type_path':
            if self.fname[-6:-4] == 'EO':
                return self.fname[:-6] + 'IR.png'
            if self.fname[-6:-4] == 'IR':
                return self.fname[:-6] + 'EO.png'
        if case == 'now_index':
            return self.fileLists.index("/".join(self.fname.split("/")[:-2]))

    def fileDialogOpen(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fname = QFileDialog.getOpenFileName(self, 'Open File', options=options)[0]
        self.folderPath = self.fileTextExtractor('folder_path')
        self.fileLists = getAbsoluteFilePath(self.folderPath)

        self.folderlabel.setText(f'폴더명 : {self.folderPath}')
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
                self.selected = button.text()  # EO, IR, EO+IR
                if self.selected in {'EO', 'IR'}:
                    self.imgType = self.selected
                    self.fname = self.fname[:-6] + f'{self.imgType}.png'
                    self.changeImage()
                if self.selected == 'EO+IR':
                    self.eoirFile()

    def changeImageInfo(self):
        self.nowIndex = self.fileTextExtractor('now_index')
        self.fileNumName.setText(f'{self.nowIndex}번째 파일 | 현재 파일명: {self.fileTextExtractor("image_name")}')

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
        hbox = QHBoxLayout()
        hbox.addWidget(self.center_checkbtn)
        hbox.addWidget(self.bbox_checkbtn)
        hbox.addWidget(self.label_checkbtn)
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

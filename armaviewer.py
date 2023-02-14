#
# armaviewer.py
# arma-rs-image-viewer
#
# Created by Junggyun Oh on 02/06/2023.
# Copyright (c) 2023 Junggyun Oh All rights reserved.
#
import os
import os.path as pth
import sys
import random
import re
import math
import glob
from datetime import datetime

import cv2
import numpy as np
import pandas as pd

import qimage2ndarray as q2n
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QFileDialog, QLabel, QPushButton, QCheckBox, QButtonGroup, QMessageBox, QInputDialog, QSizePolicy


def getAbsoluteFilePath(directory):
    dirlist = []
    for filenames in os.listdir(directory):
        dirlist.append(os.path.abspath(os.path.join(directory, filenames)))
    return sorted(dirlist)


class ArmaViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.fname: str = 'None'
        self.folderPath: str = 'None'
        self.fileLists: list = []
        self.nowIndex: int = 0
        self.imgType: str = ''
        self.selected: str = ''
        self.checked: list = []
        self.anno_file = None
        self.label_color = {}

        self.folderlabel = QLabel(f'폴더명 : {self.fname}', self)
        self.folderImagePairNumLabel = QLabel('Image PAIR: _ | EO: _ | IR: _')
        self.folderImagePairNumLabel.setAlignment(Qt.AlignHCenter)
        self.fileNumName = QLabel(f'n번째 파일 | 현재 파일명: {self.fname}')

        self.pixmap = QPixmap(self.fname)
        self.lbl_img = QLabel()

        self.eo_radiobtn = QRadioButton('EO', self)
        self.ir_radiobtn = QRadioButton('IR', self)
        self.eoir_radiobtn = QRadioButton('EO+IR', self)

        self.btnGroup = QButtonGroup()
        self.btnGroup.setExclusive(True)
        self.btnGroup.addButton(self.eo_radiobtn, 1)
        self.btnGroup.addButton(self.ir_radiobtn, 2)
        self.btnGroup.addButton(self.eoir_radiobtn, 3)
        self.btnGroup.buttonClicked[int].connect(self.btnClicked)

        self.center_checkbtn = QCheckBox('Center Point', self)
        self.bbox_checkbtn = QCheckBox('BBOX', self)
        self.rbox_checkbtn = QCheckBox('Round Box', self)
        self.label_checkbtn = QCheckBox('Label', self)
        self.center_checkbtn.toggled.connect(self.checkboxToggle)
        self.bbox_checkbtn.toggled.connect(self.checkboxToggle)
        self.rbox_checkbtn.toggled.connect(self.checkboxToggle)
        self.label_checkbtn.toggled.connect(self.checkboxToggle)
        self.initUI()

    def fileDialogOpen(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fname = QFileDialog.getOpenFileName(self, 'Open File', options=options)[0]
        self.folderPath = self.fileTextExtractor('folder_path')
        p = re.compile('[a-z]+-[a-z]+-[0-9]+-[0-9]+')
        if p.match(self.fileTextExtractor('folder_name')) is None:
            QMessageBox.critical(self, 'Wrong Directory',
                                 "You pick the wrong directory.\n"
                                 "Select Dir [MAP]-[WEATHER]-[MONTH]-[DATE]\n"
                                 "EX) \'malden-sunny-10-08\'")
            return
        t = re.compile('[0-9]{5}.classes_[A-Z].csv.result')
        if t.match(self.fileTextExtractor('image_name')) is None:
            QMessageBox.critical(self, 'Wrong Image',
                                 "You pick the wrong image directory.\n"
                                 "EX) \'00000.classes_W.csv.result\'")
            return
        self.fileLists = getAbsoluteFilePath(self.folderPath)

        self.folderlabel.setText(f'Folder Name : {self.folderPath}')
        EO, IR = self.countEOandIR()
        self.folderImagePairNumLabel.setText(f'Image PAIR: {len(self.fileLists)} | EO: {EO} | IR: {IR}')
        self.countEOandIR()
        self.imgType = self.fileTextExtractor('img_type')
        self.selected = self.imgType
        self.checkboxToggle()
        self.plot()
        self.changeImageInfo()

        if self.imgType == 'EO':
            self.eo_radiobtn.setChecked(True)
        elif self.imgType == 'IR':
            self.ir_radiobtn.setChecked(True)

    def countEOandIR(self):
        return [len(glob.glob(f'{self.fileTextExtractor("folder_path")}/*/IMG/{x}.png')) for x in ['EO', 'IR']]

    def checkboxToggle(self):
        self.checked = []
        if self.center_checkbtn.isChecked(): self.checked.append(0)
        if self.bbox_checkbtn.isChecked(): self.checked.append(1)
        if self.rbox_checkbtn.isChecked(): self.checked.append(2)
        if self.label_checkbtn.isChecked(): self.checked.append(3)
        self.plot()

    def plot(self):
        if self.selected == 'EO+IR':
            eo_canvas = cv2.imread(self.fileTextExtractor('eo_full_path'))
            ir_canvas = cv2.imread(self.fileTextExtractor('ir_full_path'))
            eo_canvas = cv2.cvtColor(eo_canvas, cv2.COLOR_BGR2RGB)
            ir_canvas = cv2.cvtColor(ir_canvas, cv2.COLOR_BGR2RGB)
            canvas = cv2.addWeighted(eo_canvas, 0.5, ir_canvas, 0.5, 0)
            canvas = self.plotCanvas(canvas)
            self.pixmap = QPixmap(q2n.array2qimage(canvas, normalize=False))
            self.lbl_img.setPixmap(self.pixmap)
            self.lbl_img.setScaledContents(True)
            self.lbl_img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            return
        if self.selected == 'EO':
            canvas = cv2.cvtColor(cv2.imread(self.fileTextExtractor('eo_full_path')), cv2.COLOR_BGR2RGB)
            canvas = self.plotCanvas(canvas)
            self.pixmap = QPixmap(q2n.array2qimage(canvas, normalize=False))
            self.lbl_img.setPixmap(self.pixmap)
            self.lbl_img.setScaledContents(True)
            self.lbl_img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            return
        if self.selected == 'IR':
            canvas = cv2.cvtColor(cv2.imread(self.fileTextExtractor('ir_full_path')), cv2.COLOR_BGR2RGB)
            canvas = self.plotCanvas(canvas)
            self.pixmap = QPixmap(q2n.array2qimage(canvas, normalize=False))
            self.lbl_img.setPixmap(self.pixmap)
            self.lbl_img.setScaledContents(True)
            self.lbl_img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            return

    def plotCanvas(self, canvas):
        self.anno_file = pd.read_csv(self.fileTextExtractor('annotation_path'))
        for _, row in self.anno_file.iterrows():
            self.label_color[f'{row["main_class"]}-{row["middle_class"]}'] = \
                (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
        if 0 in self.checked: canvas = self.plotCenteredPtsImage(canvas)
        if 1 in self.checked: canvas = self.plotBboxImage(canvas)
        if 2 in self.checked: canvas = self.plotRboxImage(canvas)
        if 3 in self.checked: canvas = self.plotLabelImage(canvas)
        return canvas

    def plotCenteredPtsImage(self, canvas):
        self.anno_file = pd.read_csv(self.fileTextExtractor('annotation_path'))
        for _, row in self.anno_file.iterrows():
            center = list(map(int, row['center_x':'center_y']))
            cv2.circle(canvas, center, 1, self.label_color[f'{row["main_class"]}-{row["middle_class"]}'], 2)
        return canvas

    def plotBboxImage(self, canvas):
        self.anno_file = pd.read_csv(self.fileTextExtractor('annotation_path'))
        for _, row in self.anno_file.iterrows():
            pts = list(map(list, [row['x1':'y1'], row['x2':'y2'], row['x3':'y3'], row['x4':'y4']]))
            polygon = np.array([pts], dtype=np.int32)
            cv2.polylines(canvas, [polygon], True, self.label_color[f'{row["main_class"]}-{row["middle_class"]}'], 2)
        return canvas

    def plotRboxImage(self, canvas):
        def dist(center, point):
            a, b = center[0] - point[0], center[1] - point[1]
            return int(math.sqrt(a ** 2 + b ** 2))

        self.anno_file = pd.read_csv(self.fileTextExtractor('annotation_path'))
        for _, row in self.anno_file.iterrows():
            center = list(map(int, row['center_x':'center_y']))
            cv2.circle(canvas, center, dist(center, row['x1':'y1']),
                       self.label_color[f'{row["main_class"]}-{row["middle_class"]}'], 2)
        return canvas

    def plotLabelImage(self, canvas):
        self.anno_file = pd.read_csv(self.fileTextExtractor('annotation_path'))
        for _, row in self.anno_file.iterrows():
            center = list(map(int, row['center_x':'center_y']))
            cv2.putText(canvas, f'{row["main_class"]}-{row["middle_class"]}', (center[0] + 5, center[1] + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.label_color[f'{row["main_class"]}-{row["middle_class"]}'],
                        2)
        return canvas

    def fileTextExtractor(self, case: str):
        # /home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/EO.png
        if case == 'pick_full_path': return self.fname
        # /home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/EO.png
        if case == 'eo_full_path': return pth.join(pth.dirname(self.fname), 'EO.png')
        # /home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/IR.png
        if case == 'ir_full_path': return pth.join(pth.dirname(self.fname), 'IR.png')
        # /home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/annotation.csv
        if case == 'annotation_path': return f'{pth.sep.join(self.fname.split(pth.sep)[:-2])}{pth.sep}annotations.csv'
        # malden-sunny-10-08
        if case == 'folder_name': return pth.basename(pth.dirname(pth.dirname(pth.dirname(self.fname))))
        # /home/dodant/Downloads/malden-sunny-10-08
        if case == 'folder_path': return pth.sep.join(self.fname.split(pth.sep)[:-3])
        # 00000.classes_W.csv.result
        if case == 'image_name': return pth.basename(pth.dirname(pth.dirname(self.fname)))
        # EO
        if case == 'img_type': return self.fname[-6:-4]
        if case == 'opposite_type':
            if self.fname[-6:-4] == 'EO': return 'IR'
            if self.fname[-6:-4] == 'IR': return 'EO'
        if case == 'opposite_type_path':
            if self.fname[-6:-4] == 'EO': return pth.join(pth.dirname(self.fname), 'IR.png')
            if self.fname[-6:-4] == 'IR': return pth.join(pth.dirname(self.fname), 'EO.png')
        if case == 'now_index': return self.fileLists.index(pth.sep.join(self.fname.split(pth.sep)[:-2]))

    def btnClicked(self, sign):
        for button in self.btnGroup.buttons():
            if button is self.btnGroup.button(sign):
                self.selected = button.text()  # EO, IR, EO+IR
                if self.selected in ['EO', 'IR']:
                    self.imgType = self.selected
                    self.fname = pth.join(pth.dirname(self.fname), f'{self.imgType}.png')
                    self.checkboxToggle()
                    self.plot()
                if self.selected == 'EO+IR':
                    self.checkboxToggle()
                    self.plot()

    def changeImageInfo(self):
        self.nowIndex = self.fileTextExtractor('now_index')
        self.fileNumName.setText(f'{self.nowIndex}번째 파일 | 현재 파일명: {self.fileTextExtractor("image_name")}')

    def imageMix(self):
        random.shuffle(self.fileLists)

    def imageSorted(self):
        self.fileLists.sort()

    def goToPrevImage(self):
        self.nowIndex -= 1
        if self.nowIndex < 0: self.nowIndex = len(self.fileLists) - 1
        self.fname = pth.join(self.fileLists[self.nowIndex], 'IMG', f'{self.imgType}.png')
        self.checkboxToggle()
        self.plot()
        self.changeImageInfo()

    def goToNextImage(self):
        self.nowIndex += 1
        if self.nowIndex >= len(self.fileLists): self.nowIndex = 0
        self.fname = pth.join(self.fileLists[self.nowIndex], 'IMG', f'{self.imgType}.png')
        self.checkboxToggle()
        self.plot()
        self.changeImageInfo()

    def reportDialog(self):
        text, ok = QInputDialog.getMultiLineText(self, 'Report', "What\'s the issue?")
        if ok:
            f = open(pth.join(self.fileTextExtractor("folder_path"), 'report.csv'), 'a')
            f.write(f'{self.fileTextExtractor("pick_full_path")},{datetime.now().strftime("%Y%m%d%H%M")}.,{text}\n')
            f.close()

    def extraDialog(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Hello Out There")
        msgBox.setTextFormat(Qt.RichText)
        msg = "¯\_(ツ)_/¯ \
            <br> Copyright (c) 2023 Junggyun Oh. All rights reserved. \
            <br> Please Report Bug and Additional Requirements Here. And Give Me Star. \
            <br> => <a href='https://github.com/Dodant/arma-rs-image-viewer'>Dodant/arma-rs-image-viewer</a>"
        msgBox.setText(msg)
        msgBox.exec()

    def initUI(self):
        # Horizontal 폴더 열기 & 폴더명
        self.fileDialogOpen()

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
        prevBtn = QPushButton('<< <<< <', self)
        nextBtn = QPushButton('> >>> >>', self)
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
        reportBtn = QPushButton('Report Issue', self)
        extraBtn = QPushButton('Hello Out There', self)
        reportBtn.clicked.connect(self.reportDialog)
        extraBtn.clicked.connect(self.extraDialog)

        hhbox = QHBoxLayout()
        hhbox.addStretch(1)
        hhbox.addWidget(reportBtn)
        hhbox.addWidget(extraBtn)
        hhbox.addStretch(1)

        # Total Vertical Layout
        vbox = QVBoxLayout()
        vbox.addLayout(fhbox)
        vbox.addLayout(imageMixSortBox)
        vbox.addLayout(prenextBox)
        vbox.addLayout(hbox)
        vbox.addWidget(self.lbl_img)
        vbox.addLayout(hhbox)

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
        hbox.addWidget(self.rbox_checkbtn)
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
            self.selected = 'EO'
            self.fname = self.fileTextExtractor('eo_full_path')
            self.checkboxToggle()
            self.plot()
            self.eo_radiobtn.setChecked(True)
        elif e.key() == Qt.Key_S:
            self.selected = 'IR'
            self.fname = self.fileTextExtractor('ir_full_path')
            self.checkboxToggle()
            self.plot()
            self.ir_radiobtn.setChecked(True)


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = ArmaViewer()
    sys.exit(viewer.exec_())

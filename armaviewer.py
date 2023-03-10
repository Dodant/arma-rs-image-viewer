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
import platform
from datetime import datetime

import cv2
import numpy as np
import pandas as pd

import qimage2ndarray as q2n
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QRadioButton, QGroupBox, QHBoxLayout, QVBoxLayout, \
    QFileDialog, QLabel, QPushButton, QCheckBox, QButtonGroup, QMessageBox, QInputDialog, QSizePolicy


class ArmaViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.fname: str = 'None'
        self.fileLists: list = []
        self.nowIndex: int = 0
        self.imgType: str = ''
        self.selected: str = ''
        self.checked: list = []
        self.anno_file = None
        self.label_color = {}
        self.currentOS = platform.system()

        self.folderlabel = QLabel(f'Folder Name : {self.fname}', self)
        self.folderImagePairNumLabel = QLabel('Image PAIR: _ | EO: _ | IR: _')
        self.folderImagePairNumLabel.setAlignment(Qt.AlignHCenter)
        self.fileNumName = QLabel(f'#0 | File Name : {self.fname}')

        self.pixmap = QPixmap(self.fname)
        self.lbl_img = QLabel()

        self.btnGroup = QButtonGroup()
        self.radioBtns = ['EO','IR','EO+IR']

        self.center_checkbtn = QCheckBox('Center Point', self)
        self.bbox_checkbtn = QCheckBox('BBOX', self)
        self.rbox_checkbtn = QCheckBox('Round Box', self)
        self.label_checkbtn = QCheckBox('Label', self)

        self.initUI()

    def fileDialogOpen(self):

        def getAbsoluteFilePath(directory):
            dirlist = []
            for filenames in os.listdir(directory):
                dirlist.append(os.path.abspath(os.path.join(directory, filenames)))
            return sorted(dirlist)

        def countEOandIR():
            return [len(glob.glob(f'{self.fileExtractor("folder_path")}/*/IMG/{x}.png')) for x in ['EO', 'IR']]

        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fname = QFileDialog.getOpenFileName(self, 'Open File', options=options)[0]
        if re.compile('[a-z]+-[a-z]+-[0-9]+-[0-9]+').match(self.fileExtractor('folder_name')) is None:
            QMessageBox.critical(self, 'Wrong Directory',
                                 "You pick the wrong directory.\n "
                                 "Select Dir [MAP]-[WEATHER]-[MONTH]-[DATE]\n "
                                 "EX) 'malden-sunny-10-08 (Sample Data)'")
            return
        if re.compile('[0-9]+.classes_[A-Z].csv.result').match(self.fileExtractor('image_name')) is None:
            QMessageBox.critical(self, 'Wrong Image',
                                 "You pick the wrong image directory.\n "
                                 "EX) '00000.classes_W.csv.result'")
            return
        self.fileLists = getAbsoluteFilePath(self.fileExtractor('folder_path'))
        self.folderlabel.setText(f'Folder Name : {self.fileExtractor("folder_name")}')
        EO, IR = countEOandIR()
        self.folderImagePairNumLabel.setText(f'Image PAIR: {len(self.fileLists)} | EO: {EO} | IR: {IR}')
        self.selected = self.imgType = self.fileExtractor('img_type')
        self.changeImageAtAllOnce()

        if self.imgType == 'EO': self.btnGroup.button(1).setChecked(True)
        elif self.imgType == 'IR': self.btnGroup.button(2).setChecked(True)

    def changeImageAtAllOnce(self):
        self.checkboxToggle()
        self.plot()
        self.changeImageInfo()

    def checkboxToggle(self):
        self.checked = []
        if self.center_checkbtn.isChecked(): self.checked.append(0)
        if self.bbox_checkbtn.isChecked(): self.checked.append(1)
        if self.rbox_checkbtn.isChecked(): self.checked.append(2)
        if self.label_checkbtn.isChecked(): self.checked.append(3)
        self.plot()

    def plot(self):

        def plotCanvas(canvas):

            def plotCenteredPtsImage(canvas_):
                self.anno_file = pd.read_csv(self.fileExtractor('annotation_path'))
                for _, row_ in self.anno_file.iterrows():
                    center = list(map(int, row_['center_x':'center_y']))
                    cv2.circle(canvas_, center, 1, self.label_color[f'{row_["main_class"]}-{row_["middle_class"]}'], 2)
                return canvas_

            def plotBboxImage(canvas_):
                self.anno_file = pd.read_csv(self.fileExtractor('annotation_path'))
                for _, row_ in self.anno_file.iterrows():
                    pts = list(map(list, [row_['x1':'y1'], row_['x2':'y2'], row_['x3':'y3'], row_['x4':'y4']]))
                    polygon = np.array([pts], dtype=np.int32)
                    cv2.polylines(canvas_, [polygon], True,
                                  self.label_color[f'{row_["main_class"]}-{row_["middle_class"]}'], 2)
                return canvas_

            def plotRboxImage(canvas_):

                def dist(center_, point):
                    a, b = center_[0] - point[0], center_[1] - point[1]
                    return int(math.sqrt(a ** 2 + b ** 2))

                self.anno_file = pd.read_csv(self.fileExtractor('annotation_path'))
                for _, row_ in self.anno_file.iterrows():
                    center = list(map(int, row_['center_x':'center_y']))
                    cv2.circle(canvas_, center, dist(center, row_['x1':'y1']),
                               self.label_color[f'{row_["main_class"]}-{row_["middle_class"]}'], 2)
                return canvas_

            def plotLabelImage(canvas_):
                self.anno_file = pd.read_csv(self.fileExtractor('annotation_path'))
                for _, row_ in self.anno_file.iterrows():
                    center = list(map(int, row_['center_x':'center_y']))
                    cv2.putText(canvas_, f'{row_["main_class"]}-{row_["middle_class"]}', (center[0] + 5, center[1] + 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                self.label_color[f'{row_["main_class"]}-{row_["middle_class"]}'], 2)
                return canvas_

            self.anno_file = pd.read_csv(self.fileExtractor('annotation_path'))
            for _, row in self.anno_file.iterrows():
                self.label_color[f'{row["main_class"]}-{row["middle_class"]}'] = \
                    (random.randint(128, 255), random.randint(128, 255), random.randint(128, 255))
            if 0 in self.checked: canvas = plotCenteredPtsImage(canvas)
            if 1 in self.checked: canvas = plotBboxImage(canvas)
            if 2 in self.checked: canvas = plotRboxImage(canvas)
            if 3 in self.checked: canvas = plotLabelImage(canvas)
            return canvas

        def setScaleAndPolicy(canvas):
            canvas = plotCanvas(canvas)
            self.pixmap = QPixmap(q2n.array2qimage(canvas, normalize=False))
            self.lbl_img.setPixmap(self.pixmap)
            self.lbl_img.setScaledContents(True)
            self.lbl_img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if self.selected == 'EO+IR':
            eo_canvas = cv2.imread(self.fileExtractor('eo_full_path'))
            ir_canvas = cv2.imread(self.fileExtractor('ir_full_path'))
            eo_canvas = cv2.cvtColor(eo_canvas, cv2.COLOR_BGR2RGB)
            ir_canvas = cv2.cvtColor(ir_canvas, cv2.COLOR_BGR2RGB)
            setScaleAndPolicy(cv2.addWeighted(eo_canvas, 0.5, ir_canvas, 0.5, 0))
        if self.selected == 'EO':
            setScaleAndPolicy(cv2.cvtColor(cv2.imread(self.fileExtractor('eo_full_path')), cv2.COLOR_BGR2RGB))
        if self.selected == 'IR':
            setScaleAndPolicy(cv2.cvtColor(cv2.imread(self.fileExtractor('ir_full_path')), cv2.COLOR_BGR2RGB))

    def fileExtractor(self, case: str):
        # /home/dodant/Downloads/malden-sunny-10-08 (Sample Data)/00000.classes_W.csv.result/IMG/EO.png
        if case == 'eo_full_path':
            if self.currentOS == 'Linux': return pth.join(pth.dirname(self.fname), 'EO.png')
            if self.currentOS == 'Windows': return pth.dirname(self.fname) + '/EO.png'
        # /home/dodant/Downloads/malden-sunny-10-08 (Sample Data)/00000.classes_W.csv.result/IMG/IR.png
        if case == 'ir_full_path':
            if self.currentOS == 'Linux': return pth.join(pth.dirname(self.fname), 'IR.png')
            if self.currentOS == 'Windows': return pth.dirname(self.fname) + '/IR.png'
        # /home/dodant/Downloads/malden-sunny-10-08 (Sample Data)/00000.classes_W.csv.result/annotation.csv
        if case == 'annotation_path':
            if self.currentOS == 'Linux': return f'{pth.sep.join(self.fname.split(pth.sep)[:-2])}{pth.sep}annotations.csv'
            if self.currentOS == 'Windows': return '\\'.join(self.fname.split('/')[:-2]) + '\\' + 'annotations.csv'
        # malden-sunny-10-08 (Sample Data)
        if case == 'folder_name': return pth.basename(pth.dirname(pth.dirname(pth.dirname(self.fname))))
        # /home/dodant/Downloads/malden-sunny-10-08 (Sample Data)
        if case == 'folder_path':
            if self.currentOS == 'Linux': return pth.sep.join(self.fname.split(pth.sep)[:-3])
            if self.currentOS == 'Windows': return '/'.join(self.fname.split('/')[:-3])
        # 00000.classes_W.csv.result
        if case == 'image_name': return pth.basename(pth.dirname(pth.dirname(self.fname)))
        # EO
        if case == 'img_type': return self.fname[-6:-4]
        if case == 'now_index':
            if self.currentOS == 'Linux': return self.fileLists.index(pth.sep.join(self.fname.split(pth.sep)[:-2]))
            if self.currentOS == 'Windows': return self.fileLists.index('\\'.join(self.fname.split('/')[:-2]))

    def btnClicked(self, sign):
        for button in self.btnGroup.buttons():
            if button is self.btnGroup.button(sign):
                self.selected = button.text()  # EO, IR, EO+IR
                if self.selected in ['EO', 'IR']:
                    self.imgType = self.selected
                    self.fname = pth.join(pth.dirname(self.fname), f'{self.imgType}.png')
                    self.changeImageAtAllOnce()
                if self.selected == 'EO+IR':
                    self.changeImageAtAllOnce()

    def changeImageInfo(self):
        self.fileNumName.setText(f'#{self.fileExtractor("now_index")} | File Name : {self.fileExtractor("image_name")}')

    def goToImage(self):
        if not self.fileLists: return
        if self.sender().text() == '<<< << <':
            self.nowIndex -= 1
            if self.nowIndex < 0: self.nowIndex = len(self.fileLists) - 1
        elif self.sender().text() == '> >> >>>':
            self.nowIndex += 1
            if self.nowIndex >= len(self.fileLists): self.nowIndex = 0
        self.fname = pth.join(self.fileLists[self.nowIndex], 'IMG', f'{self.imgType}.png')
        self.changeImageAtAllOnce()

    def reportDialog(self):
        text, ok = QInputDialog.getMultiLineText(self, 'Report', "What\'s the issue?")
        if ok:
            f = open(pth.join(self.fileExtractor("folder_path"), 'report.csv'), 'a')
            f.write(f'{self.fname},{datetime.now().strftime("%Y%m%d%H%M")}.,{text}\n')
            f.close()

    def extraDialog(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Hello Out There")
        msgBox.setTextFormat(Qt.RichText)
        msg = "??\\_(???)_/?? \
            <br> Copyright (c) 2023 Junggyun Oh. All rights reserved. \
            <br> Please Report Bug and Additional Requirements Here. And Give Me Star. \
            <br> => <a href='https://github.com/Dodant/arma-rs-image-viewer'>Dodant/arma-rs-image-viewer</a>"
        msgBox.setText(msg)
        msgBox.exec()

    def initUI(self):

        folderSelectBtn = QPushButton('Open Folder', self)
        folderSelectBtn.clicked.connect(self.fileDialogOpen)

        fhbox = QHBoxLayout()
        fhbox.addStretch(1)
        fhbox.addWidget(folderSelectBtn, alignment=Qt.AlignCenter)
        fhbox.addWidget(self.folderlabel, alignment=Qt.AlignCenter)
        fhbox.addStretch(1)

        imageMixBtn = QPushButton('Shuffle Images', self)
        imageSortBtn = QPushButton('Sort Images', self)
        imageMixBtn.clicked.connect(lambda: random.shuffle(self.fileLists))
        imageSortBtn.clicked.connect(lambda: self.fileLists.sort())

        imageMixSortBox = QHBoxLayout()
        imageMixSortBox.addStretch(1)
        imageMixSortBox.addWidget(self.folderImagePairNumLabel, alignment=Qt.AlignCenter)
        imageMixSortBox.addWidget(imageMixBtn, alignment=Qt.AlignCenter)
        imageMixSortBox.addWidget(imageSortBtn, alignment=Qt.AlignCenter)
        imageMixSortBox.addStretch(1)

        prevBtn = QPushButton('<<< << <', self)
        nextBtn = QPushButton('> >> >>>', self)
        prevBtn.clicked.connect(self.goToImage)
        nextBtn.clicked.connect(self.goToImage)

        prenextBox = QHBoxLayout()
        prenextBox.addStretch(1)
        prenextBox.addWidget(prevBtn, alignment=Qt.AlignCenter)
        prenextBox.addWidget(self.fileNumName, alignment=Qt.AlignCenter)
        prenextBox.addWidget(nextBtn, alignment=Qt.AlignCenter)
        prenextBox.addStretch(1)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.createImageGroup(), alignment=Qt.AlignCenter)
        hbox.addWidget(self.createLabelGroup(), alignment=Qt.AlignCenter)
        hbox.addStretch(1)

        reportBtn = QPushButton('Report Issue', self)
        extraBtn = QPushButton('Hello Out There', self)
        reportBtn.clicked.connect(self.reportDialog)
        extraBtn.clicked.connect(self.extraDialog)

        hhbox = QHBoxLayout()
        hhbox.addStretch(1)
        hhbox.addWidget(reportBtn, alignment=Qt.AlignCenter)
        hhbox.addWidget(extraBtn, alignment=Qt.AlignCenter)
        hhbox.addStretch(1)

        vbox = QVBoxLayout()
        vbox.addLayout(fhbox)
        vbox.addLayout(imageMixSortBox)
        vbox.addLayout(prenextBox)
        vbox.addLayout(hbox)
        vbox.addWidget(self.lbl_img, alignment=Qt.AlignCenter)
        vbox.addLayout(hhbox)

        self.setLayout(vbox)
        self.setWindowTitle('ARMA3 RS Image Viewer')
        self.resize(1000, 800)
        self.center()
        self.show()

        self.fileDialogOpen()

    def createImageGroup(self):
        hbox = QHBoxLayout()
        groupbox = QGroupBox('Image Setting')
        groupbox.setLayout(hbox)
        self.btnGroup.setExclusive(True)
        for idx, item in enumerate(self.radioBtns):
            btn = QRadioButton(item)
            self.btnGroup.addButton(btn, idx+1)
            hbox.addWidget(btn, alignment=Qt.AlignLeading)
        self.btnGroup.buttonClicked[int].connect(self.btnClicked)
        return groupbox

    def createLabelGroup(self):
        hbox = QHBoxLayout()
        groupbox = QGroupBox('Label Setting')
        groupbox.setLayout(hbox)
        for i in [self.center_checkbtn, self.bbox_checkbtn, self.rbox_checkbtn, self.label_checkbtn]:
            hbox.addWidget(i, alignment=Qt.AlignCenter)
            i.toggled.connect(self.checkboxToggle)
        return groupbox

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_A: self.goToImage()
        if e.key() == Qt.Key_D: self.goToImage()
        if e.key() == Qt.Key_W:
            self.selected = 'EO'
            self.fname = self.fileExtractor('eo_full_path')
            self.changeImageAtAllOnce()
            self.eo_radiobtn.setChecked(True)
        if e.key() == Qt.Key_S:
            self.selected = 'IR'
            self.fname = self.fileExtractor('ir_full_path')
            self.changeImageAtAllOnce()
            self.ir_radiobtn.setChecked(True)


if __name__ == '__main__':
    viewer = QApplication(sys.argv)
    ex = ArmaViewer()
    sys.exit(viewer.exec_())

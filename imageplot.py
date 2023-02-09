import cv2
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

eo_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/EO.png'
ir_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/IR.png'
anno_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/annotations.csv'

original = cv2.imread(eo_filepath)
canvas = original.copy()

anno_file = pd.read_csv(anno_filepath)

cv2.startWindowThread()

for _, row in anno_file.iterrows():
    ## centered point
    # center_x, center_y = int(row['center_x']), int(row['center_y'])
    # cv2.circle(canvas, (center_x, center_y), 1, (0,0,255), 2)

    ## bbox
    # pts = list(map(list, [row['x1':'y1'], row['x2':'y2'], row['x3':'y3'], row['x4':'y4']]))
    # polygon = np.array([pts], dtype=np.int32)
    # cv2.polylines(canvas, [polygon], True, (0, 0, 255), 1)

    ## label
    center_x, center_y = int(row['center_x']), int(row['center_y'])
    cv2.putText(canvas, row['sub_class'], (center_x+5, center_y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

cv2.imshow('canvas', canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()
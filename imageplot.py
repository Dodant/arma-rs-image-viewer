import cv2
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pandas as pd

eo_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/EO.png'
ir_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/IR.png'
anno_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/annotations.csv'

original = cv2.imread(eo_filepath)
canvas = original.copy()

anno_file = pd.read_csv(anno_filepath)

cv2.startWindowThread()

for _, row in anno_file.iterrows():
    # center_x, center_y = int(row['center_x']), int(row['center_y'])
    # cv2.circle(canvas, (center_x, center_y), 1, (0,0,255), 2)
    print(list(map(int, row['x1':'y4'])))
    pts = list(row['x1'], row['y1']), list(row['x2'], row['y2']), list(row['x3'], row['y3']), int(row['x4'], row['y4'])
    polygon = np.array([pts], dtype=np.int32)
    cv2.polylines(canvas, [polygon], True, (0, 0, 255), 2)

# cv2.imshow('canvas', canvas)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# cv2.waitKey(1)
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pandas as pd

eo_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/EO.png'
ir_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/IMG/IR.png'
anno_filepath = '/home/dodant/Downloads/malden-sunny-10-08/00000.classes_W.csv.result/annotations.csv'

eo_canvas = cv2.imread(eo_filepath)
ir_canvas = cv2.imread(ir_filepath)

anno_file = pd.read_csv(anno_filepath)



for _, row in anno_file.iterrows():
    ## centered point
    center_x, center_y = int(row['center_x']), int(row['center_y'])
    cv2.circle(eo_canvas, (center_x, center_y), 1, (0, 0, 255), 2)
    ## bbox
    pts = list(map(list, [row['x1':'y1'], row['x2':'y2'], row['x3':'y3'], row['x4':'y4']]))
    polygon = np.array([pts], dtype=np.int32)
    cv2.polylines(eo_canvas, [polygon], True, (0, 0, 255), 1)
    ## label
    center_x, center_y = int(row['center_x']), int(row['center_y'])
    cv2.putText(eo_canvas, row['sub_class'], (center_x+5, center_y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)


# cv2.imshow('canvas', eo_canvas)

## blend image
dst = cv2.addWeighted(eo_canvas, 0.6, ir_canvas, 0.5, 0)
cv2.imshow('blend', dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
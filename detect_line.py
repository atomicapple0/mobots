import cv2
import numpy as np
import os

import cv_utils
from cv_utils import *
from otsu import otsu

cv_utils.IMSHOW_MODE = cv_utils.NO_OP
# cv_utils.IMSHOW_MODE = cv_utils.CV2_SHOW_BLOCKING

# images are (height=480, width=640)
# horiz slice from rows 100 to 150
# otsu threshold that slice
# threshold

class Blob():
    def __init__(self, size, center, col_lo, col_hi):
        self.size = size
        self.center = center
        self.col_lo = col_lo
        self.col_hi = col_hi
        self.row_lo = 100
        self.row_hi = 150
    
    def draw_bbox(self, img):
        cv2.rectangle(img, (self.col_lo, self.row_lo), (self.col_hi, self.row_hi), (0,255,0), 2)
        cv2.circle(img, (int(self.center), int((self.row_lo+self.row_hi)/2)), 5, (0,0,255), -1)
    
    def overlapping(self, other):
        return max(self.col_lo, other.col_lo) <= min(self.col_hi, other.col_hi)
    
    def merge(self, other):
        self.centroid = (self.size * self.center + other.size * other.center) / (self.size + other.size)
        self.size = self.size + other.size
        self.col_lo = min(self.col_lo, other.col_lo)
        self.col_hi = max(self.col_hi, other.col_hi)
    
    def __repr__(self):
        return f'Blob(size={self.size}, center={self.center}, col_lo={self.col_lo}, col_hi={self.col_hi})'

def detect_line(img):
    hsv = bgr2hsv(img)
    val = hsv[:,:,2]
    val = cv2.GaussianBlur(val,(7,7),0)
    thresh_val = max(otsu(val[100:150,:]), 140)
    print(f'thresh_val: {thresh_val}')
    _, thresh = cv2.threshold(val,thresh_val,255,cv2.THRESH_BINARY)
    thresh[:100,:] = 0
    thresh[150:,:] = 0

    labels = []
    try:
        nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
            thresh, connectivity=8
        )
        sizes = stats[:, -1].copy()
        max_label = 1
        max_size = sizes[1]
        for i in range(2, nb_components):
            if sizes[i] > max_size:
                max_label = i
                max_size = sizes[i]
        print(f'1 {max_size} {centroids[max_label]}')
        labels.append(max_label)

        sizes[max_label] = -1
        max_label = 1
        max_size = sizes[1]
        for i in range(2, nb_components):
            if sizes[i] > max_size:
                max_label = i
                max_size = sizes[i]
        if max_size > 500:
            labels.append(max_label)
            print(f'2 {max_size} {centroids[max_label]}')
            
    except Exception as e:
        print(e)

    blobs = []
    for label in labels:
        blob = Blob(
            size=stats[label][4],
            center=centroids[label][0],
            col_lo=stats[label][0],
            col_hi=stats[label][0]+stats[label][2],
        )
        blobs.append(blob)
        print(f'size: {blob.size}', end=' ')
    if len(blobs) > 1 and blobs[0].overlapping(blobs[1]):
        blobs[0].merge(blobs[1])
        blobs.pop(1)
    print()

    thresh = gray2bgr(thresh)
    for blob in blobs:
        blob.draw_bbox(img)
        blob.draw_bbox(thresh)
    out=np.hstack((img,thresh))
    return out, blobs

if __name__ == '__main__':
    img_idx = 0
    fname = f'./tests/{img_idx}.png'
    while os.path.exists(fname):
        print(f'reading: {fname}')
        img = cv2.imread(fname)
        out, blobs = detect_line(img)
        cv2_imshow(out=out)
        cv2.imwrite(f'./results/{img_idx}.png', out)
        img_idx += 1
        fname = f'./tests/{img_idx}.png'
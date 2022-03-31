import cv2
from cv2 import blur
import numpy as np
from cv2_utils import *

from skimage import filters

class RowLines():
    def __init__(self, r, c_rngs):
        self.r = r
        self.c_rngs = c_rngs
        self.down_edges = [-1 for _ in range(len(c_rngs))]
    
    def draw_lines(self, orig):
        for c_rng in self.c_rngs:
            cv2.line(orig, (c_rng[0], self.r), (c_rng[1], self.r), (0, 0, 255), 1)
    
    def draw_interrow_lines(self, orig, prev_row_lines):
        for i in range(len(self.c_rngs)):
            for j in range(len(prev_row_lines.c_rngs)):
                c_rng = self.c_rngs[i]
                prev_c_rng = prev_row_lines.c_rngs[j]
                lo = max(c_rng[0], prev_c_rng[0])
                hi = min(c_rng[1], prev_c_rng[1])
                if lo < hi:
                    num_overlaps = hi - lo
                    if .8 * (c_rng[1] - c_rng[0]) < num_overlaps and .8 * (prev_c_rng[1] - prev_c_rng[0]) < num_overlaps:
                        curr_cntr = int(np.mean(c_rng))
                        prev_cntr = int(np.mean(prev_c_rng))
                        cv2.line(orig, (prev_cntr, prev_row_lines.r), (curr_cntr, self.r), (0, 255, 0), 3)
                        self.down_edges[i] = j
                        break
        print(self.c_rngs)
        print(prev_row_lines.c_rngs)
        print(self.down_edges)

    def __repr__(self):
        return f'row_lines({self.r}, {self.c_rngs})'

def draw_lines(orig, segmented, r):
    lines = []
    line_start = -1
    length = 0
    for c in range(orig.shape[1]):
        if line_start == -1:
            line_start = c
        if segmented[r, c] == 255:
            length += 1
        else:
            if 15 < length:
                lines.append((line_start, c-1))
            line_start = -1
            length = 0
    return lines

img_idx = 0
while True:
    fname = f'test/{img_idx}.jpg'
    print(fname)
    orig = cv2.imread(fname)
    if orig is None:
        break
    pix = 500
    orig = rescale(orig, pix=pix)
    cv2_view(orig=orig)

    gray = bgr2gray(orig)
    gray[:pix//5,:] = np.mean(gray)
    cv2_view(gray=gray)
    gray = cv2.blur(gray, (10,10))
    cv2_view(blur=gray)

    crop = gray[-int(gray.shape[0]*.5):,:]
    thresh_val = np.percentile(crop, 90, axis=(0,1))
    print(thresh_val)

    # accentuate curves
    blur_new = cv2.blur(bgr2gray(orig), (25,25))
    edges = cv2.Sobel(blur_new,cv2.CV_8U,1,0,ksize=5)
    edges[edges < np.percentile(edges, 98)] = 0
    edges[edges >= np.percentile(edges, 98)] = 255
    cv2_view(edges=edges)

    blur[edges==255] = blur*1.3
    blur = blur / np.max(blur)
    cv2_view(edges=blur)
    
    # globally segment lines generously
    val = filters.threshold_otsu(crop)
    _, thresh_init = cv2.threshold(gray,val-5,255,cv2.THRESH_BINARY)
    gray[thresh_init==0] = 0
    cv2_view(thresh=thresh_init)
    cv2_view(blur=gray)

    # cleanup stray bits
    print(np.std(gray), np.std(gray[thresh_init!=0]))
    val = filters.threshold_otsu(gray[thresh_init!=0])-10
    _, thresh_stray = cv2.threshold(gray,val,255,cv2.THRESH_BINARY)
    gray[thresh_stray==0] = 0
    cv2_view(thresh_stray=thresh_stray)

    # remove small segments
    min_size = pix * pix / 250
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        gray, connectivity=8
    )
    sizes = stats[:, -1]
    max_label = 1
    for i in range(2, nb_components):
        if sizes[i] < min_size:
            gray[output == i] = 0

    cv2_view(gray=gray)
    gray = cv2.blur(gray, (5, 25))
    gray[gray!=0] = 255

    cv2_view(gray=gray)
    binary = gray
    
    # find midpoints

    # for each line
    # if too thick compared to previous, 
    #   throw away points that are not white compared to previous line

    # if not many points around it, toss
    # partition points into sets with dist less than 50

    lines_by_row = []
    for r in range(0, orig.shape[0], 10):
        lines_by_row.append(RowLines(r, draw_lines(orig, binary, r)))
    cv2_view(final=orig)

    for r in range(len(lines_by_row)):
        lines_by_row[r].draw_lines(orig)

    for r in range(1, len(lines_by_row)):
        rp = len(lines_by_row)-r-1
        lines_by_row[rp].draw_interrow_lines(orig, lines_by_row[rp+1])

    # through away connected segments with fewer than 10 points

    # cntr_pts = []
    # for i, line in enumerate(flatten_array(lines_by_row)):
    #     cntr_pts.append([int(np.mean(line[1:])), line[0]])
    # cntr_pts = np.array(cntr_pts)

    # new_lines = lines
    # for i, line in enumerate(1, lines):
    #     prev_line_thickness = lines[i-1][2] - lines[i-1][1]
    #     line_thickness = lines[i][2] - lines[i][1]
    #     new_lines.append(line_thickness / prev_line_thickness)

    # count number of points within 5 pixels of pt in cntr_pts
    # cntr_pts_new = []
    # for i, pt in enumerate(cntr_pts):
    #     count = 0
    #     for j, pt2 in enumerate(cntr_pts):
    #         if i != j:
    #             if np.linalg.norm(pt-pt2) < 10:
    #                 count += 1
    #     print(count)
    #     if 4 < count:
    #         cntr_pts_new.append((pt[0], pt[1]))
    # cntr_pts = np.array(cntr_pts_new)

    # for line in lines:
    #     cv2.line(orig, (line[1], line[0]), (line[2], line[0]), (0, 0, 255), 1)

    # for pt in cntr_pts:
    #     cv2.circle(orig, (pt[0], pt[1]), 3, (0, 255, 0), -1)



    # # lines = cv2.HoughLinesP(
    # #     edges, # Input edge image
    # #     1, # Distance resolution in pixels
    # #     np.pi/180, # Angle resolution in radians
    # #     threshold=100, # Min number of votes for valid line
    # #     minLineLength=5, # Min allowed length of line
    # #     maxLineGap=10 # Max allowed gap between line for joining them
    # # )
    # # Iterate over points
    # # lines = lines if lines is not None else None
    # # for points in lines:
    # #     # Extracted points nested in the list
    # #     x1,y1,x2,y2=points[0]
    # #     # Draw the lines joing the points
    # #     # On the original image
    # #     cv2.line(img, (x1,y1),(x2,y2),(0,255,0),2)
    # # cv2.imshow('img', img)
    # # cv2_wait()
    
    # # circ = blur.copy()
    # # circles = cv2.HoughCircles(circ, cv2.HOUGH_GRADIENT, 1, 100)
    # # # If some circle is found
    # # if circles is not None:
    # #     # Get the (x, y, r) as integers
    # #     circles = np.round(circles[0, :]).astype("int")
    # #     print(circles)
    # #     # loop over the circles
    # #     for (x, y, r) in circles:
    # #         cv2.circle(circ, (x, y), r, (0,255,0), 2)
    # # cv2.imshow("img",circ)
    # # cv2_wait()
    
    cv2.imwrite('results/%d.jpg' % img_idx, orig)
    img_idx += 1
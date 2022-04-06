import cv2
import numpy as np
from skimage import filters
from utils import *
from cv2_utils import *

start_time = tic()

INF = 10000000
EPS = 1/INF

class Line:
    def __init__(self, p0, p1):
        if p1[0] != p0[0]:
            self.m = (p1[1] - p0[1]) / (p1[0] - p0[0])
        else:
            self.m = INF
        self.p0 = np.array(p0)
        self.p1 = np.array(p1)
        self.d_p0_p1 = np.linalg.norm(self.p1 - self.p0)
        self.a = 1
        self.b = -self.m
        self.c = p0[1] - self.m * p0[0]

    def dist_pt(self, pt):
        # https://stackoverflow.com/questions/849211/shortest-distance-between-a-point-and-a-line-segment
        x, y = pt
        px = self.p1[0] - self.p0[0]
        py = self.p1[1] - self.p0[1]
        norm = px*px + py*py + EPS
        u =  ((x - self.p0[0]) * px + (y - self.p0[1]) * py) / float(norm)
        if u > 1:
            u = 1
        elif u < 0:
            u = 0
        xp = self.p0[0] + u * px
        yp = self.p0[1] + u * py
        return np.linalg.norm([xp - x, yp - y])

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
            if 10 < length:
                if lines and line_start - lines[-1][-1] < 20:
                    lines[-1][-1] = c-1
                else:
                    lines.append([line_start, c-1])
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
    min_size = 1000
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

    binary = gray
    cv2_view(binary=binary)
    
    # find midpoints

    # for each line
    # if too thick compared to previous, 
    #   throw away points that are not white compared to previous line

    # if not many points around it, toss
    # partition points into sets with dist less than 50

    pts = []
    for r in range(0, orig.shape[0], 10):
        row_lines = draw_lines(orig, binary, r)
        for line in row_lines:
            pts.append(((line[0] + line[1]) // 2, r))
            cv2.line(orig, (line[0], r), (line[1], r), (0, 0, 255), 1)
            cv2.circle(orig, (pts[-1][0], pts[-1][1]), 3, (255, 255, 0), -1)
        
    cv2_view(final=orig)

    bottom_4th = np.array([[c,r] for (c,r) in pts if r > orig.shape[0]*.75 and orig.shape[1]*.3 < c < orig.shape[1]*.7])
    r_base = int(orig.shape[0]-1)
    c_base = np.mean(bottom_4th[:,0])

    line_length = -200
    best_angle, best_score = None, -1
    for angle in np.arange(45, 135, 10):
        angle_rad = np.deg2rad(angle)
        line = Line((c_base, r_base), (c_base + line_length * np.cos(angle_rad), r_base + line_length * np.sin(angle_rad)))
        score = 0
        for pt in pts:
            if line.dist_pt(pt) < 10:
                score += 1
        if score > best_score:
            best_angle = angle
            best_score = score

    print(c_base, r_base)
    print(f'{best_angle} degrees!', best_score)

    angle_rad = np.deg2rad(best_angle)
    cv2.arrowedLine(
        orig, 
        (int(c_base), r_base), 
        (int(c_base + line_length * np.cos(angle_rad)), int(r_base + line_length * np.sin(angle_rad))), 
        (0, 255, 255), 
        10
    )
    
    cv2_view(orig=orig)
    cv2.imwrite('results/%d.jpg' % img_idx, orig)
    img_idx += 1

print(f'{toc(start_time) / img_idx} seconds per image')
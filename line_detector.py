import cv2
import numpy as np
from cv2_utils import *

from skimage import filters

img_idx = 0
while True:
    fname = f'test/{img_idx}.jpg'
    print(fname)
    orig = cv2.imread(fname)
    if orig is None:
        break
    orig = rescale(orig)
    cv2_view(orig=orig)

    gray = bgr2gray(orig)
    gray[:100,:] = np.mean(gray)
    cv2_view(gray=gray)
    blur = cv2.blur(gray, (10,10))
    cv2_view(blur=blur)

    crop = blur[-int(blur.shape[0]*.5):,:]
    thresh_val = np.percentile(crop, 90, axis=(0,1))
    print(thresh_val)
    
    # globally segment lines generously
    val = filters.threshold_otsu(crop)
    _, thresh_init = cv2.threshold(blur,val-5,255,cv2.THRESH_BINARY)
    blur[thresh_init==0] = 0
    cv2_view(thresh=thresh_init)
    cv2_view(blur=blur)

    # deal with brighter floor patches
    # thresh_regions = thresh_init.copy()
    # region_height = 100
    # for i in range(blur.shape[0] // region_height + 1):
    #     region = blur[i*region_height:min((i+1)*region_height,blur.shape[0]),:]
    #     # std = np.std(region[region!=0])
    #     # mean = np.mean(region[region!=0] - .2*std)
    #     # region[region==0] = np.random.normal(loc=mean, scale=std)
    #     # region[region==0] = np.random.randint(0,256)
    #     region = np.where(region==0,np.random.randint(0,256,size=region.shape),region).astype(np.uint8)
    #     val = calc_threshold(region)
    #     print(val)
    #     _, thresh_region = cv2.threshold(region,val,255,cv2.THRESH_BINARY)
    #     thresh_regions[i*region_height:(i+1)*region_height,:] = thresh_region
    # thresh_full = bin2gray(np.bitwise_and(thresh_regions==255, thresh_init==255))
    # blur[thresh_full==0] = 0
    # cv2_view(thresh_regions=thresh_regions)
    # cv2_view(thresh_full=thresh_full)
    # cv2_view(blur=blur)

    # cleanup stray bits
    val = filters.threshold_otsu(blur[thresh_init!=0])-5
    _, thresh_stray = cv2.threshold(blur,val,255,cv2.THRESH_BINARY)
    cv2_view(thresh_stray=thresh_stray)

    binary = thresh_stray


    # crop = blur[-int(blur.shape[0]*.4):,:]
    # thresh_val = np.percentile(crop, 90, axis=-1)
    # print(thresh_val)

    # th3 = cv2.adaptiveThreshold(bgr2gray(cv2.blur(img, (10,10))), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #         cv2.THRESH_BINARY,201,0)
    # print('adaptive')
    # cv2.imshow('img', th3)
    # cv2_wait()

    # thresh = np.all(np.percentile(crop, 90, axis=(0,1)) < blur, axis=-1).astype(np.uint8)*255
    # # thresh = ((thresh_val < img) & (img < 255)).astype(np.uint8) * 255
    # print('threshold')
    # cv2.imshow('img', thresh)
    # cv2_wait()

    # blur = cv2.blur(thresh, (3, 6))
    # print('blur')
    # cv2.imshow('img', blur)
    # cv2_wait()

    # blur[blur > 0] = 255
    # print('blur binarize')
    # cv2.imshow('img', blur)
    # cv2_wait()

    # min_size = 1000
    # nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
    #     blur, connectivity=8
    # )
    # sizes = stats[:, -1]
    # max_label = 1
    # for i in range(2, nb_components):
    #     if sizes[i] < min_size:
    #         blur[output == i] = 0
    
    # print('blur remove small components')
    # cv2.imshow('img', blur)
    # cv2_wait()

    # vert = cv2.blur(blur, (1, 20))
    # vert[vert > 0] = 255
    # print('blur vertically')
    # cv2.imshow('img', vert)
    # cv2_wait()

    # nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
    #     vert, connectivity=8
    # )
    # # stats is left, top, width, height, area
    # max_label = 1
    # for i in range(1, nb_components):
    #     # top plus height
    #     bottom_row = stats[i, 1] + stats[i, 3]
    #     if bottom_row < img.shape[0] * .3:
    #         vert[output == i] = 0
    # vert[:int(vert.shape[0]*.1),:] = 0
    # print('remove skyline and things near top')
    # cv2.imshow('img', vert)
    # cv2_wait()

    # # within a 50 pix radius of that, if pixel color is in range, yes
    # # rad = cv2.blur(vert, (25,50))
    # # low_val = np.percentile(crop, 30)
    # # high_val = np.percentile(crop, 60)
    # # img = ((low_val < img) & (img < high_val))
    # # vert[np.logical_and(img > 0, rad > 0)] = 255
    # # print('bullshit')
    # # cv2.imshow('img', vert)
    # # cv2_wait()

    # nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
    #     vert, connectivity=8
    # )
    # sizes = stats[:, -1]
    # max_label = 1
    # max_size = sizes[1]
    # for i in range(1, nb_components):
    #     if sizes[i] > max_size:
    #         max_label = i
    #         max_size = sizes[i]
    # largest = np.zeros(blur.shape).astype(np.uint8)
    # largest[output == max_label] = 255
    # centroid = tuple(centroids[max_label].astype(int))
    # cv2.circle(largest, centroid, 10, (255, 255, 255), 1)
    # print('grab largest component')
    # cv2.imshow('img', largest)
    # cv2_wait()

    for r in range(0, orig.shape[0], 3):
        draw_line(orig, binary, r)
    print('fuckky')
    cv2_view(final=orig)


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
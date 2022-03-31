import cv2
import numpy as np

def rescale(img, pix=500):
    img_radius = np.min(img.shape[:2])
    return cv2.resize(img, dsize=(0, 0), fx=pix/img_radius, fy=pix/img_radius)

def cv2_wait(t=0):
    key = cv2.waitKey(t) & 0xFF
    if key == ord("q"):
        exit()

def bgr2gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def draw_line(orig, segmented, r):
    length_threshold = 10
    length = 0
    for c in range(orig.shape[1]):
        if segmented[r, c] == 255:
            length += 1
            if length_threshold == length:
                for cc in range(c-1, -1):
                    if segmented[r, cc] == 0:
                        break
                    orig[r, cc] = (0, 0, 255)
            if length_threshold < length:
                orig[r, c] = (0, 0, 255)
            
        else:
            length = 0

img_idx = 0
while True:
    print(img_idx)
    img = cv2.imread(f'test/{img_idx}.jpg')
    if img is None:
        break
    img = rescale(img)
    print('img')
    cv2.imshow('img', img)
    cv2_wait()

    blur = cv2.blur(img, (3,3))
    print('blur init')
    cv2.imshow('img', blur)
    cv2_wait()

    # for i in range(100):
    #     lol = np.all(np.percentile(blur, i, axis=(0,1)) < blur, axis=-1).astype(np.uint8)*255
    #     print(i)
    #     cv2.imshow('img', lol)
    #     cv2_wait(1)

    crop = blur[-int(blur.shape[0]*.4):,:]
    thresh_val = np.percentile(crop, 90, axis=-1)
    print(thresh_val)

    blur = cv2.adaptiveThreshold(bgr2gray(cv2.blur(img, (10,10))), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,201,-10)
    print('adaptive')
    cv2.imshow('img', blur)
    cv2_wait()

    min_size = 1000
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        blur, connectivity=8
    )
    sizes = stats[:, -1]
    max_label = 1
    for i in range(2, nb_components):
        if sizes[i] < min_size:
            blur[output == i] = 0
    
    print('blur remove small components')
    cv2.imshow('img', blur)
    cv2_wait()

    vert = cv2.blur(blur, (1, 20))
    vert[vert > 0] = 255
    print('blur vertically')
    cv2.imshow('img', vert)
    cv2_wait()

    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        vert, connectivity=8
    )
    # stats is left, top, width, height, area
    max_label = 1
    for i in range(1, nb_components):
        # top plus height
        bottom_row = stats[i, 1] + stats[i, 3]
        if bottom_row < img.shape[0] * .3:
            vert[output == i] = 0
    vert[:int(vert.shape[0]*.1),:] = 0
    print('remove skyline and things near top')
    cv2.imshow('img', vert)
    cv2_wait()

    # within a 50 pix radius of that, if pixel color is in range, yes
    # rad = cv2.blur(vert, (25,50))
    # low_val = np.percentile(crop, 30)
    # high_val = np.percentile(crop, 60)
    # img = ((low_val < img) & (img < high_val))
    # vert[np.logical_and(img > 0, rad > 0)] = 255
    # print('bullshit')
    # cv2.imshow('img', vert)
    # cv2_wait()

    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        vert, connectivity=8
    )
    sizes = stats[:, -1]
    max_label = 1
    max_size = sizes[1]
    for i in range(1, nb_components):
        if sizes[i] > max_size:
            max_label = i
            max_size = sizes[i]
    largest = np.zeros(blur.shape).astype(np.uint8)
    largest[output == max_label] = 255
    centroid = tuple(centroids[max_label].astype(int))
    cv2.circle(largest, centroid, 10, (255, 255, 255), 1)
    print('grab largest component')
    cv2.imshow('img', largest)
    cv2_wait()

    out = vert
    for r in range(0, largest.shape[0], 3):
        draw_line(img, vert, r)
    print('fuckky')
    cv2.imshow('img', img)
    cv2_wait()


    # lines = cv2.HoughLinesP(
    #     edges, # Input edge image
    #     1, # Distance resolution in pixels
    #     np.pi/180, # Angle resolution in radians
    #     threshold=100, # Min number of votes for valid line
    #     minLineLength=5, # Min allowed length of line
    #     maxLineGap=10 # Max allowed gap between line for joining them
    # )
    # Iterate over points
    # lines = lines if lines is not None else None
    # for points in lines:
    #     # Extracted points nested in the list
    #     x1,y1,x2,y2=points[0]
    #     # Draw the lines joing the points
    #     # On the original image
    #     cv2.line(img, (x1,y1),(x2,y2),(0,255,0),2)
    # cv2.imshow('img', img)
    # cv2_wait()
    
    # circ = blur.copy()
    # circles = cv2.HoughCircles(circ, cv2.HOUGH_GRADIENT, 1, 100)
    # # If some circle is found
    # if circles is not None:
    #     # Get the (x, y, r) as integers
    #     circles = np.round(circles[0, :]).astype("int")
    #     print(circles)
    #     # loop over the circles
    #     for (x, y, r) in circles:
    #         cv2.circle(circ, (x, y), r, (0,255,0), 2)
    # cv2.imshow("img",circ)
    # cv2_wait()
    
    cv2.imwrite('results-2/%d.jpg' % img_idx, img)
    img_idx += 1
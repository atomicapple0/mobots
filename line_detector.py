import cv2
import numpy as np

def rescale(img, pix=500):
    img_radius = np.min(img.shape[:2])
    return cv2.resize(img, dsize=(0, 0), fx=pix/img_radius, fy=pix/img_radius)

def cv2_wait():
    key = cv2.waitKey(0) & 0xFF
    if key == ord("q"):
        exit()

img_idx = 2
while True:
    print(img_idx)
    img = cv2.imread(f'test/{img_idx}.jpg', cv2.IMREAD_GRAYSCALE)
    if img is None:
        break
    img = rescale(img)
    cv2.imshow('img', img)
    cv2_wait()

    crop = img[-100:,:]
    thresh_val = np.percentile(crop, 95)
    print(thresh_val)
    
    thresh = ((thresh_val < img) & (img < 255)).astype(np.uint8) * 255
    cv2.imshow('img', thresh)
    cv2_wait()

    blur = cv2.blur(thresh, (5, 5))
    cv2.imshow('img', blur)
    cv2_wait()

    blur[blur > 0] = 255
    cv2.imshow('img', blur)
    cv2_wait()

    min_size = 300  
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        blur, connectivity=8
    )
    sizes = stats[:, -1]
    max_label = 1
    for i in range(2, nb_components):
        if sizes[i] < min_size:
            blur[output == i] = 0
    
    cv2.imshow('img', blur)
    cv2.waitKey(0)

    kernel_size = 30
    kernel_v = np.zeros((kernel_size, kernel_size))
    kernel_v[:, int((kernel_size - 1)/2)] = np.ones(kernel_size)
    kernel_v /= kernel_size
    vert = cv2.filter2D(blur, -1, kernel_v)
    vert[vert > 0] = 255
    print(kernel_v)
    cv2.imshow('img', vert)
    cv2_wait()


    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        vert, connectivity=8
    )
    sizes = stats[:, -1]
    max_label = 1
    max_size = sizes[1]
    for i in range(2, nb_components):
        if sizes[i] > max_size:
            max_label = i
            max_size = sizes[i]
    largest = np.zeros(blur.shape).astype(np.uint8)
    largest[output == max_label] = 255
    centroid = tuple(centroids[max_label].astype(int))
    cv2.circle(largest, centroid, 10, (255, 255, 255), 1)
    cv2.imshow('img', largest)
    cv2_wait()

    edges = cv2.Canny(blur, 100, 200)
    cv2.imshow('img', edges)
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
    
    img_idx += 1
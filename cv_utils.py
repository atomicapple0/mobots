import cv2
import numpy as np

import matplotlib.pyplot as plt

NO_OP = -1
CV2_SHOW_BLOCKING = 0
CV2_SHOW_NONBLOCKING = 1
PLT_SHOW_BLOCKING = 2
PLT_SAVE = 3
IMSHOW_MODE = CV2_SHOW_BLOCKING

def calc_threshold(img):
    img = img[img!=0].flatten()
    val = min(120, np.percentile(img, 70) - 5)
    # view_hist(img, val=val)
    return val

def rescale(img, pix=500):
    img_radius = np.min(img.shape[:2])
    return cv2.resize(img, dsize=(0, 0), fx=pix/img_radius, fy=pix/img_radius)

def cv2_imshow(t=-1, **kwargs):
    if IMSHOW_MODE == NO_OP:
        return
    # check if dictionary is empty
    if len(kwargs) == 0:
        print('warning: no arguments passed to kwargs for cv2_imshow')
    for name,img in kwargs.items():
        print(f'displaying {name}')
        try:
            if t > -1:
                cv2.imshow('img', img)
                cv2_wait(t)
            if IMSHOW_MODE == CV2_SHOW_BLOCKING:
                cv2.imshow('img', img)
                cv2_wait(0)
            elif IMSHOW_MODE == CV2_SHOW_NONBLOCKING:
                cv2.imshow(name, img)
                cv2_wait(1)
            elif IMSHOW_MODE == PLT_SHOW_BLOCKING:
                img = bgr2rgb(img)
                plt.imshow(img)
                plt.show()
            elif IMSHOW_MODE == PLT_SAVE:
                img = bgr2rgb(img)
                plt.imsave(f'cv2_imshow/{name}.png', img)
        except Exception as e:
            print(e)

def cv2_wait(t=0):
    key = cv2.waitKey(t) & 0xFF
    if key == ord("q"):
        exit()

def bgr2gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def gray2bgr(img):
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

def bgr2rgb(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

def bgr2hsv(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

def bin2gray(img):
    return img.astype(np.uint8) * 255

def flatten_array(arr):
    return [x for sublist in arr for x in sublist]

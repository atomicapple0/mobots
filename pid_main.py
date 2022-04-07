# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

from detect_line import *

camera = PiCamera()
camera.resolution = RESOLUTION
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=camera.resolution)

errs = [0]

time.sleep(1)
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame.array
    processed, blobs = detect_line(img)

    # for blob in blobs:
    #     print(blob)

    blob = blobs[-1]
    err = CENTER_COL - blob.center
    errs.append(err)

    if -50 < err <  50: # good zone
        print('straight', end=' ')
    elif err < 0: # we need to turn left
        print('left', end=' ')
    elif err >= 0: # we need to turn right
        print('right', end=' ')

    p_err = errs[-1]
    d_err = errs[-1] - errs[-2]
    i_err = sum(errs[max(len(errs)-100,0):]) / len(errs)

    k_p, k_d, k_i = 0, 0, 0
    k_p = 30 / RESOLUTION[0] / 2
    # k_i = 1 / RESOLUTION[0] / 2
    # k_d = 1 / RESOLUTION[0] / 2
    w = k_p * d_err + k_d * d_err + k_i * i_err

    print(f'p_err: {p_err}, w: {w}')
    
    rawCapture.truncate(0)

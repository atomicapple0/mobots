# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
from pid import pid
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
    pid(blobs)
    rawCapture.truncate(0)

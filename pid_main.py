# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time

from detect_line import detect_line

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(1)
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    print('next frame')
    img = frame.array
    processed, blobs = detect_line(img)

    for blob in blobs:
        print(blob)

    ADJUSTMENT = -200
    COL_CENTER = camera.resolution[1] / 2
    blob = blobs[0]
    actual = blob.center + ADJUSTMENT
    if actual < COL_CENTER:
        print('left')
    if actual >= COL_CENTER:
        print('right')
    
    rawCapture.truncate(0)

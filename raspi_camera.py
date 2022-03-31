# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import os
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

from matplotlib import pyplot as plt
fig = plt.figure()
ax = fig.add_subplot()
plt.ion()

# allow the camera to warmup
time.sleep(1)
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    print('next frame')
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    # show the frame
    ax.imshow(image)
    plt.draw()
    plt.show()
    
    # key = cv2.waitKey(0)
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # if the `q` key was pressed, break from the loop
    # if key == ord("q"):
    #   break
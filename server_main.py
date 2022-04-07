import os
import io
import re
import numpy as np
import cv2
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from detect_line import *
from robot import *

print("Running sudo sh ~/RPi_Cam_Web_Interface/stop.sh")
os.system("sudo sh ~/RPi_Cam_Web_Interface/stop.sh")
os.system("rm -f stop.txt")
out = os.popen("ps -aux | grep raspimjpeg").read()
for line in out.split('\n'):
    try:
        pid = re.split('\s+', line)[1]
    except:
        continue
    os.system("pkill %s" % pid)
    print("pkill %s" % pid)
print("\n")
print("Starting stream at http://172.26.229.47:4444/index.html")

with open("./rpi-cam-slow/index.html") as f:
    PAGE = f.read()

R = Robot()
errs = []

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    try:
                        img = cv2.imdecode(np.fromstring(frame, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                        img, blobs = detect_line(img)
                        frame = cv2.imencode('.jpg', img)[1].tostring()
                        # random shit here:
                        # for blob in blobs:
                        #     print(blob)
                        if blobs:
                            blob = blobs[-1]
                            err = CENTER_COL - blob.center
                            errs.append(err)

                            if -50 < err < 50: # good zone
                                print('straight', end=' ')
                            elif err < 0: # we need to turn left
                                print('left', end=' ')
                            elif err >= 0: # we need to turn right
                                print('right', end=' ')

                            p_err = errs[-1]
                            d_err = errs[-1] - errs[-2]
                            i_err = sum(errs[max(len(errs)-100,0):]) / len(errs)

                            k_p, k_d, k_i = 0, 0, 0
                            k_p = 20 / 100
                            # k_i = 1 / RESOLUTION[0] / 2
                            # k_d = 1 / RESOLUTION[0] / 2
                            W = k_p * p_err + k_d * d_err + k_i * i_err

                            print(f'p_err: {p_err}, W: {W}')
                            V = 25
                            R.send_power_pair(V+W, V-W)

                    except Exception as e:
                        print(e)
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='320x240', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 4444)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
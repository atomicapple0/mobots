import os
import traceback
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
from pid import pid

print("Running sudo sh ~/RPi_Cam_Web_Interface/stop.sh")
os.system("sudo sh ~/RPi_Cam_Web_Interface/stop.sh")
os.system("rm -f stop.txt")
out = os.popen("ps -aux | grep raspimjpeg").read()
for line in out.split('\n'):
    try:
        process_id = re.split('\s+', line)[1]
    except:
        continue
    os.system("pkill %s" % process_id)
    print("pkill %s" % process_id)
print("\n")
print("Starting stream at http://172.26.229.47:4444/index.html")

with open("./rpi-cam-slow/index.html") as f:
    PAGE = f.read()

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
                    img = cv2.imdecode(np.fromstring(frame, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
                    try:
                        img, blobs = detect_line(img)
                        pid(blobs)
                    except:
                        print(traceback.format_exc())
                    frame = cv2.imencode('.jpg', img)[1].tostring()
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
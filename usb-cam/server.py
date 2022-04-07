from flask import Flask, render_template, Response, request
import cv2
from usb_camera import Camera

camera = Camera()
app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        camera.screenshot()
        return "hello world!"
    return render_template('index.html')

def gen():
    while True:
        image = camera.get_image()
        _, jpeg = cv2.imencode('.jpg', image)
        jpeg = jpeg.tobytes()
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1111, debug=True, use_reloader=False)
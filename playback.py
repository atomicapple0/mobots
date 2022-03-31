from flask import Flask, render_template, Response
import os

# os.system('ffmpeg -i static/output.avi -c:v libvpx -speed 8 static/output.webm -y')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('player.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=True, use_reloader=False)
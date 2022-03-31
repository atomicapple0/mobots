import cv2
import os

class Camera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(1)
        self.width = int(self.video.get(3))
        self.height = int(self.video.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.writer = cv2.VideoWriter(
            'static/output.avi',
            fourcc, 
            24., 
            (self.width, self.height)
        )
        print('Created camera object')
    
    def __del__(self):
        print('Freeing resources')
        self.video.release()
        self.writer.release()

    def get_image(self, write=False):
        _, image = self.video.read()
        if write:
            self.writer.write(image)
        return image

    def screenshot(self):
        image = self.get_image()
        idx = 0
        if not os.path.exists('imgs'):
            os.makedirs('imgs')
        while True:
            fname = 'imgs/%d.png' % idx
            if not os.path.exists(fname):
                cv2.imwrite(fname, image)
                print('saved: ' + fname)
                break
            idx += 1
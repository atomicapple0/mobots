from utils import *
from robot import *
import time

R = Robot()

try:
    while True:
        v = 20
        w = 0
            
        R.send_power_pair(v+w, v-w)
        R.step()
        delay(HZ=100)

except KeyboardInterrupt:
    pass

R.stop()
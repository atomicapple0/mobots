from utils import *
from robot import *
import time

target = 2000
R = Robot()
TRAILING = 100
IDX = TRAILING
ERR = np.zeros(INF)

try:
    while True:
        p_err = R.get_lght() - target
        ERR[IDX] = p_err
        IDX += 1

        d_err = ERR[IDX] - ERR[IDX-1]
        i_err = np.sum(ERR[IDX-TRAILING:IDX])
        k_p = 15 / 200.
        k_d = 7 / 200.
        k_i = 1 / 200.
        w = k_p * p_err + k_d * d_err + k_i * i_err

        v = 14
        if abs(p_err) > 200:
            v = 1
            
        R.send_power_pair(v-w, v+w)
        delay(HZ=100)
        R.step()

except KeyboardInterrupt:
    pass

R.stop()
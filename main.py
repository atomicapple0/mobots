from keyboard import Keyboard
from robot import *
from utils import *

# [forward, rotate, mode]
FWD, ROT, MDE = 0, 1, 2
SLOW = np.array([25, 50, 'SLOW'], dtype=object)
NORMAL = np.array([50, 40, 'NORMAL'], dtype=object)
RUBBLE = np.array([40, 60, 'RUBBLE'], dtype=object)
RAMP = np.array([55, 65, 'RAMP'], dtype=object)
XTREME = np.array([80, 75, 'XTREME'], dtype=object)

KB = Keyboard()
R = Robot()

servo_angle = 0
try:
    no_op = 0
    key = '~'
    MODE = NORMAL.copy()
    HZ = 100
    R.send_power_pair(0,0)
    while True:
        delay(HZ)
        dx, dth = R.step()
        print(f'[Key]: {key}, '
              f'[MODE]: {MODE[MDE]}, '
              f'[FWD]: {MODE[FWD]}, '
              f'[ROT]: {MODE[ROT]}')

        if KB.kbhit():
            no_op = 0
            key = KB.getch()
        else:
            no_op += 1
        if no_op > 5:
            key = '~'
        
        if key == '1':
            MODE = SLOW.copy()
        elif key == '2':
            MODE = NORMAL.copy()
        elif key == '3':
            MODE = RUBBLE.copy()
        elif key == '4':
            MODE = RAMP.copy()
        elif key == '5':
            MODE = XTREME.copy()

        L_POW, R_POW, = 0, 0
        if key == 'w':
            L_POW, R_POW = (MODE[FWD],MODE[FWD])
        elif key == 'a':
            L_POW, R_POW = (-MODE[ROT],MODE[ROT])
        elif key == 's':
            L_POW, R_POW = (-MODE[FWD],-MODE[FWD])
        elif key == 'd':
            L_POW, R_POW = (MODE[ROT],-MODE[ROT])
        elif key == 'q':
            L_POW, R_POW = (10,60)
        elif key == 'e':
            L_POW, R_POW = (60,10)
        elif key == '-':
            MODE[FWD] -= .1
            MODE[ROT] -= .1
        elif key == '=':
            MODE[FWD] += .1
            MODE[ROT] += .1
        elif key == 'z':
            break
        R.send_power_pair(L_POW, R_POW)

except KeyboardInterrupt:
    pass

R.stop()

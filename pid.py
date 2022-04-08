import numpy as np
from robot import *
from detect_line import *

errs = []
R = Robot()

LEFT = 0
RIGHT = 1
# L R S??? 
TURNS = [LEFT, RIGHT, RIGHT, RIGHT, LEFT, RIGHT]

# todo:
# figure out which blob to use
# if two blobs
# check if they are from "splitting" previous frame
# if not, ignore
# no_op until they exist for a couple frames (?)
# incr number of forks after they dissapear for a couple frames (?)
# figure out which fork we are at
# start looking for forks again after a few seconds

# estimate pixel width of track
# estimate pixel width of diverge
# estimate pixel width of straight

def pid(blobs):
    V = 30
    W = 10
    if blobs:
        blob = blobs[-1]

        # negative err -> turn left
        # positive err -> turn right
        err = CENTER_COL - blob.center
        errs.append(err)

        p_err = errs[-1]
        d_err = errs[-1] - errs[-2]
        i_err = sum(errs[max(len(errs)-100,0):]) / len(errs)

        k_p, k_d, k_i = 0, 0, 0
        k_p = 20 / 100
        # k_i = 1 / RESOLUTION[0] / 2
        # k_d = 1 / RESOLUTION[0] / 2
        W = k_p * p_err + k_d * d_err + k_i * i_err

        # print(f'p_err: {p_err}, W: {W}')
    R.send_power_pair(V+W, V-W)
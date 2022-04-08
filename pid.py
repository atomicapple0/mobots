import numpy as np
from robot import *
from detect_line import *

R = Robot()
ERRS = [0]
LOST_TRACK = 0
LEFT, RIGHT = 0, 1
TURNS = [LEFT, LEFT, RIGHT, RIGHT, RIGHT, LEFT, RIGHT]
# TURNS = [RIGHT, LEFT, RIGHT, LEFT, RIGHT, LEFT, RIGHT]
# TURNS = [LEFT]
FORK_NUM = 0
OPEN_TO_CHANGING_PREFERENCE = 0
PREV_BLOBS = None
PREV_BLOB_CHOICE = 0

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
    global ERRS, LOST_TRACK, LEFT, RIGHT, TURNS, FORK_NUM, OPEN_TO_CHANGING_PREFERENCE, PREV_BLOBS, PREV_BLOB_CHOICE
    # go forward by
    V, W = 45, 0
    p_err, d_err, i_err = 0,0,0
    if blobs:
        LOST_TRACK = 0
        if len(blobs) == 2 and OPEN_TO_CHANGING_PREFERENCE > 0:
            blob = blobs[TURNS[FORK_NUM]]
            PREV_BLOB_CHOICE = TURNS[FORK_NUM]
        elif len(blobs) == 2 and PREV_BLOBS is not None:
            prev_blob = PREV_BLOBS[PREV_BLOB_CHOICE]
            if abs(prev_blob.center - blobs[0].center) < abs(prev_blob.center - blobs[1].center):
                blob = blobs[0]
                PREV_BLOB_CHOICE = 0
            else:
                blob = blobs[1]
                PREV_BLOB_CHOICE = 1
        else:
            blob = blobs[0]
            PREV_BLOB_CHOICE = 0

        if (PREV_BLOBS is not None and
            len(PREV_BLOBS) == 1 and
            len(blobs) == 2 and
            OPEN_TO_CHANGING_PREFERENCE <= 0 and
            PREV_BLOBS[0].overlapping(blobs[0]) and
            PREV_BLOBS[0].overlapping(blobs[1]) and
            FORK_NUM < len(TURNS)-1):
                FORK_NUM += 1
                OPEN_TO_CHANGING_PREFERENCE = 10
                blob = blobs[TURNS[FORK_NUM]]
                PREV_BLOB_CHOICE = TURNS[FORK_NUM]

        PREV_BLOBS = blobs

        # negative err -> turn left
        # positive err -> turn right
        err = CENTER_COL - blob.center
        ERRS.append(err)

        trailing_window = ERRS[max(len(ERRS)-10,0):]
        trailing_abs_err = np.mean(np.abs(trailing_window)) 

        p_err = ERRS[-1]
        d_err = ERRS[-1] - ERRS[-2]
        i_err = np.mean(trailing_window)

        k_p, k_d, k_i = 0, 0, 0
        k_p = 40 / 100
        # k_i = 1 / 100
        k_d = 20 / 100
        W = k_p * p_err + k_d * d_err + k_i * i_err
        if OPEN_TO_CHANGING_PREFERENCE <= 0:
            W = np.sign(W) * min(abs(W), 12)
        # execute the turn!
        if OPEN_TO_CHANGING_PREFERENCE > 0 and abs(p_err) > 30:
            V = 20
            W = np.sign(W) * min(abs(W), 40)
        # go fast if vibing
        elif abs(p_err) < 40:
            # V = 30
            if FORK_NUM < 1:
                V = 70
            else:
                V = 60
    else:
        LOST_TRACK += 1
        V, W = 25, (15*np.sign(ERRS[-1]))
        if LOST_TRACK > 300:
            V, W = 0, 0

    OPEN_TO_CHANGING_PREFERENCE -= 1
    print(f'[{FORK_NUM}->{TURNS[FORK_NUM]}]\tERR=[{p_err:.02f},{d_err:.02f},{i_err:.02f}]\tVW=[{V:.02f},{W:.02f}]\tIDX={R.IDX}')
    R.send_power_pair(V+W, V-W)
    R.step()
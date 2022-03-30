import time
import os
import numpy as np
from matplotlib import pyplot as plt

def normalize_angles(th):
    return np.arctan2(np.sin(th), np.cos(th))

def tic():
    return time.time()

def toc(tic):
    return time.time() - tic

def save_plot(name, t, data):
    plt.figure()
    if type(data) == dict:
        for k, v in data.items():
            plt.plot(t, v, label=k)
        plt.legend()
    else:
        plt.plot(t, data)
    if not os.path.exists('plots'):
        os.makedirs('plots')
    plt.savefig('plots/%s.png' % name)
    print('save plots/%s.png' % name)

def save_traj(xs, ys):
    plt.figure()
    plt.plot(xs, ys)
    plt.axis('square')
    if not os.path.exists('plots'):
        os.makedirs('plots')
    plt.savefig('plots/traj.png')
    print('save plots/traj.png')

def cap_value_at(d, big):
    if abs(d) > big:
        d = np.sign(d) * big
    return d

def abs_to_rel_pose(rob_pose, rel_pose):
    """
    rob_pose wrt to world
    rel_pose wrt to world
    return rel_pose wrt to rob
    """
    T = np.array(
        [
            [np.cos(rob_pose[2]), -np.sin(rob_pose[2]), rob_pose[0]],
            [np.sin(rob_pose[2]), np.cos(rob_pose[2]), rob_pose[1]],
            [0, 0, 1],
        ]
    )
    xy = np.linalg.inv(T) @ np.array([rel_pose[0], rel_pose[1], 1])
    th = normalize_angles(rel_pose[2] - rob_pose[2])
    rel_pose = np.array([float(xy[0]), float(xy[1]), th])
    return rel_pose


def rel_to_abs_pose(rob_pose, rel_pose):
    """
    rob_pose wrt to world
    rel_pose wrt to robot
    return rel_pose wrt to world
    """
    T = np.array(
        [
            [np.cos(rob_pose[2]), -np.sin(rob_pose[2]), rob_pose[0]],
            [np.sin(rob_pose[2]), np.cos(rob_pose[2]), rob_pose[1]],
            [0, 0, 1],
        ]
    )
    xy = T @ np.array([rel_pose[0], rel_pose[1], 1])
    th = normalize_angles(rel_pose[2] + rob_pose[2])
    abs_pose = np.array([float(xy[0]), float(xy[1]), th])
    return abs_pose

def angle_between(dxdy):
    return np.arctan2(dxdy[1], dxdy[0])

def to_rad(deg):
    return deg / 180 * np.pi
from utils import *
import numpy as np
import time
import brickpi3

# Params
INF = 10000000
WHEEL_BASE_DIAMETER = 6.75 # inches
WHEEL_DIAMETER = 3.25 # inches
TICKS_PER_REV = 360

# Setup
BP = brickpi3.BrickPi3()
print('[VOLTAGE] ' + str(BP.get_voltage_battery()))
BP.reset_all()

# Ports
LEFT_MOTOR_PORT = BP.PORT_D
RIGHT_MOTOR_PORT = BP.PORT_C
LIGHT_SENSOR_PORT = BP.PORT_1

BP.set_sensor_type(BP.PORT_1, BP.SENSOR_TYPE.NXT_LIGHT_ON)
BP.offset_motor_encoder(LEFT_MOTOR_PORT, BP.get_motor_encoder(LEFT_MOTOR_PORT))
BP.offset_motor_encoder(RIGHT_MOTOR_PORT, BP.get_motor_encoder(RIGHT_MOTOR_PORT))

class Robot():
    def __init__(self, init_pose=[0,0,0]):
        self.BP = BP
        time.sleep(3)

        self.IDX = 0
        self.t = np.zeros(INF)
        self.encs = np.zeros((INF,2))
        self.pows = np.zeros((INF,2))
        self.lghts = np.zeros(INF)
        self.rob_poses = np.zeros((INF,3))
        self.t_init = tic()

        self.encs[self.IDX,0] = BP.get_motor_encoder(LEFT_MOTOR_PORT)
        self.encs[self.IDX,1] = BP.get_motor_encoder(RIGHT_MOTOR_PORT)
        self.lghts[self.IDX] = BP.get_sensor(BP.PORT_1)
        self.curr_pows = [0, 0]
        self.pows[self.IDX,:] = self.curr_pows
        self.t[self.IDX] = 0
        self.rob_poses[self.IDX,:] = init_pose

        self.IDX += 1
        print('[ROBOT READY]')
    
    def step(self):
        # process sensor data
        self.encs[self.IDX,0] = BP.get_motor_encoder(LEFT_MOTOR_PORT)
        self.encs[self.IDX,1] = BP.get_motor_encoder(RIGHT_MOTOR_PORT)
        self.lghts[self.IDX] = BP.get_sensor(BP.PORT_1)
        self.pows[self.IDX,:] = self.curr_pows

        # always check directionaility of encoder integration!!!
        dl = (self.encs[self.IDX,0] - self.encs[self.IDX-1,0]) / TICKS_PER_REV * WHEEL_DIAMETER * np.pi
        dr = (self.encs[self.IDX,1] - self.encs[self.IDX-1,1]) / TICKS_PER_REV * WHEEL_DIAMETER * np.pi
        ds = (dl + dr) / 2
        dth = (dr - dl) / WHEEL_BASE_DIAMETER

        self.t[self.IDX] = toc(self.t_init)
        self.rob_poses[self.IDX,2] = self.rob_poses[self.IDX-1,2] + dth/2
        self.rob_poses[self.IDX,0] = self.rob_poses[self.IDX-1,0] + ds*np.cos(self.rob_poses[self.IDX,2])
        self.rob_poses[self.IDX,1] = self.rob_poses[self.IDX-1,1] + ds*np.sin(self.rob_poses[self.IDX,2])
        self.rob_poses[self.IDX,2] = self.rob_poses[self.IDX-1,2] + dth

        # print('[ODOMETRY] ' + str(self.rob_poses[self.IDX]))
        self.IDX += 1
        return ds, dth

    def get_pose(self,idx=0):
        return self.rob_poses[self.IDX+idx-1]

    def get_lght(self,idx=0):
        return self.lghts[self.IDX+idx-1]

    def send_power_pair(self, l_pow, r_pow):
        wasLimited = False
        scale = abs(r_pow) / 100
        if scale > 1.0:
            r_pow = r_pow/scale
            l_pow = l_pow/scale
            wasLimited = True
        scale = abs(l_pow) / 100
        if scale > 1.0:
            r_pow = r_pow/scale
            l_pow = l_pow/scale
            wasLimited = True
        self.curr_pows = [l_pow, r_pow]
        # print('[MOTOR POWERS] ' + str((l_pow, r_pow)) + (' (LIMITED!)' if wasLimited else ''))
        self.BP.set_motor_power(LEFT_MOTOR_PORT, l_pow)
        self.BP.set_motor_power(RIGHT_MOTOR_PORT, r_pow)
    
    def stop(self):
        self.send_power_pair(0, 0)
        self.save_data()
        self.BP.reset_all()

    def save_data(self):
        save_plot("enc", self.t[:self.IDX], {'enc_l':self.encs[:self.IDX,0], 'enc_r':self.encs[:self.IDX,1]})
        save_plot("lghts", self.t[:self.IDX], self.lghts[:self.IDX])
        save_plot("pows", self.t[:self.IDX], {'l_pows':self.pows[:self.IDX,0], 'r_pows':self.pows[:self.IDX,1]})
        save_traj(self.rob_poses[:self.IDX,0], self.rob_poses[:self.IDX,1])
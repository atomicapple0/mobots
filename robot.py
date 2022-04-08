from utils import *
import numpy as np
import time
import brickpi3
import RPi.GPIO as GPIO

#########################################################################
#  HARDWARE SPECS
#########################################################################
#    BrickPi Pinouts:
#     _______S2_S1_MA_
#    |                |
#    POW   BrickPi    MB
#    |                MC
#    |_______S3_S4_MD_|
#
#    Servo Pinouts:
#      - Forklift Servo 1: Gray (5V), White (GND), Black (GPIO14)
#      - Clamp Servo 2: Purple (5V), Blue (GND), Green (GPIO15)
#
#      _WB_____WA_ 
#     | Robot   ..|
#     |        \__/  -> (Bearing)
#     |_WC_____WD_| 
#
#########################################################################

# PARAMS
INF = 10000000
WHEEL_BASE_DIAMETER = 6.75 # inches
WHEEL_DIAMETER = 3.25 # inches
TICKS_PER_REV = 360

# SETUP
BP = brickpi3.BrickPi3()
print(f'[VOLTAGE] {BP.get_voltage_battery()}')
BP.reset_all()

# MOTORS
# Convention: [forward port, backward port]
LEFT_MOTOR_PORTS = [BP.PORT_B]
LEFT_MOTOR_DIRECTIONALITY = [1]
RIGHT_MOTOR_PORTS = [BP.PORT_C]
RIGHT_MOTOR_DIRECTIONALITY = [1]
for port in LEFT_MOTOR_PORTS + RIGHT_MOTOR_PORTS:
    BP.offset_motor_encoder(port, port)

# SENSORS
ULTRASONIC_PORT = BP.PORT_4
LIGHT_PORT = BP.PORT_3
BP.set_sensor_type(ULTRASONIC_PORT, BP.SENSOR_TYPE.NXT_ULTRASONIC)
BP.set_sensor_type(LIGHT_PORT, BP.SENSOR_TYPE.NXT_LIGHT_ON)

class Robot(object):
    def __init__(self, init_pose=[0,0,0]):
        self.BP = BP
        time.sleep(2)

        self.IDX = 0
        self.t = np.zeros(INF)
        self.encs = np.zeros((INF,2))
        self.pows = np.zeros((INF,2))
        self.rob_poses = np.zeros((INF,3))
        self.t_init = tic()
        
        self.encs[self.IDX,0] = BP.get_motor_encoder(LEFT_MOTOR_PORTS[0])
        self.encs[self.IDX,1] = BP.get_motor_encoder(RIGHT_MOTOR_PORTS[0])
        self.curr_pows = [0, 0]
        self.pows[self.IDX,:] = self.curr_pows
        self.t[self.IDX] = 0
        self.rob_poses[self.IDX,:] = init_pose

        self.IDX += 1
        print('[ROBOT READY]')
    
    def get_light(self):
        try:
            return BP.get_sensor(LIGHT_PORT)
        except:
            return -1

    def get_ultrasonic(self):
        try:
            return BP.get_sensor(ULTRASONIC_PORT)
        except:
            return -1
    
    def step(self):
        self.encs[self.IDX,0] = BP.get_motor_encoder(LEFT_MOTOR_PORTS[0])
        self.encs[self.IDX,1] = BP.get_motor_encoder(RIGHT_MOTOR_PORTS[0])
        self.pows[self.IDX,:] = self.curr_pows

        # always check directionaility of encoder integration!!!
        dl = (self.encs[self.IDX,0] - self.encs[self.IDX-1,0]) / float(TICKS_PER_REV) * WHEEL_DIAMETER * np.pi
        dr = (self.encs[self.IDX,1] - self.encs[self.IDX-1,1]) / float(TICKS_PER_REV) * WHEEL_DIAMETER * np.pi
        ds = (dl + dr) / 2
        dth = (dr - dl) / WHEEL_BASE_DIAMETER

        self.t[self.IDX] = toc(self.t_init)
        self.rob_poses[self.IDX,2] = self.rob_poses[self.IDX-1,2] + dth/2
        self.rob_poses[self.IDX,0] = self.rob_poses[self.IDX-1,0] + ds*np.cos(self.rob_poses[self.IDX,2])
        self.rob_poses[self.IDX,1] = self.rob_poses[self.IDX-1,1] + ds*np.sin(self.rob_poses[self.IDX,2])
        self.rob_poses[self.IDX,2] = self.rob_poses[self.IDX-1,2] + dth

        # print(f'[ODOMETRY] {self.rob_poses[self.IDX]}')
        self.IDX += 1
        return ds, dth

    def get_pose(self,idx=0):
        return self.rob_poses[self.IDX+idx-1]

    def send_power_pair(self, l_pow, r_pow):
        if self.curr_pows[0] < l_pow:
            self.curr_pows[0] = min(l_pow, self.curr_pows[0] + 10)
            l_pow = self.curr_pows[0]
        if self.curr_pows[0] > l_pow:
            self.curr_pows[0] = max(l_pow, self.curr_pows[0] - 10)
            l_pow = self.curr_pows[0]
        if self.curr_pows[1] < r_pow:
            self.curr_pows[1] = min(r_pow, self.curr_pows[1] + 10)
            r_pow = self.curr_pows[1]
        if self.curr_pows[1] > r_pow:
            self.curr_pows[1] = max(r_pow, self.curr_pows[1] - 10)
            r_pow = self.curr_pows[1]
            
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
        for port, directionality in zip(LEFT_MOTOR_PORTS, LEFT_MOTOR_DIRECTIONALITY):
            self.BP.set_motor_power(port, directionality * l_pow)
        for port, directionality in zip(RIGHT_MOTOR_PORTS, RIGHT_MOTOR_DIRECTIONALITY):
            self.BP.set_motor_power(port, directionality * r_pow)
        print(f"[MOTOR POWERS] {(l_pow, r_pow)} {'(LIMITED!)' if wasLimited else ''}")
    
    def stop(self):
        print('[STOP]')
        self.send_power_pair(0, 0)
        # self.save_data()
        self.BP.reset_all()
    
    def __del__(self):
        self.stop()

    def save_data(self):
        save_plot("enc", self.t[:self.IDX], {'enc_l':self.encs[:self.IDX,0], 'enc_r':self.encs[:self.IDX,1]})
        save_plot("pows", self.t[:self.IDX], {'l_pows':self.pows[:self.IDX,0], 'r_pows':self.pows[:self.IDX,1]})
        save_traj(self.rob_poses[:self.IDX,0], self.rob_poses[:self.IDX,1])
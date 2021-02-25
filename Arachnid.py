#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import signal
import sys
import math
from adafruit_servokit import ServoKit
import smbus
import math
 
kit = ServoKit(channels=16)

def now():
	return time.time()

class Movement:
    COSINE="cosine"
    COSINE_PARABOLIC="COSINE_PARABOLIC"

    def __init__(self, target_pos, target_time, start_pos, start_time, shape=COSINE):
        self._target_position = target_pos
        self._target_time = target_time
        self._start_time = start_time
        self._start_position = start_pos
        self._shape = shape

class ServoType:
    Generic=[1000,2000,0,180]
    Hextronic_HXT900=[1120,2000,0,180]
    Eflite_EFLRS75=[1000,2000,0,180]

class Servo:
    class MovementInProcess(Exception):
        pass
    
    def __init__(self, pwd_channel, rest_angle, servo_type=ServoType.Generic):
        self._min_pwd = servo_type[0]
        self._max_pwd = servo_type[1]
        self._min_angle = servo_type[2]
        self._max_angle = servo_type[3]
        self._rest = self._in_bounds(rest_angle)
        self._pwd_channel = pwd_channel
        self._current_position = self._rest
        self._reversed = False
        

        # Set the initial position of the server so we know where it is
        kit.servo[self._pwd_channel].set_pulse_width_range(self._min_pwd, self._max_pwd)
        print("align ", self._min_pwd, self._max_pwd)
        kit.servo[self._pwd_channel].angle = self._rest

        # Clear the desired movement
        self._moving = False
        self.active_target = Movement(self._rest, now(), self._rest, now())
    
    def set_reversed(self, yesno):
        self._reversed = yesno

    def set_target(self, position, done_by):
        if(self._moving):
            raise self.MovementInProcess
        self._moving = True
        if(self._reversed):
            position = self._max_angle - position
        
        self.active_target = Movement(position, done_by, self._current_position, now())

    def set_target_parabolic(self, position, done_by):
        if(self._moving):
            raise self.MovementInProcess
        self._moving = True
        if(self._reversed):
            position = self._max_angle - position
        
        self.active_target = Movement(position, done_by, self._current_position, now(), Movement.COSINE_PARABOLIC)

    def clear_target(self):
        self._moving = False

    def update_tick(self, current_time):
        # Exit if we're not moving
        if(not self._moving):
            return
        
        # print("Servo = %1i : Start = %.2f : End = %.2f" % (self._pwd_channel, self.active_target._start_position, self.active_target._target_position))

        remaining_time = self.active_target._target_time - current_time

        # Stop completed movements
        if(remaining_time <= 0):
            self._moving = False

        if(self.active_target._shape == Movement.COSINE):
            self._update_tick_cosine(current_time)
        elif(self.active_target._shape == Movement.COSINE_PARABOLIC):
            self._update_tick_cosine_parabolic(current_time)

    def _update_tick_cosine(self, current_time):
        # Calculate current servo position
        animation_time = self.active_target._target_time - self.active_target._start_time

        time_delta = (current_time - self.active_target._start_time)
        animation_perc = time_delta % animation_time

        x = time_delta / animation_time
        
        new_angle = self._interpolate(self.active_target._start_position, self.active_target._target_position, x)

        # Clamp the angles
        if(new_angle < 0):
            new_angle = 0
        if(new_angle > 180):
            new_angle = 180
        
        # Move the leg
        # print("%1i:Ani Percent = %.3f : Servo ∠ = %.2f : X = %.2f" % (self._pwd_channel, animation_perc, new_angle, x))
        kit.servo[self._pwd_channel].angle = new_angle
        self._current_position = new_angle

    def _update_tick_cosine_parabolic(self, current_time):
        # Calculate current servo position
        animation_time = self.active_target._target_time - self.active_target._start_time
        animation_perc = (current_time - self.active_target._start_time) / (animation_time)
        x = animation_perc * 2

        # Trying to alter the curve, turns out this isn't what's causing the stutter
        # cubic_shim = self.active_target._target_position - self.active_target._start_position
        # cubic_shim *= 0.2
        # sp = self.active_target._start_position
        # tp = self.active_target._target_position
        # if(animation_perc * 2 >= 1.0):
        #     new_angle = self._cubic_interpolate(sp + cubic_shim, sp, tp, tp + cubic_shim, 1.0 - x)
        # else:
        #     new_angle = self._cubic_interpolate(sp + cubic_shim, sp, tp, tp + cubic_shim, x)

        if(animation_perc >= 0.5):
            x = 2.0 - x

        new_angle = self._interpolate(self.active_target._start_position, self.active_target._target_position, x)

        # Clamp the angles
        if(new_angle < 0):
            new_angle = 0
        if(new_angle > 180):
            new_angle = 180


        # Move the leg
        # print("Ani Percent = %.3f : Servo ∠ = %.2f : X = %.2f" % (animation_perc, new_angle, x))
        kit.servo[self._pwd_channel].angle = new_angle
        self._current_position = new_angle

    def _interpolate(self, y1, y2, mu):
        # return self._cubic_interpolate(y1, y1, y2, y2, mu)
        return self._cosine_interpolate(y1, y2, mu)
    
    def _cosine_interpolate(self, y1, y2, mu):
        mu2 = (1-math.cos(mu*math.pi))/2
        return (y1*(1-mu2)+y2*mu2)

    def _cubic_interpolate(self, y0, y1, y2, y3, mu):
        mu2 = mu * mu
        a0 = y3 - y2 - y0 + y1
        a1 = y0 - y1 - a0
        a2 = y2 - y0
        a3 = y1

        return a0*mu*mu2+a1*mu2+a2*mu+a3
        
    def _in_bounds(self, desired_angle):
        if(desired_angle < self._min_angle):
            desired_angle = self._min_angle
        if(desired_angle > self._max_angle):
            desired_angle = self._max_angle
        return desired_angle

    def _set_rest_position(self, rest_position):        
        self._rest = in_bounds(rest_position)
    
    def _get_rest_position(self):
        return self._rest
    
    rest_position = property(_get_rest_position, _set_rest_position)
    moving = property(lambda self: self._moving)


class Leg:
    def __init__(self, base_id, arm_id, finger_id):
        self._base = Servo(base_id, 150)
        self._arm = Servo(arm_id,180)
        self._finger = Servo(finger_id,180)
    
    def complete_movements(self):
        while self.moving:
            current_time = now()
            self.update_tick(current_time)


    def update_tick(self, current_time):
        self._base.update_tick(current_time)
        self._arm.update_tick(current_time)
        self._finger.update_tick(current_time)

    def __del__(self):
        pass

    def clear_targets(self):
        self._base.clear_target()
        self._arm.clear_target()
        self._finger.clear_target()

    def goto_rest_position(self):
        fold_time = 1.0
        self.clear_targets()
        
        self._base.set_target(self._base.rest_position, now() + fold_time)
        self._arm.set_target(self._arm.rest_position, now() + fold_time)
        self._finger.set_target(self._finger.rest_position, now() + fold_time)

        # while True:
        #     time.sleep(0.01)
        #     self._base.update_tick(now())
        #     self._arm.update_tick(now())
        #     self._finger.update_tick(now())

        #     if(self._base.moving is False and self._arm.moving is False and self._finger.moving is False):
        #         break


    def am_i_moving(self):
        if(self._base.moving or self._arm.moving or self._finger.moving):
            return True
        else:
            return False

    moving = property(am_i_moving)


class Gyro:
    def __init__(self):
        self.power_mgmt_1 = 0x6b
        self.power_mgmt_2 = 0x6c
        self.bus = smbus.SMBus(1)
        self.address =0x68

        # Activate the Gyro Sensor
        self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)
    
    def __del__(self):
        # TODO: Is this even right?
        self.bus.write_byte_data(self.address, self.power_mgmt_2, 0)

    def read_byte(reg):
        return self.bus.read_byte_data(self.address, reg)
    
    def read_word(self, reg):
        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg+1)
        value = (h << 8) + l
        return value
    
    def read_word_2c(self, reg):
        val = self.read_word(reg)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val
    
    def dist(self, a,b):
        return math.sqrt((a*a)+(b*b))
    
    def get_y_rotation(self):
        x, y, z = self.get_orientation()
        radians = math.atan2(x, self.dist(y,z))
        return -math.degrees(radians)
    
    def get_x_rotation(self):
        x, y, z = self.get_orientation()
        radians = math.atan2(y, self.dist(x,z))
        return math.degrees(radians)

    def get_orientation(self):
        xout = self.read_word_2c(0x3b)
        yout = self.read_word_2c(0x3d)
        zout = self.read_word_2c(0x3f)

        xout_ = xout / 16384.0
        yout_ = yout / 16384.0
        zout_ = zout / 16384.0

        return (xout_, yout_, zout_)
    
    def get_acceleration(self):
        accel_xout = self.read_word_2c(0x43)
        accel_yout = self.read_word_2c(0x45)
        accel_zout = self.read_word_2c(0x47)

        return (accel_xout, accel_yout, accel_zout)

class Arachnid:
    def __init__(self):
        print("initialize")
    
    def __del__(self):
        pass

#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import signal
import sys
import math

from Arachnid import Arachnid,  Servo, now, ServoType

def shutdown_demo():
    fold_time = 1.0
    base.clear_target()
    arm.clear_target()
    finger.clear_target()
    base.set_target(base.rest_position, now() + fold_time)
    arm.set_target(arm.rest_position, now() + fold_time)
    finger.set_target(finger.rest_position, now() + fold_time)

    while True:
        time.sleep(0.01)
        base.update_tick(now())
        arm.update_tick(now())
        finger.update_tick(now())

        if(base.moving is False and arm.moving is False and finger.moving is False):
            break

    GPIO.cleanup()

def main():
    while True:
        def add_set(x, y, z):
            base_target_list.insert(0, x)
            arm_target_list.insert(0, y)
            finger_target_list.insert(0, z)
        
        base_target_list = []
        arm_target_list = []
        finger_target_list = []

        # add_set(0, 0, 0)
        add_set(0, 20, 40)
        add_set(180, 20, 40)
        add_set(100, 140, 140)

        while True:
            time.sleep(0.01)
            base.update_tick(now())
            arm.update_tick(now())
            finger.update_tick(now())

            movement_speed = 0.3

            if(base.moving is False):
                if(len(base_target_list) > 0):
                    next_target = base_target_list.pop()
                    base.set_target(next_target, now() + movement_speed)

            if(arm.moving is False):
                if(len(arm_target_list) > 0):
                    next_target = arm_target_list.pop()
                    arm.set_target(next_target, now() + movement_speed)

            if(finger.moving is False):
                if(len(finger_target_list) > 0):
                    next_target = finger_target_list.pop()
                    finger.set_target(next_target, now() + movement_speed)
            
            if(base.moving is False and arm.moving is False and finger.moving is False):
                break
    
        # break


if __name__ == '__main__':
    try:
        base = Servo(3,50, ServoType.Hextronic_HXT900)
        base.set_reversed(True)
        arm = Servo(4,180)
        finger = Servo(5,180)

        main()
    except KeyboardInterrupt:
        shutdown_demo()

    print("shutdown")
    shutdown_demo()

#talon.py -- Controls the Talon
# Nov 2023, dlb

# This code assumes that the Talon has been calibrated so that a pulsewidth
# of 950 is the most negitave output, and 2050 is the most postive output.
# And 1500 is assumed to be no ouptut.

# Note, in our oscilloscope experiments with the Talon, we found that no
# output occurs from 1470 to 1540.  These numbers are used in the code
# below to avoid this deadband.

import micropython
import machine
from machine import Pin, PWM
import time
from const import *

MIN_PULSEWIDTH       =  950
OFF_PULSEWIDTH_START = 1470
OFF_PULSEWIDTH       = 1500
OFF_PULSEWIDTH_END   = 1540
MAX_PULSEWIDTH       = 2050
low_pw_span   = OFF_PULSEWIDTH_START - MIN_PULSEWIDTH
high_pw_span  = MAX_PULSEWIDTH - OFF_PULSEWIDTH_END 

pwm_pin = Pin(PIN_PWM)
pwm = PWM(pwm_pin)
pwm.freq(PWM_FREQ)
current_pw = 0
    
def set_pwm_pulsewidth_us(pw):
    """ Low level function to set pwm pulsewidth. """
    global current_pw
    current_pw = pw
    tick_us = 1000000 * PWM_PERIOD / 65536.0
    nticks = int(pw / tick_us)
    pwm.duty_u16(nticks)
        
def set_speed(s):
    """ Sets speed direct, -1 to 1. Zero=Off. """
    if s < 0:
        s = 0 - s
        if s > 1: s = 1
        pw = OFF_PULSEWIDTH_START - (low_pw_span * s)
        set_pwm_pulsewidth_us(pw)
        return
    if s == 0:
        set_pwm_pulsewidth_us(OFF_PULSEWIDTH)
        return
    if s > 0:
        if s > 1: s = 1
        pw = OFF_PULSEWIDTH_END + (high_pw_span * s)
        set_pwm_pulsewidth_us(pw)
        return
    
def get_speed():
    pw = current_pw
    if pw < OFF_PULSEWIDTH_START:
        frac = -1.0 * (OFF_PULSEWIDTH_START - pw) / low_pw_span
        return frac
    if pw > OFF_PULSEWIDTH_END:
        frac = (pw - OFF_PULSEWIDTH_END) / high_pw_span
        return frac
    return 0.0

def ramp_speed(target, interval, update_period=0.04):
    """ Ramps the speed from the current speed to the target, over the
    interval, given in seconds.  Blocks until target is reached."""
    speed = get_speed()
    if target < -1: target = -1
    if target > 1: target = 1
    span = target - speed
    nsteps = interval / update_period
    step = span / nsteps
    set_speed(speed)
    time.sleep(update_period)
    for i in range(nsteps):
        set_speed(speed + i * step)
        time.sleep(update_period)
    set_speed(target)
    time.sleep(update_period)
    
def cal_talon():
    """Used to calibrate the talon."""
    print("Sending PWM Calibration Limits")
    set_speed(0.0)
    for i in range(3):
        ramp_speed(1.0, 1.0)  # Ramp to max in one second
        print("At Max Speed..")
        ramp_speed(-1.0, 2.0) # Ramp to min in two seconds
        print("At Min Speed..")
        ramp_speed(0.0, 1.0)  # Ramp to zero in one second
    set_speed(0.0)
    print("Calibration Routine Finished.")

def stop():
    """ Stops the motor immediately. """
    set_speed(0)
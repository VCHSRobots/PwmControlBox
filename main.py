# main.py -- Main routines to run PWM Talon Controller
# dlb, Nov 2023

import machine
from machine import Pin
from machine import Timer
import talon
import battery
import time
from const import *

BLINK_PERIOD = 50   # In 10ms units

pot = machine.ADC(0)
led_pwr = Pin(PIN_LED_GREEN, Pin.OUT)
led_neg = Pin(PIN_LED_YELLOW, Pin.OUT)
led_pos = Pin(PIN_LED_ORANGE, Pin.OUT)

pwr_cycle = 0
pwr_mode = 0
pwr_read = 0
pwm_setting = 0
blink_counter = 0

def get_pot():
    ''' Returns the pot value (-1 to 1).  Also
    adds a 10% deadband around zero.'''
    r = pot.read_u16()
    f = 2 * ((r / 65336.0) - 0.5)
    f = -f
    if f > 1.0: f = 1.0
    if f < -1.0: f = -1.0
    if f > -0.1 and f < 0.1:
        #in deadband
        return 0.0
    if f > 0.0: f = 1.111 * (f - 0.1)
    if f < 0.0: f = 1.111 * (f + 0.1)
    return f

def startup():
    talon.stop()
    led_pwr.value(1)
    led_neg.value(1)
    led_pos.value(1)
    time.sleep(0.5)
    led_neg.value(0)
    led_pos.value(0)

def pwr_light():
    global pwr_cycle, pwr_read, pwr_mode
    pwr_read += 1
    if pwr_read >= 1000:
        pwr_read = 0
        v = battery.get_voltage()
        if v > 2.5: pwr_mode = 0
        elif v > 2.2: pwr_mode = 1
        elif v > 2.0: pwr_mode = 2
        else: pwr_mode = 3
    if pwr_mode == 0:
        # Mostly full power, don't blink
        led_pwr.value(1)
        pwr_cycle += 1
        if pwr_cycle >= 100: pwr_cycle = 0
        return
    if pwr_mode == 1:
        # blink every 2 secs
        pwr_cycle += 1
        if pwr_cycle >= 200: pwr_cycle = 0
        if pwr_cycle > 180: led_pwr.value(0)
        else: led_pwr.value(1)
        return
    if pwr_mode == 2:
        # blink every 1 sec
        pwr_cycle += 1
        if pwr_cycle >= 100: pwr_cycle = 0
        if pwr_cycle > 75: led_pwr.value(0)
        else: led_pwr.value(1)
        return
    # bad new, power almost gone.  Blink lots.
    pwr_cycle += 1
    if pwr_cycle >= 20: pwr_cycle = 0
    if pwr_cycle > 10: led_pwr.value(0)
    else: led_pwr.value(1)

def pos_light():
    global pwm_setting
    if pwm_setting == 0.0:
        led_pos.value(1)
        return
    if pwm_setting <= 0.0:
        led_pos.value(0)
        return
    ticks = pwm_setting * BLINK_PERIOD    
    if blink_counter >= ticks: led_pos.value(0)
    else: led_pos.value(1)
    
def neg_light():
    global pwm_setting
    if pwm_setting == 0.0:
        led_neg.value(1)
        return
    if pwm_setting >= 0.0:
        led_neg.value(0)
        return
    ticks = (-pwm_setting) * BLINK_PERIOD
    if blink_counter >= ticks: led_neg.value(0)
    else: led_neg.value(1)
    
def lights(tmr):
    global blink_counter
    blink_counter += 1
    if blink_counter >= BLINK_PERIOD: blink_counter = 0
    pwr_light()
    neg_light()
    pos_light()

def run():
    global pwm_setting
    t1 = Timer(period=10, mode=Timer.PERIODIC, callback=lights)
    while True:
        pwm_setting = get_pot()
        talon.set_speed(pwm_setting)

    
    


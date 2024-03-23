#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board

# global variables defined
i2c = busio.I2C(board.SCL, board.SDA) #defining which pins for i2c bus connection
ads = ADS.ADS1115(i2c) #object for specific ADS board

#communication channel for analog signals
channel0 = AnalogIn(ads, ADS.P0)
channel1 = AnalogIn(ads, ADS.P1)

def setup():
    return None

def loop():
    wind_direction = (channel0.voltage/3.3*360*2/3)
    wind_speed = channel1.voltage/3.3*50*2/3
    print("direction:", wind_direction, "speed:", wind_speed)

    time.sleep(0.2)

if __name__ == '__main__':
    setup()
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        GPIO.cleanup()

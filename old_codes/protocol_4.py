#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board

# global variables
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

shadow_A = 0
shadow_B = 120
yaw_error_cutoff = 5

# communication channels
wind_dir_ch = AnalogIn(ads, ADS.P0)
wind_vel_ch = AnalogIn(ads, ADS.P1)
# yaw_ire_ch = AnalogIn(ads, ADS.P2) # add when using real stuff

class protocol_4:
    
    # setup function basically, since using OOPs
    def __init__(self):
        # defining pins (BCM mode)
        self.cw_contactor = 17
        self.acw_contactor = 27

        # initialize relevant variables
        self.start_time = time.time()
        self.wind_dir = 0
        self.wind_speed = 0
        self.nacelle_dir = 0 # in degrees
        self.sense = 0

        # GPIO modes for the raspi
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.cw_contactor, GPIO.OUT)
        GPIO.setup(self.acw_contactor, GPIO.OUT)
        GPIO.output(self.cw_contactor, GPIO.HIGH)
        GPIO.output(self.acw_contactor, GPIO.HIGH)

    #Possible changes here in +/- and degrees [59.95, 60]
    def yawing(self, t, direction):
        if direction == 1:
            #anticlockwise yaw
            GPIO.output(self.acw_contactor, GPIO.HIGH)
            GPIO.output(self.cw_contactor, GPIO.LOW)
            print("rotating anticlockwise..")
            self.nacelle_dir = (self.nacelle_dir - t*1.92*59.95)%360
            
        elif direction == -1:
            #clockwise yaw
            GPIO.output(self.acw_contactor, GPIO.LOW)
            GPIO.output(self.cw_contactor, GPIO.HIGH)
            print("rotating clockwise..")
            self.nacelle_dir = (self.nacelle_dir + t*1.92*59.95)%360
            
        time.sleep(t)
    
    #calculates yawing sense and yawing time
    def yaw_finder(self, error, flag=0):
        if not flag:
            if(self.nacelle_dir > self.wind_dir):
                t = error/6/1.92
                print("rotating for %5.3f seconds" % (t))
                self.yawing(t, 1)
            else:
                t = error/6/1.92
                print("rotating for %5.3f seconds" % (t))
                self.yawing(t, -1)
        else:
            if(self.nacelle_dir > self.wind_dir):
                t = error/6/1.92
                print("rotating for %5.3f seconds" % (t))
                self.yawing(t, -1)
            else:
                t = error/6/1.92
                print("rotating for %5.3f seconds" % (t))
                self.yawing(t, 1)
    
    # to be called every 10 seconds (rn)
    def update_values(self):
        # getting current data and appending to avg_lists
        self.wind_speed = wind_vel_ch.voltage/3.3*50
        self.wind_dir = (wind_dir_ch.voltage/3.3*360)%360 # [0,360]
        self.is_Shadow()
        
        print("current speed, dir:", self.wind_speed, self.wind_dir)
        print("nacelle direction:", self.nacelle_dir)
        
    # Check if wind is in shadow sector
    def is_Shadow(self):
        # sense = 0: outside shadow, 1: top half (near shadow_A), 2: bottom half (near shadow_B)
        mid = 1.0*(shadow_B + shadow_A)/2
        if((self.wind_dir >= shadow_A) and (self.wind_dir < mid)): # [A,mid)
            self.sense = 1
        elif((self.wind_dir <= shadow_B) and (self.wind_dir >= mid)): # [mid,B]
            self.sense = 2
        else:
            self.sense = 0    
        
    # loop which runs throughout
    def loop(self):
        # at each loop instance, get updated values (with added condition for time interval)
        self.update_values()
        
        #looks and declares error
        error = abs(self.nacelle_dir - self.wind_dir)
        print("absolute error is:", error)
        
        #Checks if the wind is in shadow sector
        if self.sense > 0:
            print("Wind is in shadow sector")
            print("Optimizing system")

            if self.sense == 1:
                self.wind_dir = shadow_A
            else:
                self.wind_dir = shadow_B
            
            #updates the error
            error = abs(self.nacelle_dir - self.wind_dir)
            print("new error is:", error)
        
        #checks if the wind is more that 5 degrees away
        if error > yaw_error_cutoff:
            if error > 180:
                #Reverse mode
                self.yaw_finder(error%180, flag=1)
            else:
                #Normal correction
                self.yaw_finder(error)
                
        self.shutdown()
        time.sleep(2)
        print()
        
    def shutdown(self):
        print("Turning off contactors...")
        GPIO.output(self.acw_contactor, GPIO.HIGH)
        GPIO.output(self.cw_contactor, GPIO.HIGH)

if __name__ == '__main__':
    protocol_testing_object = protocol_4() # runs the __init__ function = setup
    print("initialising...")
    try:
        while True:
            protocol_testing_object.loop()

    except KeyboardInterrupt:
        protocol_testing_object.shutdown()
        GPIO.cleanup()

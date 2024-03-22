#!/usr/bin/env python3

'''
This file contains all global variables' declarations
Updates the required global variables
Adds delay after being given some time
'''

import RPi.GPIO as GPIO
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
from csv import writer
from csv import reader

# EVERYTHING inside a class, so the SAME can be used everywhere
class update:
    # setup function basically, since using OOPs
    def __init__(self):
        # i2c stuff (not class variables)
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)

        # communication channels
        self.wind_dir_ch = AnalogIn(ads, ADS.P0)
        self.wind_vel_ch = AnalogIn(ads, ADS.P1)
        self.nacelle_dir_ch = AnalogIn(ads, ADS.P2)
        self.machine_vel_ch = AnalogIn(ads, ADS.P3)

        # defining pins (BCM mode)
        self.switching_pin = 17
        self.breaking_pin = 27
        self.cw_contactor = 23
        self.acw_contactor = 24

        # initialize relevant variables
        self.counter = 0
        self.start_time = time.time()
        self.break_status = 1
        self.machine_status = 0
        self.wind_dir_avg = []
        self.wind_vel_avg = []
        self.nacelle_dir = 0
        self.machine_vel = 0
        self.wind_vel1 = 0 # average 1
        self.wind_dir1 = 0 # average 1
        self.wind_vel2 = 0 # average 2
        self.wind_dir2 = 0 # average 2
        
        # only needed when this program starting for the first time
        # get the previous 600 bits of data and set first averages
        try:
            with open('wind_data.csv', 'r') as f:
                reader_obj = list(reader(f))
                
                # add elements to list
                if len(reader_obj) < 600 and len(reader_obj) > 0:
                    for obj in reader_obj:
                        self.wind_vel_avg.append(float(obj[1]))
                        self.wind_dir_avg.append(float(obj[2]))
                elif len(reader_obj) >= 600:
                    for x in range(1,601):
                        self.wind_vel_avg.append(float(reader_obj[-x][1]))
                        self.wind_dir_avg.append(float(reader_obj[-x][1]))
                
                # if length > 0, update avgs
                if len(self.wind_dir_avg) > 0:
                    self.wind_vel1 = sum(self.wind_vel_avg)/len(self.wind_vel_avg)
                    self.wind_dir1 = sum(self.wind_dir_avg)/len(self.wind_dir_avg)
                    self.wind_vel2 = self.wind_vel1
                    self.wind_dir2 = self.wind_dir1
        except: # non-existant file
            pass

        # GPIO modes for the raspi
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.switching_pin, GPIO.OUT)
        GPIO.setup(self.breaking_pin, GPIO.OUT)
        GPIO.setup(self.acw_contactor, GPIO.OUT)
        GPIO.setup(self.cw_contactor, GPIO.OUT)
        
        # initialize outputs
        self.update_values()
        GPIO.output(self.switching_pin, GPIO.LOW) # machine OFF initially
        GPIO.output(self.breaking_pin, GPIO.HIGH) # break ON initially
        GPIO.output(self.acw_contactor, GPIO.LOW)
        GPIO.output(self.cw_contactor, GPIO.LOW)
        self.update_values()

    # to add elements to list while updating avg
    def update_avg(self, c_vel, c_dir):
        # length before appending
        length = len(self.wind_dir_avg)
        
        # updating old values
        old_vel1 = 0
        old_dir1 = 0
        old_vel2 = 0
        old_dir2 = 0
        if length >= 600:
            # get old values after popping
            old_vel1 = self.wind_vel_avg.pop(0)
            old_dir1 = self.wind_dir_avg.pop(0)
        if length >= 60:
            old_vel2 = self.wind_vel_avg[-60]
            old_dir2 = self.wind_dir_avg[-60]
        
        # append new values, final size <= 600
        self.wind_vel_avg.append(c_vel)
        self.wind_dir_avg.append(c_dir)
        
        # new avg = (old avg * length - old + new)/length
        # this approach avoids taking avg of 600 things, faster (by a tiny bit)
        # old avg > 0 since length > 0
        if length > 0 and length < 60:
            self.wind_vel1 = (self.wind_vel1*length + c_vel)/(length+1)
            self.wind_dir1 = (self.wind_dir1*length + c_dir)/(length+1)
            self.wind_vel2 = (self.wind_vel2*length + c_vel)/(length+1)
            self.wind_dir2 = (self.wind_dir2*length + c_dir)/(length+1)
            
        elif length >= 60 and length < 600:
            self.wind_vel1 = (self.wind_vel1*length + c_vel)/(length+1)
            self.wind_dir1 = (self.wind_dir1*length + c_dir)/(length+1)
            self.wind_vel2 = (self.wind_vel2*60 - old_vel2 + c_vel)/60
            self.wind_dir2 = (self.wind_dir2*60 - old_dir2 + c_dir)/60
            
        elif length >= 600:
            self.wind_vel1 = (self.wind_vel1*600 - old_vel1 + c_vel)/600
            self.wind_dir1 = (self.wind_dir1*600 - old_dir1 + c_dir)/600
            self.wind_vel2 = (self.wind_vel2*60 - old_vel2 + c_vel)/60
            self.wind_dir2 = (self.wind_dir2*60 - old_dir2 + c_dir)/60
            
        else:
            # only one element, which is set as current average too
            self.wind_vel1 = c_vel
            self.wind_dir1 = c_dir
            self.wind_vel2 = c_vel
            self.wind_dir2 = c_dir

        self.counter += 1
            
    # updates all values, puts into csv
    def update_values(self):
        # getting current data
        cur_wind_vel = self.wind_vel_ch.voltage/3.3*50
        cur_wind_dir = (self.wind_dir_ch.voltage/3.3*360) % 360
        
        # check stuff for IRE, not analog inputs
        self.nacelle_dir = (self.nacelle_dir_ch.voltage/3.3*360) % 360
        self.machine_vel = self.machine_vel_ch.voltage/3.3*50 # fix the constants accordingly
        
        # setting global averages according to mode set and updating lists
        self.update_avg(cur_wind_vel, cur_wind_dir)
        
        # writing into csv file (to be modified accordingly)
        if self.counter >= 60:
            self.counter = 0
            l = [time.time(),
                cur_wind_vel,
                cur_wind_dir,
                self.machine_vel,
                self.nacelle_dir,
                self.break_status,      # set status manually in machine.py by using object properties
                self.machine_status]    # set status manually in machine.py by using object properties
            with open('wind_data.csv', 'a+') as f:
                writer_obj = writer(f)
                writer_obj.writerow(l)
                f.close()

        print("10 min average speed, dir:", self.wind_vel1, self.wind_dir1)
        print("1 min average speed, dir:", self.wind_vel2, self.wind_dir2)

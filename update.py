'''
This file contains all global variables' declarations 
Updates the required global variables which are used to make logcial decisions
ONLY this file takes input from the external outputs and stores processed results in variables 
Doesn't have output functions
'''

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

        # communication channels to be used by other functions inside update ONLY
        self.wind_dir_ch = AnalogIn(ads, ADS.P0)
        self.wind_vel_ch = AnalogIn(ads, ADS.P1)
        self.nacelle_dir_ch = AnalogIn(ads, ADS.P2)
        self.machine_vel_ch = AnalogIn(ads, ADS.P3)

        # relevant constants used in update and outside
        self.cut_in = 1.3
        self.cut_out = 9
        self.extreme_wind = 15
        
        # initialize relevant variables which are used outside update
        self.counter = 0
        self.extreme = 0 # 0: non extreme, 1: extreme
        self.mode = 0 # 0: normal, 1: non normal
        self.wind_dir_avg = []
        self.wind_vel_avg = []
        self.nacelle_dir = 0
        self.machine_vel = 0
        self.wind_dir = [0,0] # 0: normal, 1: non normal
        self.wind_vel = [0,0] # 0: normal, 1: non normal
        
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
                        self.wind_dir_avg.append(float(reader_obj[-x][2]))
                
                # if length > 0, update avgs
                if len(self.wind_dir_avg) > 0:
                    self.wind_vel[0] = sum(self.wind_vel_avg)/len(self.wind_vel_avg)
                    self.wind_dir[0] = (sum(self.wind_dir_avg)/len(self.wind_dir_avg)) % 360
                    self.wind_vel[1] = self.wind_vel[0]
                    self.wind_dir[1] = self.wind_dir[0]
                    
                    # if 1 min avg exceeds value, keep alert
                    if self.wind_vel[1] > self.cut_out:
                        self.mode = 1
        except: # non-existant file
            pass

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
            self.wind_vel[0] = (self.wind_vel[0]*length + c_vel)/(length+1)
            self.wind_dir[0] = ((self.wind_dir[0]*length + c_dir)/(length+1)) % 360
            self.wind_vel[1] = (self.wind_vel[1]*length + c_vel)/(length+1)
            self.wind_dir[1] = ((self.wind_dir[1]*length + c_dir)/(length+1)) % 360
            
        elif length >= 60 and length < 600:
            self.wind_vel[0] = (self.wind_vel[0]*length + c_vel)/(length+1)
            self.wind_dir[0] = ((self.wind_dir[0]*length + c_dir)/(length+1)) % 360
            self.wind_vel[1] = (self.wind_vel[1]*60 - old_vel2 + c_vel)/60
            self.wind_dir[1] = ((self.wind_dir[1]*60 - old_dir2 + c_dir)/60) % 360
            
        elif length >= 600:
            self.wind_vel[0] = (self.wind_vel[0]*600 - old_vel1 + c_vel)/600
            self.wind_dir[0] = ((self.wind_dir[0]*600 - old_dir1 + c_dir)/600) % 360
            self.wind_vel[1] = (self.wind_vel[1]*60 - old_vel2 + c_vel)/60
            self.wind_dir[1] = ((self.wind_dir[1]*60 - old_dir2 + c_dir)/60) % 360
            
        else:
            # only one element, which is set as current average too
            self.wind_vel[0] = c_vel
            self.wind_dir[0] = c_dir % 360
            self.wind_vel[1] = c_vel
            self.wind_dir[1] = c_dir % 360

        # setting mode of operation
        if self.wind_vel[1] > self.cut_out or self.wind_vel[0] > self.cut_out: # cutout wind speed
            self.mode = 1
        else:
            self.mode = 0

        self.counter += 1
            
    # updates all values, puts into csv
    def update_values(self):
        # getting current data
        cur_wind_vel = self.wind_vel_ch.voltage/3.3*50
        cur_wind_dir = (self.wind_dir_ch.voltage/3.3*360) % 360
        
        # check stuff for IRE, not analog inputs
        self.nacelle_dir = (self.nacelle_dir_ch.voltage/3.3*360) % 360
        self.machine_vel = self.machine_vel_ch.voltage/3.3*50 # fix the constants accordingly
        
        # setting global averages and mode according to mode set and updating lists 
        self.update_avg(cur_wind_vel, cur_wind_dir)

        # writing into csv file every minute(to be modified accordingly)
        if self.counter >= 60:
            self.counter = 0
            l = [time.time(),
                cur_wind_vel,
                cur_wind_dir,
                self.machine_vel,
                self.nacelle_dir]
            with open('wind_data.csv', 'a+') as f:
                writer_obj = writer(f)
                writer_obj.writerow(l)
                f.close()

        print("10 min average speed, dir:", self.wind_vel[0], self.wind_dir[0])
        print("1 min average speed, dir:", self.wind_vel[1], self.wind_dir[1])
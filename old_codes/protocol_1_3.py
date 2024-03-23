#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
from csv import writer
from csv import reader

# global variables
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# communication channels
wind_dir_ch = AnalogIn(ads, ADS.P0)
wind_vel_ch = AnalogIn(ads, ADS.P1)

class protocol_1_3:
    # setup function basically, since using OOPs
    def __init__(self):
        # defining pins (BCM mode)
        self.switching_pin = 17
        self.breaking_pin = 27

        # initialize relevant variables
        self.start_time = time.time()
        self.wind_speed = 0
        self.wind_dir = 0
        self.break_status = 1
        self.machine_status = 0
        self.running_speed_avg = []
        self.running_dir_avg = []

        # GPIO modes for the raspi
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.switching_pin, GPIO.OUT)
        GPIO.setup(self.breaking_pin, GPIO.OUT)
        GPIO.output(self.switching_pin, GPIO.LOW)
        GPIO.output(self.breaking_pin, GPIO.HIGH)

    # to be called every 10 seconds (rn)
    def update_values(self):
        # getting current data and appending to avg_lists
        wind_speed = wind_vel_ch.voltage/3.3*50
        wind_dir = wind_dir_ch.voltage/3.3*360
        self.running_speed_avg.append(wind_speed)
        self.running_dir_avg.append(wind_sir)

        # printing relevant data
        l = [time.time(), wind_speed, wind_dir, self.machine_status, self.break_status]
        t = (time.time() - self.start_time)
        print("time elapsed:", t//60, 'm', int(t%60), 's')
        print("current speed, dir:", wind_speed, wind_dir)

        # writing into csv file
        with open('html/wind_data.csv', 'a+') as f:
            writer_obj = writer(f)
            writer_obj.writerow(l)
            f.close()

        # setting global averages once a minute passes (6 = 60/10)
        if(len(self.running_speed_avg) >= 6):
            # set the control variables to averages
            self.wind_speed = sum(self.running_speed_avg)/6
            self.wind_dir = sum(self.running_dir_avg)/6
            
            # set averages to null
            self.running_speed_avg = []
            self.running_dir_avg = []

        print("average speed, dir:", self.wind_speed, self.wind_dir)

    # loop which runs throughout
    def loop(self):
        # at each loop instance, get updated values (with added condition for time interval)
        self.update_values()

        # cut in commands
        if self.wind_speed < 1.3:
            # turn OFF motor and turn ON breaks
            GPIO.output(self.switching_pin, GPIO.LOW)
            time.sleep(1) # time delay for safety
            GPIO.output(self.breaking_pin, GPIO.HIGH)
            print("Cut IN commands")
            print("machine OFF \nbreaks ON")
            self.break_status = 1
            self.machine_status = 0
            time.sleep(9) # in total 10 seconds delay

        # normal working
        elif self.wind_speed > 1.3 and self.wind_speed < 9:
            # turn ON motor and turn OFF breaks
            GPIO.output(self.switching_pin, GPIO.HIGH)
            GPIO.output(self.breaking_pin, GPIO.LOW)
            print("Normal wind speed")
            print("machine ON \nbreaks OFF")
            self.break_status = 0
            self.machine_status = 1
            time.sleep(10)

        # cut out commands
        else:
            '''print("checking rpm for protocol 3")
            # protocol 3 controls with ire data
            if self.main_shaft_rpm > 45:
                # turn OFF motor and turn ON breaks
                GPIO.output(self.switching_pin, GPIO.LOW)
                time.sleep(1) # time delay for safety
                GPIO.output(self.breaking_pin, GPIO.HIGH)
                print("working protocol 3")'''
            # turn OFF motor and turn ON breaks
            GPIO.output(self.switching_pin, GPIO.LOW)
            time.sleep(1) # time delay for safety
            GPIO.output(self.breaking_pin, GPIO.HIGH)
            print("Cut OUT command")
            print("Machine OFF \nbreaks ON")
            self.break_status = 1
            self.machine_status = 0
            time.sleep(10)

        print()

if __name__ == '__main__':
    protocol_testing_object = protocol_1_3() # runs the __init__ function = setup
    print("initialising...")
    print("machine OFF \nbreaks ON\n")
    try:
        while True:
            protocol_testing_object.loop()
    except KeyboardInterrupt:
        GPIO.cleanup()


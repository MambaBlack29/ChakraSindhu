#!/usr/bin/env python3

from update import *
# YAW ONLY WHEN MOTOR STOPS

# global variables
shadow_A = 0
shadow_B = 120
yaw_error_cutoff = 5

class yaw:
    
    # setup function basically, since using OOPs
    def __init__(self):
        self.sense = 0
        self.base = update() # update object

    #Possible changes here in +/- and degrees [5.95, 6]
    def yawing(self, t, direction):
        if direction == 1:
            #anticlockwise yaw
            GPIO.output(self.base.acw_contactor, GPIO.HIGH)
            GPIO.output(self.base.cw_contactor, GPIO.LOW)
            print("rotating anticlockwise..")
            self.base.nacelle_dir = (self.base.nacelle_dir - t*1.92*5.95)%360 #TEMPORARY
            
        elif direction == -1:
            #clockwise yaw
            GPIO.output(self.base.acw_contactor, GPIO.LOW)
            GPIO.output(self.base.cw_contactor, GPIO.HIGH)
            print("rotating clockwise..")
            self.base.nacelle_dir = (self.base.nacelle_dir + t*1.92*5.95)%360
            
        time.sleep(t)
    
    #calculates yawing sense and yawing time
    def yaw_finder(self, error, flag=0):
        if not flag:
            if(self.base.nacelle_dir > self.base.wind_dir):
                t = error/6/1.92
                print("rotating for %5.3f seconds" % (t))
                self.yawing(t, 1)
            else:
                t = error/6/1.92
                print("rotating for %5.3f seconds" % (t))
                self.yawing(t, -1)
        else:
            if(self.base.nacelle_dir > self.base.wind_dir):
                t = error/6/1.92
                print("rotating for %5.3f seconds" % (t))
                self.yawing(t, -1)
            else:
                t = error/6/1.92
                print("rotating for %5.3f seconds" % (t))
                self.yawing(t, 1)
        
    # Check if wind is in shadow sector
    def is_Shadow(self):
        # sense = 0: outside shadow, 1: top half (near shadow_A), 2: bottom half (near shadow_B)
        mid = 1.0*(shadow_B + shadow_A)/2
        if((self.base.wind_dir >= shadow_A) and (self.base.wind_dir < mid)): # [A,mid)
            self.sense = 1
        elif((self.base.wind_dir <= shadow_B) and (self.base.wind_dir >= mid)): # [mid,B]
            self.sense = 2
        else:
            self.sense = 0    
        
    # loop which runs throughout
    def loop(self):
        # at each loop instance, get updated values (with added condition for time interval)
        self.update_values()
        is_Shadow()
        
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

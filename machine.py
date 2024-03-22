#!/usr/bin/env python3

from update import *

base = update() # update class variable

class protocol_1_3:
    # loop which runs throughout
    def loop(self):
        # at each loop instance, get updated values (with added condition for time interval)
        base.update_values()

        # cut in commands
        if base.wind_speed < 1.3:
            # turn OFF motor and turn ON breaks
            GPIO.output(base.switching_pin, GPIO.LOW)
            time.sleep(1) # time delay for safety
            GPIO.output(base.breaking_pin, GPIO.HIGH)
            print("Cut IN commands")
            print("machine OFF \nbreaks ON")
            base.break_status = 1
            base.machine_status = 0
            time.sleep(9) # in total 10 seconds delay

        # normal working
        elif base.wind_speed > 1.3 and base.wind_speed < 9:
            # turn ON motor and turn OFF breaks
            GPIO.output(base.switching_pin, GPIO.HIGH)
            GPIO.output(base.breaking_pin, GPIO.LOW)
            print("Normal wind speed")
            print("machine ON \nbreaks OFF")
            base.break_status = 0
            base.machine_status = 1
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
            GPIO.output(base.switching_pin, GPIO.LOW)
            time.sleep(1) # time delay for safety
            GPIO.output(base.breaking_pin, GPIO.HIGH)
            print("Cut OUT command")
            print("Machine OFF \nbreaks ON")
            base.break_status = 1
            base.machine_status = 0
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


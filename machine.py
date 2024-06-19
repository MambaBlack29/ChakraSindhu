'''
All functions will have a 'data' variable = update object passed through main.py
Update object has all necessary functions/variables needed to find logic and output
'''

from update import update

class machine:
    '''
    Machine object to control the Turbine based on wind speed and machine speed
    Control the motor and brake based on the wind speed and machine speed
    
    Attributes:
    ----------
    data: object of update class
    rpm_cut_out: int, constant value for cut_out speed of the machine
    motor: int, 0 or 1, 0 for OFF and 1 for ON
    brake: int, 0 or 1, 0 for OFF and 1 for ON
    extreme: int, 0 or 1, 0 for normal and 1 for extreme conditions
    '''
    def __init__(self, update_obj: update):
        '''
        Initialize the machine object with the update object
        '''
        # processed input data from update.py and mode from main.py
        self.data = update_obj

        # global constants to be used in here
        self.rpm_cut_out = 45

        # global variables which are set after finding the logic
        self.motor = 0
        self.brake = 1
        self.extreme = 0

    def get_machine_brake(self):
        '''
        based on direct wind speed and parsed mode data
        
        Underspeed control:
        Keeps motor OFF and brake ON when wind speed is less than cut-in speed
        Keeps motor ON and brake OFF when wind speed is between cut-in and cut-out speeds
        Overspeed control:
        Keeps motor OFF and brake ON when wind speed is more than cut-out speed
        '''
        # keep motor OFF and brake ON when slower than cut_in speed
        if self.data.wind_vel[self.data.mode] < self.data.cut_in:
            self.motor = 0
            self.brake = 1
            self.extreme = 0
        # check whether motor speed is relevant or not
        elif self.data.wind_vel[self.data.mode] >= self.data.cut_in:
            if self.data.mode == 0: # less than cut_out speed
                self.motor = 1
                self.brake = 0
                self.extreme = 0
            else:
                # overspeed and extreme control
                if self.data.machine_vel >= self.rpm_cut_out:
                    self.motor = 0
                    self.brake = 1
                    if self.data.wind_vel[self.data.mode] >= self.data.extreme_wind:
                        self.extreme = 1
                    else:
                        self.extreme = 0
                # not overspeed, but will keep observing
                else:
                    self.motor = 1
                    self.brake = 0
                    self.extreme = 0
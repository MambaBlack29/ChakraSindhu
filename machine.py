'''
All functions will have a 'data' variable = update object passed through main.py
Update object has all necessary functions/variables needed to find logic and output
'''

class machine:
    def __init__(self, update_obj):
        # processed input data from update.py and mode from main.py
        self.data = update_obj

        # global variables used here and there
        self.cut_in = 1.3
        self.extreme_wind = 15
        self.rpm_cut_out = 45

        # global variables which are set after finding the logic
        self.motor = 0
        self.brake = 1
        self.extreme = 0
        self.stopped = 0

    # based on direct wind speed and parsed mode data
    def get_machine_brake(self):
        # keep motor OFF and brake ON when slower than cut_in speed
        if self.data.wind_vel[self.data.mode] < self.cut_in:
            self.motor = 0
            self.brake = 1
            self.extreme = 0
        # check whether motor speed is relevant or not
        elif self.data.wind_vel[self.data.mode] >= self.cut_in:
            if self.data.mode == 0: # less than cut_out speed
                self.motor = 1
                self.brake = 0
                self.extreme = 0
            else:
                # overspeed and extreme control
                if self.data.machine_vel >= self.rpm_cut_out:
                    self.motor = 0
                    self.brake = 1
                    if self.data.wind_vel[self.data.mode] >= self.extreme_wind:
                        self.extreme = 1
                    else:
                        self.extreme = 0
                # not overspeed, but will keep observing
                else:
                    self.motor = 1
                    self.brake = 0
                    self.extreme = 0
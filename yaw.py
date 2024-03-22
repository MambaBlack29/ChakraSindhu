'''
All functions will have a 'data' variable = update object passed through main.py
Update object has all necessary functions/variables needed to find logic and output
'''

class yaw:
    # setup function with relevant variable declarations
    def __init__(self, update_obj):
        # processed input data from update.py and mode from main.py
        self.data = update_obj

        # global variables used here and there
        self.shadow_A = 240
        self.shadow_B = 360
        self.yaw_tolerance = 5

        # global variables which are set after using the finding the logic
        self.shadow_sense = 0 # 0: not in shadow, 1: between shadow_A and mid, 2: between mid and shadow_B
        self.direction = 0 # 0: clockwise, 1: anticlockwise
        self.error = 0
    
    # finds whether the wind vane is in the shadow sector or not
    def is_shadow(self):
        # using the global shadow_sense variable since data changes to be made to that
        mid = 1.0*(self.shadow_B + self.shadow_A)/2
        # [A,mid)
        if((self.data.wind_dir[self.data.mode] >= self.shadow_A) and (self.data.wind_dir[self.data.mode] < mid)):
            self.shadow_sense = 1
        # [mid,B]
        elif((self.data.wind_dir[self.data.mode] <= self.shadow_B) and (self.data.wind_dir[self.data.mode] >= mid)):
            self.shadow_sense = 2
        else:
            self.shadow_sense = 0
    
    # finds the error and direction to go to based on where the vane is, used by main
    def get_error_direction(self):
        # figures whether it is in shadow region or not
        self.is_shadow()

        # error = nacelle - avg_error
        if self.shadow_sense == 0:
            self.error = abs(self.data.nacelle_dir - self.data.wind_dir[self.data.mode]) % 360
            if self.data.nacelle_dir > self.data.wind_dir[self.data.mode]:
                # should rotate clockwise
                self.direction = 0
            else:
                # should rotate anticlockwise
                self.direction = 1
        # error based on where in the shadow sector
        elif self.shadow_sense == 1:
            self.error = abs(self.data.nacelle_dir - self.shadow_A) % 360
            self.direction = 1 
        else:
            # veify once again with updated shadow angles
            self.error = abs(self.data.nacelle_dir - self.shadow_B) % 360
            self.direction = 0
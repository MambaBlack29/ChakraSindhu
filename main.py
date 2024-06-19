'''
Main file which compiles everything and manages all the control decisions
Gets inputs from update file
Gets logical made by yaw and machine files
Sends output from out file
'''

import asyncio
import update
import out
import machine
import yaw

class main:
    '''
    Attributes:
    ----------
    update_obj: object of update class
    yaw_obj: object of yaw class
    machine_obj: object of machine class
    out_obj: object of out class
    '''
    def __init__(self):
        '''
        Initialize all the objects and variables
        '''
        
        self.update_obj = update.update()
        self.yaw_obj = yaw.yaw()
        self.machine_obj = machine.machine()
        self.out_obj = out.out()

        self.update_obj.update_values()
    
    # loop function, runs infinitely later on
    async def loop(self):
        '''
        An async function which runs infinitely, updating all the values and making decisions
        '''
        # create async delay object to get exactly 1 second delay
        delay_coroutine = asyncio.sleep(1)

        # get the data from update
        self.update_obj.update_values()

        # based on the data, make changes in the logical variables
        self.machine_obj.get_machine_brake()
        self.yaw_obj.get_error_direction()

        # now we have all the data, we can call output functions based on control values
        # non extreme working conditions
        if self.update_obj.mode == 0:
            # avg direction of wind is more than tolerable
            if self.yaw_obj.error > self.yaw_obj.yaw_tolerance_check:
                # brake until motor off
                while self.update_obj.machine_vel > 0:
                    self.out_obj.brake_on()
                    self.update_obj.update_values()
                # yaw until error within tolerance
                while self.yaw_obj.error > self.yaw_obj.yaw_tolerance_update:
                    self.out_obj.yaw_out()
                    self.update_obj.update_values()
            
            # in either case, after error correction, run machine normally
            self.out_obj.machine_out()
        
        # extreme or abornal conditions
        else:
            # if:
            pass

        # waits for the remainder of 1 second till ending loop function
        await delay_coroutine

if __name__ == '__main__':
    main_obj = main() # runs the __init__ function = setup
    try:
        while True:
            asyncio.run(main_obj.loop())
    except KeyboardInterrupt:
        main_obj.out_obj.cleanup()
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
    # setup function, creates objects of all relevant files
    def __init__(self):
        self.update_obj = update()
        self.yaw_obj = yaw()
        self.machine_obj = machine()
        self.out_obj = out()
    
    # loop function, runs infinitely later on
    async def loop(self):
        # create async delay object to get exactly 1 second delay
        delay_coroutine = asyncio.sleep(1)

        # get the data from update
        self.update_obj.update_values()

        # based on the data, make changes in the logical variables
        self.machine_obj.get_machine_brake()
        self.yaw_obj.get_error_direction()

        # now we have all the data, we can call output functions based on control values
        if self.machine_obj.extreme == 0:
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
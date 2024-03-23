# ChakraSindhu
The control codes for the Chakra Sindhu Project as part of the stage 5 work

---
## Code Structure
### 1. `update.py` 
- has all necessary variables and functions inside a class which are needed by all control protocols
- imported by the `main.py` file and made use of in all the other files
- takes in input and buffers it in a readable fashion

### 2. `machine.py` 
- has all necessary logical functions which are needed to control the main motor and the brakes
- makes use of the `update` class and functions from the `update.py` file
- sets all variables related to brake and main motor after determining operating conditions

### 3. `yaw.py`
- has all necessary logical functions which are needed to control the yaw motor
- makes use of the `update` class and functions from the `update.py` file
- sets all variables related to yaw-contactors after determining operating conditions

### 4. `out.py`
- needs `machine` and `yaw` objects in order to make use of variables associated with actuators
- flushes the pre-determined logical output onto real actuators
- called by the `main.py` file

### 5. `main.py`
- imports all the files above and creates their objects
- makes the final control decisions and calls the output functions accordingly
- only this file is run

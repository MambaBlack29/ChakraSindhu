# ChakraSindhu
The control codes for the Chakra Sindhu Project as part of the stage 5 work

---
## Code Structure
# 1. `update.py` 
- has all necessary variables and functions inside a class which are needed by all control protocols
- imported by the `main.py` file and made use of in all the other files

# 2. `machine.py` 
- has all necessary logical functions which are needed to control the main motor and the breaks
- makes use of the `update` class and functions from the `update.py` file

# 3. 'yaw.py`
- has all necessary logical functions which are needed to control the yaw motor
- makes use of the `update` class and functions from the `update.py` file
- has both `yaw` and `anti_yaw` functions which are called for normal and extreme weather conditions respectively

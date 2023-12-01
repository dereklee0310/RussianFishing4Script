"""
    Functionality:
        1. Activate game window (if any)
        2. Start moving forward
        3. press w to toggle/untoggle moving, and press s to quit
    Todo:
        Handle the exception for non-existing game window
        Update setup.py to initialize config.ini properly
"""

from pyautogui import *
from time import sleep
from windowcontroller import WindowController
from pynput import keyboard 
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')

# show prompt and count down
if not config['misc'].getboolean('disable_count_down'):
    print('Press S to terminate the script')
    for i in range(3, 0, -1):
        print(f'The script will start in: {i} seconds', end='\r')
        sleep(1)

# activate the game window
controller = WindowController('Russian Fishing 4')
controller.activate_game_window()

sleep(0.25)

# start moving
if not config['misc'].getboolean('running_by_default'):
    keyDown('shift')
keyDown('w')

# main keyboard listener loop
stop_flag = False
while True:
    with keyboard.Events() as events:
        event = events.get(1.0) # block at most one second
        if not event or type(event) == keyboard.Events.Release:
            continue

        key = str(event.key).lower()
        if key == "'s'":
            break
        elif key == "'w'": # \'w\'
            if not stop_flag:
                stop_flag = True
                keyUp('w')
            else:
                stop_flag = False
                sleep(0.25) # this must be added to function correctly
                keyDown('w')

# stop moving
if not config['misc'].getboolean('running_by_default'):
    keyUp('shift')
keyUp('w')

# controller.activate_script_window() # reactivate the terminal
print(end='\x1b[2K')
print('The script has been terminated', end='')

# ANSI erase reference: https://itnext.io/overwrite-previously-printed-lines-4218a9563527
# pynput reference: https://pynput.readthedocs.io/en/latest/keyboard.html
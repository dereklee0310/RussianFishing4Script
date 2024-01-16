"""
Activate game window and start making things until running out of materials.

Usage: make.py
"""
from time import sleep

from pyautogui import *

from monitor import *
from script import activate_game_window
    
if __name__ == '__main__':
    activate_game_window()
    moveTo(get_make_position())
    try:
        while True:
            click() # click make button

            # recipe is not complete
            if is_operation_failed():
                press('space')
                break
            
            # waiting for result
            sleep(4)
            while not get_ok_position() and not is_operation_failed():
                sleep(0.25)
            press('space')
            sleep(0.1)
    except KeyboardInterrupt:
        exit()
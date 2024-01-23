"""
Activate game window and start making things until running out of materials.

Usage: make.py
"""
from time import sleep

from pyautogui import *

from windowcontroller import WindowController
from monitor import *
from script import is_countdown_enabled, start_count_down
    
if __name__ == '__main__':
    if is_countdown_enabled():
        print('Navigate to the making menu and select the materials before you start')
        start_count_down()

    controller = WindowController()
    controller.activate_game_window()

    moveTo(get_make_position())
    try:
        while True:
            click() # click make button
            # recipe is not complete
            if is_operation_failed():
                press('space')
                break
            # wait for result
            sleep(4)
            while not get_ok_position() and not is_operation_failed():
                sleep(0.25)
            press('space')
            sleep(0.1)
    except KeyboardInterrupt:
        exit()
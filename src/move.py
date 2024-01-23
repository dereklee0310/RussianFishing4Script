"""
Activate game window and start moving forward.

Usage: move.py, press w to toggle/untoggle moving, and press s to quit
"""
from time import sleep

from pyautogui import *
from pynput import keyboard 

from windowcontroller import WindowController
from script import is_countdown_enabled, start_count_down, is_running_enabled

if __name__ == '__main__':
    if is_countdown_enabled():
        print('Press W to toggle/untoggle moving, S to terminate the script')
        start_count_down()

    controller = WindowController()
    controller.activate_game_window()

    # start moving
    if not is_running_enabled():
        keyDown('shift')
    keyDown('w')

    # keyboard listener loop
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
    if not is_running_enabled():
        keyUp('shift')
    keyUp('w')

    print(end='\x1b[2K')
    print('The script has been terminated', end='')

# ANSI erase reference: https://itnext.io/overwrite-previously-printed-lines-4218a9563527
# pynput reference: https://pynput.readthedocs.io/en/latest/keyboard.html
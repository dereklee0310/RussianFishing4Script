"""
Activate game window and start moving forward.

Usage: move.py, press W to toggle/untoggle moving, S to quit
"""
from time import sleep

import argparse
from pyautogui import keyDown, keyUp
from pynput import keyboard

from windowcontroller import WindowController
from script import is_countdown_enabled, start_count_down

def parse_args() -> argparse.Namespace:
    """Cofigure argparser and parse the command line arguments.

    :return dict-like object of parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
                        prog='move.py', 
                        description='Activate game window and start moving forward', 
                        epilog='')
    parser.add_argument('-s', '--shift', action='store_true',
                        help="Hold Shift key while moving forward")
    return parser.parse_args()

if __name__ == '__main__':
    # must be parsed first to display help information
    enable_shift_holding = parse_args().shift

    if is_countdown_enabled():
        print('Press W to toggle/untoggle moving, S to terminate the script')
        start_count_down()

    controller = WindowController()
    controller.activate_game_window()
    print('The script has been started')

    if enable_shift_holding:
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
                    sleep(0.25) # this must be added wtf?
                    keyDown('w')

    keyUp('w')
    if enable_shift_holding:
        keyUp('shift')

    print(end='\x1b[2K')
    print('The script has been terminated', end='')

# ANSI erase reference: https://itnext.io/overwrite-previously-printed-lines-4218a9563527
# pynput reference: https://pynput.readthedocs.io/en/latest/keyboard.html
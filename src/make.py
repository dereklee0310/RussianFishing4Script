"""
Activate game window and start crafting things until running out of materials.

Usage: make.py
"""
from time import sleep
import argparse

from pyautogui import *

from windowcontroller import WindowController
from monitor import *
from script import is_countdown_enabled, start_count_down

def parse_args() -> argparse.Namespace:
    """Cofigure argparser and parse the command line arguments.

    :return dict-like object of parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
                        prog='make.py', 
                        description='Activate game window and start making things until running out of materials', 
                        epilog='')
    parser.add_argument('-n', '--quantity', type=int, default=-1,
                            help='the number of item to craft, no limit by default')
    return parser.parse_args()

    
if __name__ == '__main__':
    limit = parse_args().quantity
    print(limit)

    if is_countdown_enabled():
        print('Navigate to the making menu and select the materials before you start')
        start_count_down()

    controller = WindowController()
    controller.activate_game_window()

    count = 0
    moveTo(get_make_position())
    try:
        while True:
            click() # click make button

            # recipe not complete, fail immediately
            if is_operation_failed():
                press('space')
                break

            # wait for result
            sleep(4)
            while not get_ok_position() and not is_operation_failed():
                sleep(0.25)
            press('space')
            sleep(0.1)

            count += 1
            if count == limit:
                break
    except KeyboardInterrupt:
        exit()
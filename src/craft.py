"""
Activate game window and start crafting things until running out of materials.

Usage: make.py
"""
from time import sleep
import argparse

import pyautogui as pag

from windowcontroller import WindowController
from monitor import get_make_position, is_operation_failed, get_ok_position
from script import ask_for_confirmation

def parse_args() -> argparse.Namespace:
    """Cofigure argparser and parse the command line arguments.

    :return dict-like object of parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
                        prog='make.py', 
                        description='Activate game window and start making things until running out of materials', 
                        epilog='')
    parser.add_argument('-d', '--discard', action='store_true',
                            help='discard all the crafted items')
    parser.add_argument('-n', '--quantity', type=int, default=-1,
                            help='the number of item to craft, no limit if not specified')
    return parser.parse_args()
    
if __name__ == '__main__':
    args = parse_args()
    limit = args.quantity
    enable_discard = args.discard
    count = 0

    ask_for_confirmation('Are you ready to start crafting')
    WindowController().activate_game_window()

    pag.moveTo(get_make_position())
    try:
        while True:
            pag.click() # click make button

            # recipe not complete
            if is_operation_failed():
                pag.press('space')
                break

            # crafting, wait for result
            sleep(4)
            while (not get_ok_position() and 
                   not is_operation_failed()):
                sleep(0.25)

            # handle result
            key = 'backspace' if enable_discard else 'space'
            pag.press(key)
            sleep(0.1)
            count += 1
            if count == limit:
                break
    except KeyboardInterrupt:
        pass
    print('The bot has been terminated')
    print('Number of crafted items:', count)
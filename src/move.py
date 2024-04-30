"""
Activate game window and start moving forward.

Usage: move.py, press W to toggle moving, S to quit
"""
import argparse
import pyautogui as pag
from pynput import keyboard

from windowcontroller import WindowController
from script import ask_for_confirmation

holding_w = True # w key will be pressed first

def on_press(key: keyboard.KeyCode) -> None:
    """Callback for pressing button.

    :param key: key code used by OS
    :type key: keyboard.KeyCode
    """
    if str(key) == "'s'":
        exit()

def on_release(key: keyboard.KeyCode) -> None:
    """Callback for releasing button, including w key toggle control.

    :param key: key code used by OS
    :type key: keyboard.KeyCode
    """
    global holding_w
    if str(key) != "'w'":
        return
    elif holding_w == True:
        holding_w = False
        return

    pag.keyDown('w')
    holding_w = True

def parse_args() -> argparse.Namespace:
    """Cofigure argparser and parse the command line arguments.

    :return dict-like parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
                        prog='move.py',
                        description='Activate game window and start moving forward',
                        epilog='')
    parser.add_argument('-s', '--shift', action='store_true',
                        help="Hold Shift key while moving")
    return parser.parse_args()

if __name__ == '__main__':
    # must be parsed first to display help information
    enable_shift_holding = parse_args().shift

    ask_for_confirmation('Are you ready to start moving')
    WindowController().activate_game_window()

    if enable_shift_holding:
        pag.keyDown('shift')
    pag.keyDown('w')

    # blocking listener loop
    with keyboard.Listener( on_press=on_press, on_release=on_release) as listener:
        listener.join()

    pag.keyUp('w')
    if enable_shift_holding:
        pag.keyUp('shift')

# press/release detection: https://stackoverflow.com/questions/65890326/keyboard-press-detection-with-pynput
# listner loop : https://stackoverflow.com/questions/75784939/pynput-difference-between-listener-join-and-listener-start
# ANSI erase : https://itnext.io/overwrite-previously-printed-lines-4218a9563527
# pynput : https://pynput.readthedocs.io/en/latest/keyboard.html
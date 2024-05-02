"""
Activate game window and start moving forward.

Usage: move.py, press W to toggle moving, S to quit
"""
import sys
import argparse
import pyautogui as pag
from pynput import keyboard

from windowcontroller import WindowController
from script import ask_for_confirmation

def on_press(key: keyboard.KeyCode) -> None:
    """Callback for pressing button.

    :param key: key code used by OS
    :type key: keyboard.KeyCode
    """
    if str(key).lower() == "'s'":
        sys.exit()


def on_release(key: keyboard.KeyCode) -> None:
    """Callback for releasing button, including w key toggle control.

    :param key: key code used by OS
    :type key: keyboard.KeyCode
    """
    global w_holding
    if str(key).lower() != "'w'":
        return

    if w_holding:
        w_holding = False
        return

    pag.keyDown('w')
    w_holding = True


def parse_args() -> argparse.Namespace:
    """Cofigure argparser and parse the command line arguments.

    :return dict-like parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description='Moving the game character forward with W key.'
    )
    parser.add_argument(
        '-s', '--shift', action='store_true',
        help='Hold Shift key while moving'
    )
    return parser.parse_args()


if __name__ == '__main__':
    shift_holding_enabled = parse_args().shift

    ask_for_confirmation('Are you ready to start moving')
    WindowController().activate_game_window()

    if shift_holding_enabled:
        pag.keyDown('shift')
    pag.keyDown('w')
    w_holding = True

    # blocking listener loop
    with keyboard.Listener(on_press, on_release) as listener:
        listener.join()

    pag.keyUp('w')
    if shift_holding_enabled:
        pag.keyUp('shift')

# press/release detection: https://stackoverflow.com/questions/65890326/keyboard-press-detection-with-pynput
# listner loop : https://stackoverflow.com/questions/75784939/pynput-difference-between-listener-join-and-listener-start
# ANSI erase : https://itnext.io/overwrite-previously-printed-lines-4218a9563527
# pynput : https://pynput.readthedocs.io/en/latest/keyboard.html
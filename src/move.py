"""
Activate game window and start moving forward.

Usage: move.py, press W to toggle moving, S to quit
"""

import sys
import argparse
import pyautogui as pag
from pynput import keyboard

from windowcontroller import WindowController  # pylint: disable=c-extension-no-member
from script import ask_for_confirmation


class App:
    """Main application class."""

    def __init__(self):
        """Initialize moving flag."""
        self.w_key_pressed = False

    def parse_args(self) -> argparse.Namespace:
        """Cofigure argparser and parse the command line arguments.

        :return dict-like parsed arguments
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(
            description="Moving the game character forward with W key."
        )
        parser.add_argument(
            "-s", "--shift", action="store_true", help="Hold Shift key while moving"
        )
        return parser.parse_args()

    def on_press(self, key: keyboard.KeyCode) -> None:
        """Callback for pressing button.

        :param key: key code used by OS
        :type key: keyboard.KeyCode
        """
        if str(key).lower() == "'s'":
            sys.exit()

    def on_release(self, key: keyboard.KeyCode) -> None:
        """Callback for releasing button, including w key toggle control.

        :param key: key code used by OS
        :type key: keyboard.KeyCode
        """
        if str(key).lower() != "'w'":
            return

        if w_key_pressed:
            w_key_pressed = False
            return

        pag.keyDown("w")
        w_key_pressed = True


if __name__ == "__main__":
    app = App()
    shift_holding_enabled = app.parse_args().shift

    ask_for_confirmation("Are you ready to start moving")
    WindowController().activate_game_window()

    if shift_holding_enabled:
        pag.keyDown("shift")
    pag.keyDown("w")

    # blocking listener loop
    with keyboard.Listener(app.on_press, app.on_release) as listener:
        listener.join()

    pag.keyUp("w")
    if shift_holding_enabled:
        pag.keyUp("shift")

# press/release detection
# https://stackoverflow.com/questions/65890326/keyboard-press-detection-with-pynput
# listner loop
# https://stackoverflow.com/questions/75784939/
# ANSI erase
# https://itnext.io/overwrite-previously-printed-lines-4218a9563527
# pynput
# https://pynput.readthedocs.io/en/latest/keyboard.html

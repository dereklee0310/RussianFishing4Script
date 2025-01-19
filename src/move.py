"""
Activate game window and start moving forward.

Usage: move.py, press W to toggle moving, S to quit
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly

import argparse
import sys

import pyautogui as pag
from pynput import keyboard

import script

# ------------------ flag name, attribute name, description ------------------ #
ARGS = (("shift", "shift_key_holding_enabled", "_"),)


class App:
    """Main application class."""

    @script.initialize_setting_and_monitor(ARGS)
    def __init__(self):
        """Initialize moving flag."""
        self.w_key_pressed = True

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

        if self.w_key_pressed:
            self.w_key_pressed = False
            return

        pag.keyDown("w")
        self.w_key_pressed = True

    @script.release_keys_after
    def start(self):
        if self.setting.shift_key_holding_enabled:
            pag.keyDown("shift")
        pag.keyDown("w")

        # blocking listener loop
        with keyboard.Listener(self.on_press, self.on_release) as listener:
            listener.join()


if __name__ == "__main__":
    script.start_app(App(), None)

# press/release detection
# https://stackoverflow.com/questions/65890326/keyboard-press-detection-with-pynput
# listner loop
# https://stackoverflow.com/questions/75784939/
# ANSI erase
# https://itnext.io/overwrite-previously-printed-lines-4218a9563527
# pynput
# https://pynput.readthedocs.io/en/latest/keyboard.html

"""
Activate game window and start moving forward.

Usage: move.py, press W to toggle moving, S to quit
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly

import argparse
import sys
from pathlib import Path

import pyautogui as pag
from pynput import keyboard
from yacs.config import CfgNode as CN

sys.path.append(".")

import argparse

from rf4s import utils
from rf4s.config import config
from rf4s.controller.window import Window

ROOT = Path(__file__).resolve().parents[1]


class App:
    """Main application class."""

    def __init__(self):
        self.cfg = config.setup_cfg()
        self.cfg.merge_from_file(ROOT / "config.yaml")
        args = self.parse_args()
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(args.opts)

        # Dummy mode
        dummy = CN({"SELECTED": config.dict_to_cfg({"MODE": "spin"})})
        self.cfg.merge_from_other_cfg(dummy)

        # Format key
        self.cfg.ARGS.EXIT_KEY = f"'{self.cfg.ARGS.EXIT_KEY}'"
        self.cfg.ARGS.PAUSE_KEY = f"'{self.cfg.ARGS.PAUSE_KEY}'"

        self.cfg.freeze()

        self.window = Window()
        self.w_key_pressed = True


    def parse_args(self) -> argparse.Namespace:
        """Cofigure argparser and parse the command line arguments.

        :return dict-like parsed arguments
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(
            description="Moving the game character forward with W key."
        )
        parser.add_argument("opts", nargs="*", help="overwrite configuration")
        parser.add_argument(
            "-s", "--shift", action="store_true", help="Hold Shift key while moving"
        )
        parser.add_argument(
            "-e",
            "--exit-key",
            default="s",
            type=str,
            help="key to quit the script, s by default",
            metavar="KEY",
        )
        parser.add_argument(
            "-r",
            "--pause-key",
            default="w",
            type=str,
            help="key to pause the script, w by default",
            metavar="KEY",
        )
        return parser.parse_args()

    def on_release(self, key: keyboard.KeyCode) -> None:
        """Callback for releasing button, including w key toggle control.

        :param key: key code used by OS
        :type key: keyboard.KeyCode
        """
        if str(key).lower() == self.cfg.ARGS.EXIT_KEY:
            sys.exit()
        elif str(key).lower() == self.cfg.ARGS.PAUSE_KEY:
            if self.w_key_pressed:
                self.w_key_pressed = False
                return
            pag.keyDown("w")
            self.w_key_pressed = True

    @utils.release_keys_after
    def start(self):
        if self.cfg.ARGS.SHIFT:
            pag.keyDown("shift")
        pag.keyDown("w")

        # blocking listener loop
        with keyboard.Listener(self.on_release) as listener:
            listener.join()


if __name__ == "__main__":
    utils.start_app(App(), None)

# press/release detection
# https://stackoverflow.com/questions/65890326/keyboard-press-detection-with-pynput
# listner loop
# https://stackoverflow.com/questions/75784939/
# ANSI erase
# https://itnext.io/overwrite-previously-printed-lines-4218a9563527
# pynput
# https://pynput.readthedocs.io/en/latest/keyboard.html

"""Movement automation for Russian Fishing 4 using keyboard controls.

This module automates character movement in Russian Fishing 4 by simulating W key presses.
Supports toggling movement state and includes optional Shift key integration for sprinting.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

# pylint: disable=no-member

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
    """Main controller for movement automation in Russian Fishing 4.

    Manages configuration, keyboard event listeners, and W/Shift key simulation.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments.
        window (Window): Game window controller instance.
        w_key_pressed (bool): Tracks current state of W key simulation.
    """

    def __init__(self):
        """Initialize configuration, CLI arguments, and game window.

        Merges configurations from multiple sources (YAML, CLI) and prepares
        the game window controller.
        """
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
        """Parse command-line arguments.

        :return: Parsed arguments containing runtime configuration.
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
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
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
    def start(self) -> None:
        """Start automation and keyboard listener.

        Begins W key simulation (with optional Shift key) and enters blocking listener loop.
        Automatically releases keys when stopped via decorator.
        """
        if self.cfg.ARGS.SHIFT:
            pag.keyDown("shift")
        pag.keyDown("w")

        # blocking listener loop
        with keyboard.Listener(self.on_release) as listener:
            listener.join()


if __name__ == "__main__":
    utils.start_app(App(), None)

# (Original comments remain unchanged below)
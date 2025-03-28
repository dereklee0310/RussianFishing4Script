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

sys.path.append(".")

from rf4s import utils
from rf4s.app.app import App
from rf4s.config.config import print_cfg

ROOT = Path(__file__).resolve().parents[1]


class MoveApp(App):
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
        super().__init__()

        # Format key
        self.cfg.defrost()
        self.cfg.ARGS.EXIT_KEY = f"'{self.cfg.ARGS.EXIT_KEY}'"
        self.cfg.ARGS.PAUSE_KEY = f"'{self.cfg.ARGS.PAUSE_KEY}'"
        self.cfg.freeze()
        print_cfg(self.cfg.ARGS)

        self.w_key_pressed = True

    def _parse_args(self) -> argparse.Namespace:
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

    def _on_release(self, key: keyboard.KeyCode) -> None:
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

    @utils.release_keys_after(arrow_keys=True)
    def _start(self) -> None:
        """Start automation and keyboard listener.

        Begins W key simulation (with optional Shift key) and enters blocking listener loop.
        Automatically releases keys when stopped via decorator.
        """

        if self.cfg.ARGS.SHIFT:
            pag.keyDown("shift")
        pag.keyDown("w")

        # blocking listener loop
        with keyboard.Listener(on_release=self._on_release) as listener:
            listener.join()


if __name__ == "__main__":
    MoveApp().start()

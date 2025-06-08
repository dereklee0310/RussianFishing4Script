"""Movement automation for Russian Fishing 4 using keyboard controls.

This module automates character movement in Russian Fishing 4 by simulating W key presses.
Supports toggling movement state and includes optional Shift key integration for sprinting.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import argparse
import sys
from pathlib import Path

import pyautogui as pag
from pynput import keyboard
from rich import print

sys.path.append(".")
from rf4s import utils
from rf4s.app.app import ToolApp
from rf4s.config.config import print_cfg
from rf4s.utils import create_rich_logger, safe_exit, update_argv

ROOT = Path(__file__).resolve().parents[1]

logger = create_rich_logger()


class MoveApp(ToolApp):
    """Main controller for movement automation in Russian Fishing 4.

    Manages configuration, keyboard event listeners, and W/Shift key simulation.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments.
        w_key_pressed (bool): Tracks current state of W key simulation.
    """

    def __init__(self):
        """Initialize configuration, CLI arguments, and game window.

        1. Format keybinds in cfg node.
        2. Create w key flag.
        """
        super().__init__()

        # Format key
        self.cfg.defrost()
        self.cfg.ARGS.PAUSE_KEY = f"'{self.cfg.ARGS.PAUSE_KEY}'"
        self.cfg.ARGS.QUIT_KEY = f"'{self.cfg.ARGS.QUIT_KEY}'"
        self.cfg.freeze()
        print_cfg(self.cfg.ARGS)

        self.w_key_pressed = True

    def create_parser(self) -> argparse.ArgumentParser:
        """Create an argument parser for the application.

        :return: Configured argument parser.
        :rtype: argparse.ArgumentParser
        """
        parser = argparse.ArgumentParser(
            description="Moving the game character forward with W key."
        )
        parser.add_argument("opts", nargs="*", help="overwrite configuration")
        parser.add_argument(
            "-s", "--shift", action="store_true", help="Hold Shift key while moving"
        )
        parser.add_argument(
            "-p",
            "--pause-key",
            default="w",
            type=str,
            help="key to pause the script, w by default",
            metavar="KEY",
        )
        parser.add_argument(
            "-q",
            "--quit-key",
            default="s",
            type=str,
            help="key to quit the script, s by default",
            metavar="KEY",
        )
        return parser

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
        :type key: keyboard.KeyCode
        """
        if str(key).lower() == self.cfg.ARGS.QUIT_KEY:
            sys.exit()
        elif str(key).lower() == self.cfg.ARGS.PAUSE_KEY:
            if self.w_key_pressed:
                self.w_key_pressed = False
                return
            pag.keyDown("w")
            self.w_key_pressed = True

    @utils.release_keys_after(arrow_keys=True)
    def _start(self) -> None:
        """Start W key automation and keyboard listener."""
        print(
            f"Press {self.cfg.ARGS.PAUSE_KEY[1:-1]} to pause, "
            f"{self.cfg.ARGS.QUIT_KEY[1:-1]} to quit."
        )
        if self.cfg.ARGS.SHIFT:
            pag.keyDown("shift")
        pag.keyDown("w")
        # Blocking listener loop
        with keyboard.Listener(on_release=self._on_release) as listener:
            listener.join()


def run_app_from_main():
    try:
        MoveApp().start()
    except Exception as e:
        logger.critical(e, exc_info=True)
    safe_exit()


if __name__ == "__main__":
    update_argv()
    try:
        MoveApp().start()
    except Exception as e:
        logger.critical(e, exc_info=True)
    safe_exit()

"""Automate friction brake adjustments in Russian Fishing 4.

This module provides functionality to automatically adjust the friction brake
based on in-game conditions. It supports key bindings for exiting the script
and resetting the friction brake.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import argparse
import sys
from multiprocessing import Lock

from pynput import keyboard
from rich import print

sys.path.append(".")
from rf4s.app.app import ToolApp
from rf4s.component.friction_brake import FrictionBrake
from rf4s.config.config import print_cfg
from rf4s.utils import create_rich_logger, safe_exit, update_argv

logger = create_rich_logger()


class FrictionBrakeApp(ToolApp):
    """Main application class for automating friction brake adjustments.

    This class manages the configuration, detection, and execution of the friction
    brake automation process. It also handles key bindings for exiting and resetting.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments.
        friction_brake (FrictionBrake): Friction brake controller instance.
    """

    def __init__(self):
        """Initialize the application.

        1. Check the game window state.
        2. Format keybinds in cfg node.
        3. Display cfg node.
        4. Initialize a friction brake instance.
        """
        super().__init__()
        if not self.is_game_window_valid():
            safe_exit()

        # Format keys
        self.cfg.defrost()
        self.cfg.ARGS.QUIT_KEY = f"'{self.cfg.ARGS.QUIT_KEY}'"
        self.cfg.ARGS.RESET_KEY = f"'{self.cfg.ARGS.RESET_KEY}'"
        self.cfg.freeze()
        print_cfg(self.cfg.ARGS)
        print_cfg(self.cfg.FRICTION_BRAKE)

        self.friction_brake = FrictionBrake(self.cfg, Lock(), self.detection)

    def is_game_window_valid(self) -> bool:
        """Check if the game window mode and size are valid.

        :return: True if valid, False otherwise
        :rtype: bool
        """
        if self.window.is_title_bar_exist():
            logger.info("Window mode detected. Please don't move the game window")
        if not self.window.is_size_supported():
            logger.critical(
                'Window mode must be "Borderless windowed" or "Window mode"'
            )
            logger.critical(
                "Unsupported window size '%s', "
                "use '2560x1440', '1920x1080' or '1600x900'",
                self.window.get_resolution_str(),
            )
            return False
        return True

    def create_parser(self) -> argparse.ArgumentParser:
        """Create an argument parser for the application.

        :return: Configured argument parser.
        :rtype: argparse.ArgumentParser
        """
        parser = argparse.ArgumentParser(description="Automate friction brake.")
        parser.add_argument("opts", nargs="*", help="overwrite configuration")
        parser.add_argument(
            "-r",
            "--reset-key",
            default="g",
            type=str,
            help="key to reset friction brake, g by default",
            metavar="KEY",
        )
        parser.add_argument(
            "-q",
            "--quit-key",
            default="h",
            type=str,
            help="key to quit the script, h by default",
            metavar="KEY",
        )
        return parser

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle exit and quit events.

        :param key: The key that was released.
        :type key: keyboard.KeyCode
        """
        keystroke = str(key).lower()
        if keystroke == self.cfg.ARGS.QUIT_KEY:
            self.friction_brake.monitor_process.terminate()
            sys.exit()
        if keystroke == self.cfg.ARGS.RESET_KEY:
            self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

    def _start(self):
        """Start the friction brake automation process.

        Begins the friction brake monitoring process and starts a keyboard listener
        to handle control keys.
        """
        print(
            f"Press {self.cfg.ARGS.RESET_KEY[1:-1]} to reset friction brake, "
            f"{self.cfg.ARGS.QUIT_KEY[1:-1]} to quit."
        )
        self.friction_brake.monitor_process.start()
        with keyboard.Listener(on_release=self._on_release) as listener:
            listener.join()


def run_app_from_main():
    try:
        FrictionBrakeApp().start()
    except Exception as e:
        logger.critical(e, exc_info=True)
    safe_exit()


if __name__ == "__main__":
    update_argv()
    try:
        FrictionBrakeApp().start()
    except Exception as e:
        logger.critical(e, exc_info=True)
    safe_exit()

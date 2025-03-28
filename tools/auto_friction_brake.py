"""Automate friction brake adjustments in Russian Fishing 4.

This module provides functionality to automatically adjust the friction brake
based on in-game conditions. It supports key bindings for exiting the script
and resetting the friction brake.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import argparse
import logging
import shlex
import sys
from multiprocessing import Lock
from pathlib import Path

from pynput import keyboard
from rich.logging import RichHandler
from yacs.config import CfgNode as CN

sys.path.append(".")


from rf4s.app.app import App
from rf4s.component.friction_brake import FrictionBrake
from rf4s.config import config
from rf4s.controller.detection import Detection

EXIT = "'h'"
RESET = "'g'"
ROOT = Path(__file__).resolve().parents[1]

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("rich")


class FrictionBrakeApp(App):
    """Main application class for automating friction brake adjustments.

    This class manages the configuration, detection, and execution of the friction
    brake automation process. It also handles key bindings for exiting and resetting.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments.
        window (Window): Game window controller instance.
        detection (Detection): Detection instance for in-game state checks.
        friction_brake_lock (Lock): Dummy lock for thread synchronization.
        friction_brake (FrictionBrake): Friction brake controller instance.
    """

    def __init__(self):
        """Initialize the application.

        Loads configuration, parses command-line arguments, sets up the game window,
        and initializes the friction brake controller.
        """
        super().__init__()

        # Format key
        self.cfg.defrost()
        self.cfg.ARGS.EXIT_KEY = f"'{self.cfg.ARGS.EXIT_KEY}'"
        self.cfg.ARGS.RESET_KEY = f"'{self.cfg.ARGS.RESET_KEY}'"
        self.cfg.freeze()
        config.print_cfg(self.cfg.FRICTION_BRAKE)

        width, height = self.window.box[:2]
        if self.window.title_bar_exist:
            logger.info("Window mode detected. Please don't move the game window")
        if not self.window.supported:
            logger.warning('Window mode must be "Borderless windowed" or "Window mode"')
            logger.critical(
                "Invalid window size '%s', use '2560x1440', '1920x1080' or '1600x900'",
                f"{width}x{height}",
            )
            sys.exit(1)

        self.detection = Detection(self.cfg, self.window)

        self.friction_brake_lock = Lock()  # dummy lock
        self.friction_brake = FrictionBrake(
            self.cfg, self.friction_brake_lock, self.detection
        )

    def _parse_args(self) -> argparse.Namespace:
        """Configure argument parser and parse command-line arguments.

        :return: Parsed command-line arguments.
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(description="Automate friction brake.")
        parser.add_argument("opts", nargs="*", help="overwrite configuration")
        parser.add_argument(
            "-e",
            "--exit-key",
            default="h",
            type=str,
            help="key to quit the script, h by default",
            metavar="KEY",
        )
        parser.add_argument(
            "-r",
            "--reset-key",
            default="g",
            type=str,
            help="key to reset friction brake, g by default",
            metavar="KEY",
        )
        args_list = shlex.split(self.cfg.SCRIPT.LAUNCH_OPTIONS) + sys.argv[1:]
        return parser.parse_args(args_list)

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle key release events for controlling the application.

        Exits the script or resets the friction brake based on the key pressed.

        :param key: The key that was released.
        :type key: keyboard.KeyCode
        """
        keystroke = str(key).lower()
        if keystroke == self.cfg.ARGS.EXIT_KEY:
            self.friction_brake.monitor_process.terminate()
            sys.exit()
        if keystroke == self.cfg.ARGS.RESET_KEY:
            self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

    def _start(self):
        """Start the friction brake automation process.

        Begins the friction brake monitoring process and starts a keyboard listener
        to handle control keys.
        """
        self.friction_brake.monitor_process.start()
        with keyboard.Listener(on_release=self._on_release) as listener:
            listener.join()


if __name__ == "__main__":
    FrictionBrakeApp.start()

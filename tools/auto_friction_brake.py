import argparse
import sys
import shlex
import logging
from yacs.config import CfgNode as CN
from multiprocessing import Lock
from rich.logging import RichHandler

from pathlib import Path

from pynput import keyboard

sys.path.append(".")

from rf4s import utils
from rf4s.config import config
from rf4s.controller.detection import Detection
from rf4s.component.friction_brake import FrictionBrake
from rf4s.controller.window import Window


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
        self.cfg.ARGS.RESET_KEY = f"'{self.cfg.ARGS.RESET_KEY}'"

        self.cfg.freeze()
        config.print_cfg(self.cfg.FRICTION_BRAKE)

        self.window = Window()
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

    def parse_args(self):
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

    def on_release(self, key: keyboard.KeyCode) -> None:
        """Callback for releasing button, including w key toggle control.

        :param key: key code used by OS
        :type key: keyboard.KeyCode
        """
        keystroke = str(key).lower()
        if keystroke == self.cfg.ARGS.EXIT_KEY:
            self.friction_brake.monitor_process.terminate()
            sys.exit()
        if keystroke == self.cfg.ARGS.RESET_KEY:
            self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

    def start(self):
        self.friction_brake.monitor_process.start()
        with keyboard.Listener(on_release=self.on_release) as listener:
            listener.join()


if __name__ == "__main__":
    app = App()
    utils.start_app(app, None)

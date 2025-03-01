"""
Activate game window and start crafting things until running out of materials.

Usage: craft.py
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly

import argparse
import logging
import sys
from pathlib import Path

import pyautogui as pag
from rich.logging import RichHandler
from yacs.config import CfgNode as CN

sys.path.append(".")

import argparse
import logging
import random
import sys
from datetime import datetime
from time import sleep

from rf4s import utils
from rf4s.config import config
from rf4s.controller.detection import Detection
from rf4s.controller.window import Window

CRAFT_DELAY = 4.0
CRAFT_DELAY_2X = 8.0

ANIMATION_DELAY = 0.5
ANIMATION_DELAY_2X = 1.0
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

        self.cfg.freeze()

        self.window = Window()
        self.detection = Detection(self.cfg, self.window)

        self.success_count = 0
        self.fail_count = 0
        self.craft_count = 0

    def parse_args(self) -> argparse.Namespace:
        """Cofigure argparser and parse the command line arguments.

        :return parsed args
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(description="Craft items automatically.")
        parser.add_argument("opts", nargs="*", help="overwrite configuration")
        parser.add_argument(
            "-d",
            "--discard",
            action="store_true",
            help="discard all the crafted items (for groundbaits)",
        )
        parser.add_argument(
            "-f",
            "--fast",
            action="store_true",
            help="disable delay randomization to speed up crafting",
        )
        parser.add_argument(
            "-n",
            "--craft-limit",
            type=int,
            default=-1,
            help="number of items to craft, no limit by default",
            metavar="LIMIT",
        )
        return parser.parse_args()

    def start(self) -> None:
        """Main crafting loop."""
        random.seed(datetime.now().timestamp())
        craft_delay = CRAFT_DELAY
        click_delay = ANIMATION_DELAY

        make_btn_coord = self.detection.get_make_position()
        if make_btn_coord is None:
            logger.critical(
                "Make button not found, please set the interface scale to "
                "1x or move your mouse around"
            )
            self.window.activate_script_window()
            return
        pag.moveTo(make_btn_coord)

        while self.detection.is_material_complete():
            logger.info("Crafting item")
            pag.click()

            if not self.cfg.ARGS.FAST:
                craft_delay = random.uniform(CRAFT_DELAY, CRAFT_DELAY_2X)
                click_delay = random.uniform(ANIMATION_DELAY, ANIMATION_DELAY_2X)
            sleep(craft_delay)

            while True:
                if self.detection.is_operation_success():
                    logger.info("Item crafted successfully")
                    self.success_count += 1
                    break

                if self.detection.is_operation_failed():
                    logger.warning("Failed to craft item")
                    self.fail_count += 1
                    break
                sleep(ANIMATION_DELAY)
            self.craft_count += 1

            pag.press("backspace" if self.cfg.ARGS.DISCARD else "space")
            if self.craft_count >= self.cfg.ARGS.CRAFT_LIMIT:
                break
            sleep(click_delay)


if __name__ == "__main__":
    app = App()
    utils.start_app(
        app,
        (
            ("Successful Crafts", app.success_count),
            ("Failed Crafts", app.fail_count),
            ("Materials Used", app.craft_count),
        ),
    )

"""Activate game window and start crafting things until running out of materials.

This module automates the crafting process in Russian Fishing 4. It supports
discarding crafted items, fast crafting mode, and a configurable crafting limit.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly

import argparse
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from time import sleep

import pyautogui as pag
from rich.logging import RichHandler
from yacs.config import CfgNode as CN

sys.path.append(".")

from rf4s import utils
from rf4s.app.app import App
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


class CraftApp(App):
    """Main application class for automating crafting.

    This class manages the configuration, detection, and execution of the crafting
    process. It tracks the number of successful and failed crafts, as well as the
    total number of materials used.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments.
        window (Window): Game window controller instance.
        detection (Detection): Detection instance for in-game state checks.
        success_count (int): Number of successful crafts.
        fail_count (int): Number of failed crafts.
        craft_count (int): Total number of crafting attempts.
    """

    def __init__(self):
        """Initialize the application.

        Loads configuration, parses command-line arguments, and sets up the game window
        and detection instances.
        """
        super().__init__()

        self.detection = Detection(self.cfg, self.window)

        self.success_count = 0
        self.fail_count = 0
        self.craft_count = 0

    def _parse_args(self) -> argparse.Namespace:
        """Configure argument parser and parse command-line arguments.

        :return: Parsed command-line arguments.
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

    def _start(self) -> None:
        """Main loop for crafting items.

        Executes the primary loop for crafting items until materials are exhausted or
        the crafting limit is reached. Supports fast crafting mode and discarding items.
        """
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
    CraftApp().start(
        (
            ("Successful Crafts", "success_count"),
            ("Failed Crafts", "fail_count"),
            ("Materials Used", "craft_count"),
        ),
    )

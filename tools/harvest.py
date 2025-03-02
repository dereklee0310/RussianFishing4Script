"""Script for automatic baits harvesting and hunger/comfort refill.

This module provides functionality to automate the harvesting of baits and refilling
of hunger and comfort in Russian Fishing 4. It includes options for power-saving
mode and configurable check delays.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly

import argparse
import logging
import sys
from pathlib import Path
from time import sleep

import pyautogui as pag
from rich.logging import RichHandler
from yacs.config import CfgNode as CN

sys.path.append(".")

from rf4s import utils
from rf4s.config import config
from rf4s.controller.detection import Detection
from rf4s.controller.timer import Timer
from rf4s.controller.window import Window

ROOT = Path(__file__).resolve().parents[1]

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("rich")

ANIMATION_DELAY = 0.5


class App:
    """Main application class for automating bait harvesting and hunger/comfort refill.

    This class manages the configuration, detection, and execution of the harvesting
    and refill processes. It also handles power-saving mode and check delays.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments.
        window (Window): Game window controller instance.
        detection (Detection): Detection instance for in-game state checks.
        timer (Timer): Timer instance for managing cooldowns.
        tea_count (int): Number of tea consumed.
        carrot_count (int): Number of carrots consumed.
        harvest_count (int): Number of baits harvested.
    """

    def __init__(self):
        """Initialize the application.

        Loads configuration, parses command-line arguments, and sets up the game window,
        detection, and timer instances.
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

        self.cfg.freeze()

        self.window = Window()
        self.detection = Detection(self.cfg, self.window)
        self.timer = Timer(self.cfg)

        self.tea_count = 0
        self.carrot_count = 0
        self.harvest_count = 0

    def parse_args(self) -> argparse.Namespace:
        """Configure argument parser and parse command-line arguments.

        :return: Parsed command-line arguments.
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(
            description="Harvest baits and refill hunger/comfort automatically.",
        )
        parser.add_argument("opts", nargs="*", help="overwrite configuration")
        parser.add_argument(
            "-r",
            "--refill",
            action="store_true",
            help="refill hunger and comfort by consuming tea and carrot",
        )
        parser.add_argument(
            "-s",
            "--power-saving",
            action="store_true",
            help="open control panel between checks to reduce power consumption",
        )
        parser.add_argument(
            "-n",
            "--check-delay",
            type=int,
            default=32,
            help="delay time between each checks, 32s by default",
        )
        return parser.parse_args()

    def start(self) -> None:
        """Main loop for eating and harvesting.

        Executes the primary loop for checking hunger/comfort levels, consuming food,
        and harvesting baits. Supports power-saving mode and configurable check delays.
        """
        pag.press(str(self.cfg.KEY.DIGGING_TOOL))
        sleep(3)
        while True:
            if self.cfg.ARGS.REFILL:
                if self.detection.is_comfort_low() and self.timer.is_tea_drinkable():
                    self._consume_food("tea")
                    self.tea_count += 1

                if self.detection.is_hunger_low():
                    self._consume_food("carrot")
                    self.carrot_count += 1

            if not self.detection.is_energy_high():
                logger.info("Energy is not high enough")
            self._harvest_baits()
            self.harvest_count += 1

            if self.cfg.ARGS.POWER_SAVING:
                pag.press("esc")
            sleep(self.cfg.ARGS.CHECK_DELAY)
            if self.cfg.ARGS.POWER_SAVING:
                pag.press("esc")
            sleep(ANIMATION_DELAY)

    def _harvest_baits(self) -> None:
        """Harvest baits from the game.

        The digging tool should be pulled out before calling this method. Waits for
        harvest success and presses the spacebar to complete the process.
        """
        logger.info("Harvesting baits")
        # Dig and wait (4 + 1)s
        pag.click()
        sleep(5)

        i = 64
        while i > 0 and not self.detection.is_harvest_success():
            i = utils.sleep_and_decrease(i, 2)
        pag.press("space")
        logger.info("Baits harvested succussfully")
        sleep(ANIMATION_DELAY)

    def _consume_food(self, food: str) -> None:
        """Consume a specific type of food.

        Opens the food menu, moves the cursor to the food's position, and clicks to consume it.

        :param food: The type of food to consume (e.g., "tea" or "carrot").
        :type food: str
        """
        logger.info("Consuming %s", food)
        with pag.hold("t"):
            sleep(ANIMATION_DELAY)
            pag.moveTo(self.detection.get_food_position(food))
            pag.click()
        sleep(ANIMATION_DELAY)


if __name__ == "__main__":
    app = App()
    utils.start_app(
        app,
        (
            ("Tea consumed", app.tea_count),
            ("Carrot consumed", app.carrot_count),
            ("Number of harvests", app.harvest_count),
        ),
    )

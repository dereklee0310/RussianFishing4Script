"""Script for automatic baits harvesting and hunger/comfort refill.

This module provides functionality to automate the harvesting of baits and refilling
of hunger and comfort in Russian Fishing 4. It includes options for power-saving
mode and configurable check delays.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import argparse
import sys
from pathlib import Path
from time import sleep

import pyautogui as pag
from pynput import keyboard

sys.path.append(".")

from rf4s.app.app import ToolApp
from rf4s.config.config import print_cfg
from rf4s.controller.timer import Timer
from rf4s.result.result import HarvestResult
from rf4s.utils import create_rich_logger, safe_exit, update_argv

ROOT = Path(__file__).resolve().parents[1]
DIG_DELAY = 5  # 4 + 1 s
CHECK_DELAY = 0.5
ANIMATION_DELAY = 0.5

logger = create_rich_logger()


class HarvestApp(ToolApp):
    """Main application class for automating bait harvesting and hunger/comfort refill.

    This class manages the configuration, detection, and execution of the harvesting
    and refill processes. It also handles power-saving mode and check delays.

    Attributes:
        timer (Timer): Timer instance for managing cooldowns.
    """

    def __init__(self):
        """Initialize the application.

        Loads configuration, parses command-line arguments, and sets up the game window,
        detection, and timer instances.
        """
        super().__init__()
        print_cfg(self.cfg.ARGS)

        self.timer = Timer(self.cfg)
        self.result = HarvestResult()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create an argument parser for the application.

        :return: Configured argument parser.
        :rtype: argparse.ArgumentParser
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
        return parser

    def harvest_baits(self) -> None:
        """Harvest baits using shovel/spoon.

        The digging tool should be pulled out before calling this method. Waits for
        harvest success and presses the spacebar to complete the process.
        """
        logger.info("Harvesting baits")
        pag.click()
        sleep(DIG_DELAY)
        while not self.detection.is_harvest_success():
            sleep(CHECK_DELAY)
        pag.press("space")
        logger.info("Baits harvested succussfully")
        sleep(ANIMATION_DELAY)

    def refill_player_stats(self) -> None:
        """Refill player stats using tea and carrot."""
        if not self.cfg.ARGS.REFILL:
            return

        logger.info("Refilling player stats")
        # Comfort is affected by weather, add a check to avoid over drink
        if self.detection.is_comfort_low() and self.timer.is_tea_drinkable():
            self._use_item("tea")
            self.result.tea += 1

        if self.detection.is_hunger_low():
            self._use_item("carrot")
            self.result.carrot += 1

    def _use_item(self, item: str) -> None:
        """Access an item by name using quick selection shortcut or menu.

        :param item: The name of the item to access.
        :type item: str
        """
        logger.info("Using item: %s", item)
        key = str(self.cfg.KEY[item.upper()])
        if key != "-1":  # Use shortcut
            pag.press(key)
        else:  # Open food menu
            with pag.hold("t"):
                sleep(ANIMATION_DELAY)
                food_position = self.detection.get_food_position(item)
                pag.moveTo(food_position)
                pag.click()
        sleep(ANIMATION_DELAY)

    def _start(self) -> None:
        """Main loop for eating and harvesting.

        Executes the primary loop for checking hunger/comfort levels, consuming food,
        and harvesting baits. Supports power-saving mode and configurable check delays.
        """
        if self.cfg.KEY.QUIT != "CTRL-C":
            listener = keyboard.Listener(on_release=self._on_release)
            listener.start()
        print(f"Press {self.cfg.KEY.QUIT} to quit.")

        pag.press(str(self.cfg.KEY.DIGGING_TOOL))
        sleep(3)
        while True:
            self.refill_player_stats()
            if self.detection.is_energy_high():
                self.harvest_baits()
                self.result.bait += 1
            else:
                logger.info("Energy is not high enough")

            if self.cfg.ARGS.POWER_SAVING:
                pag.press("esc")
                sleep(self.cfg.ARGS.CHECK_DELAY)
                pag.press("esc")
            else:
                sleep(self.cfg.ARGS.CHECK_DELAY)
            sleep(ANIMATION_DELAY)


def run_app_from_main():
    try:
        HarvestApp().start()
    except Exception as e:
        logger.critical(e, exc_info=True)
    safe_exit()


if __name__ == "__main__":
    update_argv()
    try:
        HarvestApp().start()
    except Exception as e:
        logger.critical(e, exc_info=True)
    safe_exit()

"""
Script for automatic baits harvesting and hunger/comfort refill.

Usage: harvest.py
"""

import logging
import configparser
import argparse
import pathlib
from time import time, sleep

import pyautogui as pag
from prettytable import PrettyTable

import monitor
from windowcontroller import WindowController
from script import sleep_and_decrease, ask_for_confirmation

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class App:
    """Main application class."""

    def __init__(self):
        """Initialize counters and parse command line arguments."""
        args = self.parse_args()
        config = configparser.ConfigParser()
        config.read(pathlib.Path(__file__).resolve().parents[1] / "config.ini")

        self.power_saving_enabled = args.power_saving_
        self.check_delay_second = args.check_delay_second

        self.energy_threshold = config["game"].getfloat("harvest_baits_threshold")
        self.shovel_spoon_shortcut = config["shortcut"].get("shovel_spoon")

        self.tea_count = 0
        self.carrot_count = 0
        self.harvest_count = 0

    def parse_args(self) -> argparse.Namespace:
        """Cofigure argparser and parse the command line arguments.

        :return dict-like parsed arguments
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(
            description="Harvest baits, refill hunger and comfort if needed",
        )
        parser.add_argument(
            "-s",
            "--power-saving",
            action="store_true",
            help="Open control panel between checks to reduce power consumption",
        )
        parser.add_argument(
            "-n",
            "--check-delay-second",
            type=int,
            default=32,
            help="The delay time between each checks, default to 32 (seconds)",
        )
        return parser.parse_args()

    def start_harvesting_loop(self) -> None:
        """Main harvesting loop."""
        pre_refill_time = 0

        while True:
            if time() - pre_refill_time > 300 and monitor.is_comfort_low():
                logger.info("Low comfort level")
                pre_refill_time = time()
                self.consume_food("tea")
                self.tea_count += 1

            if monitor.is_hunger_low():
                logger.info("Low hunger level")
                self.consume_food("carrot")
                self.carrot_count += 1

            if monitor.is_energy_high(self.energy_threshold):
                logger.info("High energy level")
                self.harvest_baits()
                self.harvest_count += 1

            logger.info("Waiting for energy regeneration")
            if self.power_saving_enabled:
                pag.press("esc")
            sleep(self.check_delay_second)
            if self.power_saving_enabled:
                pag.press("esc")
            sleep(0.25)

    def harvest_baits(self) -> None:
        """Harvest baits."""
        logger.info("Harvesting baits")
        pag.click()

        # wait for result
        sleep(5)  # 4 + 1 for flexibility
        i = 64
        while i > 0 and not monitor.is_harvest_success():
            i = sleep_and_decrease(i, 4)

        # accept result
        pag.press("space")
        sleep(0.25)

    def consume_food(self, food: str) -> None:
        """Open food menu, then click on the food icon to consume it.

        :param food: food's name
        :type food: str
        """
        logger.info("Consume %s", food)
        with pag.hold("t"):
            sleep(0.25)
            food_position = getattr(monitor, f"get_{food}_icon_position")()
            pag.moveTo(food_position)
            pag.click()
            sleep(0.25)


if __name__ == "__main__":
    app = App()
    ask_for_confirmation("Are you ready to start harvesting baits")
    WindowController().activate_game_window()

    pag.press(app.shovel_spoon_shortcut)
    sleep(3)
    try:
        app.start_harvesting_loop()
    except KeyboardInterrupt:
        pass

    table = PrettyTable(header=False, align="l")
    table.title = "Running Results"
    table.add_rows(
        [
            ["Harvest baits count", app.harvest_count],
            ["Tea consumed", app.tea_count],
            ["Carrot consumed", app.carrot_count],
        ]
    )
    print(table)

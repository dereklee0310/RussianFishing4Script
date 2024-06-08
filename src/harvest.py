"""
Script for automatic baits harvesting and hunger/comfort refill.

Usage: harvest.py
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly

import argparse
import time

import pyautogui as pag

import script
from timer import Timer

# ------------------ flag name, attribute name, description ------------------ #
ARGS = (
    ("power_saving", "power_saving_enabled", "_"),
    ("check_delay_second", "check_delay_second", "_"),
)

# ------------------------ attribute name, description ----------------------- #
RESULTS = (
    ("tea_count", "Tea consumed"),
    ("carrot_count", "Carrot consumed"),
    ("harvest_count", "Number of harvests"),
)


class App:
    """Main application class."""

    @script.initialize_setting_and_monitor(ARGS)
    def __init__(self):
        """Initialize counters and merge args into setting node."""
        self.timer = Timer()
        self.tea_count = 0
        self.carrot_count = 0
        self.harvest_count = 0

    def parse_args(self) -> argparse.Namespace:
        """Cofigure argparser and parse the command line arguments.

        :return dict-like parsed arguments
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(
            description="Harvest baits and refill hunger/comfort automatically.",
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

    def start(self) -> None:
        """Main harvesting loop."""
        pag.press(self.setting.shovel_spoon_shortcut)
        time.sleep(3)
        while True:
            if self.monitor.is_comfort_low() and self.timer.is_tea_drinkable():
                self._consume_food("tea")
                self.tea_count += 1

            if self.monitor.is_hunger_low():
                self._consume_food("carrot")
                self.carrot_count += 1

            if self.monitor.is_energy_high():
                self._harvest_baits()
                self.harvest_count += 1

            if self.setting.power_saving_enabled:
                pag.press("esc")
            time.sleep(self.setting.check_delay_second)
            if self.setting.power_saving_enabled:
                pag.press("esc")
            time.sleep(0.25)

    def _harvest_baits(self) -> None:
        """Harvest baits, the tool should be pulled out in start_harvesting_loop()."""
        # dig and wait (4 + 1)s
        pag.click()
        time.sleep(5)

        i = 64
        while i > 0 and not self.monitor.is_harvest_success():
            i = script.sleep_and_decrease(i, 2)

        # accept result
        pag.press("space")
        time.sleep(0.25)

    def _consume_food(self, food: str) -> None:
        """Open food menu, then click on the food icon to consume it.

        :param food: food name
        :type food: str
        """
        with pag.hold("t"):
            time.sleep(0.25)
            pag.moveTo(self.monitor.get_food_position(food))
            pag.click()
            time.sleep(0.25)


if __name__ == "__main__":
    script.start_app(App(), RESULTS)

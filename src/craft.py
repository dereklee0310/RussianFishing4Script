"""
Activate game window and start crafting things until running out of materials.

Usage: craft.py
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly

import argparse
import random
from datetime import datetime
from time import sleep

import pyautogui as pag

import script

# ------------------ flag name, attribute name, description ------------------ #
ARGS = (
    ("discard", "discard_enabled", "_"),
    ("craft_limit", "craft_limit", "_"),
)

# ------------------------ attribute_name, description ----------------------- #
RESULTS = (
    ("success_count", "Item crafted"),
    ("fail_count", "Number of failures"),
    ("craft_count", "Materials used"),
)


class App:
    """Main application class."""

    @script.initialize_setting_and_monitor(ARGS)
    def __init__(self):
        """Initialize counters and merge args into setting node."""
        self.success_count = 0
        self.fail_count = 0
        self.craft_count = 0

    def parse_args(self) -> argparse.Namespace:
        """Cofigure argparser and parse the command line arguments.

        :return parsed args
        :rtype: argparse.Namespace
        """
        parser = argparse.ArgumentParser(description="Craft items automatically.")
        parser.add_argument(
            "-d", "--discard", action="store_true", help="Discard all the crafted items"
        )
        parser.add_argument(
            "-n",
            "--craft-limit",
            type=int,
            default=-1,
            help="Number of items to craft, no limit if not specified",
        )
        return parser.parse_args()

    def start(self) -> None:
        """Main crafting loop."""
        random.seed(datetime.now().timestamp())
        pag.moveTo(self.monitor.get_make_position())
        while True:
            pag.click()  # click make button

            # recipe not complete
            if self.monitor.is_operation_failed():
                pag.press("space")
                break

            # crafting, wait at least 4 seconds
            delay = random.uniform(4, 6)
            sleep(delay)
            while True:
                if self.monitor.is_operation_success():
                    self.success_count += 1
                    break

                if self.monitor.is_operation_failed():
                    self.fail_count += 1
                    break
                sleep(0.25)
            self.craft_count += 1

            # handle result
            key = "backspace" if self.setting.discard_enabled else "space"
            pag.press(key)
            if self.craft_count == self.setting.craft_limit:
                break
            sleep(0.25)  # wait for animation


if __name__ == "__main__":
    script.start_app(App(), RESULTS)

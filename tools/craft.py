"""
Activate game window and start crafting things until running out of materials.

Usage: craft.py
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly
import logging
import argparse
import random
from datetime import datetime
from time import sleep

import pyautogui as pag

import script

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

CRAFT_DELAY = 4.0
CRAFT_DELAY_2X = 8.0

ANIMATION_DELAY = 0.5
ANIMATION_DELAY_2X = 1.0

# ------------------ flag name, attribute name, description ------------------ #
ARGS = (
    ("discard", "discard_enabled", "_"),
    ("craft_limit", "craft_limit", "_"),
    ("fast", "fast_enabled", "_"),
)

# ------------------------ attribute_name, description ----------------------- #
RESULTS = (
    ("success_count", "Successful Crafts"),
    ("fail_count", "Failed Attempts"),
    ("craft_count", "Materials Used"),
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
            "-d", "--discard", action="store_true", help="discard all the crafted items"
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
            help="number of items to craft, no limit if not specified",
            metavar="LIMIT"
        )
        return parser.parse_args()

    def start(self) -> None:
        """Main crafting loop."""
        random.seed(datetime.now().timestamp())
        craft_delay = CRAFT_DELAY
        click_delay = ANIMATION_DELAY

        # locate make button
        make_btn_coord = self.monitor.get_make_position()
        if make_btn_coord is None:
            logger.error("Make button not found, please set the interface scale to "
                         "1x or move your mouse around")
            self.setting.window_controller.activate_script_window()
            return
        pag.moveTo(make_btn_coord)


        while self.monitor.is_material_complete():
            pag.click()

            # crafting
            if not self.setting.fast_enabled:
                craft_delay = random.uniform(CRAFT_DELAY, CRAFT_DELAY_2X)
                click_delay = random.uniform(ANIMATION_DELAY, ANIMATION_DELAY_2X)
            sleep(craft_delay)

            # checking
            while True:
                if self.monitor.is_operation_success():
                    self.success_count += 1
                    break

                if self.monitor.is_operation_failed():
                    self.fail_count += 1
                    break
                sleep(ANIMATION_DELAY)
            self.craft_count += 1

            # handle result
            pag.press("backspace" if self.setting.discard_enabled else "space")
            if self.craft_count == self.setting.craft_limit:
                break
            sleep(click_delay)


if __name__ == "__main__":
    script.start_app(App(), RESULTS)

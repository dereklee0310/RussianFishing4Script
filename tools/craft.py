"""Activate game window and start crafting things until running out of materials.

This module automates the crafting process in Russian Fishing 4. It supports
discarding crafted items, fast crafting mode, and a configurable crafting limit.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path
from time import sleep

import pyautogui as pag

sys.path.append(".")
from rf4s.app.app import ToolApp
from rf4s.config.config import print_cfg
from rf4s.utils import create_rich_logger

CRAFT_DELAY = 4.0
CRAFT_DELAY_2X = CRAFT_DELAY * 2
LOOP_DELAY = 0.5
LOOP_DELAY_2X = LOOP_DELAY * 2
ROOT = Path(__file__).resolve().parents[1]

logger = create_rich_logger()


class CraftApp(ToolApp):
    """Main application class for automating crafting.

    This class manages the configuration, detection, and execution of the crafting
    process. It tracks the number of successful and failed crafts, as well as the
    total number of materials used.
    """

    def __init__(self):
        """Initialize the application.

        1. Display cfg node.
        2. Initialize results dictionary.
        """
        super().__init__()
        print_cfg(self.cfg.ARGS)

        self.results["Successful crafts"] = 0
        self.results["Failed crafts"] = 0
        self.results["Materials used"] = 0

    def create_parser(self) -> argparse.ArgumentParser:
        """Create an argument parser for the application.

        :return: Configured argument parser.
        :rtype: argparse.ArgumentParser
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
        return parser

    def get_action_delays(self) -> tuple[float, float]:
        """Get crafting and checking delays.

        :return: Two delays in seconds
        :rtype: tuple[float, float]
        """
        if not self.cfg.ARGS.FAST:
            return CRAFT_DELAY, LOOP_DELAY
        return (
            random.uniform(CRAFT_DELAY, CRAFT_DELAY_2X),
            random.uniform(LOOP_DELAY, LOOP_DELAY_2X),
        )

    def move_cursor_to_make_button(self) -> None:
        """Move the cursor to the make button position.

        This method uses the Detection class to find the position of the make button
        and moves the cursor to that position.
        """
        make_button_position = self.detection.get_make_button_position()
        if make_button_position is None:
            logger.critical(
                "Make button not found, please set the interface scale to "
                "1x or move your mouse around"
            )
            self.window.activate_script_window()
            return
        pag.moveTo(make_button_position)

    def craft_item(
        self, craft_delay: float, accept_delay: float, accept_key: str
    ) -> None:
        """Craft an item.

        :param craft_delay: Delay in seconds before accepting the crafted item.
        :type craft_delay: float
        :param accept_delay: Delay in seconds after accepting the crafted item.
        :type accept_delay: float
        :param accept_key: Key to press after accepting the crafted item.
        :type accept_key: str
        """
        logger.info("Crafting item")
        pag.click()
        sleep(craft_delay)
        self.results["Materials used"] += 1
        while True:
            if self.detection.is_operation_success():
                logger.info("Crafting successed")
                self.results["Successful crafts"] += 1
                break

            if self.detection.is_operation_failed():
                logger.warning("Crafting failed")
                self.results["Failed crafts"] += 1
                break
            sleep(LOOP_DELAY)
        pag.press(accept_key)
        sleep(accept_delay)

    def _start(self) -> None:
        """Main loop for crafting items.

        Executes the primary loop for crafting items until materials are exhausted or
        the crafting limit is reached. Supports fast crafting mode and discarding items.
        """
        random.seed(datetime.now().timestamp())
        accept_key = "backspace" if self.cfg.ARGS.DISCARD else "space"
        self.move_cursor_to_make_button()
        while (
            self.detection.is_material_complete()
            and self.results["Materials used"] < self.cfg.ARGS.CRAFT_LIMIT
        ):
            self.craft_item(*self.get_action_delays(), accept_key)


if __name__ == "__main__":
    CraftApp().start()

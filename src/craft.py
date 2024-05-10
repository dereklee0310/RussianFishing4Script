"""
Activate game window and start crafting things until running out of materials.

Usage: craft.py
"""

import argparse
import logging
import random
from time import sleep
from datetime import datetime

from prettytable import PrettyTable
import pyautogui as pag

import monitor
from windowcontroller import WindowController
from script import ask_for_confirmation

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
random.seed(datetime.now().timestamp())


def parse_args() -> argparse.Namespace:
    """Cofigure argparser and parse the command line arguments.

    :return dict-like parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        description="Crafting items until running out of materials"
    )
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


def start_crafting_loop(craft_limit: bool, discard_enabled: bool) -> None:
    """Main crafting loop

    :param craft_limit: argument from argparser
    :type craft_limit: bool
    :param discard_enabled: argument from argparser
    :type discard_enabled: bool
    """
    global success_count, fail_count

    while True:
        logger.info("Crafting")
        pag.click()  # click make button

        # recipe not complete
        if monitor.is_operation_failed():
            logger.warning("Out of materials")
            pag.press("space")
            break

        # crafiting, wait at least 4 seconds
        delay = random.uniform(4, 6)
        sleep(delay)
        while True:
            if monitor.is_operation_success():
                logger.info("Crafting succeed")
                success_count += 1
                break
            elif monitor.is_operation_failed():
                logger.info("Crafting failed")
                fail_count += 1
                break
            sleep(0.25)

        # handle result
        key = "backspace" if discard_enabled else "space"
        pag.press(key)
        if success_count + fail_count == craft_limit:
            break
        sleep(0.25)  # wait for animation


if __name__ == "__main__":
    args = parse_args()
    craft_limit = args.craft_limit
    discard_enabled = args.discard
    success_count = 0
    fail_count = 0

    ask_for_confirmation("Are you ready to start crafting")
    WindowController().activate_game_window()

    pag.moveTo(monitor.get_make_position())
    try:
        start_crafting_loop(args.craft_limit, args.discard)
    except KeyboardInterrupt:
        pass

    table = PrettyTable(header=False, align="l")
    table.title = "Running Results"
    table.add_rows(
        [
            ["Item crafted", success_count],
            ["Number of failures", fail_count],
            ["Materials used", success_count + fail_count],
        ]
    )
    print(table)

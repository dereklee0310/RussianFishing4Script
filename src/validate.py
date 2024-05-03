"""
Check if the spool is fully loaded and is in the right position.

Usage: validate.py
"""

import logging

from windowcontroller import WindowController
from monitor import is_spool_icon_valid
from script import ask_for_confirmation

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    ask_for_confirmation("Are you ready to start validation")
    WindowController().activate_game_window()

    if not is_spool_icon_valid():
        logger.error("TEST FAILED")
        print(
            "Please make sure your reel is at full capacity or adjust the game resolution and try again"
        )
    else:
        logger.info("TEST PASSED")

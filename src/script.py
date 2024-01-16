"""
Some helper functions.
"""

from time import sleep

from pyautogui import *
from pyautogui import getWindowsWithTitle
import configparser

def hold_left_click(duration: float=1) -> None:
    """Hold left mouse button.

    :param duration: hold time, defaults to 1
    :type duration: float, optional
    """
    mouseDown()
    sleep(duration)
    mouseUp()
    if duration >= 2.2:
        click()

def hold_right_click(duration: float=1) -> None:
    """Hold right mouse button.

    :param duration: hold time, defaults to 1
    :type duration: float, optional
    """
    mouseDown(button="right")
    sleep(duration)
    mouseUp(button="right")

def sleep_and_decrease(num: int , delay: int) -> int:
    """Self-decrement with a delay.

    :param num: the variable to decrease
    :type num: int
    :param delay: sleep time
    :type delay: int
    :return: decreased num
    :rtype: int
    """
    sleep(delay)
    return num - delay

def activate_game_window() -> None:
    """Activate game window with English title.
    """
    window = getWindowsWithTitle("Russian Fishing 4")[0]
    window.activate()
    sleep(0.25)

def get_image_dir_path() -> str:
    """Build the path for static images based on language option.

    :return: ../static/{language}/
    :rtype: str
    """
    config = configparser.ConfigParser()
    config.read('../config.ini')
    return fr"../static/{config['game']['language']}/"
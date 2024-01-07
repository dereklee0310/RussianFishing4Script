"""
Some helper functions.
"""

from pyautogui import *
from pyautogui import getWindowsWithTitle
from time import sleep

def hold_left_click(duration: float=1) -> None:
    """Hold left mouse button.

    :param duration: hold time, defaults to 1
    :type duration: float, optional
    """
    mouseDown()
    sleep(duration)
    mouseUp()

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
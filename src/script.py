"""
Some helper functions.
"""

from time import sleep

from pyautogui import *
from pyautogui import getWindowsWithTitle
import configparser

config = configparser.ConfigParser()
config.read('../config.ini')

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

def get_image_dir_path() -> str:
    """Build the path for static images based on language option.

    :return: ../static/{language}/
    :rtype: str
    """
    config = configparser.ConfigParser()
    config.read('../config.ini')
    return fr"../static/{config['game']['language']}/"

def is_countdown_enabled() -> bool:
    """Get the value of 'enable_count_down' in config.ini

    :return: True if countdown is enabled, False otherwise
    :rtype: bool
    """
    return config['game'].getboolean('enable_count_down')

def is_running_enabled() -> bool:
    """Get the value of 'running_by_default' in config.ini

    :return: True if accelerated running is enabled, False otherwise
    :rtype: bool
    """
    return config['game'].getboolean('running_by_default')

def start_count_down() -> None:
    """If the 'enable_count_down' option is enabled, 
    start a count down before executing the script.
    """
    print("Hint: Edit 'enable_count_down' option in config.ini to disable the count down")
    for i in range(5, 0, -1):
        print(f'The script will start in: {i} seconds', end='\r')
        sleep(1)
    print('')

def msg_exit(msg: str, is_error=False) -> None:
    """Print message, then exit the program

    :param msg: error message
    :type msg: str
    """
    if is_error:
        msg = f'Error: {msg}'
    print(msg)
    exit()

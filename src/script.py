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

def ask_for_confirmation(msg: str) -> None:
    """Ask for confirmation of user settings if it's enabled.

    :param msg: confirmation message
    :type msg: str
    """
    if not config['game'].getboolean('enable_confirmation'):
        return

    while True:
        ans = input(f'{msg}? [Y/n] ').strip().lower()
        if ans == 'y':
            print('The bot has been started')
            return 
        elif ans == 'n': # quit only when the input is 'n'
            print('The bot has been terminated')
            exit() 

if __name__ == '__main__':
    ask_for_confirmation()

# ! archived
# def start_count_down() -> None:
#     """If the 'enable_count_down' option is enabled, 
#     start a count down before executing the script.
#     """
#     print("Hint: Edit 'enable_count_down' option in config.ini to disable the count down")
#     for i in range(5, 0, -1):
#         print(f'The script will start in: {i} seconds', end='\r')
#         sleep(1)
#     print('')
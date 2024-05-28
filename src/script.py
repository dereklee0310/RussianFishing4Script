"""
Some helper functions.
"""

import sys
from time import sleep

import pyautogui as pag
from prettytable import PrettyTable


def hold_left_click(duration: float = 1) -> None:
    """Hold left mouse button.

    :param duration: hold time, defaults to 1
    :type duration: float, optional
    """
    pag.mouseDown()
    sleep(duration)
    pag.mouseUp()
    if duration >= 2.1:  # + 0.1 due to pag.mouseDown() delay
        pag.click()


def hold_right_click(duration: float = 1) -> None:
    """Hold right mouse button.

    :param duration: hold time, defaults to 1
    :type duration: float, optional
    """
    pag.mouseDown(button="right")
    sleep(duration)
    pag.mouseUp(button="right")


def sleep_and_decrease(num: int, delay: int) -> int:
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


def ask_for_confirmation(msg: str) -> None:
    """Ask for confirmation of user settings if it's enabled.

    :param msg: confirmation message
    :type msg: str
    """
    while True:
        ans = input(f"{msg}? [Y/n] ").strip().lower()
        if ans == "y":
            print("The bot has been started")
            break
        if ans == "n":  # quit only when the input is 'n'
            print("The bot has been terminated")
            sys.exit()


def display_running_results(app: object, result_map: tuple[tuple]) -> None:
    """Display the running results of different apps.

    :param app: caller app
    :type app: object
    :param result_map: attribute name - column name mapping
    :type result_map: tuple[tuple]
    """
    table = PrettyTable(header=False, align="l")
    table.title = "Running Results"
    for attribute_name, column_name in result_map:
        table.add_row([column_name, getattr(app, attribute_name)])
    print(table)


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

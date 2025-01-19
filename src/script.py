"""
Some helper functions.
"""

import sys
from time import sleep

import pyautogui as pag
from prettytable import PrettyTable
from pyscreeze import Box

from monitor import Monitor
from setting import Setting

# BASE_DELAY + LOOP_DELAY >= 2.2 to trigger clicklock
BASE_DELAY = 1
LOOP_DELAY = 2

# ---------------------------------------------------------------------------- #
#                            common functionalities                            #
# ---------------------------------------------------------------------------- #


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


def ask_for_confirmation(msg: str = "Ready to start") -> None:
    """Ask for confirmation of user settings if it's enabled.

    :param msg: confirmation message, defaults to "Ready to start"
    :type msg: str
    """
    while True:
        ans = input(f"{msg}? [Y/n] ").strip().lower()
        if ans in ("y", ""):
            break
        if ans == "n":
            sys.exit()


def display_running_results(app: object, result_map: tuple[tuple]) -> None:
    """Display the running results of different apps.

    :param app: caller object
    :type app: object
    :param result_map: attribute name - column name mapping
    :type result_map: tuple[tuple]
    """
    table = PrettyTable(header=False, align="l")
    table.title = "Running Results"
    # table.field_names = ['Record', 'Value']
    for attribute_name, column_name in result_map:
        table.add_row([column_name, getattr(app, attribute_name)])
    print(table)


def get_box_center(box: Box) -> tuple[int, int]:
    """Get the center coordinate (x, y) of the given box.

    # (x, y, w, h) -> (x, y), np.int64 -> int

    :param box: box coordinates (x, y, w, h)
    :type box: Box
    :return: x and y coordinates of the center point
    :rtype: tuple[int, int]
    """
    return int(box.left + box.width // 2), int(box.top + box.height // 2)


def start_app(app: object, results: tuple[tuple]) -> None:
    """A wrapper for confirmation, window activatioin, and start.

    :param app: main application class
    :type app: object
    :param results: counter lookup table
    :type results: tuple[tuple]
    """

    if app.setting.confirmation_enabled:
        ask_for_confirmation()
    app.setting.window_controller.activate_game_window()
    try:
        app.start()
    except KeyboardInterrupt:
        pass

    if results is not None:
        display_running_results(app, results)
    app.setting.window_controller.activate_script_window()


# ---------------------------------------------------------------------------- #
#                                  decorators                                  #
# ---------------------------------------------------------------------------- #


def initialize_setting_and_monitor(args_map: tuple[tuple]):
    """Initialize a setting node and a screen monitor for given application.

    This is a simple decorator that used for constructors in harvest and craft modules.

    :param args_map: args lookup table
    :type args_map: tuple[tuple]
    """

    def func_wrapper(func):
        def args_wrapper(caller):
            args = caller.parse_args()
            caller.setting = Setting()
            caller.setting.merge_args(args, args_map)
            caller.monitor = Monitor(caller.setting)
            func(caller)

        return args_wrapper

    return func_wrapper


def toggle_clicklock(func):
    """Toggle clicklock before and after calling the function."""

    def wrapper(self, *args):
        pag.mouseDown()
        sleep(BASE_DELAY + LOOP_DELAY)
        try:
            func(self, *args)
            pag.click()
        except Exception as e:
            pag.click()
            raise e

    return wrapper


def toggle_right_mouse_button(func):
    """Toggle clicklock before and after calling the function."""

    def wrapper(self, *args):
        pag.mouseDown(button="right")
        try:
            func(self, *args)
            pag.mouseUp(button="right")
        except Exception as e:
            pag.mouseUp(button="right")
            raise e

    return wrapper


def release_shift_key_after(func):
    """Release Shift key after calling the function."""

    def wrapper(self, *args):
        try:
            func(self, *args)
            pag.keyUp("shift")
        except Exception as e:
            pag.keyUp("shift")
            raise e

    return wrapper


def release_ctrl_key_after(func):
    """Release ctrl key after calling the function."""

    def wrapper(self, *args):
        try:
            func(self, *args)
            pag.keyUp("ctrl")
        except Exception as e:
            pag.keyUp("ctrl")
            raise e

    return wrapper


# there's lots of early return in player._resetting_stage(),
# so use a decorator here to simplify the code
def reset_friction_brake_after(func):
    """Reset friction brake after calling the function."""

    def wrapper(self, *args):
        func(self, *args)
        if not self.setting.friction_brake_changing_enabled:
            return

        with self.friction_brake_lock:
            self.friction_brake.reset(
                self.setting.initial_friction_brake)

    return wrapper


def release_keys():
    """Release keys that might be holding down."""
    pag.keyUp("shift")
    pag.keyUp("a")
    pag.keyUp("d")

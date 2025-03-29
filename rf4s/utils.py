"""Helper functions for automation scripts.

This module provides utility functions for common tasks such as mouse control,
keyboard input, and result display. It also includes decorators for managing
key and mouse states during automation.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import logging
import sys
from time import sleep

import pyautogui as pag
from pyscreeze import Box
from rich import print
from rich.console import Console
from rich.text import Text

# BASE_DELAY + LOOP_DELAY >= 2.2 to trigger clicklock
BASE_DELAY = 1.2
LOOP_DELAY = 1

ANIMATION_DELAY = 1

logger = logging.getLogger("rich")

# ---------------------------------------------------------------------------- #
#                            common functionalities                            #
# ---------------------------------------------------------------------------- #


def hold_mouse_button(duration: float = 1, button: str = "left") -> None:
    """Hold left or right mouse button.

    :param duration: Hold time, defaults to 1.
    :type duration: float, optional
    :param button: Button to click, defaults to "left".
    :type button: str, optional
    """
    if duration == 0:
        return

    pag.mouseDown(button=button)
    sleep(duration)
    pag.mouseUp(button=button)
    if button == "left" and duration >= 2.1:  # + 0.1 due to pag.mouseDown() delay
        pag.click()


def hold_mouse_buttons(duration: float = 1) -> None:
    """Hold left and right mouse buttons simultaneously.

    :param duration: Hold time, defaults to 1.
    :type duration: float, optional
    """
    pag.mouseDown()
    pag.mouseDown(button="right")
    sleep(duration)
    pag.mouseUp()
    pag.mouseUp(button="right")
    if duration >= 2.1:  # + 0.1 due to pag.mouseDown() delay
        pag.click()


def sleep_and_decrease(num: int, delay: int) -> int:
    """Self-decrement with a delay.

    :param num: The variable to decrease.
    :type num: int
    :param delay: Sleep time.
    :type delay: int
    :return: Decreased num.
    :rtype: int
    """
    sleep(delay)
    return num - delay


def ask_for_confirmation(msg: str = "Ready to start") -> None:
    """Ask for confirmation of user settings if it's enabled.

    :param msg: Confirmation message, defaults to "Ready to start".
    :type msg: str
    """
    while True:
        ans = input(f"{msg}? [Y/n] ").strip().lower()
        if ans in ("y", ""):
            break
        if ans == "n":
            sys.exit()


def get_box_center(box: Box) -> tuple[int, int]:
    """Get the center coordinate (x, y) of the given box.

    # (x, y, w, h) -> (x, y), np.int64 -> int

    :param box: Box coordinates (x, y, w, h).
    :type box: Box
    :return: x and y coordinates of the center point.
    :rtype: tuple[int, int]
    """
    return int(box.left + box.width // 2), int(box.top + box.height // 2)


# ---------------------------------------------------------------------------- #
#                                  decorators                                  #
# ---------------------------------------------------------------------------- #


def toggle_clicklock(func):
    """Toggle clicklock before and after calling the function."""

    def wrapper(self, *args, **kwargs):
        # ELECTRO must be enabled, always use electric mode if GEAR_RATIO is disabled
        # otherwise, only use electric mode when it's the first time
        if self.cfg.ARGS.ELECTRO and (not self.cfg.ARGS.GEAR_RATIO or args[0]):
            pag.click(clicks=2, interval=0.1)
        else:
            pag.mouseDown()
        sleep(BASE_DELAY + LOOP_DELAY)
        try:
            func(self, *args, **kwargs)
        finally:
            if self.cfg.ARGS.ELECTRO:
                pag.click(clicks=2, interval=0.1)
            else:
                pag.click()

    return wrapper


def toggle_right_mouse_button(func):
    """Toggle right mouse button before and after calling the function."""

    def wrapper(*args, **kwargs):
        pag.mouseDown(button="right")
        try:
            func(*args, **kwargs)
        finally:
            pag.mouseUp(button="right")

    return wrapper


def press_before_and_after(key):
    def func_wrapper(func):
        def args_wrapper(*args, **kwargs):
            pag.press(key)
            sleep(ANIMATION_DELAY)
            try:
                func(*args, **kwargs)
            finally:
                pag.press(key)
                sleep(ANIMATION_DELAY)

        return args_wrapper

    return func_wrapper


def release_keys_after(arrow_keys: bool = False):
    """Release keys that might have been holding down

    :param arrow_keys: whether to toggle arrow keys, defaults to False
    :type arrow_keys: bool, optional
    """

    def release_keys(arrow_keys):
        pag.keyUp("ctrl")
        pag.keyUp("shift")
        if arrow_keys:
            pag.keyUp("w")
            pag.keyUp("a")
            pag.keyUp("d")

    def func_wrapper(func):  # Capture arrow_keys as default arg
        def args_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            finally:
                release_keys(arrow_keys)  # Uses the captured value

        return args_wrapper

    return func_wrapper


def print_error(msg):
    text = Text(msg)
    text.stylize("red")
    Console().print(text)


# There's lots of early return in player._resetting_stage(),
# so use a decorator here to simplify the code
def reset_friction_brake_after(func):
    """Reset friction brake after calling the function."""

    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        if not self.cfg.ARGS.FRICTION_BRAKE:
            return

        with self.friction_brake_lock:
            self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

    return wrapper

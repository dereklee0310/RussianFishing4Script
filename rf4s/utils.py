"""Helper functions for automation scripts.

This module provides utility functions for common tasks such as mouse control,
keyboard input, and result display. It also includes decorators for managing
key and mouse states during automation.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import ctypes
import msvcrt
import sys
from time import sleep

import pyautogui as pag
from pyscreeze import Box
from rich import box, print
from rich.panel import Panel

from rf4s.controller.console import console

LOOP_DELAY = 1

ANIMATION_DELAY = 0.5

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


# There's lots of early return in player._resetting_stage(),
# so use a decorator here to simplify the code
def reset_friction_brake_after(func):
    """Reset friction brake after calling the function."""

    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        if not self.cfg.ARGS.FRICTION_BRAKE:
            return

        self.friction_brake.reset(self.cfg.BOT.FRICTION_BRAKE.INITIAL)

    return wrapper


def is_compiled():
    return "__compiled__" in globals()  # Nuitka style


def is_run_by_clicking():
    # Load kernel32.dll
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    # Create an array to store the processes in.  This doesn't actually need to
    # be large enough to store the whole process list since GetConsoleProcessList()
    # just returns the number of processes if the array is too small.
    process_array = (ctypes.c_uint * 1)()
    num_processes = kernel32.GetConsoleProcessList(process_array, 1)
    # num_processes may be 1 if your compiled program doesn't have a launcher/wrapper.
    # If run from Python interpreter, num_processes would also be 2
    # We also need to check if it's an executable to make it work
    return is_compiled() and num_processes == 2


def print_logo_box(logo: str) -> None:
    print(Panel.fit(logo, box=box.HEAVY, style="bright_white"))


def print_usage_box(msg: str) -> None:
    print(Panel.fit(msg, style="steel_blue1"))


def print_description_box(msg: str) -> None:
    print(Panel.fit(f"You're now using: {msg}"))


def print_hint_box(msg: str) -> None:
    print(Panel.fit(f"Hint: {msg}", style="green"))


def print_error(msg: str) -> None:
    console.print(msg, style="red")


def safe_exit():
    if is_run_by_clicking():
        print_usage_box("Press any key to quit.")
        # KeyboardInterrupt will mess with stdin, input will crash silently
        # Use msvcrt.getch() because it doesn't depends on stdin
        msvcrt.getch()
    # Skip this because it will trigger a right click to open context menu
    # pag.mouseUp(button="right", _pause=False)
    pag.keyUp("w", _pause=False)
    pag.keyUp("a", _pause=False)
    pag.keyUp("d", _pause=False)
    sys.exit()

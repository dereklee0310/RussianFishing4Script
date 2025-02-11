"""
Module for window controller.
"""

import logging
import sys
from time import sleep
from pathlib import Path

# import win32api, win32con
import pyautogui as pag
import win32con
import win32gui

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]

class Window:
    """Controller for terminal and game windows management."""

    def __init__(self, game_window_title="Russian Fishing 4"):
        """Constructor method.

        :param title: game title, defaults to 'Russian Fishing 4'
        :type title: str, optional
        """
        self._title = game_window_title
        self._script_hwnd = self._get_cur_hwnd()
        self._game_hwnd = self._get_game_hwnd()

    def _get_cur_hwnd(self) -> int:
        """Get the handle of the terminal.

        :return: process handle
        :rtype: int
        """
        return win32gui.GetForegroundWindow()

    def _get_game_hwnd(self) -> int:
        """Get the handle of the game.

        :return: process handle
        :rtype: int
        """
        hwnd = win32gui.FindWindow(None, self._title)
        # print(win32gui.GetClassName(hwnd)) # class name: UnityWndClass
        if not hwnd:
            logger.error("Failed to locate the game window: %s", self._title)
            sys.exit()
        return hwnd

    def is_title_bar_exist(self) -> bool:
        """Check if the game window is in windowed mode.

        :return: True if yes, False otherwise
        :rtype: bool
        """
        style = win32gui.GetWindowLong(self._game_hwnd, win32con.GWL_STYLE)
        return style & win32con.WS_CAPTION

    def get_box(self):
        base_x, base_y, _, _ = win32gui.GetWindowRect(self._game_hwnd)
        if self.is_title_bar_exist():
            base_x += 8
            base_y += 31
        left, top, right, bottom = win32gui.GetClientRect(self._game_hwnd)
        width = right - left
        height = bottom - top
        return base_x, base_y, width, height

    def activate_script_window(self) -> None:
        """Focus terminal."""
        pag.press("alt")
        win32gui.SetForegroundWindow(
            self._script_hwnd
        )  # fullscreen mode is not supported
        sleep(0.25)

    def activate_game_window(self) -> None:
        """Focus game window."""
        pag.press("alt")
        win32gui.SetForegroundWindow(
            self._game_hwnd
        )  # fullscreen mode is not supported
        sleep(0.25)


    def is_size_valid(self) -> bool:
        if self.is_title_bar_exist():
            logger.info("Window mode detected. Please don't move the game window")
        width, height = self.get_box()[2:]
        if (width, height) in ((2560, 1440), (1920, 1080), (1600, 900)):
            return True

        logger.warning(
            "Window size %s not supported, must be 2560x1440, 1920x1080 or 1600x900",
            f"{width}x{height}",
        )
        logger.error('Window mode must be "Borderless windowed" or "Window mode"')
        logger.info("Snag detection and friction brake changing will be disabled")
        return False

    def save_screenshot(self, time) -> None:
        """Save screenshot to screenshots/."""
        # datetime.now().strftime("%H:%M:%S")
        pag.screenshot(
            # imageFilename=rf"../screenshots/{time}.png",
            imageFilename=ROOT / "screenshots" / f"{time}.png",
            region=self.get_box(),
        )


if __name__ == "__main__":
    w = Window("Russian Fishing 4")
    w.activate_game_window()
    print(w.get_window_size())
    print(w.get_coord_bases())

# SetForegroundWindow bug reference :
# https://stackoverflow.com/questions/56857560/win32gui-setforegroundwindowhandle-not-working-in-loop

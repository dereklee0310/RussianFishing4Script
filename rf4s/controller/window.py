"""Module for window controller.

This module provides functionality for managing and interacting with the game window
and terminal window in Russian Fishing 4.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import logging
import sys
from pathlib import Path
from time import sleep

# import win32api, win32con
import pyautogui as pag
import win32con
import win32gui

logger = logging.getLogger("rich")

ROOT = Path(__file__).resolve().parents[2]


class Window:
    """Controller for terminal and game windows management.

    This class handles window focus, size detection, and screenshot functionality
    for the game and terminal windows.

    Attributes:
        _title (str): Title of the game window.
        _script_hwnd (int): Handle of the terminal window.
        _game_hwnd (int): Handle of the game window.
        box (tuple[int, int, int, int]): Coordinates and dimensions of the game window.
        title_bar_exist (bool): Whether the game window has a title bar.
        supported (bool): Whether the game window size is supported.
    """

    def __init__(self, window_title: str = "Russian Fishing 4"):
        """Initialize the Window class with the game window title.

        :param window_title: Title of the game window, defaults to "Russian Fishing 4".
        :type window_title: str, optional
        """
        self._title = window_title
        self._script_hwnd = self._get_cur_hwnd()
        self._game_hwnd = self._get_game_hwnd()
        self.box = self._get_box()
        self.title_bar_exist = self._is_title_bar_exist()
        self.supported = self._is_size_supported()

    def _get_cur_hwnd(self) -> int:
        """Get the handle of the terminal window.

        :return: Process handle of the terminal window.
        :rtype: int
        """
        return win32gui.GetForegroundWindow()

    def _get_game_hwnd(self) -> int:
        """Get the handle of the game window.

        :return: Process handle of the game window.
        :rtype: int
        """
        hwnd = win32gui.FindWindow(None, self._title)
        # print(win32gui.GetClassName(hwnd)) # class name: UnityWndClass
        if not hwnd:
            logger.error("Failed to locate the game window: %s", self._title)
            sys.exit()
        return hwnd

    def _is_title_bar_exist(self) -> bool:
        """Check if the game window is in windowed mode.

        :return: True if the game window has a title bar, False otherwise.
        :rtype: bool
        """
        style = win32gui.GetWindowLong(self._game_hwnd, win32con.GWL_STYLE)
        return style & win32con.WS_CAPTION

    def _get_box(self) -> tuple[int, int, int, int]:
        """Get the coordinates and dimensions of the game window.

        :return: Tuple containing (x, y, width, height) of the game window.
        :rtype: tuple[int, int, int, int]
        """
        base_x, base_y, _, _ = win32gui.GetWindowRect(self._game_hwnd)
        if self._is_title_bar_exist():
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

    def _is_size_supported(self) -> bool:
        """Check if the game window size is supported.

        :return: True if the window size is supported, False otherwise.
        :rtype: bool
        """
        if self.box[2:] in ((2560, 1440), (1920, 1080), (1600, 900)):
            return True
        return False

    def save_screenshot(self, time) -> None:
        """Save a screenshot of the game window to the screenshots directory.

        :param time: Timestamp to use as the filename.
        :type time: str
        """
        # datetime.now().strftime("%H:%M:%S")
        pag.screenshot(
            # imageFilename=rf"../screenshots/{time}.png",
            imageFilename=ROOT / "screenshots" / f"{time}.png",
            region=self.box,
        )


if __name__ == "__main__":
    w = Window("Russian Fishing 4")
    w.activate_game_window()

# SetForegroundWindow bug reference :
# https://stackoverflow.com/questions/56857560/win32gui-setforegroundwindowhandle-not-working-in-loop

"""
Module for window controller.
"""

import logging
import sys
from time import sleep

# import win32api, win32con
import pyautogui as pag
import win32con
import win32gui

logger = logging.getLogger(__name__)


class WindowController:
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

    def get_window_size(self) -> str:
        """Get the width and height of the game window.
        :return: formatted window size
        :rtype: str
        """
        left, top, right, bottom = win32gui.GetClientRect(self._game_hwnd)
        return right - left, bottom - top

    def get_coord_bases(self) -> tuple[int, int]:
        """Get base x and y coordinates of the game window.

        :return: base x, base y
        :rtype: tuple[int, int]
        """
        x, y, _, _ = win32gui.GetWindowRect(self._game_hwnd)
        if self.is_title_bar_exist():
            return x + 8, y + 31 # title bar
        return x, y

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


if __name__ == "__main__":
    w = WindowController("Russian Fishing 4")
    w.activate_game_window()
    print(w.get_window_size())
    print(w.get_coord_bases())

# SetForegroundWindow bug reference :
# https://stackoverflow.com/questions/56857560/win32gui-setforegroundwindowhandle-not-working-in-loop

"""
Module for window controller.
"""

import sys
import logging
from time import sleep

import win32gui
# import win32api, win32con
import pyautogui as pag


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
        self._game_rect = win32gui.GetWindowRect(self._game_hwnd)

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
            logger.error(f'Failed to locate the game window: "{self._title}"')
            sys.exit()
        return hwnd

    def get_window_size(self) -> str:
        """Get the window size in "{width}x{height}" format.
        :return: formatted window size
        :rtype: str
        """
        width = self._game_rect[2] - self._game_rect[0]
        height = self._game_rect[3] - self._game_rect[1]
        return f"{width}x{height}"

    def get_base_coords(self) -> tuple[int, int]:
        """Get base x and y coordinates.

        :return: base x, base y
        :rtype: tuple[int, int]
        """
        return self._game_rect[0], self._game_rect[1]

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
    # w.activate_game_window()
    print(w.get_window_size())
    print(w.get_base_coords())

# SetForegroundWindow bug reference :
# https://stackoverflow.com/questions/56857560/win32gui-setforegroundwindowhandle-not-working-in-loop

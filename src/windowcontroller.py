"""
Module for window controller.
"""
from time import sleep

from pyautogui import *
import win32api, win32con, win32gui

class WindowController():
    """Controller for terminal and game windows management.
    """
    def __init__(self, game_window_title='Russian Fishing 4'):
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
            print(f'Failed to locate the window with title "{self._title}"')
            exit()
        return hwnd
            
    def activate_script_window(self) -> None:
        """Focus terminal.
        """
        win32gui.SetForegroundWindow(self._script_hwnd) # fullscreen mode is not supported
        sleep(0.25)

    def activate_game_window(self) -> None:
        """Focus game window.
        """
        win32gui.SetForegroundWindow(self._game_hwnd) # fullscreen mode is not supported
        sleep(0.25)

# if __name__ == '__main__':
#     from pyautogui import getWindowsWithTitle
#     w = WindowController('Russian Fishing 4')
#     w.get_hwnd()
#     w.activate_window()

#     window = getWindowsWithTitle("Russian Fishing 4")[0]
#     print(window)
#     print(getWindowsWithTitle('123'))
#     getWindowsWithTitle('123')[0].activate()
#     window.activate()
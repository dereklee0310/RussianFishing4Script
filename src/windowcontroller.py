from pyautogui import *
from time import sleep
import win32api, win32con, win32gui

# sleep(3)
# keyDown('w')
class WindowController():
    def __init__(self, title=None):
        self._title = title
        self._script_hwnd = self._get_cur_hwnd()
        self._game_hwnd = self._get_game_hwnd()

    def _get_cur_hwnd(self):
        return win32gui.GetForegroundWindow()

    def _get_game_hwnd(self):
        hwnd = win32gui.FindWindow(None, self._title) # english window title only
        # print(win32gui.GetClassName(hwnd)) # class name: UnityWndClass
        if not hwnd:
            print(f'Fatal error: Failed to locate the game window: {self._title}') # log
            exit()
        return hwnd
            
    def activate_script_window(self):
        win32gui.SetForegroundWindow(self._script_hwnd) # fullscreen mode is not supported

    def activate_game_window(self):
        win32gui.SetForegroundWindow(self._game_hwnd) # fullscreen mode is not supported

# w = WindowController('Russian Fishing 4')
# w.get_hwnd()
# w.activate_window()

# window = getWindowsWithTitle("Russian Fishing 4")[0]
# print(window)
# print(getWindowsWithTitle('123'))
# getWindowsWithTitle('123')[0].activate()
# window.activate()
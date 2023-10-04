from pyautogui import *

import pyautogui
import pydirectinput
import time
import keyboard
import random  
import win32api, win32con
import random
from time import sleep
import sys
import pyuac

# if not pyuac.isUserAdmin():
#     print("Re-launching as admin!")
#     pyuac.runAsAdmin()

# for i in range(3, 0, -1):
#     sleep(1)
#     print(i)
# # pydirectinput.moveRel(0, -200, duration=1)
# pydirectinput.moveRel(0, -1000, duration=10)
# # pyautogui.moveRel(0, -1000, duration=10)

# import win32con

# import win32api
# from time import sleep

# sleep(3)

# win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(0), int(100), 0, 0)
for i in range(3, 0, -1):
    sleep(1)
press('esc')

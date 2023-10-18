from pyautogui import *
import time
import keyboard
import random  
import win32api, win32con
import random
from time import sleep
import sys
import datetime

class Mouse():
    def hold_left_click(timeout=1):
        mouseDown()
        sleep(timeout)
        mouseUp()

# class FailureRecord():
#     reset_fail = 0
from pyautogui import *

import pyautogui
import time
import keyboard
import random  
import win32api, win32con
import random
from time import sleep
import sys
import datetime

sleep(1)

window = pyautogui.getWindowsWithTitle("Russian Fishing 4")[0]
window.activate()
pyautogui.moveTo(pyautogui.locateOnScreen('quit.png', confidence=0.9), duration=0.2)
pyautogui.click()
pyautogui.moveTo(pyautogui.locateOnScreen('yes.png', confidence=0.9), duration=0.2)

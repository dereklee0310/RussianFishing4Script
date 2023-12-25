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
# from src.timer import Timer

# import sys, os
# script_dir = sys.path[0]
# print(script_dir)


# from pathlib import Path
# output_file = Path("./test/baz.txt")
# output_file.parent.mkdir(exist_ok=True, parents=True)


with open(fr'../screenshots/{123}.png', 'wb') as file: 
            screenshot().save(file, 'png')




# sleep(1)

# window = pyautogui.getWindowsWithTitle("Russian Fishing 4")[0]
# window.activate()
# pyautogui.moveTo(pyautogui.locateOnScreen('quit.png', confidence=0.9), duration=0.2)
# pyautogui.click()
# pyautogui.moveTo(pyautogui.locateOnScreen('yes.png', confidence=0.9), duration=0.2)

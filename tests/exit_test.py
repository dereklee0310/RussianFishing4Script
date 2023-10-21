from pyautogui import *
from pyautogui import getWindowsWithTitle
from time import sleep
from rod import Rod
import keyboard
import sys
from inputimeout import inputimeout, TimeoutOccurred
import datetime
from timer import Timer


sleep(3)
press('esc')
keyDown('shift')
moveTo(locateOnScreen('quit.png', confidence=0.9), duration=0.2)
click()
moveTo(locateOnScreen('yes.png', confidence=0.9), duration=0.2)
click()
keyUp('shift')
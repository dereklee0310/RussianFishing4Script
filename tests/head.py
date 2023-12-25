from pyautogui import *
import random
from time import sleep

sleep(3)

while not locateOnScreen(r'..\static\wheel.png', confidence=0.988):
    pass
click()
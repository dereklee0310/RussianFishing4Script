"""
This is only for testing purposes and should not be used.
"""
from pyautogui import *

# import sys
# sys.path.append(r'../')

# import src.script
from windowcontroller import WindowController

WindowController().activate_game_window()
from monitor import is_disconnected

from time import sleep

# loc = locateCenterOnScreen(r'../static/tmp/heart.png', confidence=0.9)
# loc = locateCenterOnScreen(r'../static/en/temperature.png', confidence=0.9)
# loc = locateCenterOnScreen(r'../static/en/energy.png', confidence=0.9)
loc = locateCenterOnScreen(r'../static/en/food.png', confidence=0.9)
print(loc)
print(type(loc.x))
x, y = int(loc.x), int(loc.y)

i = 0
tmp = 0
while True:
    # print(pixel(x + i, y), i)
    if pixel(x + i, y) != pixel(x + i + 1, y):
        print(pixel(x + i, y), tmp, i)
        tmp = 0
    i += 1
    tmp += 1

# print(pixel(x + 18, y), pixel(x + 169, y))
# moveTo(loc)

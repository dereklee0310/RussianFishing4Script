"""
This is only for testing purposes and should not be used.
"""
from pyautogui import *

# import sys
# sys.path.append(r'../')

# import src.script
from windowcontroller import WindowController

controller = WindowController()
controller.activate_game_window()
from monitor import is_disconnected

if is_disconnected():
    print('hehe')
else:
    print('huh')

from time import sleep

# loc = locateCenterOnScreen(r'../static/heart.png', confidence=0.9)
# print(loc)
# x, y = int(loc.x), int(loc.y)

# press('esc')
# sleep(1)
# moveTo(x, y)
# sleep(1)
# press('esc')
# print(x, y)

# i = 0
# tmp = 0
# while True:
#     # print(pixel(x + i, y), i)
#     if pixel(x + i, y) != pixel(x + i + 1, y):
#         print(pixel(x + i, y), tmp, i)
#         tmp = 0
#     i += 1
#     tmp += 1

# print(pixel(x + 18, y), pixel(x + 169, y))
# moveTo(loc)

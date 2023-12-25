# f = open("../static/wheel.png", "rb")
# print(f.read())

from pyautogui import *
print(locateOnScreen(r'..\static\tmp.png', confidence=0.9))
print(locateOnScreen(r'..\static\wheel.png', confidence=0.9))
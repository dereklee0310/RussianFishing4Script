from pyautogui import *

print(position())
while True:
    p = position()
    x, y = p.x, p.y
    print(pixel(x, y))
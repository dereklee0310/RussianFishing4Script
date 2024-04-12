from pyautogui import *
from time import sleep

print(position())
while True:
    sleep(2)
    p = position()
    print(p)
    x, y = p.x, p.y
    # print(pixel(x, y))
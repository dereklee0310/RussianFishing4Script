from pyautogui import *
from time import sleep
import cv2

sleep(1)
min = 2
while True:
    i = 0.9
    while i > 0:
        print(i)
        loc = locateOnScreen('../static/mark.png', confidence=i)
        if loc:
            moveTo(loc)
            min = i if i < min else min
            print('current:', i)
            print('min:', min)
            sleep(3)
            press('right')
            break
        i -= 0.01
        sleep(0.1)

# i = 1.0
# while i > 0:
#     print(i)
#     if locateOnScreen('../static/mark.png', confidence=i):
#         moveTo(locateOnScreen('../static/mark.png', confidence=i))
#         # press('right')
#         min = i if i < min else min
#         print('current:', i)
#         print('min:', min)
#         break
#     i -= 0.01
#     sleep(0.1)
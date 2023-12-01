from pyautogui import *
sleep(3)
print(locateOnScreen('../static/mark.png', confidence=0.7))
moveTo(locateOnScreen('../static/mark.png', confidence=0.7))
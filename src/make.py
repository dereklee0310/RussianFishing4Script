from pyautogui import *
from pyautogui import getWindowsWithTitle
from time import sleep

window = getWindowsWithTitle("Russian Fishing 4")[0]
window.activate()
moveTo(locateOnScreen('../static/make.png', confidence=0.8))
try:
    while True:
        click()
        if locateOnScreen('../static/warning.png', confidence=0.8):
            press('space')
            break
        sleep(4)
        while not locateOnScreen('../static/ok.png', confidence=0.8) and not locateOnScreen('../static/warning.png', confidence=0.8):
            sleep(0.25)
        press('space')
        sleep(0.1)
except KeyboardInterrupt:
    exit()
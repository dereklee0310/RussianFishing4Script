from pyautogui import *
from time import sleep

def hold_left_click(duration=1):
    mouseDown()
    sleep(duration)
    mouseUp()

def hold_right_click(duration=1):
    mouseDown(button="right")
    sleep(duration)
    mouseUp(button="right")

# class FailureRecord():
#     reset_fail = 0
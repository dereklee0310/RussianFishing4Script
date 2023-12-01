from pyautogui import *
from time import sleep
import keyboard
import sys
from timer import Timer
import time
import win32api, win32con
from threading import Thread

class Monitor():
    # def __init__(self):
    #     #todo: init thread
    #     pass
        
    #todo: use thread.stop?
    # def examine_rod(self):
    #     while True:
    #         sleep(32)
    #         if self.is_rod_broked():
    #             #todo: exit
    #             pass

    def is_fish_hooked(self):
        return locateOnScreen('../static/get.png', confidence=0.8)
    
    def is_rod_broked(self):
        return locateOnScreen('../static/broke.png', confidence=0.6)
    
    def is_fish_captured(self):
        return locateOnScreen('../static/keep.png', confidence=0.9)
    
    def is_retrieve_finished(self):
        return locateOnScreen('../static/wheel.png', confidence=0.985)
    
    def is_rod_ready(self):
        return locateOnScreen('../static/ready.png', confidence=0.6)
    
    def is_fish_marked(self):
        return locateOnScreen('../static/mark.png', confidence=0.7)
    
    #todo is_rod_snagged(self): ...
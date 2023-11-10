from pyautogui import *
from time import sleep
from mouse import Mouse
import sys

class Rod():
    def __init__(self):
        self.READY_TIMEOUT = 8
        self.RETRIEVE_BASE_TIME = 32
        self.RETRIEVE_TIMEOUT = 600
        self.PULL_FISH_TIMEOUT = 4

    def fast_retrieve(self, duration, delay):
        with hold('shift'):
            Mouse.hold_left_click(duration)
            sleep(delay)

    def slow_retrieve(self, duration, delay):
        Mouse.hold_left_click(duration)
        if duration >= 2.2:
            click()
        sleep(delay)

    def reset(self, trophy_mode=None):
        i = self.READY_TIMEOUT if not trophy_mode else 12
        print('Resetting')
        while i > 0 and not locateOnScreen('../static/ready.png', confidence=0.6):
            self.slow_retrieve(duration=4, delay=0.25)
            i -= 1
        
        if not i:
            print('! Failed to reset the tackle')
            # FailureRecord.reset_fail += 1 #todo
    
    def cast(self):
        print('Casting')
        with hold('shift'):
            Mouse.hold_left_click(1)
        sleep(6) # wait for the lure to sink
    
    def retrieve(self, duration=None, delay=4):
        print('Retrieving')

        if not duration:
            duration = self.RETRIEVE_BASE_TIME
        Mouse.hold_left_click(duration)
        i = self.RETRIEVE_TIMEOUT
        while i > 0 and not locateOnScreen('../static/wheel.png', confidence=0.988):
            i -= 1
        sleep(delay) # wait for the line to be fully retrieved
        click()

    def tighten_fishline(self):
        for i in range(2):
            self.slow_retrieve(2, 0.25)

    def is_fish_hooked(self):
        return locateOnScreen('../static/get.png', confidence=0.8)

    def pull(self, i=None):
        print('Pulling')
        mouseDown(button='right')
        i = self.PULL_FISH_TIMEOUT if not i else i
        while i > 0 and not locateOnScreen('../static/keep.png', confidence=0.9):
            self.slow_retrieve(2, 0.25)
            i -= 1
        mouseUp(button='right')
        sleep(1) # leave some time to inspect the fish
        return i 

    def is_broked(self):
        return locateOnScreen('../static/broke.png', confidence=0.6)
        
        # if self.is_keepnet_full():
        #     self.logout()
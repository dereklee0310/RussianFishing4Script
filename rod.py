from pyautogui import *
from time import sleep
from mouse import Mouse
import sys

class Rod():
    def __init__(self):
        self.READY_TIMEOUT = 10
        self.RETRIEVE_BASE_TIME = 10
        self.RETRIEVE_TIMEOUT = 300
        self.PULL_FISH_TIMEOUT = 10

    def fast_retrieve(self, duration, delay):
        with hold('shift'):
            Mouse.hold_left_click(duration)
            sleep(delay)

    def slow_retrieve(self, duration, delay):
        Mouse.hold_left_click(duration)
        sleep(delay)

    def reset(self):
        i = self.READY_TIMEOUT
        print('resetting')
        while i > 0 and not locateOnScreen('ready.png', confidence=0.6):
            self.slow_retrieve(duration=2, delay=0.25)
            i -= 1
        
        if not i:
            print('! failed to reset the tackle')
            # FailureRecord.reset_fail += 1 #todo
    
    def cast(self):
        print('casting')
        with hold('shift'):
            Mouse.hold_left_click(1)
        sleep(6) # wait for the lure to sink
    
    def retrieve(self):
        print('retrieving')
        Mouse.hold_left_click(self.RETRIEVE_BASE_TIME)
        i = self.RETRIEVE_TIMEOUT
        while i > 0 and not locateOnScreen('wheel.png', confidence=0.985):
            i -= 1
        sleep(8) # wait for the line to be fully retrieved
        click()

    def tighten_fishline(self):
        for i in range(2):
            self.slow_retrieve(2, 0.25)

    def is_fish_hooked(self):
        return locateOnScreen('get.png', confidence=0.8)

    def pull(self):
        print('pulling')
        mouseDown(button='right')
        i = self.PULL_FISH_TIMEOUT
        while i > 0 and not locateOnScreen('keep.png', confidence=0.9):
            self.slow_retrieve(1, 0.25)
            i -= 1
        mouseUp(button='right')
        sleep(1) # leave some time to inspect the fish
        return i 

    def is_broked(self):
        return locateOnScreen('broke.png', confidence=0.6)
        
        # if self.is_keepnet_full():
        #     self.logout()
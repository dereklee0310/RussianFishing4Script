from pyautogui import *
from time import sleep
from mouse import hold_left_click
from monitor import *
from reel import *

class Tackle():
    def __init__(self, profile):
        self.RESET_TIMEOUT = 16
        self.RETRIEVE_BASE_TIME = 32
        self.RETRIEVE_TIMEOUT = 600
        self.PULL_TIMEOUT = 16
        self.reel = globals()[profile.reel_name]()

    def _sleep_and_decrease(self, num, delay):
        sleep(delay)
        return num - delay

    def reset(self, trophy_mode=None):
        print('Resetting')

        if is_tackle_ready():
            return True
        mouseDown()
        i = self.RESET_TIMEOUT if not trophy_mode else 12
        while i > 0 and not is_tackle_ready():
            i = self._sleep_and_decrease(i, 2)
        mouseUp()
        click()
        
        msg = 'Tackle is ready' if i else '! Failed to reset the tackle'
        print(msg)
        return i
    
    def cast(self, power=100, delay=0.1):
        print('Casting')
        if power == 100:
            with hold('shift'):
                hold_left_click(1)
        else:
            hold_left_click(0.8) # 50~60%
        sleep(6) # wait for the lure to sink
        click()
        sleep(delay)
    
    def retrieve(self, duration=None, delay=8):
        print('Retrieving')

        if not duration:
            duration = self.RETRIEVE_BASE_TIME
        self.reel.full_retrieve(duration=duration)
        i = self.RETRIEVE_TIMEOUT
        while i > 0 and not is_retrieve_finished():
            i = self._sleep_and_decrease(i, 4)
        print('Retrieval is finished')
        sleep(delay) # wait for the line to be fully retrieved
        click()

    def special_retrieve(self, duration=0.25, delay=1):
        print('Walking the dog')
        i = self.RETRIEVE_TIMEOUT
        while i > 0 and not is_fish_hooked() and not is_retrieve_finished():
            self.fast_retrieve(duration=0.25, delay=delay)
            i -= 1

        if not is_fish_hooked():
            for i in range(12):
                if is_fish_hooked():
                    break
                self.fast_retrieve(duration=0.25, delay=delay)

        hold_left_click(4)
        while i > 0 and not is_retrieve_finished():
            i -= 1

        print('Retrieve done')
        sleep(4) # wait for the line to be fully retrieved
        click()

    def jig_step(self, duration=0.52, delay=3):
        print('Jig step')
        i = self.RETRIEVE_TIMEOUT
        while i > 0 and not is_fish_hooked() and not is_retrieve_finished():
            self.slow_retrieve(duration=duration, delay=delay)
            i -= 1

        # if not is_fish_hooked():
        #     for i in range(12):
        #         if is_fish_hooked():
        #             break
        #         self.slow_retrieve(duration=duration, delay=delay)

        hold_left_click(4)
        while i > 0 and not is_retrieve_finished():
            i -= 1

        print('Retrieve done')
        sleep(30) # wait for the line to be fully retrieved
        click()

    # todo: default pull timeout
    def pull(self, i=None):
        print('Pulling')
        mouseDown(button='right')
        mouseDown()
        i = self.PULL_TIMEOUT if not i else i
        while i > 0 and not is_fish_captured():
            print(i)
            i = self._sleep_and_decrease(i, 2)
        mouseUp(button='right')
        mouseDown()
        click()
        sleep(1) # leave some time to inspect the fish
        return i 
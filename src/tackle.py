from pyautogui import *
from time import sleep
from mouse import hold_left_click
from monitor import *
from reel import *

class Tackle():
    def __init__(self, reel_name):
        self.RESET_TIMEOUT = 16
        self.RETRIEVE_BASE_TIME = 32
        self.RETRIEVE_TIMEOUT = 600
        self.PULL_TIMEOUT = 32
        self.reel = globals()[reel_name]()

    def _sleep_and_decrease(self, num, delay) -> int:
        """Wrapper for self-decrement and sleep function.

        :param num: the variable to decrease
        :type num: int
        :param delay: time to sleep
        :type delay: int
        :return: the variable after decrement
        :rtype: int
        """
        sleep(delay)
        return num - delay

    def reset(self, trophy_mode=None):
        #todo: revise docstring
        """_summary_

        :param trophy_mode: _description_, defaults to None
        :type trophy_mode: _type_, optional
        :return: _description_
        :rtype: _type_
        """
        print('Resetting')
        mouseDown()
        i = self.RESET_TIMEOUT if not trophy_mode else 12
        while i > 0 and not is_tackle_ready():
            i = self._sleep_and_decrease(i, 2)
        mouseUp()
        click()
        
        msg = 'Tackle is ready' if i else '! Failed to reset the tackle'
        print(msg)
        return i
    
    def cast(self, power_level=3, cast_delay=6, sink_delay=0.1):
        """Universal cast function for all types of fishing strategies.

        :param power_level: casting power, 1: 0%, 2: 50%, 3: 100%+, defaults to 3
        :type power_level: int, optional
        :param cast_delay: time to wait until the lure/bait contact with the water, defaults to 6
        :type cast_delay: int, optional
        :param sink_delay: time to wait until the lure/bait sink beneath the water, defaults to 0.1
        :type sink_delay: float, optional
        :raises ValueError: #todo: _description_
        """
        print('Casting')
        match power_level:
            case 1:
                click()
            case 2:
                hold_left_click(0.8)
            case 3:
                with hold('shift'):
                    hold_left_click(1)
            case _:
                raise ValueError('Invalid power level') #todo
        sleep(cast_delay)
        click()
        sleep(sink_delay)   
    
    def retrieve(self, duration=None, delay=4):
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

    def pull(self) -> bool:
        """Pull the fish until it has been captured or timeout.

        :return: True if fish is successfully captured, False otherwise
        :rtype: bool
        """
        print('Pulling')

        mouseDown() # keep retrieving until fish is captured
        mouseDown(button='right')
        i = self.PULL_TIMEOUT
        while i > 0 and not is_fish_captured():
            i = self._sleep_and_decrease(i, 2)
            
        # retrieve 8 more seconds
        if not i:
            sleep(8)
        mouseUp()
        mouseUp(button='right')
        click()

        msg = 'Fish is captured' if i else '! Failed to pull the fish up'
        sleep(1) # wait for user to inspect the fish
        return i
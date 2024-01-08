"""
Module for Tackle class

Todo: special retrieval for jig step, twitchiing...
"""
from pyautogui import *
from time import sleep
from script import *
from monitor import *
from reel import *

class Tackle():
    """Class for all tackle depentent methods.
    """
    def __init__(self, reel_name: str):
        """Constructor method.

        :param reel_name: reel name
        :type reel_name: str
        """
        self.RESET_TIMEOUT = 32
        self.RETRIEVE_TIMEOUT = 300
        self.PULL_TIMEOUT = 32
        self.reel = globals()[reel_name]()
        self.PIRKING_TIMEOUT = 8

    def reset(self, trophy_mode=None) -> bool:
        #todo: revise trophy mode and docstring
        """Reset the tackle with a timeout.

        :param trophy_mode: _description_, defaults to None
        :type trophy_mode: _type_, optional
        :return: True if the reset is successful, False otherwise 
        :rtype: bool
        """
        print('Resetting')

        mouseDown()
        i = self.RESET_TIMEOUT if not trophy_mode else 12
        while i > 0 and not is_tackle_ready():
            i = sleep_and_decrease(i, 3) # > ClickLock duration (2.2)
        mouseUp()
        click()
        
        msg = 'Resetting success' if i > 0 else '! Failed to reset the tackle'
        print(msg)
        return i > 0
    
    def cast(self, 
             power_level: int | None=3, 
             cast_delay: int | None=6,
             sink_delay: int | None=0) -> None:
        """Cast the rod.

        :param power_level: casting power, 1: 0%, 2: 50%, 3: 100%+, defaults to 3
        :type power_level: int, optional
        :param cast_delay: time to wait until lure/bait contact withwater, defaults to 6
        :type cast_delay: int, optional
        :param sink_delay: time to wait until lure/bait sink beneath water, defaults to 0
        :type sink_delay: int, optional
        :raises ValueError: #todo: _description_
        """
        print('Casting')

        match power_level:
            case 1:
                click()
                return # early return for marine fishing
            case 2:
                hold_left_click(0.8)
            case 3:
                with hold('shift'):
                    hold_left_click(1)
            case _:
                raise ValueError('Invalid power level') #todo
            
        sleep(cast_delay)
        click()
        if sink_delay:
            sleep(sink_delay)   
    

    def retrieve(self, duration: int, delay: int) -> bool:
        """Retrieve the lure/bait with a timeout.

        :param duration: base time of retrieval
        :type duration: int, optional
        :param delay: delay after retrieval
        :type delay: int, optional
        :return: True if the retrieval is successful, False otherwise
        :rtype: bool
        """
        print('Retrieving')

        self.reel.full_retrieve(duration=duration)
        i = self.RETRIEVE_TIMEOUT
        while i > 0 and not is_retrieve_finished():
            i = sleep_and_decrease(i, 3)
        sleep(delay) # wait for the line to be fully retrieved
        click()

        msg = 'Retrieving success' if i > 0 else '! Timeout reached'
        print(msg)
        return i > 0

    def pirking(self, duration: float, delay: float) -> bool:
        """Do pirking with a time out.

        :param duration: rod lifting time
        :type duration: float
        :param delay: delay after lifting
        :type delay: float
        :return: True if a fish is hooked, False otherwise
        :rtype: bool
        """
        print('Pirking')

        i = self.PIRKING_TIMEOUT
        while i > 0 and not is_fish_hooked():
            i -= 1
            hold_right_click(duration=duration)
            sleep(delay)

        msg = 'Pirking success' if i > 0 else '! Timeout reached'
        print(msg)
        return i > 0

    def pull(self) -> bool:
        """Pull the fish with a timeout.

        :return: True if the pulling is successful, False otherwise
        :rtype: bool
        """
        print('Pulling')

        mouseDown() # keep retrieving until fish is captured
        mouseDown(button='right')
        i = self.PULL_TIMEOUT
        while i > 0 and not is_fish_captured():
            i = sleep_and_decrease(i, 3) # > ClickLock duration (2.2)
        mouseUp()
        mouseUp(button='right')
        click()

        msg = 'Pulling success' if i > 0 else '! Failed to pull the fish up'
        print(msg)
        sleep(1) # wait for user to inspect the fish
        return i > 0
    

    #todo
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
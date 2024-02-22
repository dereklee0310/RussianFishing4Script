"""
Module for Tackle class

Todo: special retrieval for jig step, twitchiing...
"""
from time import sleep

from pyautogui import *

from script import *
from monitor import *
from reel import *

class Tackle():
    """Class for all tackle dependent methods.
    """
    def __init__(self, timer):
        """Constructor method.

        :param timer: timer initialized in Player class
        :type timer: Timer
        """
        self.timer = timer
        self.RESET_TIMEOUT = 16
        self.RETRIEVE_TIMEOUT = 60
        self.PULL_TIMEOUT = 32
        self.PIRKING_TIMEOUT = 32
        self.RETRIEVE_WITH_PAUSE_TIMEOUT = 128
        self.reel = Reel()

    def reset(self) -> bool:
        """Reset the tackle with a timeout.

        :return: True if the reset is successful, False otherwise 
        :rtype: bool
        """
        print('Resetting')

        if is_tackle_ready():
            return True

        mouseDown()
        i = self.RESET_TIMEOUT
        while i > 0 and not is_tackle_ready():
            i = sleep_and_decrease(i, 3) # > ClickLock duration (2.2)
        mouseUp()
        click()
        
        msg = 'Resetting success' if i > 0 else '! Failed to reset the tackle'
        print(msg)
        return i > 0
    
    def cast(self, 
             power_level: float | None=3, 
             cast_delay: int | None=6,
             sink_delay: int | None=0) -> None:
        """Cast the rod.

        :param power_level: casting power, 1: 0%, 2: ~25%, 3: ~50%, 4: ~75% 5: 100%+, defaults to 3
        :type power_level: float, optional
        :param cast_delay: time to wait until lure/bait contact with water, defaults to 6
        :type cast_delay: int, optional
        :param sink_delay: time to wait until lure/bait sink below water, defaults to 0
        :type sink_delay: int, optional
        :raises ValueError: raise if the cast power level is invalid
        """
        print('Casting')

        if power_level < 0 or power_level > 5:
            print('! Invalid power level')
            exit()
        elif power_level == 1:
            click()
        elif power_level == 5:
            with hold('shift'):
                hold_left_click(1)
        else:
            duration = 1.6 * (power_level - 1) / 4 # -1 to keep consistent with old settings
            hold_left_click(duration)
            
        sleep(cast_delay)
        if sink_delay:
            sleep(sink_delay)
        
        self.timer.update_cast_hour()
        print('Casting success')

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
        """Perform pirking with a time out.

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
            hold_right_click(duration=duration)
            i = sleep_and_decrease(i, delay)

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

        if i <= 0:
            press('space') # use landing net
            sleep(6)
            if is_fish_captured():
                i = 1 # small trick to indicate success
            else:
                # hide landing net if failed
                press('space') 
                sleep(0.5)
        mouseUp()
        mouseUp(button='right')
        click()

        msg = 'Pulling success' if i > 0 else '! Failed to pull the fish up'
        print(msg)
        sleep(1) # wait for user to inspect the fish
        return i > 0

    #todo: refactor iteration
    def retrieve_with_pause(self, 
                            duration: float, 
                            delay: float, 
                            base_iteration: int, 
                            enable_acceleration: bool):
        """Repeat retrieval with pause until timeout.

        :param duration: retrieval duration
        :type duration: float
        :param delay: delay after retrieval
        :type delay: float
        :param base_iteration: minimum number of iterations
        :type base_iteration: int
        :param enable_acceleration: determine if the shift key should be pressed
        :type base_iteration: bool
        """
        print('Retrieving with pause')
        if enable_acceleration:
            keyDown('shift')
        
        i = self.RETRIEVE_WITH_PAUSE_TIMEOUT
        iteration = 0
        while i > 0:
            if is_fish_hooked():
                break
            elif iteration >= base_iteration and is_retrieve_finished():
                break
            self.reel.retrieve_with_pause(duration, delay)
            i -= delay
            iteration += 1

        if enable_acceleration:
            keyUp('shift')
        print('Retrieving with pause success')
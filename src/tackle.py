"""
Module for Tackle class

Todo: special retrieval for jig step, twitchiing...
"""
from time import sleep

# from pyautogui import *
import pyautogui as pag
import logging

import monitor
from script import sleep_and_decrease, hold_right_click
from reel import *

logger = logging.getLogger(__name__)

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
        # self.PIRKING_TIMEOUT = 32
        self.RETRIEVE_WITH_PAUSE_TIMEOUT = 128
        self.reel = Reel()

    def reset(self) -> bool:
        """Reset the tackle with a timeout.

        :return: True if the reset is successful, False otherwise 
        :rtype: bool
        """
        logger.info('Resetting')

        if monitor.is_tackle_ready():
            return True

        pag.mouseDown()
        i = self.RESET_TIMEOUT
        while i > 0 and not monitor.is_tackle_ready():
            i = sleep_and_decrease(i, 3) # > ClickLock duration (2.2)
        pag.mouseUp()
        pag.click()
        
        msg = 'Resetting success' if i > 0 else '! Failed to reset the tackle'
        logger.info(msg)
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
        logger.info('Casting')

        if power_level < 0 or power_level > 5:
            logger.error('Invalid power level')
            exit()
        elif power_level == 1:
            pag.click()
        elif power_level == 5:
            with pag.hold('shift'):
                hold_left_click(1)
        else:
            duration = 1.6 * (power_level - 1) / 4 # -1 to keep consistent with old settings
            hold_left_click(duration)
            
        sleep(cast_delay)
        if sink_delay:
            sleep(sink_delay)
        
        self.timer.update_cast_hour()
        logger.info('Casting success')

    def retrieve(self, duration: int, delay: int) -> bool:
        """Retrieve the lure/bait with a timeout.

        :param duration: base time of retrieval
        :type duration: int, optional
        :param delay: delay after retrieval
        :type delay: int, optional
        :return: True if the retrieval is successful, False otherwise
        :rtype: bool
        """
        logger.info('Retrieving')

        self.reel.full_retrieve(duration=duration)
        i = self.RETRIEVE_TIMEOUT
        while i > 0:
            if monitor.is_line_at_end():
                logger.warning('Fishing line is at its end')
                return False
            elif monitor.is_retrieve_finished():
                break
            i = sleep_and_decrease(i, 3)

        sleep(delay) # wait for the line to be fully retrieved
        pag.click()

        msg = 'Retrieving success' if i > 0 else '! Timeout reached'
        logger.info(msg)
        return i > 0

    def pirk(self, duration: float, delay: float, timeout: float) -> bool:
        """Perform pirking with a time out.

        :param duration: rod lifting time
        :type duration: float
        :param delay: delay after lifting
        :type delay: float
        :param timeout: timeout for a single pirking routine
        :type timeout: float
        :return: True if a fish is hooked, False otherwise
        :rtype: bool
        """
        logger.info('Pirking')

        i = timeout
        while i > 0 and not monitor.is_fish_hooked():
            hold_right_click(duration=duration)
            i = sleep_and_decrease(i, delay)

        msg = 'Pirking success' if i > 0 else '! Timeout reached'
        logger.info(msg)
        return i > 0
    
    def wakey_pirking(self, delay: float) -> bool:
        """todo

        :param delay: _description_
        :type delay: float
        :return: _description_
        :rtype: bool
        """
        logger.info('Pirking')

        i = self.PIRKING_TIMEOUT
        while i > 0 and not monitor.is_fish_hooked():
            with pag.hold('ctrl'):
                pag.click(button='right')
            i = sleep_and_decrease(i, delay)


    def pull(self) -> bool:
        """Pull the fish with a timeout.

        :return: True if the pulling is successful, False otherwise
        :rtype: bool
        """
        logger.info('Pulling')

        pag.mouseDown() # keep retrieving until fish is captured
        pag.mouseDown(button='right')
        i = self.PULL_TIMEOUT
        while i > 0 and not monitor.is_fish_captured():
            i = sleep_and_decrease(i, 3) # > ClickLock duration (2.2)

        if i <= 0:
            pag.press('space') # use landing net
            sleep(6)
            if monitor.is_fish_captured():
                i = 1 # small trick to indicate success
            else:
                # hide landing net if failed
                pag.press('space') 
                sleep(0.5)
        pag.mouseUp()
        pag.mouseUp(button='right')
        pag.click()

        msg = 'Pulling success' if i > 0 else '! Failed to pull the fish up'
        logger.info(msg)
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
        logger.info('Retrieving with pause')
        if enable_acceleration:
            pag.keyDown('shift')
        
        i = self.RETRIEVE_WITH_PAUSE_TIMEOUT
        iteration = 0
        while i > 0:
            if monitor.is_fish_hooked():
                break
            elif iteration >= base_iteration and monitor.is_retrieve_finished():
                break
            self.reel.retrieve_with_pause(duration, delay)
            i -= delay
            iteration += 1

        if enable_acceleration:
            pag.keyUp('shift')
        logger.info('Retrieving with pause success')
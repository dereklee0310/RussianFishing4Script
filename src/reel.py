"""
Module for Reel class
"""
from time import sleep
# from abc import ABC, abstractmethod

import pyautogui as pag

from script import hold_left_click

class Reel():
    """General reel class.
    """
    def full_retrieve(self, duration=3) -> None:
        """Press down left mouse button longer than 2.2 seconds to lock it.

        :param duration: base retrieval duration, defaults to 3
        :type duration: int, optional
        """
        # use this instead of hold_left_click to lock the mouse button
        pag.mouseDown()
        sleep(duration)
        pag.mouseUp()

    def retrieve_with_pause(self, duration: float, delay: float) -> None:
        """Wrapper for retrieval and delay

        :param duration: retrieval duration
        :type duration: float
        :param delay: retrieval delay
        :type delay: float
        """
        hold_left_click(duration)
        sleep(delay)

    def tighten_line(self, duration: float=1.04) -> None:
        """Tighten the line for bottom layer pirking

        :param duration: 2 rotations for 202s (0.52 * 2), defaults to 1.04
        :type duration: float, optional
        """
        hold_left_click(duration)

    def switch_gear_ratio(self) -> None:
        """Switch gear ratio, designed for conventional reel.
        """
        with pag.hold('ctrl'):
            pag.press('space')
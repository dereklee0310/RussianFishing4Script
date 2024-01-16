"""
Module for Classes of different types of reels

Todo: docstrings
"""
from pyautogui import *
from time import sleep
from abc import ABC, abstractmethod
from script import hold_left_click

class Reel(ABC):
    def full_retrieve(self, duration=3):
        # use this instead of hold_left_click to lock the mouse button
        mouseDown()
        sleep(duration)
        mouseUp()

    def retrieve_with_pause(self, duration, delay):
        hold_left_click(duration)
        sleep(delay)

class ConventionalReel(Reel):
    def switch_ratio(self):
        with keyDown('ctrl'):
            press('space')

class SpinningReel(Reel):
    pass

class Narga8000(SpinningReel):
    # todo
    SPEED = 50
    TWITCHING_DURATION = 0.1
    TWITCHING_INTERVAL = 1

    # ONE_ROTATION_DURATION = 0.52  # narga
    # ONE_ROTATION_DURATION = 0.25  # 202s shift
    ONE_ROTATION_DURATION = 0.52  # 202s shift?
    ONE_ROTATION_INTERVAL = 1

    JIG_STEP_DURATION = ONE_ROTATION_DURATION
    JIG_STEP_INTERVAL = 2

    STOP_AND_GO_DURATION = ONE_ROTATION_INTERVAL * 3 
    STOP_AND_GO_INTERVAL =  2


class Meteor30s(SpinningReel):
    pass

class Venga10000(SpinningReel):
    ONE_ROTATION_DURATION = 0.55  # 202s shift?
    ONE_ROTATION_INTERVAL = 1

    # JIG_STEP_DURATION = 0.86
    # JIG_STEP_DURATION = 0.52
    JIG_STEP_DURATION = 0.55 * 2
    # JIG_STEP_INTERVAL = 2
    JIG_STEP_INTERVAL = 3

    def retrieve_with_pause(self, duration, delay):
        hold_left_click(duration)
        sleep(delay)

class Lacerti24000S(SpinningReel):
    pass

class Rigal202s(ConventionalReel):
    ONE_ROTATION_DURATION = 0.52  # 202s
    ONE_ROTATION_INTERVAL = 1

    PRE_ROTATION_DURATION = ONE_ROTATION_DURATION * 2
    def do_pre_rotation(self):
        hold_left_click(self.PRE_ROTATION_DURATION)
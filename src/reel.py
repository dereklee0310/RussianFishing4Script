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
        hold_left_click(duration=duration)

    def retrieve_and_sleep(self, duration, delay):
        hold_left_click(duration=duration)
        if duration >= 2.2:
            click()
        sleep(delay)

    @abstractmethod
    def walk_the_dog(self):
        pass
    
    @abstractmethod
    def twitching(self):
        pass

    @abstractmethod
    def jig_step(self):
        pass

    @abstractmethod
    def stop_and_go(self):
        pass

    @abstractmethod
    def retrieval_and_pause(self):
        pass

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

    # ONE_ROTATION_DURATION = 0.52  # narga??
    # ONE_ROTATION_DURATION = 0.25  # 202s shift?
    ONE_ROTATION_DURATION = 0.52  # 202s shift?
    ONE_ROTATION_INTERVAL = 1

    JIG_STEP_DURATION = ONE_ROTATION_DURATION
    JIG_STEP_INTERVAL = 2

    STOP_AND_GO_DURATION = ONE_ROTATION_INTERVAL * 3 
    STOP_AND_GO_INTERVAL =  2
    
    def walk_the_dog(self):
        with hold('shift'):
            hold_left_click(self.ONE_ROTATION_DURATION)
            sleep(self.ONE_ROTATION_INTERVAL)
    
    def twitching(self):
        hold_left_click(self.TWITCHING_DURATION)
        sleep(self.TWITCHING_INTERVAL)

    def jig_step(self):
        hold_left_click(self.JIG_STEP_DURATION)
        sleep(self.JIG_STEP_INTERVAL)

    def stop_and_go(self):
        hold_left_click(self.JIG_STEP_DURATION)
        click()
        sleep(self.JIG_STEP_INTERVAL)

    def retrieval_and_pause(self):
        pass


class Meteor30s(SpinningReel):
    def walk_the_dog(self):
        pass
    
    def twitching(self):
        pass

    def jig_step(self):
        pass

    def stop_and_go(self):
        pass

    def retrieval_and_pause(self):
        pass

class Venga10000(SpinningReel):
    def walk_the_dog(self):
        pass
    
    def twitching(self):
        pass

    def jig_step(self):
        pass

    def stop_and_go(self):
        pass

    def retrieval_and_pause(self):
        pass

class Lacerti24000S(SpinningReel):
    def walk_the_dog(self):
        pass
    
    def twitching(self):
        pass

    def jig_step(self):
        pass

    def stop_and_go(self):
        pass

    def retrieval_and_pause(self):
        pass

class Rigal202s(ConventionalReel):
    ONE_ROTATION_DURATION = 0.52  # 202s
    ONE_ROTATION_INTERVAL = 1

    PRE_ROTATION_DURATION = ONE_ROTATION_DURATION * 2

    def walk_the_dog(self):
        pass
    
    def twitching(self):
        pass

    def jig_step(self):
        pass

    def stop_and_go(self):
        pass

    def retrieval_and_pause(self):
        pass

    def do_pre_rotation(self):
        hold_left_click(self.PRE_ROTATION_DURATION)
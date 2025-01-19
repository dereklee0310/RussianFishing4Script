"""
Module for Tackle class and some decorators.

"""

# pylint: disable=c-extension-no-member

import logging
import random
from time import sleep

import pyautogui as pag
import win32api
import win32con

import exceptions
import script
from monitor import Monitor
from setting import Setting
from timer import Timer

logger = logging.getLogger(__name__)

RESET_TIMEOUT = 16
CAST_SCALE = 0.4  # 25% / 0.4s

# BASE_DELAY + LOOP_DELAY >= 2.2 to trigger clicklock
BASE_DELAY = 1
LOOP_DELAY = 2

ANIMATION_DELAY = 0.5

RETRIEVAL_TIMEOUT = 32
PULL_TIMEOUT = 32
RETRIEVAL_WITH_PAUSE_TIMEOUT = 128
LIFT_DURATION = 3
TELESCOPIC_RETRIEVAL_TIMEOUT = 8
LANDING_NET_DURATION = 6
LANDING_NET_DELAY = 0.5


OFFSET = 100
NUM_OF_MOVEMENT = 4


class Tackle:
    """Class for all tackle dependent methods."""

    def __init__(self, setting: Setting, monitor: Monitor, timer: Timer):
        """Get timer and setting from caller (Player).

        :param setting: universal setting node
        :type setting: Setting
        :param setting: universal monitor node
        :type setting: Monitor
        :param timer: object for timing methods
        :type timer: Timer
        """
        self.timer = timer
        self.setting = setting
        self.monitor = monitor

        self.landing_net_out = False  # for telescopic_pull()

    @script.toggle_clicklock
    def reset(self) -> None:
        """Reset the tackle till ready and detect unexpected events.

        :raises exceptions.FishHookedError: a fish is hooked
        :raises exceptions.FishCapturedError: a fish is captured
        :raises exceptions.TimeoutError: loop timed out
        """
        logger.info("Resetting")
        i = RESET_TIMEOUT
        while i > 0:
            if self.monitor.is_tackle_ready():
                return

            # also check for exceptions that occur frequently
            if self.monitor.is_fish_hooked():
                raise exceptions.FishHookedError
            if self.monitor.is_fish_captured():
                raise exceptions.FishCapturedError
            if self.monitor.is_groundbait_not_chosen():
                raise exceptions.GroundbaitNotChosenError
            i = script.sleep_and_decrease(i, LOOP_DELAY)

        raise TimeoutError

    def cast(self, update=True) -> None:
        """Cast the rod, then wait for the lure/bait to fly and sink.

        :param update: update the record or not (for spod rod), defaults to True
        :type update: bool, optional
        """
        logger.info("Casting")
        if self.setting.mouse_moving_enabled:
            self.move_mouse_randomly()
        match self.setting.cast_power_level:
            case 1:  # 0%
                pag.click()
            case 5:  # power cast
                with pag.hold("shift"):
                    script.hold_mouse_button(1)
            case _:
                # level -1 for backward compatibility
                duration = CAST_SCALE * (self.setting.cast_power_level - 1)
                script.hold_mouse_button(duration)

        sleep(self.setting.cast_delay)
        if update:
            self.timer.update_cast_hour()

    def sink(self, marine: bool = True) -> None:
        """Sink the lure until an event happend, designed for marine and wakey rig.

        :param marine: whether to check is lure moving in bottom layer, defaults to True
        :type marine: bool, optional
        """
        logger.info("Sinking Lure")
        i = self.setting.sink_timeout
        while i > 0:
            i = script.sleep_and_decrease(i, LOOP_DELAY)
            if marine and self.monitor.is_moving_in_bottom_layer():
                logger.info("Lure reached bottom layer")
                break

            if self.is_fish_hooked_twice():
                logger.info("Fish hooked")
                pag.click()
                return

        script.hold_mouse_button(self.setting.tighten_duration)

    def is_fish_hooked_twice(self) -> bool:
        """Check if the fish is still hooked after a short delay.

        :return: True if the fish is still hooked, False otherwise
        :rtype: bool
        """
        if not self.monitor.is_fish_hooked():
            return False

        # check if the fish got away after a short delay
        sleep(self.setting.fish_hooked_delay)
        if self.monitor.is_fish_hooked():
            return True
        return False

    @script.toggle_clicklock
    @script.release_keys_after
    def retrieve(self, first: bool = True) -> None:
        """Retrieve the line till the end is reached and detect unexpected events.

        :param first: whether it's invoked for the first time, defaults to True
        :type first: bool, optional
        :raises exceptions.FishCapturedError: a fish is captured
        :raises exceptions.LineAtEndError: line is at its end
        :raises exceptions.TimeoutError: loop timed out
        """
        logger.info("Retrieving")

        i = RETRIEVAL_TIMEOUT
        while i > 0:
            if self.monitor.is_fish_hooked():
                if self.setting.post_acceleration_enabled == "always":
                    pag.keyDown("shift")
                elif self.setting.post_acceleration_enabled == "auto" and first:
                    pag.keyDown("shift")

                if self.setting.lifting_enabled:
                    script.hold_mouse_button(LIFT_DURATION, button="right")

            if self.monitor.is_retrieval_finished():
                finish_delay = 0 if self.setting.rainbow_line_enabled else 2
                sleep(finish_delay)  # for flexibility of default spool (improve ?)
                return

            elif self.monitor.is_fish_captured():
                raise exceptions.FishCapturedError
            if self.monitor.is_line_at_end():
                raise exceptions.LineAtEndError

            i = script.sleep_and_decrease(i, LOOP_DELAY)

        raise TimeoutError

    @script.release_keys_after
    def retrieve_with_pause(self) -> None:
        """Retreive the line, pause periodically."""
        logger.info("Retrieving with pause")

        if self.setting.pre_acceleration_enabled:
            pag.keyDown("shift")

        i = RETRIEVAL_WITH_PAUSE_TIMEOUT
        while i > 0:
            script.hold_mouse_button(self.setting.retrieval_duration)
            i = script.sleep_and_decrease(i, self.setting.retrieval_delay)
            if self.monitor.is_fish_hooked() or self.monitor.is_retrieval_finished():
                return

    @script.release_keys_after
    def pirk(self, ctrl_enabled: bool) -> None:
        """Start pirking until a fish is hooked.

        :param ctrl_enabled: whether to hold ctrl key during pirking
        :type ctrl_enabled: bool
        :raises TimeoutError: loop timed out
        """
        logger.info("Pirking")

        lift_enabled = self.setting.pirk_duration != 0 or self.setting.pirk_delay != 0
        i = self.setting.pirk_timeout
        while i > 0:
            if self.is_fish_hooked_twice():
                logger.info("Fish hooked")
                pag.click()
                return

            if lift_enabled:
                if ctrl_enabled:
                    pag.keyDown("ctrl")
                script.hold_mouse_button(self.setting.pirk_duration, button="right")
                i = script.sleep_and_decrease(i, self.setting.pirk_delay)
            else:
                i = script.sleep_and_decrease(i, LOOP_DELAY)

        raise TimeoutError

    def elevate(self, drop: bool) -> None:
        """Perform elevator tactic (drop/rise) until a fish is hooked.

        :param drop: whether to drop or rise the lure
        :type drop: bool
        """
        logger.info("Dropping" if drop else "Rising")

        lock = True  # reel is locked after tackle.sink()
        i = self.setting.elevate_timeout
        while i > 0:
            if self.is_fish_hooked_twice():
                logger.info("Fish hooked")
                pag.click()
                return

            if drop:
                pag.press("enter")
                if lock:
                    i = script.sleep_and_decrease(i, self.setting.lock_delay)
                else:
                    i = script.sleep_and_decrease(i, self.setting.lock_duration)
            else:
                if lock:
                    i = script.sleep_and_decrease(i, self.setting.lock_delay)
                else:
                    script.hold_mouse_button(self.setting.lock_duration)
                    i -= self.setting.lock_duration
            lock = not lock

        raise TimeoutError

    @script.toggle_right_mouse_button
    @script.toggle_clicklock
    def general_pull(self) -> None:
        """Pull the fish until it's captured.

        :raises exceptions.FishGotAwayError: fish got away during pulling
        :raises TimeoutError: loop timed out
        """
        logger.info("Pulling")
        i = PULL_TIMEOUT
        while i > 0:
            i = script.sleep_and_decrease(i, LOOP_DELAY)
            if self.monitor.is_fish_captured():
                return

        # try using landing net
        pag.press("space")
        sleep(LANDING_NET_DURATION)
        if self.monitor.is_fish_captured():
            return
        pag.press("space")
        sleep(LANDING_NET_DELAY)

        if not self.monitor.is_fish_hooked():
            raise exceptions.FishGotAwayError
        raise TimeoutError

    @script.toggle_clicklock
    def telescopic_pull(self) -> None:
        """Pull the fish until it's captured, designed for telescopic rod.

        :raises TimeoutError: loop timed out
        """
        logger.info("Pulling")
        # check false postive first
        if not self.monitor.is_fish_hooked():
            return

        # pull out landing net and check
        if not self.landing_net_out:
            pag.press("space")
            self.landing_net_out = True
        i = TELESCOPIC_RETRIEVAL_TIMEOUT
        while i > 0:
            i = script.sleep_and_decrease(i, LOOP_DELAY)
            if self.monitor.is_fish_captured():
                self.landing_net_out = False
                return

        raise TimeoutError()

    def switch_gear_ratio(self) -> None:
        """Switch the gear ratio of a conventional reel."""
        logger.info("Switching gear ratio")
        with pag.hold("ctrl"):
            pag.press("space")

    def move_mouse_randomly(self) -> None:
        """Randomly move the mouse for four times."""
        coords = []
        for _ in range(NUM_OF_MOVEMENT - 1):
            x, y = random.randint(-OFFSET, OFFSET), random.randint(-OFFSET, OFFSET)
            coords.append((x, y))
        coords.append((-sum(x for x, _ in coords), -sum(y for _, y in coords)))
        for x, y in coords:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
            sleep(ANIMATION_DELAY)

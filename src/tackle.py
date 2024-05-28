"""
Module for Tackle class

Todo: special retrieval for jig step, twitchiing...
"""

import logging
from time import sleep

import pyautogui as pag

import script
import exceptions
from timer import Timer
from setting import Setting
from monitor import Monitor

logger = logging.getLogger(__name__)

RESET_TIMEOUT = 16
CAST_SCALE = 0.4  # 25% / 0.4s

# BASE_DELAY + LOOP_DELAY >= 2.2 to trigger clicklock
BASE_DELAY = 1
LOOP_DELAY = 2

RETRIEVAL_TIMEOUT = 64
PULL_TIMEOUT = 32
RETRIEVAL_WITH_PAUSE_TIMEOUT = 128
FLY_SINK_DELAY = 6
LIFT_DURATION = 3
TELESCOPIC_RETRIEVAL_TIMEOUT = 8
LANDING_NET_DURATION = 6
LANDING_NET_DELAY = 0.5


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

    def reset(self) -> None:
        """Reset the tackle till ready and detect unexpected events.

        :raises exceptions.FishHookedError: a fish is hooked
        :raises exceptions.FishCapturedError: a fish is captured
        :raises exceptions.TimeoutError: loop timeouted
        """
        # todo: same as retrieve()
        logger.info("Resetting")
        pag.mouseDown()
        sleep(BASE_DELAY)
        i = RESET_TIMEOUT
        while i > 0:
            i = script.sleep_and_decrease(i, LOOP_DELAY)
            if self.monitor.is_tackle_ready():
                pag.click()
                return

            # also check for exceptions that occur frequently
            if self.monitor.is_fish_hooked():
                raise exceptions.FishHookedError
            if self.monitor.is_fish_captured():
                raise exceptions.FishCapturedError
        pag.click()
        raise TimeoutError

    def cast(self) -> None:
        """Cast the rod, then wait for the lure/bait to fly and sink."""
        # todo: verify power level
        logger.info("Casting")
        match self.setting.cast_power_level:
            case 1:  # 0%
                pag.click()
            case 5:  # power cast
                with pag.hold("shift"):
                    script.hold_left_click(1)
            case _:
                # level -1 for backward compatibility
                duration = CAST_SCALE * (self.setting.cast_power_level - 1)
                script.hold_left_click(duration)

        sleep(FLY_SINK_DELAY)
        self.timer.update_cast_hour()

    def retrieve(self) -> None:
        """Retrieve the line till the end is reached and detect unexpected events.

        :raises exceptions.FishCapturedError: a fish is captured
        :raises exceptions.LineAtEndError: line is at its end
        :raises exceptions.TimeoutError: loop timeouted
        """
        # todo: pag.mouseDown() and pag.click() should be called before and after it
        # they should be handled in decorater or exception handler
        logger.info("Retrieving")
        sleep(BASE_DELAY)
        i = RETRIEVAL_TIMEOUT
        while i > 0:
            i = script.sleep_and_decrease(i, LOOP_DELAY)
            if self.monitor.is_fish_hooked() and self.setting.lift_enabled:
                script.hold_right_click(LIFT_DURATION)

            if self.monitor.is_retrieval_finished():
                finish_delay = 0 if self.setting.rainbow_line_enabled else 2
                sleep(finish_delay)  # for flexibility of default spool (improve ?)
                return

            if self.monitor.is_fish_captured():
                raise exceptions.FishCapturedError
            if self.monitor.is_line_at_end():
                raise exceptions.LineAtEndError

        raise TimeoutError

    def retrieve_with_pause(self) -> None:
        """Retreive the line, pause periodically."""
        # todo: migrate keyDown('shift) ?
        logger.info("Retrieving with pause")
        if self.setting.acceleration_enabled:
            pag.keyDown("shift")

        i = RETRIEVAL_WITH_PAUSE_TIMEOUT
        iteration = 0
        while i > 0:
            script.hold_left_click(self.setting.retrieval_duration)
            i = script.sleep_and_decrease(i, self.setting.retrieval_delay)
            iteration += 1

            if self.monitor.is_fish_hooked():
                return
            if iteration > self.setting.base_iteration:
                raise exceptions.IterationLimitExceedError
            if self.monitor.is_retrieval_finished():
                raise exceptions.RetrieveFinishedError

        if self.setting.acceleration_enabled:
            pag.keyUp("shift")

        raise TimeoutError("retrieve_with_pause")

    def pirk(self) -> None:
        """Start pirking until a fish is hooked.

        :raises TimeoutError: loop timeouted
        """
        logger.info("Pirking")

        i = self.setting.pirk_timeout
        while i > 0:
            script.hold_right_click(self.setting.pirk_duration)
            i = script.sleep_and_decrease(i, self.setting.pirk_delay)

            if not self.monitor.is_fish_hoooked():
                continue

            # check if the fish is still hooked after x seconds
            if self.setting.fish_hooked_delay == 0:
                return
            sleep(self.setting.fish_hooked_delay)
            if self.monitor.is_fish_hooked():
                return

            raise TimeoutError("pirk")  # disable clicklock releasing

    # def wakey_pirking(self, delay: float) -> bool:
    #     """todo

    #     :param delay: _description_
    #     :type delay: float
    #     :return: _description_
    #     :rtype: bool
    #     """
    #     logger.info('Pirking')

    #     i = self.PIRKING_TIMEOUT
    #     while i > 0 and not monitor.is_fish_hooked():
    #         with pag.hold('ctrl'):
    #             pag.click(button='right')
    #         i = script.sleep_and_decrease(i, delay)

    def general_pull(self) -> None:
        """Pull the fish until it's captured.

        :raises TimeoutError: loop timeouted
        """
        # todo: migrate mouseDown(), mouseDown(button="right"), and click()
        logger.info("Pulling")
        pag.mouseDown(button="right")
        sleep(BASE_DELAY)
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
        pag.mouseUp(button="right")

        if not self.monitor.is_fish_hooked():
            raise exceptions.FishGotAwayError
        raise TimeoutError

    def telescopic_pull(self) -> None:
        """Pull the fish until it's captured, designed for telescopic rod.

        :raises TimeoutError: loop timeouted
        """
        # todo: migrate mouseDown() and click()
        logger.info("Pulling")
        # check false postive first
        sleep(BASE_DELAY + LOOP_DELAY)  # 3s is enough for most case?
        if not self.monitor.is_tackle_ready():
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

        raise TimeoutError("telescopic_pull")

    def switch_gear_ratio(self) -> None:
        """Switch the gear ratio of a conventional reel."""
        logger.info("Switching gear ratio")
        with pag.hold("ctrl"):
            pag.press("space")

"""Module for Tackle class and some decorators.

This module provides functionality for managing tackle-related actions in Russian Fishing 4,
such as casting, retrieving, and pulling fish. It also includes decorators for handling
common tasks like clicklock and key releases.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import logging
import random
from time import sleep
from typing import Literal

import pyautogui as pag
import win32api
import win32con
from pyscreeze import Box

from rf4s import exceptions, utils
from rf4s.controller.detection import Detection
from rf4s.controller.timer import Timer

logger = logging.getLogger("rich")

RESET_TIMEOUT = 16
CAST_SCALE = 0.4  # 25% / 0.4s

# BASE_DELAY + LOOP_DELAY >= 2.2 to trigger clicklock
BASE_DELAY = 1.2
LOOP_DELAY = 1

ANIMATION_DELAY = 1

RETRIEVAL_TIMEOUT = 32
PULL_TIMEOUT = 16
RETRIEVAL_WITH_PAUSE_TIMEOUT = 128
LIFT_DURATION = 3
TELESCOPIC_PULL_TIMEOUT = 8
LANDING_NET_DURATION = 6
LANDING_NET_DELAY = 0.5
SINK_DELAY = 2


OFFSET = 100
NUM_OF_MOVEMENT = 4


class Tackle:
    """Class for all tackle-dependent methods.

    This class handles actions related to the fishing tackle, such as casting,
    retrieving, and pulling fish. It also manages tackle resetting and gear ratio switching.

    Attributes:
        cfg (CfgNode): Configuration node for tackle settings.
        timer (Timer): Timer instance for timing actions.
        detection (Detection): Detection instance for in-game state checks.
        landing_net_out (bool): Whether the landing net is deployed.
        available (bool): Whether the tackle is available for use.
    """

    def __init__(self, cfg, timer: Timer, detection: Detection):
        """Initialize the Tackle class with configuration, timer, and detection.

        :param cfg: Configuration node for tackle settings.
        :type cfg: CfgNode
        :param timer: Timer instance for timing actions.
        :type timer: Timer
        :param detection: Detection instance for in-game state checks.
        :type detection: Detection
        """
        self.cfg = cfg
        self.timer = timer
        self.detection = detection
        self.landing_net_out = False  # For telescopic pull
        self.available = True

    @staticmethod
    def _check_status(func):
        def wrapper(self, *args, **kwargs):
            if not self.available:
                return
            try:
                func(self, *args)
            except Exception as e:
                raise e

        return wrapper

    def is_disconnected_or_ticketed_expired(self) -> None:
        """Check if the game disconnected or the boat ticket expired."""
        if self.detection.is_disconnected():
            raise exceptions.DisconnectedError
        if self.detection.is_ticket_expired():
            raise exceptions.TicketExpiredError

    @_check_status
    def reset(self) -> None:
        """Reset the tackle until ready and detect unexpected events.

        :raises exceptions.FishHookedError: A fish is hooked.
        :raises exceptions.FishCapturedError: A fish is captured.
        :raises exceptions.LineAtEndError: The line is at its end.
        :raises exceptions.LineSnaggedError: The line is snagged.
        :raises TimeoutError: The loop timed out.
        """
        logger.info("Resetting tackle")
        i = RESET_TIMEOUT
        while i > 0:
            if self.detection.is_tackle_ready():
                return
            if self.detection.is_fish_hooked():
                raise exceptions.FishHookedError
            if self.detection.is_fish_captured():
                raise exceptions.FishCapturedError
            if self.cfg.SCRIPT.SPOOLING_DETECTION and self.detection.is_line_at_end():
                raise exceptions.LineAtEndError
            if self.cfg.SCRIPT.SNAG_DETECTION and self.detection.is_line_snagged():
                raise exceptions.LineSnaggedError
            if self.detection.is_lure_broken():
                raise exceptions.LureBrokenError
            if self.detection.is_tackle_broken():
                raise exceptions.TackleBrokenError
            i = utils.sleep_and_decrease(i, LOOP_DELAY)

        self.is_disconnected_or_ticketed_expired()
        raise TimeoutError

    @_check_status
    def cast(self, lock: bool) -> None:
        """Cast the rod, then wait for the lure/bait to fly and sink.

        :param lock: Whether to lock the reel after casting.
        :type lock: bool
        """
        logger.info("Casting rod")
        if self.cfg.ARGS.MOUSE:
            self.move_mouse_randomly()
        match self.cfg.SELECTED.CAST_POWER_LEVEL:
            case 1:  # 0%
                pag.click()
            case 5:  # power cast
                with pag.hold("shift"):
                    utils.hold_mouse_button(1)
            case _:
                # -1 for backward compatibility
                duration = CAST_SCALE * (self.cfg.SELECTED.CAST_POWER_LEVEL - 1)
                utils.hold_mouse_button(duration)

        sleep(self.cfg.SELECTED.CAST_DELAY)
        if lock:
            pag.click()

    def sink(self) -> None:
        """Sink the lure until an event happens, designed for marine and wakey rig."""
        logger.info("Sinking lure")
        i = self.cfg.SELECTED.SINK_TIMEOUT
        while i > 0:
            i = utils.sleep_and_decrease(i, LOOP_DELAY)
            if self.detection.is_moving_in_bottom_layer():
                logger.info("Lure has reached bottom layer")
                sleep(SINK_DELAY)
                break

            if self.detection.is_fish_hooked_twice():
                pag.click()  # Lock reel
                return

        utils.hold_mouse_button(self.cfg.SELECTED.TIGHTEN_DURATION)

    @_check_status
    @utils.release_keys_after()
    def retrieve(self, first: bool = True) -> None:
        """Retrieve the line until the end is reached and detect unexpected events.

        :param first: Whether it's invoked for the first time, defaults to True.
        :type first: bool, optional

        :raises exceptions.FishCapturedError: A fish is captured.
        :raises exceptions.LineAtEndError: The line is at its end.
        :raises exceptions.LineSnaggedError: The line is snagged.
        :raises TimeoutError: The loop timed out.
        """
        logger.info("Retrieving fishing line")

        i = RETRIEVAL_TIMEOUT
        while i > 0:
            if self.detection.is_fish_hooked():
                if self.cfg.SELECTED.POST_ACCELERATION == "on":
                    pag.keyDown("shift")
                elif self.cfg.SELECTED.POST_ACCELERATION == "auto" and first:
                    pag.keyDown("shift")

                if self.cfg.ARGS.LIFT:
                    utils.hold_mouse_button(LIFT_DURATION, button="right")

            if self.detection.is_retrieval_finished():
                sleep(0 if self.cfg.ARGS.RAINBOW else 2)
                return

            if self.detection.is_fish_captured():
                raise exceptions.FishCapturedError
            if self.cfg.SCRIPT.SPOOLING_DETECTION and self.detection.is_line_at_end():
                raise exceptions.LineAtEndError
            if self.cfg.SCRIPT.SNAG_DETECTION and self.detection.is_line_snagged():
                raise exceptions.LineSnaggedError
            if self.detection.is_tackle_broken():
                raise exceptions.TackleBrokenError
            i = utils.sleep_and_decrease(i, LOOP_DELAY)

        self.is_disconnected_or_ticketed_expired()
        raise TimeoutError

    @utils.release_keys_after()
    def _special_retrieve(self, button: str) -> None:
        """Retrieve the line with special conditions (pause or lift).

        :param button: The mouse button to use for retrieval.
        :type button: str
        """
        if self.cfg.SELECTED.PRE_ACCELERATION:
            pag.keyDown("shift")
        i = RETRIEVAL_WITH_PAUSE_TIMEOUT
        while i > 0:
            utils.hold_mouse_button(self.cfg.SELECTED.RETRIEVAL_DURATION, button)
            i -= self.cfg.SELECTED.RETRIEVAL_DURATION
            i = utils.sleep_and_decrease(i, self.cfg.SELECTED.RETRIEVAL_DELAY)
            if (
                self.detection.is_fish_hooked()
                or self.detection.is_retrieval_finished()
            ):
                return

    @utils.release_keys_after()
    def pirk(self) -> None:
        """Start pirking until a fish is hooked.

        :raises exceptions.TimeoutError: The loop timed out.
        """
        logger.info("Pirking")

        i = self.cfg.SELECTED.PIRK_TIMEOUT
        while i > 0:
            if self.detection.is_tackle_ready():
                return

            if self.detection.is_fish_hooked_twice():
                pag.click()
                return

            if self.cfg.SELECTED.PIRK_DURATION > 0:
                if self.cfg.SELECTED.CTRL:
                    pag.keyDown("ctrl")
                if self.cfg.SELECTED.SHIFT:
                    pag.keyDown("shift")
                utils.hold_mouse_button(self.cfg.SELECTED.PIRK_DURATION, button="right")
                i -= self.cfg.SELECTED.PIRK_DURATION
                i = utils.sleep_and_decrease(i, self.cfg.SELECTED.PIRK_DELAY)
            else:
                i = utils.sleep_and_decrease(i, LOOP_DELAY)

        self.is_disconnected_or_ticketed_expired()
        raise TimeoutError

    def elevate(self, dropped: bool) -> None:
        """Perform elevator tactic (drop/rise) until a fish is hooked.

        :param dropped: Whether the lure is dropped.
        :type dropped: bool
        :raises exceptions.TimeoutError: The loop timed out.
        """
        locked = True  # Reel is locked after tackle.sink()
        i = self.cfg.SELECTED.ELEVATE_TIMEOUT
        while i > 0:
            if self.detection.is_fish_hooked_twice():
                pag.click()
                return

            if self.cfg.SELECTED.DROP and not dropped:
                pag.press("enter")
                if locked:
                    delay = self.cfg.SELECTED.ELEVATE_DELAY
                else:
                    delay = self.cfg.SELECTED.ELEVATE_DURATION
                i = utils.sleep_and_decrease(i, delay)
            else:
                if locked:
                    i = utils.sleep_and_decrease(i, self.cfg.SELECTED.ELEVATE_DELAY)
                else:
                    utils.hold_mouse_button(self.cfg.SELECTED.ELEVATE_DURATION)
                    i -= self.cfg.SELECTED.ELEVATE_DURATION
            locked = not locked

        self.is_disconnected_or_ticketed_expired()
        raise TimeoutError

    @_check_status
    def pull(self) -> None:
        """Pull the fish until it's captured."""
        logger.info("Pulling fish")
        if self.cfg.SELECTED.MODE == "telescopic":
            self._telescopic_pull()
        else:
            self._pull()

    @utils.toggle_right_mouse_button
    def _pull(self) -> None:
        """Pull the fish until it's captured."""
        i = PULL_TIMEOUT
        while i > 0:
            i = utils.sleep_and_decrease(i, LOOP_DELAY)
            if self.detection.is_fish_captured():
                return
            if self.cfg.SCRIPT.SNAG_DETECTION and self.detection.is_line_snagged():
                raise exceptions.LineSnaggedError

        if not self.detection.is_fish_hooked():
            return
        if self.detection.is_retrieval_finished():
            pag.press("space")
            sleep(LANDING_NET_DURATION)
            if self.detection.is_fish_captured():
                return
            pag.press("space")
            sleep(LANDING_NET_DELAY)
        if self.detection.is_tackle_broken():
            raise exceptions.TackleBrokenError

        self.is_disconnected_or_ticketed_expired()
        raise TimeoutError

    def _telescopic_pull(self) -> None:
        """Pull the fish until it's captured, designed for telescopic rod.

        :raises exceptions.TimeoutError: The loop timed out.
        """
        # Check false postive first because it happens often
        if not self.detection.is_fish_hooked():
            return

        # Toggle landing net when pull() is called for the first time
        if not self.landing_net_out:
            pag.press("space")
            self.landing_net_out = True
        i = TELESCOPIC_PULL_TIMEOUT
        while i > 0:
            i = utils.sleep_and_decrease(i, LOOP_DELAY)
            if self.detection.is_fish_captured():
                self.landing_net_out = False
                return
            if self.detection.is_tackle_broken():
                raise exceptions.TackleBrokenError

        self.is_disconnected_or_ticketed_expired()
        raise TimeoutError

    def switch_gear_ratio(self) -> None:
        """Switch the gear ratio of a conventional reel."""
        logger.info("Switching gear ratio")
        with pag.hold("ctrl"):
            pag.press("space")

    def move_mouse_randomly(self) -> None:
        """Randomly move the mouse for four times."""
        logger.info("Moving mouse randomly")
        coords = []
        for _ in range(NUM_OF_MOVEMENT - 1):
            x, y = random.randint(-OFFSET, OFFSET), random.randint(-OFFSET, OFFSET)
            coords.append((x, y))
        coords.append((-sum(x for x, _ in coords), -sum(y for _, y in coords)))
        for x, y in coords:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)
            sleep(ANIMATION_DELAY)

    def equip_item(self, item) -> None:
        """Equip an item from the menu or inventory.

        :param item: The item to equip (e.g., lure, pva, dry_mix, groundbait).
        :type item: str
        """
        if item == "lure":
            self._equip_item_from_menu(item)
        self._equip_item_from_inventory(item)  # groundbait, dry_mix, pva

    def _equip_item_from_menu(self, item: str) -> None:
        """Equip an item from the menu.

        :param item: The item to equip (e.g., lure).
        :type item: str
        """
        logger.info("Equiping new %s from menu", item)
        with pag.hold("b"):
            self._equip_favorite_item(item)
        sleep(ANIMATION_DELAY)

    @utils.press_before_and_after("v")
    def _equip_item_from_inventory(
        self, item: Literal["dry_mix", "groundbait"]
    ) -> None:
        """Equip an item from the inventory.

        :param item: The item to equip (e.g., dry_mix, groundbait).
        :type item: Literal["dry_mix", "groundbait"]
        """
        logger.info("Equiping new %s from inventory", item)
        scrollbar_position = self.detection.get_scrollbar_position()
        if scrollbar_position is None:
            pag.click(utils.get_box_center(self.get_item_position(item)))
            self._equip_favorite_item(item)
            return

        pag.moveTo(scrollbar_position)
        for _ in range(5):
            sleep(ANIMATION_DELAY)
            pag.drag(xOffset=0, yOffset=125, duration=0.5, button="left")
            position = self.get_item_position(item)
            if position is not None:
                pag.click(utils.get_box_center(position))
                self._equip_favorite_item(item)
                break

    def get_item_position(self, item: str) -> Box | None:
        """Get the position of an item.
        :param item: The item to get the position for (e.g., pva, dry_mix, groundbait)
        :type item: str
        :return: position of the item
        :rtype: Box | None
        """
        if item == "groundbait":
            return self.detection.get_groundbait_position()
        elif item == "dry_mix":
            return self.detection.get_dry_mix_position()
        else:  # pva
            return self.detection.get_pva_position()

    def _equip_favorite_item(self, item: bool):
        """Select a favorite item for replacement and replace the broken one.

        :param item: The item to equip (e.g., lure, pva, dry_mix, groundbait).
        :type item: str
        :raises exceptions.ItemNotFoundError: The item was not found.
        """
        sleep(ANIMATION_DELAY)
        logger.info("Looking for favorite items")
        favorite_item_positions = list(self.detection.get_favorite_item_positions())
        if item == "lure":
            random.shuffle(favorite_item_positions)

        for favorite_item_position in favorite_item_positions:
            x, y = utils.get_box_center(favorite_item_position)
            if item == "lure" and pag.pixel(x - 70, y + 190) == (178, 59, 30):
                continue
            pag.click(x - 70, y + 190, clicks=2, interval=0.1)
            logger.info("New %s equiped successfully", item)
            return

        # Close selection window when equiping from inventory
        if item in ("dry_mix", "groundbait"):
            pag.press("esc")
        raise exceptions.ItemNotFoundError

    def _monitor_float_state(self) -> None:
        """Monitor the state of the float."""
        logger.info("Monitoring float state")
        reference_img = pag.screenshot(region=self.detection.float_camera_rect)
        i = self.cfg.SELECTED.DRIFT_TIMEOUT
        while i > 0:
            i = utils.sleep_and_decrease(i, self.cfg.SELECTED.CHECK_DELAY)
            if self.detection.is_float_state_changed(reference_img):
                logger.info("Float status changed")
                return

        self.is_disconnected_or_ticketed_expired()
        raise TimeoutError

    def _monitor_clip_state(self) -> None:
        """Monitor the state of the bolognese clip."""
        i = self.cfg.SELECTED.DRIFT_TIMEOUT
        while i > 0:
            i = utils.sleep_and_decrease(i, self.cfg.SELECTED.CHECK_DELAY)
            if self.detection.is_clip_open():
                logger.info("Clip status changed")
                return

        self.is_disconnected_or_ticketed_expired()
        raise TimeoutError

"""Module for Tackle class and some decorators.

This module provides functionality for managing tackle-related actions in Russian Fishing 4,
such as casting, retrieving, and pulling fish. It also includes decorators for handling
common tasks like clicklock and key releases.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import random
from enum import Enum, auto
from time import sleep
from typing import Literal

import pyautogui as pag
import win32api
import win32con
from PIL import ImageFilter
from pyscreeze import Box

from rf4s import exceptions, utils
from rf4s.controller import logger
from rf4s.controller.timer import Timer
from rf4s.controller.detection import Detection
from rf4s.utils import add_jitter

CAST_SCALE = 0.4  # 25% / 0.4s
ANIMATION_DELAY = 0.6
LOOP_DELAY = 0.5
SINK_DELAY = 2
LIFT_DURATION = 3
NUM_OF_MOVEMENT = 4
LANDING_NET_DURATION = 6

OFFSET = 100


class StageId(Enum):
    RESET = auto()
    CAST = auto()
    RETRIEVE = auto()
    PULL = auto()
    PIRK = auto()
    ELEVATE = auto()
    LIFT = auto()


class Tackle:
    """Class for all tackle-dependent methods.

    This class handles actions related to the fishing tackle, such as casting,
    retrieving, and pulling fish. It also manages tackle resetting and gear ratio switching.
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
        self.available = True
        self.gear_ratio_changed = False
        self.stage = None

    def check_rare_events(self) -> None:
        """Check if the game disconnected or the boat ticket expired."""
        if self.detection.is_tackle_broken():
            raise exceptions.TackleBrokenError
        if self.detection.is_disconnected():
            raise exceptions.DisconnectedError
        if self.detection.is_ticket_expired():
            raise exceptions.TicketExpiredError
        if self.detection.is_stuck_at_casting():
            raise exceptions.StuckAtCastingError

    def reset(self) -> None:
        """Reset the tackle until ready and detect unexpected events."""
        logger.info("Resetting tackle")

        if self.stage != StageId.RESET:
            self.stage = StageId.RESET
            self.timer.set_timeout_start_time()
        while True:
            if self.detection.is_tackle_ready():
                return
            if self.detection.is_fish_hooked():
                raise exceptions.FishHookedError
            if self.detection.is_fish_captured():
                raise exceptions.FishCapturedError
            if not self.detection.is_bait_chosen():
                raise exceptions.BaitNotChosenError
            if self.cfg.BOT.SPOOLING_DETECTION and self.detection.is_line_at_end():
                raise exceptions.LineAtEndError
            if self.cfg.BOT.SNAG_DETECTION and self.detection.is_line_snagged():
                raise exceptions.LineSnaggedError
            if self.detection.is_lure_broken():
                raise exceptions.LureBrokenError
            if self.detection.is_tackle_broken():
                raise exceptions.TackleBrokenError
            if not self.detection.is_dry_mix_chosen():
                raise exceptions.DryMixNotChosenError
            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
            sleep(add_jitter(LOOP_DELAY))

    def cast(self, lock: bool) -> None:
        """Cast the rod, then wait for the lure/bait to fly and sink.

        :param lock: Whether to lock the reel after casting.
        :type lock: bool
        """
        logger.info("Casting rod")
        self.stage = StageId.CAST  # Make sure telescopic mode can get different id
        if self.cfg.ARGS.MOUSE:
            self.move_mouse_randomly()
        match self.cfg.PROFILE.CAST_POWER_LEVEL:
            case 1:  # 0%
                pag.click()
            case 5:  # power cast
                with pag.hold("shift"):
                    self.hold_mouse_button(1)
            case _:
                # -1 for backward compatibility
                duration = CAST_SCALE * (self.cfg.PROFILE.CAST_POWER_LEVEL - 1)
                self.hold_mouse_button(duration)

        sleep(add_jitter(self.cfg.PROFILE.CAST_DELAY, self.cfg.BOT.JITTER_SCALE))
        if lock:
            pag.click()

    def sink(self) -> None:
        """Sink the lure until an event happens, designed for marine and wacky rig."""
        logger.info("Sinking lure")
        self.timer.set_timeout_start_time()
        while not self.timer.is_sink_stage_timeout():
            if self.detection.is_moving_in_bottom_layer():
                logger.info("Lure has reached bottom layer")
                sleep(
                    add_jitter(SINK_DELAY)
                )  # Drop to the bottom to make the depth consistent
                self.timer.print_sink_duration()
                break

            if self.detection.is_fish_hooked_twice():
                pag.click()
                return
            sleep(add_jitter(LOOP_DELAY))
        self.hold_mouse_button(self.cfg.PROFILE.TIGHTEN_DURATION)

    def retrieve(self) -> None:
        """Retrieve the line until the end is reached and detect unexpected events.

        :raises exceptions.FishCapturedError: A fish is captured.
        :raises exceptions.LineAtEndError: The line is at its end.
        :raises exceptions.LineSnaggedError: The line is snagged.
        """
        logger.info("Retrieving fishing line")
        if self.stage != StageId.RETRIEVE:
            self.stage = StageId.RETRIEVE
            self.timer.set_timeout_start_time()
        while True:
            if self.detection.is_fish_hooked():
                return
            if self.detection.is_retrieval_finished():
                return

            if self.detection.is_fish_captured():
                raise exceptions.FishCapturedError
            if self.cfg.BOT.SPOOLING_DETECTION and self.detection.is_line_at_end():
                raise exceptions.LineAtEndError
            if self.cfg.BOT.SNAG_DETECTION and self.detection.is_line_snagged():
                raise exceptions.LineSnaggedError
            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
            sleep(add_jitter(LOOP_DELAY))

    def pull(self) -> None:
        """Retrieve the line until the end is reached and detect unexpected events.

        :raises exceptions.FishCapturedError: A fish is captured.
        :raises exceptions.LineAtEndError: The line is at its end.
        :raises exceptions.LineSnaggedError: The line is snagged.
        """
        logger.info("Pulling fish")

        if self.stage != StageId.PULL:
            self.stage = StageId.PULL
            self.timer.set_timeout_start_time()
        while True:
            if self.detection.is_retrieval_finished():
                return

            if self.cfg.ARGS.LIFT:
                self.hold_mouse_button(LIFT_DURATION, button="right")

            if self.detection.is_fish_captured():
                raise exceptions.FishCapturedError
            if self.cfg.BOT.SPOOLING_DETECTION and self.detection.is_line_at_end():
                raise exceptions.LineAtEndError
            if self.cfg.BOT.SNAG_DETECTION and self.detection.is_line_snagged():
                raise exceptions.LineSnaggedError
            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
            sleep(add_jitter(LOOP_DELAY))
            if self.timer.is_coffee_drinkable():
                raise exceptions.CoffeeTimeoutError
            if self.timer.is_gear_ratio_changeable():
                raise exceptions.GearRatioTimeoutError

    def special_retrieve(self, button: str) -> None:
        """Retrieve the line with special conditions (pause or lift).

        :param button: The mouse button to use for retrieval.
        :type button: str
        """
        self.timer.set_timeout_start_time()
        while not self.timer.is_special_retrieve_timeout():
            self.hold_mouse_button(self.cfg.PROFILE.RETRIEVAL_DURATION, button)
            sleep(
                add_jitter(self.cfg.PROFILE.RETRIEVAL_DELAY, self.cfg.BOT.JITTER_SCALE)
            )
            if (
                self.detection.is_fish_hooked()
                or self.detection.is_retrieval_finished()
            ):
                return

    def pirk(self) -> None:
        """Start pirking until a fish is hooked."""
        logger.info("Performing pirking")

        if self.stage != StageId.PIRK:
            self.stage = StageId.PIRK
            self.timer.set_timeout_start_time()
        while not self.timer.is_pirk_stage_timeout():
            if self.detection.is_tackle_ready():
                return

            if self.detection.is_fish_hooked_twice():
                # If it's enabled, mouse was already pressed by hold_keys() outside
                if not self.cfg.PROFILE.PIRK_RETRIEVAL:
                    pag.click()
                return

            if self.cfg.PROFILE.PIRK_DURATION > 0:
                if self.cfg.PROFILE.CTRL:
                    pag.keyDown("ctrl")
                if self.cfg.PROFILE.SHIFT:
                    pag.keyDown("shift")
                self.hold_mouse_button(self.cfg.PROFILE.PIRK_DURATION, button="right")
                if self.cfg.PROFILE.CTRL:
                    pag.keyUp("ctrl")
                if self.cfg.PROFILE.SHIFT:
                    pag.keyUp("shift")
                sleep(
                    add_jitter(self.cfg.PROFILE.PIRK_DELAY, self.cfg.BOT.JITTER_SCALE)
                )
            else:
                sleep(add_jitter(LOOP_DELAY))
            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
        raise exceptions.PirkTimeoutError

    def elevate(self) -> None:
        """Perform elevator tactic (drop/rise) until a fish is hooked."""
        logger.info("Performing elevating")
        locked = True  # Reel is locked after tackle.sink()
        dropped = False
        if self.stage != StageId.ELEVATE:
            self.stage = StageId.ELEVATE
            self.timer.set_timeout_start_time()
        while not self.timer.is_elevate_stage_timeout():
            if self.detection.is_fish_hooked_twice():
                # If it's enabled, mouse was already pressed by hold_keys() outside
                if not self.cfg.PROFILE.PIRK_RETRIEVAL:
                    pag.click()
                return

            if self.cfg.PROFILE.DROP and not dropped:
                pag.press("enter")
                if locked:
                    delay = self.cfg.PROFILE.ELEVATE_DELAY
                else:
                    delay = self.cfg.PROFILE.ELEVATE_DURATION
                sleep(add_jitter(delay))
            else:
                if locked:
                    sleep(add_jitter(self.cfg.PROFILE.ELEVATE_DELAY))
                else:
                    self.hold_mouse_button(self.cfg.PROFILE.ELEVATE_DURATION)
            locked = not locked

            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
                dropped = not dropped

    def lift(self) -> None:
        """Pull the fish until it's captured."""
        logger.info("Lifting rod")
        if self.stage != StageId.LIFT:
            self.stage = StageId.LIFT
            if self.cfg.PROFILE.MODE == "telescopic":
                pag.press("space")
            self.timer.set_timeout_start_time()
        if self.cfg.PROFILE.MODE == "telescopic":
            self._telescopic_lift()
        else:
            self._lift()

    @utils.toggle_right_mouse_button  # TODO: FIX THIS
    def _lift(self) -> None:
        """Pull the fish until it's captured."""
        while not self.timer.is_lift_stage_timeout():
            sleep(add_jitter(LOOP_DELAY))
            if self.detection.is_fish_captured():
                return
            if self.cfg.BOT.SNAG_DETECTION and self.detection.is_line_snagged():
                raise exceptions.LineSnaggedError
            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
            if self.timer.is_coffee_drinkable():
                raise exceptions.CoffeeTimeoutError

        if not self.detection.is_fish_hooked():
            return
        if self.detection.is_retrieval_finished():
            pag.press("space")
            sleep(add_jitter(LANDING_NET_DURATION))
            if self.detection.is_fish_captured():
                return
            pag.press("space")
            sleep(add_jitter(ANIMATION_DELAY))
        raise exceptions.LiftTimeoutError

    def _telescopic_lift(self) -> None:
        """Pull the fish until it's captured, designed for telescopic rod."""
        # Check false postive first because it happens often
        if not self.detection.is_fish_hooked():
            return

        while not self.timer.is_lift_stage_timeout():
            sleep(add_jitter(LOOP_DELAY))
            if self.detection.is_fish_captured():
                return
            if self.cfg.BOT.SNAG_DETECTION and self.detection.is_line_snagged():
                raise exceptions.LineSnaggedError
            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
            if self.timer.is_coffee_drinkable():
                raise exceptions.CoffeeTimeoutError
        raise exceptions.LiftTimeoutError

    def change_gear_ratio_or_electro_mode(self) -> None:
        """Switch the gear ratio or electro assist mode."""
        logger.info("Changing gear ratio / electro assist mode")
        with pag.hold("ctrl"):
            pag.press("space")
        self.gear_ratio_changed = not self.gear_ratio_changed

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
            sleep(add_jitter(ANIMATION_DELAY))

    def equip_item(self, item) -> None:
        """Equip an item from the menu or inventory.

        :param item: The item to equip (e.g., lure, pva, dry_mix, groundbait).
        :type item: str
        """
        if item == "lure":
            self._equip_item_from_menu(item)
        else:
            self._equip_item_from_inventory(item)  # groundbait, dry_mix, pva

    def _equip_item_from_menu(self, item: str) -> None:
        """Equip an item from the menu.

        :param item: The item to equip (e.g., lure).
        :type item: str
        """
        logger.info("Equiping new %s from menu", item)
        with pag.hold("b"):
            self._equip_favorite_item(item)
        sleep(add_jitter(ANIMATION_DELAY))

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
            pag.click(utils.get_box_center_integers(self.get_item_position(item)))
            self._equip_favorite_item(item)
            return

        pag.moveTo(utils.get_box_center_integers(scrollbar_position))
        for _ in range(5):
            sleep(add_jitter(ANIMATION_DELAY))
            pag.drag(xOffset=0, yOffset=125, duration=0.5, button="left")
            position = self.get_item_position(item)
            if position is not None:
                pag.click(utils.get_box_center_integers(position))
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
        sleep(add_jitter(ANIMATION_DELAY))
        logger.info("Looking for favorite items")
        favorite_item_positions = list(self.detection.get_favorite_item_positions())
        if item == "lure":
            random.shuffle(favorite_item_positions)

        for favorite_item_position in favorite_item_positions:
            x, y = utils.get_box_center_integers(favorite_item_position)
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
        blurred = reference_img.filter(ImageFilter.GaussianBlur(radius=3))
        self.timer.set_timeout_start_time()
        while not self.timer.is_drift_stage_timeout():
            sleep(add_jitter(self.cfg.PROFILE.CHECK_DELAY))
            if self.detection.is_float_state_changed(blurred):
                logger.info("Float status changed")
                return
            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
        raise exceptions.DriftTimeoutError

    def _monitor_clip_state(self) -> None:
        """Monitor the state of the bolognese clip."""
        logger.info("Monitoring clip state")
        self.timer.set_timeout_start_time()
        while not self.timer.is_drift_stage_timeout():
            sleep(add_jitter(self.cfg.PROFILE.CHECK_DELAY))
            if self.detection.is_clip_open():
                logger.info("Clip status changed")
                return
            if self.timer.is_rare_event_checkable():
                self.check_rare_events()
        raise exceptions.DriftTimeoutError

    def hold_mouse_button(self, duration: float = 1, button: str = "left") -> None:
        """Hold left or right mouse button.

        :param duration: Hold time, defaults to 1.
        :type duration: float, optional
        :param button: Button to click, defaults to "left".
        :type button: str, optional
        """
        if duration == 0:
            return

        pag.mouseDown(button=button)
        sleep(add_jitter(duration))
        pag.mouseUp(button=button)
        # + 0.1 due to pag.mouseDown() delay
        if self.cfg.BOT.CLICK_LOCK and button == "left" and duration >= 2.1:
            pag.click()

    def hold_mouse_buttons(self, duration: float = 1) -> None:
        """Hold left and right mouse buttons simultaneously.

        :param duration: Hold time, defaults to 1.
        :type duration: float, optional
        """
        with pag.hold("ctrl"):
            pag.mouseDown()
            pag.mouseDown(button="right")
            sleep(add_jitter(duration))
            pag.mouseUp()
            pag.mouseUp(button="right")
        # + 0.1 due to pag.mouseDown() delay
        if self.cfg.BOT.CLICK_LOCK and duration >= 2.1:
            pag.click()

"""Module for Player class.

This module provides the main interface for automating fishing activities in a game.
It includes functionality for managing fishing loops, handling player stats, and
automating various fishing techniques.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import json
import os
import random
import sys
from contextlib import contextmanager
from multiprocessing import Lock
from pathlib import Path

# from email.mime.image import MIMEImage
from time import sleep
from typing import Callable

import pyautogui as pag
from rich import box, print
from rich.table import Table

from rf4s import config, exceptions, utils
from rf4s.component.friction_brake import FrictionBrake
from rf4s.component.tackle import Tackle
from rf4s.controller import logger
from rf4s.controller.detection import Detection, TagColor
from rf4s.controller.notification import send_result, send_screenshot
from rf4s.controller.timer import Timer, add_jitter
from rf4s.i18n import t
from rf4s.result.result import BotResult

FISH_CHECK_DURATION = 0.5
ANIMATION_DELAY = 0.5
LOOP_DELAY = 1
USE_ITEM_DELAY = 1
BAD_CAST_DELAY = 1
WEAR_TEXT_UPDATE_DELAY = 2
GET_DIGGING_TOOL_DELAY = 3
CLICK_LOCK_DURATION = 2.2
TAG_ANIMATION_DELAY = 3
DROP_ROD_DELAY = 4
TICKET_EXPIRE_DELAY = 8
DISCONNECTED_DELAY = 8

TROLLING_KEY = "j"
LEFT_KEY = "a"
RIGHT_KEY = "d"

if utils.is_compiled():
    OUTER_ROOT = Path(sys.executable).parent  # Running as .exe (Nuitka/PyInstaller)
else:
    OUTER_ROOT = Path(__file__).resolve().parents[2]


class Player:
    """Main interface of fishing loops and stages.

    This class manages the automation of fishing activities, including casting,
    retrieving, and handling fish. It also handles player stats, equipment, and
    various in-game mechanics.

    :param cfg: Configuration object containing settings for the fishing process.
    :type cfg: Config
    :param window: Window object for managing the game window.
    :type window: Window
    """

    def __init__(self, cfg, timer: Timer, detection: Detection, result: BotResult):
        """Initialize monitor, timer, and some trivial counters.

        :param cfg: Configuration object containing settings for the fishing process.
        :type cfg: Config
        :param window: Window object for managing the game window.
        :type window: Window
        """
        self.cfg = cfg
        self.timer = timer
        self.detection = detection
        self.result = result

        self.tackle_idx = 0
        if self.cfg.PROFILE.MODE == "bottom":
            self.num_tackle = len(self.cfg.KEY.BOTTOM_RODS)
        else:
            self.num_tackle = 1
        self.tackles = [
            Tackle(cfg, self.timer, self.detection) for _ in range(self.num_tackle)
        ]
        self.tackle = self.tackles[self.tackle_idx]

        self.cur_coffee = 0
        self.have_new_lure = True
        self.have_new_groundbait = True
        self.have_new_dry_mix = True
        self.have_new_pva = True
        self.friction_brake = None

        self.trolling_started = False
        self.mouse_pressed = False
        self.shift_pressed = False
        self.using_spod_rod = False
        self.skip_cast = self.cfg.ARGS.SKIP_CAST

    def start_fishing(self) -> None:
        """Start the main fishing loop with the specified fishing strategy."""
        if self.cfg.ARGS.FRICTION_BRAKE:
            # Define here because we cannot start a process twice (same instance)
            self.friction_brake_lock = Lock()
            self.friction_brake = FrictionBrake(
                self.cfg, self.friction_brake_lock, self.detection
            )
            logger.info(t("player.spawning_process"))
            self.friction_brake.monitor_process.start()

        if self.detection.get_quit_position():
            logger.warning(t("player.control_panel_detected"))
            pag.press("esc")
            sleep(ANIMATION_DELAY)

        logger.info(t("player.starting_mode", mode=self.cfg.PROFILE.MODE))
        getattr(self, f"start_{self.cfg.PROFILE.MODE}_mode")()

    def hold_down_left_mouse_button(self):
        pag.mouseDown()
        if self.cfg.BOT.CLICK_LOCK:
            sleep(CLICK_LOCK_DURATION)
        self.mouse_pressed = True

    def release_left_mouse_button(self):
        if self.cfg.BOT.CLICK_LOCK:
            pag.click()
        else:
            pag.mouseUp()
        self.mouse_pressed = False

    def hold_down_shift_key(self):
        pag.keyDown("shift")
        self.shift_pressed = True

    def release_shift_key(self):
        pag.keyUp("shift")
        self.shift_pressed = False

    @contextmanager
    def hold_keys(self, mouse, shift, reset=False):
        mouse_pressed_before = self.mouse_pressed
        shift_pressed_before = self.shift_pressed
        if mouse and not self.mouse_pressed:
            self.hold_down_left_mouse_button()
        if not mouse and self.mouse_pressed:
            self.release_left_mouse_button()

        if shift and not self.shift_pressed:
            self.hold_down_shift_key()
        if not shift and self.shift_pressed:
            self.release_shift_key()

        yield

        if not reset:
            return

        if self.mouse_pressed and not mouse_pressed_before:
            self.release_left_mouse_button()
        if not self.mouse_pressed and mouse_pressed_before:
            self.hold_down_left_mouse_button()

        if self.shift_pressed and not shift_pressed_before:
            self.release_shift_key()
        if not self.shift_pressed and shift_pressed_before:
            self.hold_down_shift_key()

    @contextmanager
    def loop_restart_handler(self):
        try:
            yield
        except exceptions.FishCapturedError:
            self.handle_fish()
            if self.cfg.PROFILE.MODE == "bottom":
                with self.loop_restart_handler():
                    self.recast_tackle()
        except exceptions.LureBrokenError:
            self._handle_broken_lure()
        except exceptions.FishHookedError:
            with self.loop_restart_handler():
                if self.cfg.PROFILE.MODE != "telescopic":
                    self.pull_fish()
                else:
                    self.save_bite_screenshot()  # Should be called in _retrieve_fish()
                self.lift_fish()
        except exceptions.StuckAtCastingError:
            with self.hold_keys(mouse=False, shift=False):
                pass  # defer to reset_tackle()
            if self.cfg.PROFILE.MODE == "bottom":
                with self.loop_restart_handler():
                    self.recast_tackle()
        except exceptions.LineAtEndError:
            if self.cfg.ARGS.FRICTION_BRAKE:
                with self.friction_brake.lock:
                    self.friction_brake.change(increase=False)
            self.general_quit(t("player.line_at_end"))
        except exceptions.LineSnaggedError:
            self._handle_snagged_line()
        except exceptions.DisconnectedError:
            self.disconnected_quit()
        except exceptions.TackleBrokenError:
            self.general_quit(t("player.tackle_broken"))
        except exceptions.BaitNotChosenError:
            self.handle_bait_not_chosen()
        except exceptions.DryMixNotFoundError:
            pass
        except exceptions.DriftTimeoutError:
            pass

    # ---------------------------------------------------------------------------- #
    #                              main fishing loops                              #
    # ---------------------------------------------------------------------------- #
    def start_spin_mode(self) -> None:
        """Main spin fishing loop for 'spin' and 'spin_with_pause' modes."""
        while True:
            with self.loop_restart_handler():
                self.enable_trolling()
                if not self.skip_cast:
                    self.reset_tackle()
                    self.refill_stats()
                    self.harvest_baits(pickup=True)
                    self.change_tackle_lure()
                    self.cast_tackle()
                self.skip_cast = False

                if self.cfg.PROFILE.TYPE != "normal":
                    self.tackle.hold_mouse_button(self.cfg.PROFILE.TIGHTEN_DURATION)
                    getattr(self, f"retrieve_with_{self.cfg.PROFILE.TYPE}")()
                self.retrieve_line()
                self.lift_fish()

    def retrieve_with_pause(self) -> None:
        """Retrieve the line, pausing periodically."""
        logger.info(t("player.retrieving_with_pause"))
        with self.hold_keys(mouse=False, shift=self.cfg.PROFILE.PRE_ACCELERATION):
            self.tackle.special_retrieve(button="left")

    def retrieve_with_lift(self) -> None:
        """Retrieve the line, lifting periodically."""
        logger.info(t("player.retrieving_with_lift"))
        with self.hold_keys(mouse=True, shift=self.cfg.PROFILE.PRE_ACCELERATION):
            self.tackle.special_retrieve(button="right")

    def start_bottom_mode(self) -> None:
        """Main bottom fishing loop."""
        check_miss_counts = [0] * self.num_tackle

        while True:
            self.enable_trolling()
            if self.cfg.ARGS.SPOD_ROD and self.timer.is_spod_rod_castable():
                self.cast_spod_rod()

            self.refill_stats()
            logger.info(t("player.checking_rod", rod=self.tackle_idx + 1))
            pag.press(str(self.cfg.KEY.BOTTOM_RODS[self.tackle_idx]))
            sleep(ANIMATION_DELAY)

            with self.loop_restart_handler():
                if self.detection.is_fish_hooked():
                    check_miss_counts[self.tackle_idx] = 0
                    self.retrieve_and_recast()
                else:
                    sleep(self.cfg.PROFILE.PUT_DOWN_DELAY)
                    if self.detection.is_fish_hooked():
                        check_miss_counts[self.tackle_idx] = 0
                        self.retrieve_and_recast()
                    else:
                        self._put_down_tackle(check_miss_counts)
            # Put it here because we still need to update tackle index before next loop
            self._update_tackle()

    def retrieve_and_recast(self) -> None:
        self.retrieve_line()
        self.lift_fish()
        self.recast_tackle()

    def recast_tackle(self) -> None:
        self.reset_tackle()
        self._refill_groundbait()
        self._refill_pva()
        self.cast_tackle(lock=True)

    def start_pirk_mode(self) -> None:
        """Main marine fishing loop for pirk mode."""
        self._start_sink_mode(pirk=True)

    def start_elevator_mode(self) -> None:
        """Main marine fishing loop for elevator mode."""
        self._start_sink_mode(pirk=False)

    def _start_sink_mode(self, pirk: bool) -> None:
        """Main marine fishing loop for pirk or elevator mode.

        :param pirk: Whether to perform pirking or elevating.
        :type pirk: bool
        """
        perform_technique = self.do_pirking if pirk else self.do_elevating
        while True:
            with self.loop_restart_handler():
                self.enable_trolling()
                if not self.skip_cast:
                    self.reset_tackle()
                    self.refill_stats()
                    self.cast_tackle()
                    self.tackle.sink()
                self.skip_cast = False

                if not self.detection.is_fish_hooked():
                    perform_technique()
                self.retrieve_line()
                self.lift_fish()

    def start_telescopic_mode(self) -> None:
        """Main telescopic fishing loop."""
        self._start_float_mode(telescopic=True)

    def start_bolognese_mode(self) -> None:
        """Main bolognese fishing loop."""
        self._start_float_mode(telescopic=False)

    def _start_float_mode(self, telescopic: bool) -> None:
        """Main float fishing loop.

        :param telescopic: Whether the fishing mode is telescopic.
        :type telescopic: bool
        """
        monitor, hold_mouse_button = self._get_controllers(telescopic)
        while True:
            with self.loop_restart_handler():
                self.enable_trolling()
                if not self.skip_cast:
                    self.reset_tackle()
                    self.refill_stats()
                    self.harvest_baits(pickup=True)
                    self.cast_tackle()
                self.skip_cast = False

                with self.error_handler():
                    monitor()
                sleep(self.cfg.PROFILE.LIFT_DELAY)
                hold_mouse_button(FISH_CHECK_DURATION)
                if not telescopic:
                    self.pull_fish()
                else:
                    self.save_bite_screenshot()  # Should be called in _retrieve_fish()
                self.lift_fish()

    def harvest_baits(self, pickup: bool = False) -> None:
        """Harvest baits if energy is high.

        :param pickup: Whether to pick up the main rod after harvesting.
        :type pickup: bool
        """
        if not self.cfg.ARGS.HARVEST or not self.detection.is_energy_high():
            return
        logger.info(t("player.harvesting"))

        with self.hold_keys(mouse=False, shift=False):
            self._use_item("digging_tool")
            pag.click()

            while not self.detection.is_harvest_success():
                pag.click()
                sleep(add_jitter(LOOP_DELAY))
            pag.press("space")
            pag.press("backspace")
            sleep(ANIMATION_DELAY)
            self.result.bait += 1

            if pickup:
                self._use_item("main_rod")

    def refill_stats(self) -> None:
        """Refill player stats using tea and carrot."""
        if not self.cfg.ARGS.REFILL:
            return

        logger.info(t("player.refilling_stats"))
        item1, item2 = ("tea", "carrot") if random.random() < 0.5 else ("tea", "carrot")

        with self.hold_keys(mouse=False, shift=False):
            # Comfort is affected by weather, add a check to avoid over drink
            if self.detection.is_comfort_low() and self.timer.is_tea_drinkable():
                self._use_item(item1)
                self.result.tea += 1

            if self.detection.is_hunger_low():
                self._use_item(item2)
                self.result.carrot += 1

    def _drink_alcohol(self) -> None:
        """Drink alcohol with the given quantity."""
        if not self.cfg.ARGS.ALCOHOL or not self.timer.is_alcohol_drinkable():
            return

        logger.info(t("player.drinking_alcohol"))
        with self.hold_keys(mouse=False, shift=False):
            for _ in range(self.cfg.STAT.ALCOHOL_PER_DRINK):
                self._use_item("alcohol")
        self.result.alcohol += self.cfg.STAT.ALCOHOL_PER_DRINK

    def _drink_coffee(self) -> None:
        """Drink coffee to refill energy if energy is low."""
        if not self.cfg.ARGS.COFFEE or self.detection.is_energy_high():
            return

        # Hold left mouse button if we can use coffee by pressing a hotkey.
        # If left mouse button is not pressed, it means it's called while handling
        # LiftTimeoutError and we don't need to keep it pressed.
        mouse = True if self.mouse_pressed and self.cfg.KEY["COFFEE"] != -1 else False
        with self.hold_keys(mouse=mouse, shift=False, reset=True):
            if self.cur_coffee > self.cfg.STAT.COFFEE_LIMIT:
                self.general_quit(t("player.coffee_limit"))

            logger.info(t("player.drinking_coffee"))
            for _ in range(self.cfg.STAT.COFFEE_PER_DRINK):
                self._use_item("coffee")
            self.cur_coffee += self.cfg.STAT.COFFEE_PER_DRINK
            self.result.coffee += self.cfg.STAT.COFFEE_PER_DRINK

    def _use_item(self, item: str) -> None:
        """Access an item by name using quick selection shortcut or menu.

        :param item: The name of the item to access.
        :type item: str
        """
        logger.info(t("player.using_item", item=item))
        key = str(self.cfg.KEY[item.upper()])
        if key != "-1":  # Use shortcut
            pag.press(key)
        else:  # Open food menu
            with pag.hold("t"):
                sleep(ANIMATION_DELAY)
                food_position = self.detection.get_food_position(item)
                pag.moveTo(food_position)
                pag.click()
        sleep(add_jitter(USE_ITEM_DELAY))  # Could be followed by another _use_item()

    def reset_tackle(self) -> None:
        """Reset the tackle until it is ready."""
        if self.detection.is_tackle_ready():
            return
        if self.detection.is_lure_broken():
            self._handle_broken_lure()
            return
        if not self.detection.is_dry_mix_chosen():
            self._refill_dry_mix()
            return
        if not self.detection.is_bait_chosen():
            self.handle_bait_not_chosen()
            return

        if self.cfg.PROFILE.MODE == "spin":
            shift = self.cfg.PROFILE.RESET_ACCELERATION
        else:
            shift = True
        with self.hold_keys(mouse=True, shift=shift):
            while True:
                with self.error_handler():
                    self.tackle.reset()
                    break

    @contextmanager
    def error_handler(self):
        try:
            yield
        except exceptions.TicketExpiredError:
            self._handle_expired_ticket()
        except exceptions.CoffeeTimeoutError:
            self._drink_coffee()
        except exceptions.GearRatioTimeoutError:
            # Enable when timed out, disable after lifting (in casting stage)
            if self.cfg.ARGS.GEAR_RATIO and not self.tackle.gear_ratio_changed:
                self.tackle.change_gear_ratio_or_electro_mode()
        except exceptions.PirkTimeoutError:
            with self.hold_keys(mouse=False, shift=False, reset=True):
                if self.cfg.PROFILE.DEPTH_ADJUST_DELAY > 0:
                    logger.info(t("player.adjusting_depth"))
                    pag.press("enter")  # Open reel
                    sleep(self.cfg.PROFILE.DEPTH_ADJUST_DELAY)
                    self.tackle.hold_mouse_button(
                        self.cfg.PROFILE.DEPTH_ADJUST_DURATION
                    )
                else:
                    self.reset_tackle()
                    self.cast_tackle()
                    self.tackle.sink()
        except exceptions.LiftTimeoutError:
            with self.hold_keys(mouse=False, shift=False, reset=True):
                sleep(DROP_ROD_DELAY)
                if self.cfg.PROFILE.MODE != "telescopic":
                    self.pull_fish(save=False)
        except exceptions.DryMixNotChosenError:
            self._refill_dry_mix()

    def handle_bait_not_chosen(self) -> None:
        if len(self.tackles) == 1:
            self.general_quit(t("player.run_out_of_bait"))
        self.tackle.available = False

    def cast_spod_rod(self) -> None:
        """Cast the spod rod if dry mix is available."""
        self.using_spod_rod = True
        self._use_item("spod_rod")
        self.reset_tackle()
        self.cast_tackle(lock=True, update=False)
        pag.press("0")
        sleep(ANIMATION_DELAY)
        self.using_spod_rod = False

    def cast_tackle(self, lock: bool = False, update: bool = True) -> None:
        """Cast the current tackle.

        :param lock: Whether to lock the tackle after casting.
        :type lock: bool
        :param update: Whether to update the cast time.
        :type update: bool
        """
        if self.cfg.ARGS.PAUSE and self.timer.is_script_pausable():
            self._pause_script()

        # Reset changed states right before casting
        if self.cfg.ARGS.FRICTION_BRAKE:
            self.friction_brake.reset(self.cfg.BOT.FRICTION_BRAKE.INITIAL)

        with self.hold_keys(mouse=False, shift=False):
            if (
                self.cfg.ARGS.RANDOM_CAST
                and random.random() <= self.cfg.BOT.RANDOM_CAST_PROBABILITY
            ):
                logger.info(t("player.casting_redundantly"))
                pag.click()
                sleep(BAD_CAST_DELAY)
                self.reset_tackle()

            self.tackle.cast(lock)
            # Electro Raptor will reset to the manual mode automatically
            if not self.cfg.ARGS.ELECTRO and self.tackle.gear_ratio_changed:
                self.tackle.change_gear_ratio_or_electro_mode()
            if update:
                self.timer.update_cast_time()

    def retrieve_line(self) -> None:
        """Retrieve the fishing line until it is fully retrieved."""
        if self.detection.is_retrieval_finished():
            return

        if self.detection.is_fish_hooked():
            self.pull_fish()
        else:
            with self.hold_keys(mouse=True, shift=False):
                while True:
                    with self.error_handler():
                        self.tackle.retrieve()
                        break
                if self.detection.is_fish_hooked():
                    self.pull_fish()
        if self.cfg.ARGS.RAINBOW is None:
            sleep(self.cfg.BOT.SPOOL_RETRIEVAL_DELAY)
        elif self.cfg.ARGS.RAINBOW == 5:
            sleep(self.cfg.BOT.RAINBOW_RETRIEVAL_DELAY)

    def pull_fish(self, save: bool = True) -> None:
        if self.detection.is_retrieval_finished():
            return

        self.cur_coffee = 0
        if save:
            self.save_bite_screenshot()
        if self.cfg.ARGS.ELECTRO:
            self.tackle.change_gear_ratio_or_electro_mode()

        shift = (
            self.cfg.PROFILE.POST_ACCELERATION
            if self.cfg.PROFILE.MODE != "telescopic"
            else False
        )
        with self.hold_keys(mouse=True, shift=shift):
            while True:
                with self.error_handler():
                    self.tackle.pull()
                    break

    def save_bite_screenshot(self):
        # TODO: This is slow!
        if self.cfg.ARGS.BITE:
            self.detection.window.save_screenshot(self.timer.get_new_filepath())

    def do_pirking(self) -> None:
        """Perform pirking until a fish is hooked."""
        if self.cfg.PROFILE.PIRK_RETRIEVAL:
            with self.hold_keys(mouse=True, shift=False):
                self._do_pirking()
        else:
            self._do_pirking()

    def _do_pirking(self) -> None:
        while True:
            with self.error_handler():
                self.tackle.pirk()
                break

    def do_elevating(self) -> None:
        """Perform elevating until a fish is hooked."""
        dropped = False
        while True:
            dropped = not dropped
            with self.error_handler():
                self.tackle.elevate()
            break

    def lift_fish(self) -> None:
        """Lift the fish up and handle it."""
        if not self.detection.is_fish_hooked():
            return
        self._drink_alcohol()
        shift = (
            self.cfg.PROFILE.POST_ACCELERATION
            if self.cfg.PROFILE.MODE != "telescopic"
            else False
        )
        with self.hold_keys(mouse=True, shift=shift):
            while True:
                with self.error_handler():
                    self.tackle.lift()
                    break
        self.handle_fish()

    def _put_down_tackle(self, check_miss_counts: list[int]) -> None:
        """Put down the tackle and wait for a while.

        :param check_miss_counts: List of miss counts for all rods.
        :type check_miss_counts: list[int]
        """
        check_miss_counts[self.tackle_idx] += 1
        if check_miss_counts[self.tackle_idx] >= self.cfg.PROFILE.CHECK_MISS_LIMIT:
            check_miss_counts[self.tackle_idx] = 0
            self.reset_tackle()
            self._refill_groundbait()
            self._refill_pva()
            self.cast_tackle(lock=True)

        pag.press("0")
        self.harvest_baits()
        sleep(add_jitter(self.cfg.PROFILE.CHECK_DELAY))

    def enable_trolling(self) -> None:
        """Start trolling and change moving direction based on the trolling setting."""
        if self.cfg.ARGS.TROLLING is None:
            return
        if not self.trolling_started:
            logger.info(t("player.start_trolling"))
            pag.press(TROLLING_KEY)
        if self.cfg.ARGS.TROLLING not in ("left", "right"):  # Forward
            return
        key = LEFT_KEY if self.cfg.ARGS.TROLLING == "left" else RIGHT_KEY
        pag.keyUp(key)
        pag.keyDown(key)
        self.trolling_started = True

    def _update_tackle(self) -> None:
        """Update the current tackle (rod) being used."""
        candidates = self._get_available_rods()
        if not candidates:
            self.general_quit(t("player.all_rods_unavailable"))
        if self.cfg.PROFILE.RANDOM_ROD_SELECTION:
            self.tackle_idx = random.choice(candidates)
        else:
            self.tackle_idx = candidates[0]
        self.tackle = self.tackles[self.tackle_idx]

    def _get_available_rods(self) -> list[int]:
        """
        Get a list of available rods.

        :return: List of indices of available rods.
        :rtype: list[int]
        """
        if self.num_tackle == 1 and self.tackle.available:
            return [self.tackle]

        candidates = list(range(len(self.tackles)))
        # Rotate the candidates for sequential polling
        start = candidates.index(self.tackle_idx)
        candidates = candidates[start:] + candidates[:start]
        candidates = [i for i in candidates if self.tackles[i].available]

        #  Exclude current rod only if there's another available tackle
        if len(candidates) > 1 and self.tackle_idx in candidates:
            candidates.remove(self.tackle_idx)
        return candidates

    def change_tackle_lure(self) -> None:
        """Change the lure on the current tackle if possible."""
        if not self.cfg.ARGS.LURE or not self.have_new_lure:
            return

        with self.hold_keys(mouse=False, shift=False):
            if self.timer.is_lure_changeable():
                logger.info(t("player.changing_lure"))
                try:
                    self.tackle.equip_item("lure")
                except exceptions.ItemNotFoundError:
                    logger.error(t("player.error.lure_not_found"))
                    self.have_new_lure = False

    def _refill_pva(self) -> None:
        """Refill the PVA bag if it has been used up."""
        if not self.cfg.ARGS.PVA or not self.have_new_pva:
            return

        with self.hold_keys(mouse=False, shift=False):
            if not self.detection.is_pva_chosen():
                try:
                    self.tackle.equip_item("pva")
                except exceptions.ItemNotFoundError:
                    logger.error(t("player.error.pva_not_found"))
                    self.have_new_pva = False

    def _refill_dry_mix(self) -> None:
        """Refill the dry mix if it has been used up."""
        if not self.cfg.ARGS.DRY_MIX or not self.have_new_dry_mix:
            return

        with self.hold_keys(mouse=False, shift=False):
            try:
                self.tackle.equip_item("dry_mix")
            except exceptions.ItemNotFoundError:
                logger.error(t("player.error.dry_mix_not_found"))
                if not self.using_spod_rod:
                    self.tackle.available = False
                self.have_new_dry_mix = False
                raise exceptions.DryMixNotFoundError

    def _refill_groundbait(self) -> None:
        """Refill the groundbait if it has been used up."""
        if not self.cfg.ARGS.GROUNDBAIT or not self.have_new_groundbait:
            return

        if self.detection.is_groundbait_chosen():
            logger.info(t("player.groundbait_not_used"))
        else:
            with self.hold_keys(mouse=False, shift=False):
                try:
                    self.tackle.equip_item("groundbait")
                except exceptions.ItemNotFoundError:
                    logger.error(t("player.error.groundbait_not_found"))
                    self.have_new_groundbait = False

    # TBD: Menu, Plotter, Result, Handler
    def _get_controllers(self, telescopic: bool) -> tuple[Callable, Callable]:
        """Get the monitor and hold_mouse_button functions based on the fishing mode.

        :param telescopic: Whether the fishing mode is telescopic.
        :type telescopic: bool
        :return: Tuple containing the monitor and hold_mouse_button functions.
        :rtype: tuple[Callable, Callable]
        """
        if telescopic:
            hold_mouse_button = self.tackle.hold_mouse_button
            monitor = self.tackle._monitor_float_state
        else:
            if self.detection.is_clip_open():
                logger.warning(t("player.clip_not_set"))
                monitor = self.tackle._monitor_float_state
            else:
                monitor = self.tackle._monitor_clip_state
            hold_mouse_button = self.tackle.hold_mouse_buttons

        return monitor, hold_mouse_button

    def _pause_script(self) -> None:
        """Pause the script for a specified duration."""
        logger.info(t("player.pausing_script"))
        with self.hold_keys(mouse=False, shift=False):
            pag.press("esc")
            sleep(add_jitter(self.cfg.BOT.PAUSE_DURATION))
            pag.press("esc")
            sleep(ANIMATION_DELAY)

    def _handle_timeout(self) -> None:
        """Handle common timeout events."""
        if self.detection.is_tackle_broken():
            self.general_quit(t("player.tackle_broken"))

        if self.detection.is_disconnected():
            self.disconnected_quit()

        if self.detection.is_ticket_expired():
            self._handle_expired_ticket()

    def _handle_broken_lure(self) -> None:
        """Handle the broken lure event according to the settings."""
        if self.cfg.ARGS.BROKEN_LURE:
            with self.hold_keys(mouse=False, shift=False):
                self._replace_broken_lures()
        else:
            self.general_quit(t("player.lure_broken"))

    def handle_termination(self, msg: str, shutdown: bool, send: bool) -> None:
        """Handle script termination.

        :param msg: The reason for termination.
        :type msg: str
        :param shutdown: Whether to shutdown the computer after termination.
        :type shutdown: bool
        :param shutdown: Whether to send notification.
        :type shutdown: bool
        """
        result = self.get_result_dict(msg)
        result_table = self.get_result_table(result)
        if send:
            send_result(self.cfg, result)
        if self.cfg.ARGS.DATA:
            output_dir = self.timer.get_new_dir_path()
            output_dir.mkdir()
            self.timer.save_data(output_dir)
            with open(output_dir / "result.json", "w") as f:
                json.dump(result, f, indent=4)
            with open(output_dir / "config.yaml", "w", encoding="utf-8") as f:
                f.write(config.dump_cfg(self.cfg))
        if self.cfg.ARGS.SHUTDOWN and shutdown:
            os.system("shutdown /s /t 5")
        print(result_table)
        if self.cfg.ARGS.FRICTION_BRAKE:
            self.friction_brake.monitor_process.terminate()
        with self.hold_keys(mouse=False, shift=False):
            utils.safe_exit()

    def _handle_snagged_line(self) -> None:
        """Handle a snagged line event."""
        if len(self.tackles) == 1:
            self.general_quit(t("player.line_snagged"))
        self.tackle.available = False

    def handle_fish(self) -> None:
        if not self.detection.is_fish_captured():
            return
        if not self.cfg.ARGS.NO_ANIMATION:
            sleep(add_jitter(LOOP_DELAY))  # it's a slow animation ;)
        logger.info(t("player.handling_fish"))
        with self.hold_keys(mouse=False, shift=False):
            self.handle_events()
            if not self.cfg.ARGS.NO_ANIMATION:
                sleep(TAG_ANIMATION_DELAY)
            self._handle_fish()
            # Avoid wrong cast hour
            if self.cfg.PROFILE.MODE in ["bottom", "pirk", "elevator"]:
                self.timer.update_cast_time()
            self.timer.add_cast_time()
            limit = self.cfg.BOT.KEEPNET.CAPACITY - self.cfg.ARGS.FISHES_IN_KEEPNET
            if self.result.kept == limit:
                self.general_quit(t("player.keepnet_full"))

    def _handle_fish(self) -> None:
        """Keep or release the fish and record the fish count."""
        self.result.total += 1
        bypass = keep = fish_tagged = False
        tag_colors = []
        for tag in TagColor:
            if self.detection.is_tag_exist(tag):
                tag_color = tag.name.lower()
                tag_colors.append(tag_color)
                if tag_color in self.cfg.BOT.KEEPNET.BYPASS_TAGS:
                    bypass = True
                if tag_color in self.cfg.BOT.KEEPNET.KEEP_TAGS:
                    keep = True
                if tag_color in self.cfg.BOT.KEEPNET.SCREENSHOT_TAGS:
                    fish_tagged = True

        if (
            self.cfg.ARGS.SCREENSHOT
            and (not self.cfg.BOT.KEEPNET.SCREENSHOT_TAGS or fish_tagged)
            and "fish" in self.cfg.BOT.KEEPNET.SCREENSHOT_EVENTS
        ):
            filepath = self.timer.get_new_filepath()
            self.detection.window.save_screenshot(filepath)
            send_screenshot(self.cfg, filepath)

        if bypass:
            pag.press("space")
            self.result.kept += 1
        elif self.detection.is_fish_in_list(self.cfg.BOT.KEEPNET.BLACKLIST):
            pag.press("backspace")
        elif (
            self.cfg.ARGS.TAG
            and not keep
            and not self.detection.is_fish_in_list(self.cfg.BOT.KEEPNET.WHITELIST)
        ):
            pag.press("backspace")
        else:
            pag.press("space")
            self.result.kept += 1

        # Safe check
        sleep(ANIMATION_DELAY)
        if self.detection.is_keepnet_full():
            self.result.kept -= 1
            pag.press("esc")
            pag.press("backspace")
            sleep(ANIMATION_DELAY)
            self.general_quit("Keepnet is full")

        for tag_color in tag_colors:
            setattr(self.result, tag_color, getattr(self.result, tag_color) + 1)

    def handle_events(self) -> None:
        """Handle events like gift, card, challenge, etc."""
        while self.detection.is_event_triggered():
            if self.detection.is_gift_receieved():
                if (
                    self.cfg.ARGS.SCREENSHOT
                    and "gift" in self.cfg.BOT.KEEPNET.SCREENSHOT_EVENTS
                ):
                    filepath = self.timer.get_new_filepath()
                    self.detection.window.save_screenshot(filepath)
                    send_screenshot(self.cfg, filepath)
                self.result.gift += 1
            elif self.detection.is_card_receieved():
                if (
                    self.cfg.ARGS.SCREENSHOT
                    and "card" in self.cfg.BOT.KEEPNET.SCREENSHOT_EVENTS
                ):
                    filepath = self.timer.get_new_filepath()
                    self.detection.window.save_screenshot(filepath)
                    send_screenshot(self.cfg, filepath)
                self.result.card += 1
            else:
                logger.warning(t("player.unexpected_event"))
            pag.press("enter")
            sleep(add_jitter(LOOP_DELAY))

    def general_quit(self, msg: str) -> None:
        """Quit the game through the control panel.

        :param msg: reason for termination
        :type msg: str
        """
        logger.critical(msg)
        if self.friction_brake is not None:
            self.friction_brake.reset(self.cfg.BOT.FRICTION_BRAKE.INITIAL)
        with self.hold_keys(mouse=False, shift=False):
            sleep(ANIMATION_DELAY)
            pag.press("esc")
            sleep(ANIMATION_DELAY)
            if self.cfg.ARGS.SIGNOUT:
                pag.keyDown("shift")
            pag.moveTo(self.detection.get_quit_position())
            pag.click()
            pag.keyUp("shift")
            sleep(ANIMATION_DELAY)
            pag.moveTo(self.detection.get_yes_position())
            pag.click()

            self.handle_termination(msg, shutdown=True, send=True)

    def disconnected_quit(self) -> None:
        """Quit the game through the main menu."""
        logger.critical(t("player.game_disconnected"))
        with self.hold_keys(mouse=False, shift=False):
            pag.press("space")
            # Sleep to bypass the black screen (experimental)
            sleep(DISCONNECTED_DELAY)
            pag.press("space")
            sleep(ANIMATION_DELAY)
            if not self.cfg.ARGS.SIGNOUT:
                pag.moveTo(self.detection.get_exit_icon_position())
                pag.click()
                sleep(ANIMATION_DELAY)
                pag.moveTo(self.detection.get_confirm_button_position())
                pag.click()

            self.handle_termination(t("player.game_disconnected"), shutdown=True, send=True)

    def get_result_dict(self, msg: str):
        return self.result.as_dict(msg, self.timer)

    def get_result_table(self, result) -> Table:
        """Create a Rich table from running result.

        :return: formatted running result table
        :rtype: Table
        """
        table = Table(title=t("app.running_result"), box=box.HEAVY, show_header=False)

        for k, v in result.items():
            table.add_row(k, str(v))
        return table

    def _handle_expired_ticket(self) -> None:
        """Handle an expired boat ticket event."""
        with self.hold_keys(mouse=False, shift=False, reset=True):
            if self.cfg.ARGS.BOAT_TICKET == 0:
                pag.press("esc")
                sleep(TICKET_EXPIRE_DELAY)
                self.general_quit(t("player.ticket_expired"))

            logger.info(t("player.renewing_ticket"))
            ticket_loc = self.detection.get_ticket_position(self.cfg.ARGS.BOAT_TICKET)
            if ticket_loc is None:
                pag.press("esc")  # Close ticket menu
                sleep(TICKET_EXPIRE_DELAY)
                self.general_quit(t("player.ticket_not_found"))
            pag.moveTo(ticket_loc)
            pag.click(clicks=2, interval=0.1)  # pag.doubleClick() not implemented
            self.result.ticket += 1
            sleep(ANIMATION_DELAY)

    @utils.press_before_and_after("v")
    def _replace_broken_lures(self) -> None:
        """Replace multiple broken lures."""
        logger.info(t("player.replacing_lures"))

        scrollbar_box = self.detection.get_scrollbar_position()
        if scrollbar_box is None:
            logger.info(t("player.scrollbar_not_found"))
            while self._open_broken_lure_menu():
                self._replace_item()
            pag.press("v")
            return

        logger.info(t("player.scrollbar_found"))
        x, y = utils.get_box_center_integers(scrollbar_box)
        pag.moveTo(x, y)
        for _ in range(5):
            sleep(ANIMATION_DELAY)
            pag.drag(xOffset=0, yOffset=125, duration=0.5, button="left")
            y += 125

            while self._open_broken_lure_menu():
                self._replace_item()
            pag.moveTo((x, y))

    def _open_broken_lure_menu(self) -> bool:
        """Open the broken lure menu.

        :return: True if the broken lure is found, False otherwise.
        :rtype: bool
        """
        logger.info(t("player.looking_for_broken"))
        broken_item_position = self.detection.get_100wear_position()
        if broken_item_position is None:
            logger.warning(t("player.broken_not_found"))
            return False

        # click item to open selection menu
        pag.moveTo(broken_item_position)
        sleep(ANIMATION_DELAY)
        pag.click()
        sleep(ANIMATION_DELAY)
        return True

    def _replace_item(self) -> None:
        """Replace a broken item with a favorite item."""
        logger.info(t("player.looking_for_favorites"))
        favorite_item_positions = self.detection.get_favorite_item_positions()
        while True:
            favorite_item_position = next(favorite_item_positions, None)
            if favorite_item_position is None:
                pag.press("esc")
                sleep(ANIMATION_DELAY)
                pag.press("esc")
                self.general_quit(t("player.favorite_not_found"))

            # Check if the lure for replacement is already broken
            x, y = utils.get_box_center_integers(favorite_item_position)
            if pag.pixel(x - 70, y + 190) != (178, 59, 30):  # Magic value ;)
                logger.info(t("player.lure_replaced"))
                pag.moveTo(x - 70, y + 190)
                pag.click(clicks=2, interval=0.1)
                sleep(WEAR_TEXT_UPDATE_DELAY)
                break

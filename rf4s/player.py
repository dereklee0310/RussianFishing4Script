"""Module for Player class.

This module provides the main interface for automating fishing activities in a game.
It includes functionality for managing fishing loops, handling player stats, and
automating various fishing techniques.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import logging
import msvcrt
import os
import random
import sys
from contextlib import contextmanager
from datetime import datetime
from multiprocessing import Lock

# from email.mime.image import MIMEImage
from pathlib import Path
from time import sleep

import pyautogui as pag
from playsound import playsound
from pynput import keyboard
from rich import box, print
from rich.table import Table

from rf4s import exceptions, utils
from rf4s.component.friction_brake import FrictionBrake
from rf4s.component.tackle import Tackle
from rf4s.controller.detection import Detection, TagColor
from rf4s.controller.notification import (
    DiscordColor,
    DiscordNotification,
    EmailNotification,
    MiaotixingNotification,
)
from rf4s.controller.timer import Timer
from rf4s.controller.window import Window
from rf4s.result.result import RF4SResult

logger = logging.getLogger("rich")
random.seed(datetime.now().timestamp())

PRE_RETRIEVAL_DURATION = 0.5
PULL_OUT_DELAY = 3
DIG_DELAY = 5
DIG_TIMEOUT = 32
ANIMATION_DELAY = 1
TICKET_EXPIRE_DELAY = 16
DISCONNECTED_DELAY = 8
WEAR_TEXT_UPDATE_DELAY = 2
PUT_DOWN_DELAY = 4
SCREENSHOT_DELAY = 2

TROLLING_KEY = "j"
LEFT_KEY = "a"
RIGHT_KEY = "d"


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

    def __init__(self, cfg, window: Window):
        """Initialize monitor, timer, and some trivial counters.

        :param cfg: Configuration object containing settings for the fishing process.
        :type cfg: Config
        :param window: Window object for managing the game window.
        :type window: Window
        """
        self.cfg = cfg
        self.window = window
        self.timer = Timer(cfg)
        self.detection = Detection(cfg, window)

        self.tackle_idx = 0
        if self.cfg.SELECTED.MODE == "bottom":
            self.num_tackle = len(self.cfg.KEY.BOTTOM_RODS)
        else:
            self.num_tackle = 1
        self.tackles = [
            Tackle(cfg, self.timer, self.detection) for _ in range(self.num_tackle)
        ]
        self.tackle = self.tackles[self.tackle_idx]

        self.friction_brake_lock = Lock()
        self.friction_brake = FrictionBrake(
            cfg, self.friction_brake_lock, self.detection
        )

        self.cur_coffee = 0
        self.have_new_lure = True
        self.have_new_groundbait = True
        self.have_new_dry_mix = True
        self.have_new_pva = True
        self.result = RF4SResult()

        self.clicklock_enabled = False

    def start_fishing(self) -> None:
        """Start the main fishing loop with the specified fishing strategy."""
        if self.cfg.ARGS.FRICTION_BRAKE:
            logger.info("Spawing new process, do not quit the script")
            self.friction_brake.monitor_process.start()

        if (
            self.cfg.SELECTED.MODE not in ("telescopic", "bottom")
            and not self.cfg.ARGS.SKIP_CAST
            and not self.detection.is_retrieval_finished()
        ):
            logger.critical(
                "The spool is not fully loaded, "
                "try moving your camera, "
                "changing your game window size or fishing line"
            )
            if self.friction_brake.monitor_process.is_alive():
                self.friction_brake.monitor_process.terminate()
            utils.safe_exit()

        logger.info("Starting fishing mode: '%s'", self.cfg.SELECTED.MODE)
        self._start_trolling()
        getattr(self, f"start_{self.cfg.SELECTED.MODE}_mode")()

    # ---------------------------------------------------------------------------- #
    #                              main fishing loops                              #
    # ---------------------------------------------------------------------------- #
    def start_spin_mode(self) -> None:
        """Main spin fishing loop for 'spin' and 'spin_with_pause' modes."""
        skip_cast = self.cfg.ARGS.SKIP_CAST
        while True:
            if not skip_cast:
                self._refill_stats()
                self._harvest_baits(pickup=True)
                self.reset_tackle()
                self._change_tackle_lure()
                self._cast_tackle()
            skip_cast = False

            if self.cfg.SELECTED.TYPE != "normal":
                utils.hold_mouse_button(self.cfg.SELECTED.TIGHTEN_DURATION)
                getattr(self, f"retrieve_with_{self.cfg.SELECTED.TYPE}")()
            self.retrieve_line()

            if self.detection.is_fish_hooked():
                self.pull_fish()

    def retrieve_with_pause(self) -> None:
        """Retrieve the line, pausing periodically."""
        logger.info("Retrieving fishing line with pause")
        self.tackle._special_retrieve(button="left")

    def retrieve_with_lift(self) -> None:
        """Retrieve the line, lifting periodically."""
        logger.info("Retrieving fishing line with lift")
        with self.toggle_clicklock():
            self.tackle._special_retrieve(button="right")

    def start_bottom_mode(self) -> None:
        """Main bottom fishing loop."""
        check_miss_counts = [0] * self.num_tackle

        while True:
            if self.cfg.ARGS.SPOD_ROD and self.timer.is_spod_rod_castable():
                self._cast_spod_rod()
            self._refill_stats()
            self._harvest_baits()

            logger.info("Checking rod %s", self.tackle_idx + 1)
            pag.press(str(self.cfg.KEY.BOTTOM_RODS[self.tackle_idx]))
            sleep(ANIMATION_DELAY)
            if self.detection.is_fish_hooked():
                check_miss_counts[self.tackle_idx] = 0
                self.retrieve_and_recast()
            else:
                sleep(self.cfg.SELECTED.PUT_DOWN_DELAY)
                if self.detection.is_fish_hooked():
                    check_miss_counts[self.tackle_idx] = 0
                    self.retrieve_and_recast()
                else:
                    self._put_down_tackle(check_miss_counts)
            self._update_tackle()

    def retrieve_and_recast(self) -> None:
        self.retrieve_line()
        self.pull_fish()
        self.reset_tackle()
        self._refill_groundbait()
        self._refill_pva()
        self._cast_tackle(lock=True)

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
        skip_cast = self.cfg.ARGS.SKIP_CAST
        while True:
            if not skip_cast:
                self._refill_stats()
                self.reset_tackle()
                self._cast_tackle()
                self.tackle.sink()
            skip_cast = False

            perform_technique()
            self.retrieve_line()
            self.pull_fish()

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
            self._refill_stats()
            self._harvest_baits(pickup=True)
            self.reset_tackle()
            self._cast_tackle()

            try:
                with self.error_handler():
                    monitor()
                sleep(self.cfg.SELECTED.PULL_DELAY)
                hold_mouse_button(PRE_RETRIEVAL_DURATION)
                self.pull_fish()
            except TimeoutError:
                pass

    def _harvest_baits(self, pickup: bool = False) -> None:
        """Harvest baits if energy is high.

        :param pickup: Whether to pick up the main rod after harvesting.
        :type pickup: bool
        """
        if not self.cfg.ARGS.HARVEST or not self.detection.is_energy_high():
            return
        logger.info("Harvesting baits")
        self._use_item("digging_tool")
        sleep(PULL_OUT_DELAY)
        pag.click()

        i = DIG_TIMEOUT
        while i > 0:
            i = utils.sleep_and_decrease(i, DIG_DELAY)
            if self.detection.is_harvest_success():
                logger.info("Baits harvested successfully")
                pag.press("space")
                pag.press("backspace")
                sleep(ANIMATION_DELAY)
                self.result.bait += 1
                break

        if pickup:
            self._use_item("main_rod")
            sleep(PULL_OUT_DELAY)

        # When timed out, do not raise a TimeoutError but defer it to resetting stage

    def _refill_stats(self) -> None:
        """Refill player stats using tea and carrot."""
        if not self.cfg.ARGS.REFILL:
            return

        logger.info("Refilling player stats")
        # Comfort is affected by weather, add a check to avoid over drink
        if self.detection.is_comfort_low() and self.timer.is_tea_drinkable():
            self._use_item("tea")
            self.result.tea += 1

        if self.detection.is_hunger_low():
            self._use_item("carrot")
            self.result.carrot += 1

    def _drink_alcohol(self) -> None:
        """Drink alcohol with the given quantity."""
        if not self.cfg.ARGS.ALCOHOL or not self.timer.is_alcohol_drinkable():
            return

        logger.info("Drinking alcohol")
        for _ in range(self.cfg.STAT.ALCOHOL_PER_DRINK):
            self._use_item("alcohol")
        self.result.alcohol += self.cfg.STAT.ALCOHOL_PER_DRINK

    def _drink_coffee(self) -> None:
        """Drink coffee to refill energy if energy is low."""
        if not self.cfg.ARGS.COFFEE or self.detection.is_energy_high():
            return

        if self.cur_coffee > self.cfg.STAT.COFFEE_LIMIT:
            pag.press("esc")  # Just back to control panel to reduce power usage
            self._handle_termination("Coffee limit reached", shutdown=False)

        logger.info("Drinking coffee")
        for _ in range(self.cfg.STAT.COFFEE_PER_DRINK):
            self._use_item("coffee")
        self.cur_coffee += self.cfg.STAT.COFFEE_PER_DRINK
        self.result.coffee += self.cfg.STAT.COFFEE_PER_DRINK

    def _use_item(self, item: str) -> None:
        """Access an item by name using quick selection shortcut or menu.

        :param item: The name of the item to access.
        :type item: str
        """
        logger.info("Using %s", item)
        key = str(self.cfg.KEY[item.upper()])
        if key != "-1":  # Use shortcut
            pag.press(key)
        else:  # Open food menu
            with pag.hold("t"):
                sleep(ANIMATION_DELAY)
                food_position = self.detection.get_food_position(item)
                pag.moveTo(food_position)
                pag.click()
        sleep(ANIMATION_DELAY)

    def enable_clicklock(self):
        pag.mouseDown()
        sleep(2.2)
        self.clicklock_enabled = True

    def disable_clicklock(self):
        pag.click()
        self.clicklock_enabled = False

    @contextmanager
    def toggle_clicklock(self):
        self.enable_clicklock()
        yield
        self.disable_clicklock()

    @utils.reset_friction_brake_after
    def reset_tackle(self) -> None:
        """Reset the tackle until it is ready."""
        sleep(ANIMATION_DELAY)
        if self.detection.is_tackle_ready():
            return

        if self.detection.is_lure_broken():
            self._handle_broken_lure()
            return

        if self.cfg.ARGS.SPOD_ROD and not self.detection.is_groundbait_chosen():
            self._refill_dry_mix()
            return

        if not self.detection.is_bait_chosen():
            if len(self.tackles) == 1:
                self.general_quit("Run out of bait")
            self.tackle.available = False
            return

        with self.toggle_clicklock():
            while True:
                try:
                    # Outer -> inner
                    with (
                        self.error_handler(),
                        self.clicklock_disable_handler(),
                        pag.hold("shift"),
                    ):
                        self.tackle.reset()
                    break
                except TimeoutError:
                    # If it's a TimeoutError or an exception was transformed into a
                    # TimeoutError, enable clicklock again if necessary.
                    if not self.clicklock_enabled:
                        self.enable_clicklock()

    @contextmanager
    def error_handler(self):
        try:
            yield
        except exceptions.FishHookedError:
            self.pull_fish()
        except exceptions.FishCapturedError:
            self.handle_fish()
        except exceptions.LineAtEndError:
            if self.cfg.ARGS.FRICTION_BRAKE:
                with self.friction_brake.lock:
                    self.friction_brake.change(increase=False)
            self.general_quit("Fishing line is at its end")
        except exceptions.LineSnaggedError:
            self._handle_snagged_line()
        except exceptions.LureBrokenError:
            self._handle_broken_lure()
            raise TimeoutError  # Transform into TimeoutError to continue
        except exceptions.TackleBrokenError:
            self.general_quit("Tackle is broken")
        except exceptions.DisconnectedError:
            self.disconnected_quit()
        except exceptions.TicketExpiredError:
            self._handle_expired_ticket()
            raise TimeoutError  # Transform into TimeoutError to continue
        except TimeoutError:
            raise

    @contextmanager
    def clicklock_disable_handler(self):
        try:
            yield
        except (
            exceptions.FishHookedError,
            exceptions.FishCapturedError,
            exceptions.LineAtEndError,
            exceptions.LineSnaggedError,
            exceptions.LureBrokenError,
            exceptions.TackleBrokenError,
            exceptions.DisconnectedError,
            exceptions.TicketExpiredError,
        ):
            if self.clicklock_enabled:
                self.disable_clicklock()
            raise

    def _cast_spod_rod(self) -> None:
        """Cast the spod rod if dry mix is available."""
        self._use_item("spod_rod")
        self.reset_tackle()

        # If no dry mix is available, skip casting
        if not self.tackle.available:
            self.tackle.available = True
            return
        self._cast_tackle(lock=True, update=False)
        pag.press("0")
        sleep(ANIMATION_DELAY)

    def _cast_tackle(self, lock: bool = False, update: bool = True) -> None:
        """Cast the current tackle.

        :param lock: Whether to lock the tackle after casting.
        :type lock: bool
        :param update: Whether to update the cast time.
        :type update: bool
        """
        if self.cfg.ARGS.PAUSE and self.timer.is_script_pausable():
            self._pause_script()

        if self.cfg.ARGS.BITE:
            self.window.save_screenshot(self.timer.get_cur_timestamp())

        if (
            self.cfg.ARGS.RANDOM_CAST
            and random.random() <= self.cfg.SCRIPT.RANDOM_CAST_PROBABILITY
        ):
            logger.info("Casting rod redundantly")
            pag.click()
            sleep(2)
            self.reset_tackle()

        self.tackle.cast(lock)
        if update:
            self.timer.update_cast_time()

    def retrieve_line(self) -> None:
        """Retrieve the fishing line until it is fully retrieved."""
        if self.detection.is_retrieval_finished():
            return

        first = True
        gr_switched = False
        if self.cfg.ARGS.ELECTRO:
            self.tackle.switch_gear_ratio()  # Use electro mode

        self.cur_coffee = 0

        with self.toggle_clicklock():
            while True:
                try:
                    with (
                        self.error_handler(),
                        self.clicklock_disable_handler(),
                    ):
                        self.tackle.retrieve(first)
                    break
                except TimeoutError:
                    if not self.clicklock_enabled:
                        self.enable_clicklock()
                    first = False
                    if self.cfg.ARGS.GEAR_RATIO and not gr_switched:
                        self.tackle.switch_gear_ratio()
                        gr_switched = True
                    pag.keyUp("shift")
                    self._drink_coffee()

            pag.keyUp("shift")
            if gr_switched:
                self.tackle.switch_gear_ratio()

    def do_pirking(self) -> None:
        """Perform pirking until a fish is hooked."""
        if self.cfg.SELECTED.PIRK_RETRIEVAL:
            with self.toggle_clicklock():
                self._do_pirking()
        else:
            self._do_pirking()

    def _do_pirking(self) -> None:
        while True:
            try:
                with self.error_handler(), self.clicklock_disable_handler():
                    self.tackle.pirk()
                break
            except TimeoutError:
                if self.cfg.SELECTED.PIRK_RETRIEVAL:
                    if not self.clicklock_enabled:
                        self.enable_clicklock()
                    continue

                if self.cfg.SELECTED.DEPTH_ADJUST_DELAY > 0:
                    logger.info("Adjusting lure depth")
                    pag.press("enter")  # Open reel
                    sleep(self.cfg.SELECTED.DEPTH_ADJUST_DELAY)
                    utils.hold_mouse_button(self.cfg.SELECTED.DEPTH_ADJUST_DURATION)
                else:
                    self.reset_tackle()
                    self._cast_tackle()
                    self.tackle.sink()

    def do_elevating(self) -> None:
        """Perform elevating until a fish is hooked."""
        dropped = False
        while True:
            try:
                dropped = not dropped
                with self.error_handler():
                    self.tackle.elevate(dropped)
                break
            except TimeoutError:
                pass

    def pull_fish(self) -> None:
        """Pull the fish up and handle it."""
        if not self.detection.is_fish_hooked():
            return

        self._drink_alcohol()
        with self.toggle_clicklock():
            while True:
                try:
                    with self.error_handler(), self.clicklock_disable_handler():
                        self.tackle.pull()
                    break
                except TimeoutError:
                    self.disable_clicklock()
                    sleep(PUT_DOWN_DELAY)
                    if self.cfg.SELECTED.MODE != "telescopic":
                        self.retrieve_line()
                    if not self.clicklock_enabled:
                        self.enable_clicklock()
        self.handle_fish()

    def _put_down_tackle(self, check_miss_counts: list[int]) -> None:
        """Put down the tackle and wait for a while.

        :param check_miss_counts: List of miss counts for all rods.
        :type check_miss_counts: list[int]
        """
        check_miss_counts[self.tackle_idx] += 1
        if check_miss_counts[self.tackle_idx] >= self.cfg.SELECTED.CHECK_MISS_LIMIT:
            check_miss_counts[self.tackle_idx] = 0
            self.reset_tackle()
            self._refill_groundbait()
            self._refill_pva()
            self._cast_tackle(lock=True)

        pag.press("0")
        bound = self.cfg.SELECTED.CHECK_DELAY // 5
        random_offset = random.uniform(-bound, bound)
        sleep(self.cfg.SELECTED.CHECK_DELAY + random_offset)

    def _start_trolling(self) -> None:
        """Start trolling and change moving direction based on the trolling setting."""
        if self.cfg.ARGS.TROLLING is None:
            return
        logger.info("Starting trolling")
        pag.press(TROLLING_KEY)
        if self.cfg.ARGS.TROLLING not in ("left", "right"):  # Forward
            return
        pag.keyDown(LEFT_KEY if self.cfg.ARGS.TROLLING == "left" else RIGHT_KEY)

    def _update_tackle(self) -> None:
        """Update the current tackle (rod) being used."""
        candidates = self._get_available_rods()
        if not candidates:
            self.general_quit("All rods are unavailable")
        if self.cfg.SCRIPT.RANDOM_ROD_SELECTION:
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

    def _change_tackle_lure(self) -> None:
        """Change the lure on the current tackle if possible."""
        if not self.cfg.ARGS.LURE or not self.have_new_lure:
            return

        if self.timer.is_lure_changeable():
            logger.info("Changing lure randomly")
            try:
                self.tackle.equip_item("lure")
            except exceptions.ItemNotFoundError:
                logger.error("New lure not found")
                self.have_new_lure = False

    def _refill_pva(self) -> None:
        """Refill the PVA bag if it has been used up."""
        if not self.cfg.ARGS.PVA or not self.have_new_pva:
            return

        if not self.detection.is_pva_chosen():
            try:
                self.tackle.equip_item("pva")
            except exceptions.ItemNotFoundError:
                logger.error("New pva not found")
                self.have_new_pva = False

    def _refill_dry_mix(self) -> None:
        """Refill the dry mix if it has been used up."""
        if not self.cfg.ARGS.DRY_MIX or not self.have_new_dry_mix:
            return
        try:
            self.tackle.equip_item("dry_mix")
        except exceptions.ItemNotFoundError:
            logger.error("New dry mix not found")
            self.tackle.available = False  # Skip following stages
            self.have_new_dry_mix = False

    def _refill_groundbait(self) -> None:
        """Refill the groundbait if it has been used up."""
        if not self.cfg.ARGS.GROUNDBAIT or not self.have_new_groundbait:
            return

        if self.detection.is_groundbait_chosen():
            logger.info("Groundbait is not used up yet")
        else:
            try:
                self.tackle.equip_item("groundbait")
            except exceptions.ItemNotFoundError:
                logger.error("New groundbait not found")
                self.have_new_groundbait = False

    def test(self):
        """Boo!"""
        self.retrieve_line()

    # TBD: Menu, Plotter, Result, Handler
    def _get_controllers(self, telescopic: bool) -> tuple[callable, callable]:
        """Get the monitor and hold_mouse_button functions based on the fishing mode.

        :param telescopic: Whether the fishing mode is telescopic.
        :type telescopic: bool
        :return: Tuple containing the monitor and hold_mouse_button functions.
        :rtype: tuple[callable, callable]
        """
        if telescopic:
            hold_mouse_button = utils.hold_mouse_button
            monitor = self.tackle._monitor_float_state
        else:
            if self.detection.is_clip_open():
                logger.warning("Clip is not set, fall back to camera mode")
                monitor = self.tackle._monitor_float_state
            else:
                monitor = self.tackle._monitor_clip_state
            hold_mouse_button = utils.hold_mouse_buttons

        return monitor, hold_mouse_button

    def _pause_script(self) -> None:
        """Pause the script for a specified duration."""
        logger.info("Pausing script")
        pag.press("esc")
        bound = self.cfg.PAUSE.DURATION // 5
        offset = random.randint(-bound, bound)
        sleep(self.cfg.PAUSE.DURATION + offset)
        pag.press("esc")

    def _handle_timeout(self) -> None:
        """Handle common timeout events."""
        if self.detection.is_tackle_broken():
            self.general_quit("Tackle is broken")

        if self.detection.is_disconnected():
            self.disconnected_quit()

        if self.detection.is_ticket_expired():
            self._handle_expired_ticket()

    def _handle_broken_lure(self) -> None:
        """Handle the broken lure event according to the settings."""
        match self.cfg.ARGS.BROKEN_LURE:
            case "replace":
                self._replace_broken_lures()
            case "alarm":
                playsound(str(Path(self.cfg.SCRIPT.ALARM_SOUND).resolve()))
                self.window.activate_script_window()
                print("Please replace your lure.")
                print("Press any key to continue...")
                msvcrt.getch()
                self.window.activate_game_window()
            case _:
                self.general_quit("Lure is broken")

    @utils.release_keys_after(arrow_keys=True)
    def _handle_termination(self, msg: str, shutdown: bool) -> None:
        """Handle script termination.

        :param msg: The reason for termination.
        :type msg: str
        :param shutdown: Whether to shutdown the computer after termination.
        :type shutdown: bool
        """
        result = self.build_result_dict(msg)
        table = self.build_result_table(result)
        if self.cfg.ARGS.DISCORD:
            # TODO: dynamic color
            DiscordNotification(self.cfg, result).send(DiscordColor.BLURPLE)
        if self.cfg.ARGS.EMAIL:
            EmailNotification(self.cfg, result).send()
        if self.cfg.ARGS.MIAOTIXING:
            MiaotixingNotification(self.cfg, result).send()
        if self.cfg.ARGS.DATA:
            self.timer.save_data()
        if shutdown and self.cfg.ARGS.SHUTDOWN:
            os.system("shutdown /s /t 5")
        print(table)
        if self.friction_brake.monitor_process.is_alive():
            self.friction_brake.monitor_process.terminate()
        utils.safe_exit()

    def _handle_snagged_line(self) -> None:
        """Handle a snagged line event."""
        if len(self.tackles) == 1:
            self.general_quit("Line is snagged")
        self.tackle.available = False

    def handle_fish(self) -> None:
        if not self.detection.is_fish_captured():
            return
        logger.info("Handling fish")
        self._handle_fish()
        sleep(ANIMATION_DELAY)
        while self.detection.is_gift_receieved():
            sleep(self.cfg.KEEPNET.GIFT_DELAY)
            pag.press("space")

        limit = self.cfg.KEEPNET.CAPACITY - self.cfg.ARGS.FISHES_IN_KEEPNET
        if self.result.kept == limit:
            self._handle_full_keepnet()

    def _handle_fish(self) -> None:
        """Keep or release the fish and record the fish count."""
        tagged = False
        for tag in self.cfg.SCRIPT.SCREENSHOT_TAGS:
            if self.detection.is_tag_exist(TagColor[tag.upper()]):
                tagged = True
        tagged = not self.cfg.SCRIPT.SCREENSHOT_TAGS or tagged
        if self.cfg.ARGS.SCREENSHOT and tagged:
            self.window.save_screenshot(self.timer.get_cur_timestamp())

        self.result.total += 1
        if self.detection.is_fish_blacklisted():
            pag.press("backspace")
            return

        tagged = False
        for tag in TagColor:
            if self.detection.is_tag_exist(tag):
                tag_color = tag.name.lower()
                setattr(self.result, tag_color, getattr(self.result, tag_color) + 1)
                if tag_color in self.cfg.KEEPNET.TAGS:
                    tagged = True

        if (
            self.cfg.ARGS.TAG
            and not tagged
            and not self.detection.is_fish_whitelisted()
        ):
            pag.press("backspace")
            return

        # Fish is tagged, ARGS.TAG is disabled, or fish is in whitelist
        sleep(self.cfg.KEEPNET.FISH_DELAY)
        pag.press("space")

        self.result.kept += 1

        # Avoid wrong cast hour
        if self.cfg.SELECTED.MODE in ["bottom", "pirk", "elevator"]:
            self.timer.update_cast_time()
        self.timer.add_cast_time()

    def _handle_full_keepnet(self) -> None:
        """Handle a full keepnet event."""
        match self.cfg.KEEPNET.FULL_ACTION:
            case "alarm":
                playsound(str(Path(self.cfg.SCRIPT.ALARM_SOUND).resolve()))
                self.window.activate_script_window()
                print("Press any key to continue...")
                msvcrt.getch()
                self.window.activate_game_window()
                with keyboard.Listener(on_release=self._on_release) as listner:
                    listner.join()
                logger.info("Continue running script")
            case "quit":
                self.general_quit("Keepnet is full")
            case _:
                raise ValueError

    def _on_release(self, _: keyboard.KeyCode) -> None:
        """Handle key release events."""
        sys.exit()

    def general_quit(self, msg: str) -> None:
        """Quit the game through the control panel.

        :param msg: reason for termination
        :type msg: str
        """
        logger.critical(msg)
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

        self._handle_termination(msg, shutdown=True)

    def disconnected_quit(self) -> None:
        """Quit the game through the main menu."""
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

        self._handle_termination("Game disconnected", shutdown=True)

    def build_result_dict(self, msg: str):
        return self.result.as_dict(msg, self.timer)

    def build_result_table(self, result) -> Table:
        """Create a Rich table from running result.

        :return: formatted running result table
        :rtype: Table
        """
        table = Table(
            "Field", "Value", title="Running Result", box=box.DOUBLE, show_header=False
        )

        for k, v in result.items():
            table.add_row(k, str(v))
        return table

    def _handle_expired_ticket(self) -> None:
        """Handle an expired boat ticket event."""
        if self.cfg.ARGS.BOAT_TICKET is None:
            pag.press("esc")
            sleep(TICKET_EXPIRE_DELAY)
            self.general_quit("Boat ticket expired")

        logger.info("Renewing boat ticket")
        ticket_loc = self.detection.get_ticket_position(self.cfg.ARGS.BOAT_TICKET)
        if ticket_loc is None:
            pag.press("esc")  # Close ticket menu
            sleep(ANIMATION_DELAY)
            self.general_quit("New boat ticket not found")
        pag.moveTo(ticket_loc)
        pag.click(clicks=2, interval=0.1)  # pag.doubleClick() not implemented
        sleep(ANIMATION_DELAY)

    @utils.press_before_and_after("v")
    def _replace_broken_lures(self) -> None:
        """Replace multiple broken lures."""
        logger.info("Replacing broken lures")

        scrollbar_position = self.detection.get_scrollbar_position()
        if scrollbar_position is None:
            logger.info("Scroll bar not found, changing lures for normal rig")
            while self._open_broken_lure_menu():
                self._replace_item()
            pag.press("v")
            return

        logger.info("Scroll bar found, changing lures for dropshot rig")
        pag.moveTo(scrollbar_position)
        for _ in range(5):
            sleep(ANIMATION_DELAY)
            pag.drag(xOffset=0, yOffset=125, duration=0.5, button="left")

            replaced = False
            while self._open_broken_lure_menu():
                self._replace_item()
                replaced = True

            if replaced:
                pag.moveTo(self.detection.get_scrollbar_position())

    def _open_broken_lure_menu(self) -> bool:
        """Open the broken lure menu.

        :return: True if the broken lure is found, False otherwise.
        :rtype: bool
        """
        logger.info("Looking for broken lure")
        broken_item_position = self.detection.get_100wear_position()
        if broken_item_position is None:
            logger.warning("Broken lure not found")
            return False

        # click item to open selection menu
        pag.moveTo(broken_item_position)
        sleep(ANIMATION_DELAY)
        pag.click()
        sleep(ANIMATION_DELAY)
        return True

    def _replace_item(self) -> None:
        """Replace a broken item with a favorite item."""
        logger.info("Looking for favorite items")
        favorite_item_positions = self.detection.get_favorite_item_positions()
        while True:
            favorite_item_position = next(favorite_item_positions, None)
            if favorite_item_position is None:
                pag.press("esc")
                sleep(ANIMATION_DELAY)
                pag.press("esc")
                sleep(ANIMATION_DELAY)
                self.general_quit("Favorite item not found")

            # Check if the lure for replacement is already broken
            x, y = utils.get_box_center(favorite_item_position)
            if pag.pixel(x - 60, y + 190) != (178, 59, 30):  # Magic value #TODO
                logger.info("Lure replaced successfully")
                pag.moveTo(x - 60, y + 190)
                pag.click(clicks=2, interval=0.1)
                sleep(WEAR_TEXT_UPDATE_DELAY)
                break

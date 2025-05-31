"""Module for Player class.

This module provides the main interface for automating fishing activities in a game.
It includes functionality for managing fishing loops, handling player stats, and
automating various fishing techniques.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import json
import logging
import os
import random
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Lock
from contextlib import contextmanager

# from email.mime.image import MIMEImage
from pathlib import Path
from time import sleep
from urllib import parse, request

import pyautogui as pag
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator
from playsound import playsound
from pynput import keyboard
from rich import box, print
from rich.table import Table

from rf4s import exceptions, utils
from rf4s.component.friction_brake import FrictionBrake
from rf4s.component.tackle import Tackle
from rf4s.controller.detection import Detection
from rf4s.controller.timer import Timer
from rf4s.controller.window import Window

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
BOUND = 2
PUT_DOWN_DELAY = 4

SCREENSHOT_DELAY = 2

TROLLING_KEY = "j"

FORWARD = "w"
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

        self.result_dict = None

        self.records = {
            "tea": 0,
            "carrot": 0,
            "alcohol": 0,
            "cur_coffee": 0,
            "total_coffee": 0,
            "bait": 0,
            "kept_fish": 0,
            "marked_fish": 0,
            "unmarked_fish": 0,
            "have_new_lure": True,
            "have_new_groundbait": True,
            "have_new_dry_mix": True,
            "have_new_pva": True,
        }

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
            sys.exit(1)

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
                self._reset_tackle()
                self._change_tackle_lure()
                self._cast_tackle()
            skip_cast = False

            if self.cfg.SELECTED.TYPE != "normal":
                utils.hold_mouse_button(self.cfg.SELECTED.TIGHTEN_DURATION)
                getattr(self.tackle, f"retrieve_with_{self.cfg.SELECTED.TYPE}")()
            self._retrieve_line()

            if self.detection.is_fish_hooked():
                self._pull_fish()

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
        self._retrieve_line()
        self._pull_fish()
        self._reset_tackle()
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
        perform_technique = self._do_pirking if pirk else self._do_elevating
        skip_cast = self.cfg.ARGS.SKIP_CAST
        while True:
            if not skip_cast:
                self._refill_stats()
                self._reset_tackle()
                self._cast_tackle()
                self.tackle.sink()
            skip_cast = False

            perform_technique()
            self._retrieve_line()
            self._pull_fish()

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
            self._reset_tackle()
            self._cast_tackle()

            try:
                monitor()
            except exceptions.DisconnectedError:
                self.disconnected_quit()
            except exceptions.TicketExpiredError:
                self._handle_expired_ticket()
            except TimeoutError:
                pass

            sleep(self.cfg.SELECTED.PULL_DELAY)
            hold_mouse_button(PRE_RETRIEVAL_DURATION)
            self._pull_fish()



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
                self.records["bait"] += 1
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
            self.records["tea"] += 1

        if self.detection.is_hunger_low():
            self._use_item("carrot")
            self.records["carrot"] += 1

    def _drink_alcohol(self) -> None:
        """Drink alcohol with the given quantity."""
        if not self.cfg.ARGS.ALCOHOL or not self.timer.is_alcohol_drinkable():
            return

        logger.info("Drinking alcohol")
        for _ in range(self.cfg.STAT.ALCOHOL_PER_DRINK):
            self._use_item("alcohol")
        self.records["alcohol"] += self.cfg.STAT.ALCOHOL_PER_DRINK

    def _drink_coffee(self) -> None:
        """Drink coffee to refill energy if energy is low."""
        if not self.cfg.ARGS.COFFEE or self.detection.is_energy_high():
            return

        if self.records["cur_coffee"] > self.cfg.STAT.COFFEE_LIMIT:
            pag.press("esc")  # Just back to control panel to reduce power usage
            self._handle_termination("Coffee limit reached", shutdown=False)

        logger.info("Drinking coffee")
        for _ in range(self.cfg.STAT.COFFEE_PER_DRINK):
            self._use_item("coffee")
        self.records["cur_coffee"] += self.cfg.STAT.COFFEE_PER_DRINK
        self.records["total_coffee"] += self.cfg.STAT.COFFEE_PER_DRINK

    def _use_item(self, item: str) -> None:
        """Access an item by name using quick selection shortcut or menu.

        :param item: The name of the item to access.
        :type item: str
        """
        logger.info("Using item: %s", item)
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

    @utils.reset_friction_brake_after
    def _reset_tackle(self) -> None:
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

        while True:
            try:
                with pag.hold("shift"), self.clicklock_handler():
                    self.tackle.reset()
                    return
            except exceptions.FishHookedError:
                self._pull_fish()
                return
            except exceptions.FishCapturedError:
                self.handle_fish()
                return
            except exceptions.LineAtEndError:
                self.general_quit("Fishing line is at its end")
            except exceptions.LineSnaggedError:
                self._handle_snagged_line()
            except exceptions.LureBrokenError:
                self._handle_broken_lure()
            except exceptions.TackleBrokenError:
                self.general_quit("Tackle is broken")
            except exceptions.DisconnectedError:
                self.disconnected_quit()
            except exceptions.TicketExpiredError:
                self._handle_expired_ticket()
            except TimeoutError:
                pass

    def clicklock_handler(self, func=None):
        @contextmanager
        def _handler():
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
                exceptions.TicketExpiredError
            ):
                pag.click()
                raise

        if func is None: # Context manager
            return _handler()
        else: # Decorator
            def wrapped(*args, **kwargs):
                with _handler():
                    return func(*args, **kwargs)
            return wrapped


    def _cast_spod_rod(self) -> None:
        """Cast the spod rod if dry mix is available."""
        self._use_item("spod_rod")
        self._reset_tackle()

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
        self.tackle.cast(lock)
        if update:
            self.timer.update_cast_time()

    def _retrieve_line(self) -> None:
        """Retrieve the fishing line until it is fully retrieved."""
        if self.detection.is_retrieval_finished():
            return

        first = True
        gr_switched = False
        self.records["cur_coffee"] = 0
        while True:
            try:
                with self.clicklock_handler():
                    self.tackle.retrieve(first)
                    break
            except exceptions.FishCapturedError:
                self.handle_fish()
                break
            except exceptions.LineAtEndError:
                self.general_quit("Fishing line is at its end")
            except exceptions.LineSnaggedError:
                self._handle_snagged_line()
            except exceptions.TackleBrokenError:
                self.general_quit("Tackle is broken")
            except exceptions.DisconnectedError:
                self.disconnected_quit()
            except exceptions.TicketExpiredError:
                self._handle_expired_ticket()
            except TimeoutError:
                first = False
                if self.cfg.ARGS.GEAR_RATIO and not gr_switched:
                    self.tackle.switch_gear_ratio()
                    gr_switched = True
                pag.keyUp("shift")
                self._drink_coffee()

        pag.keyUp("shift")
        if gr_switched:
            self.tackle.switch_gear_ratio()

    def _do_pirking(self) -> None:
        """Perform pirking until a fish is hooked."""
        while True:
            try:
                self.tackle.pirk()
                break
            except exceptions.DisconnectedError:
                self.disconnected_quit()
            except exceptions.TicketExpiredError:
                self._handle_expired_ticket()
            except TimeoutError:
                if self.cfg.SELECTED.DEPTH_ADJUST_DELAY > 0:
                    logger.info("Adjusting lure depth")
                    pag.press("enter")  # Open reel
                    sleep(self.cfg.SELECTED.DEPTH_ADJUST_DELAY)
                    utils.hold_mouse_button(self.cfg.SELECTED.DEPTH_ADJUST_DURATION)
                else:
                    self._reset_tackle()
                    self._cast_tackle()
                    self.tackle.sink()

    def _do_elevating(self) -> None:
        """Perform elevating until a fish is hooked."""
        dropped = False
        while True:
            try:
                dropped = not dropped
                self.tackle.elevate(dropped)
                break
            except exceptions.DisconnectedError:
                self.disconnected_quit()
            except exceptions.TicketExpiredError:
                self._handle_expired_ticket()
            except TimeoutError:
                pass

    def _pull_fish(self) -> None:
        """Pull the fish up and handle it."""
        if not self.detection.is_fish_hooked():
            return

        self._drink_alcohol()
        while True:
            try:
                self.tackle.pull()
                self.handle_fish()
                return
            except exceptions.FishGotAwayError:
                return
            except exceptions.LineSnaggedError:
                self._handle_snagged_line()
            except exceptions.TackleBrokenError:
                self.general_quit("Tackle is broken")
            except exceptions.DisconnectedError:
                self.disconnected_quit()
            except exceptions.TicketExpiredError:
                self._handle_expired_ticket()
            except TimeoutError:
                if self.cfg.SELECTED.MODE == "float":
                    sleep(PUT_DOWN_DELAY)
                    continue
                self._retrieve_line()

    def _put_down_tackle(self, check_miss_counts: list[int]) -> None:
        """Put down the tackle and wait for a while.

        :param check_miss_counts: List of miss counts for all rods.
        :type check_miss_counts: list[int]
        """
        check_miss_counts[self.tackle_idx] += 1
        if check_miss_counts[self.tackle_idx] >= self.cfg.SELECTED.CHECK_MISS_LIMIT:
            check_miss_counts[self.tackle_idx] = 0
            self._reset_tackle()
            self._refill_groundbait()
            self._refill_pva()
            self._cast_tackle(lock=True)

        pag.press("0")
        random_offset = random.uniform(-BOUND, BOUND)
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
        if not self.cfg.ARGS.LURE or not self.records["have_new_lure"]:
            return

        if self.timer.is_lure_changeable():
            logger.info("Changing lure randomly")
            try:
                self.tackle.equip_item("lure")
            except exceptions.ItemNotFoundError:
                logger.error("New lure not found")

    def _refill_pva(self) -> None:
        """Refill the PVA bag if it has been used up."""
        if not self.cfg.ARGS.PVA or not self.records["have_new_pva"]:
            return

        if not self.detection.is_pva_chosen():
            logger.warning("Pva has been used up")
            try:
                self.tackle.equip_item("pva")
            except exceptions.ItemNotFoundError:
                logger.error("New pva not found")
                self.records["have_new_pva"] = False

    def _refill_dry_mix(self) -> None:
        """Refill the dry mix if it has been used up."""
        if not self.cfg.ARGS.DRY_MIX or not self.records["have_new_dry_mix"]:
            return
        try:
            self.tackle.equip_item("dry_mix")
        except exceptions.ItemNotFoundError:
            logger.error("New dry mix not found")
            self.tackle.available = False  # Skip following stages
            self.records["have_new_dry_mix"] = False

    def _refill_groundbait(self) -> None:
        """Refill the groundbait if it has been used up."""
        if not self.cfg.ARGS.GROUNDBAIT or not self.records["have_new_groundbait"]:
            return

        if self.detection.is_groundbait_chosen():
            logger.info("Groundbait is not used up yet")
        else:
            try:
                self.tackle.equip_item("groundbait")
            except exceptions.ItemNotFoundError:
                logger.error("New groundbait not found")

    def test(self):
        """Boo!"""
        self._retrieve_line()

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
        bound = self.cfg.PAUSE.DURATION // 20
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
                print("Please replace your lure")
                input("Press enter to continue...")
                self.window.activate_game_window()
            case _:
                self.general_quit("Lure is broken")

    @utils.release_keys_after(arrow_keys=True)
    def _handle_termination(self, termination_reason: str, shutdown: bool) -> None:
        """Handle script termination.

        :param termination_reason: The reason for termination.
        :type termination_reason: str
        :param shutdown: Whether to shutdown the computer after termination.
        :type shutdown: bool
        """
        table = self.create_table_from_results(self.create_results(termination_reason))
        if self.cfg.ARGS.EMAIL:
            self.send_email()
        if self.cfg.ARGS.MIAOTIXING:
            self.send_miaotixing()
        if self.cfg.ARGS.PLOT:
            self.plot_and_save()
        if shutdown and self.cfg.ARGS.SHUTDOWN:
            os.system("shutdown /s /t 5")
        print(table)
        sys.exit()

    def _handle_snagged_line(self) -> None:
        """Handle a snagged line event."""
        if len(self.tackles) == 1:
            self.general_quit("Line is snagged")
        self.tackle.available = False

    def handle_fish(self) -> None:
        self._handle_fish()
        sleep(ANIMATION_DELAY)
        if self.detection.is_gift_receieved():
            pag.press("space")
            return

    def _handle_fish(self) -> None:
        """Keep or release the fish and record the fish count.

        TODO: Trophy ruffe
        """
        if not self.detection.is_fish_captured():
            return
        logger.info("Handling fish")
        if self.cfg.ARGS.SCREENSHOT:
            self.window.save_screenshot(self.timer.get_cur_timestamp())

        if self.detection.is_fish_blacklisted():
            pag.press("backspace")
            return

        if self.detection.is_fish_marked():
            self.records["marked_fish"] += 1
        else:
            self.records["unmarked_fish"] += 1
            if self.cfg.ARGS.MARKED and not self.detection.is_fish_whitelisted():
                pag.press("backspace")
                return

        # Fish is marked, unmarked release is disabled, or fish is in whitelist
        sleep(self.cfg.KEEPNET.DELAY)
        pag.press("space")

        self.records["kept_fish"] += 1
        limit = self.cfg.KEEPNET.CAPACITY - self.cfg.ARGS.FISHES_IN_KEEPNET
        if self.records["kept_fish"] == limit:
            self._handle_full_keepnet()

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
                print(input("Press enter to continue..."))
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

    def general_quit(self, termination_reason: str) -> None:
        """Quit the game through the control panel.

        :param termination_reason: reason for termination
        :type termination_reason: str
        """
        logger.critical(termination_reason)
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

        self._handle_termination(termination_reason, shutdown=True)

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

    def create_results(self, termination_reason: str) -> dict:
        """Convert records into running results.

        :param termination_reason: reason for termination
        :type termination_reason: str
        :return: running results
        :rtype: dict
        """
        total_fish_count = self.records["marked_fish"] + self.records["unmarked_fish"]
        # Will be 0 if total_fish_count = 0
        mark_ratio_str = (
            f"{self.records['marked_fish']} / "
            f"{self.records['unmarked_fish']} / "
            f"{int(self.records['marked_fish'] / max(1, total_fish_count) * 100)}%"
        )
        bite_rate_str = (
            f"{total_fish_count} / "
            f"{self.records['kept_fish']} / "
            f"{(total_fish_count / self.timer.get_running_time() / 3600):.1f}/hr"
        )

        return {
            "Reason for termination": termination_reason,
            "Start time": self.timer.get_start_datetime(),
            "End time": self.timer.get_cur_datetime(),
            "Running time": self.timer.get_running_time_str(),
            "Marked / Unmarked / Mark ratio": mark_ratio_str,
            "Total  / Kept     / Bite rate ": bite_rate_str,
            "Tea consumed": self.records["tea"],
            "Carrot consumed": self.records["carrot"],
            "Alcohol consumed": self.records["alcohol"],
            "Coffee consumed": self.records["total_coffee"],
            "Bait harvested": self.records["bait"],
        }

    def create_table_from_results(self, results: dict) -> Table:
        """Create a Rich table from running results.

        :param results: running results
        :type results: dict
        :return: formatted running results table
        :rtype: Table
        """
        table = Table(
            "Field", "Value", title="Running Results", box=box.DOUBLE, show_header=False
        )

        for k, v in results.items():
            table.add_row(k, str(v))
        return table

    def send_email(self, results: dict) -> None:
        """Send a notification email to the user's email address.

        :param results: running results
        :type results: dict
        """
        logger.info("Sending email")

        msg = MIMEMultipart()
        msg["Subject"] = "RussianFishing4Script: Notice of Program Termination"
        msg["From"] = self.cfg.NOTIFICATION.EMAIL
        recipients = [self.cfg.NOTIFICATION.EMAIL]
        msg["To"] = ", ".join(recipients)

        text = ""
        for k, v in results.items():
            text += f"{k}: {v}\n"
        msg.attach(MIMEText(text))

        with smtplib.SMTP_SSL(self.cfg.NOTIFICATION.SMTP_SERVER, 465) as server:
            # smtp_server.ehlo()
            server.login(self.cfg.NOTIFICATION.EMAIL, self.cfg.NOTIFICATION.PASSWORD)
            server.sendmail(self.cfg.NOTIFICATION.EMAIL, recipients, msg.as_string())
        logger.info("Email sent successfully")

    def send_miaotixing(self, results: dict) -> None:
        """Send a notification to the user's miaotixing service.

        :param results: running results
        :type results: dict
        """
        logger.info("Sending miaotixing notification")

        text = ""
        for k, v in results.items():
            text += f"{k}: {v}\n"

        url = "http://miaotixing.com/trigger?" + parse.urlencode(
            {"id": self.cfg.NOTIFICATION.MIAO_CODE, "text": text, "type": "json"}
        )

        with request.urlopen(url) as page:
            result = page.read()
            json_object = json.loads(result)
            if json_object["code"] == 0:
                logger.info("Miaotixing notification sent successfully")
            else:
                logger.error(
                    "Miaotixing notification with error code: %s\nDescription: %s",
                    str(json_object["code"]),
                    json_object["msg"],
                )

    def plot_and_save(self) -> None:
        """Plot and save an image using rhour and ghour lists from the timer object."""
        logger.info("Plotting Curves")
        if self.records["kept_fish"] == 0:
            return

        cast_rhour_list, cast_ghour_list = self.timer.get_cast_time_list()
        _, ax = plt.subplots(nrows=1, ncols=2)
        # _.canvas.manager.set_window_title('Record')
        ax[0].set_ylabel("Fish")

        last_rhour = cast_rhour_list[-1]  # Hour: 0, 1, 2, 3, 4, "5"
        fish_per_rhour = [0] * (last_rhour + 1)  # Idx: (0, 1, 2, 3, 4, 5) = 6
        for hour in cast_rhour_list:
            fish_per_rhour[hour] += 1
        ax[0].plot(range(last_rhour + 1), fish_per_rhour)
        ax[0].set_title("Fish Caughted per Real Hour")
        ax[0].set_xticks(range(last_rhour + 2))
        ax[0].set_xlabel("Hour (real running time)")
        ax[0].yaxis.set_major_locator(MaxNLocator(integer=True))

        fish_per_ghour = [0] * 24
        for hour in cast_ghour_list:
            fish_per_ghour[hour] += 1
        ax[1].bar(range(0, 24), fish_per_ghour)
        ax[1].set_title("Fish Caughted per Game Hour")
        ax[1].set_xticks(range(0, 24, 2))
        ax[1].set_xlabel("Hour (game time)")
        ax[1].yaxis.set_major_locator(MaxNLocator(integer=True))

        # plt.tight_layout()
        plt.savefig(f"../logs/{self.timer.get_cur_timestamp()}.png")
        logger.info("Plot has been saved under logs/")

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

"""Base application class for other tools.

Provides core functionality for:
- Configuration management
- Window control
- Result display

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import argparse
import os
import random
import shlex
import signal
import smtplib
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from multiprocessing import Lock
from socket import gaierror
from time import sleep
from typing import Optional

import pyautogui as pag
import requests
from pynput import keyboard
from rich import box, print
from rich.prompt import Prompt
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s import config, exceptions, utils
from rf4s.app.core import logger
from rf4s.i18n import t
from rf4s.component.friction_brake import FrictionBrake
from rf4s.config import load_cfg
from rf4s.controller.detection import Detection
from rf4s.controller.player import Player
from rf4s.controller.timer import Timer, add_jitter
from rf4s.controller.window import Window
from rf4s.result import BotResult, CraftResult, HarvestResult, Result

BIAS = 1e-6
ANIMATION_DELAY = 0.5
THREAD_CHECK_DELAY = 0.5
LOOP_DELAY = 1
CRAFT_DELAY = 4.0
MAX_FRICTION_BRAKE = 30


class App(ABC):
    """A base application class.

    Attributes:
        cfg (yacs.config.CfgNode): Default + user's configuration file
        window (Window): Window controller
    """

    def __init__(
        self, cfg: CN, args: argparse.Namespace, parser: argparse.ArgumentParser
    ):
        """Initialize a mutable cfg node for further modification."""
        self.cfg = cfg
        self.args = args
        self.parser = parser
        self.result = None  # Dummy result

    @abstractmethod
    def _on_release(self, key: keyboard.KeyCode) -> None:
        pass

    @abstractmethod
    def start(self):
        pass

    def display_result(self) -> None:
        """Display the running result in a table format."""
        result_dict = self.result.as_dict()
        if not result_dict:
            return

        result = Table(title=t("app.running_result"), box=box.HEAVY, show_header=False)
        for name, value in self.result.as_dict().items():
            result.add_row(name, str(value))
        print(result)


class BotApp(App):
    """Main application class for Russian Fishing 4 automation.

    This class orchestrates the entire automation process, from parsing command-line
    arguments to configuring the environment and executing the fishing routine.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments
        args (Namespace): Parsed command-line arguments
        window (Window): Game window controller instance
        player (Player): Player instance for fishing automation
    """

    def __init__(
        self, cfg: CN, args: argparse.Namespace, parser: argparse.ArgumentParser
    ):
        """Initialize the application.

        Loads configuration, parses command-line arguments, and sets up the environment.
        """
        super().__init__(cfg, args, parser)
        self.setup_profile()
        self.merge_args_to_cfg()
        self.window = Window()
        # args is done now, start validation
        self.validate_cfg()
        self.cfg.freeze()  # cfg is done now
        self.display_info()

        self.result = BotResult()
        self.window = Window()
        self.player = Player(
            self.cfg, Timer(self.cfg), Detection(self.cfg, self.window), self.result
        )

        self.paused = False

    def validate_cfg(self):
        self.validate_smtp()
        self.validate_discord()
        self.validate_telegram()
        self.validate_game_window()
        self.validate_favorite_icon()
        self.validate_screenshot_notification()
        self.validate_spool_detection()

    def display_info(self):
        settings = Table(
            title=t("app.settings"), show_header=False, box=box.HEAVY, min_width=36
        )
        settings.add_row(t("app.launch_options_final"), " ".join(sys.argv[1:]))
        for k, v in self.cfg.PROFILE.items():
            if k != "DESCRIPTION":
                settings.add_row(k, str(v))
        print(settings)
        if self.cfg.PROFILE.DESCRIPTION:
            utils.print_description_box(self.cfg.PROFILE.DESCRIPTION)
        utils.print_usage_box(
            t("app.press_to_pause_quit",
              pause_key=self.cfg.KEY.PAUSE, quit_key=self.cfg.KEY.QUIT)
        )

    def validate_smtp(self) -> None:
        """Verify SMTP server connection for email notifications.

        Tests the connection to the configured SMTP server using stored
        credentials if email notifications are enabled.
        """
        if not self.cfg.ARGS.EMAIL or not self.cfg.BOT.SMTP_VERIFICATION:
            return
        logger.info(t("app.verifying_smtp"))

        try:
            with smtplib.SMTP_SSL(self.cfg.BOT.NOTIFICATION.SMTP_SERVER, 465) as server:
                server.login(
                    self.cfg.BOT.NOTIFICATION.EMAIL, self.cfg.BOT.NOTIFICATION.PASSWORD
                )
        except smtplib.SMTPAuthenticationError:
            logger.critical(t("app.error.smtp_auth"))
            utils.safe_exit()
        except (TimeoutError, gaierror):
            logger.critical(t("app.error.smtp_timeout"))
            utils.safe_exit()

    def validate_discord(self) -> None:
        if not self.cfg.ARGS.DISCORD or self.cfg.BOT.NOTIFICATION.DISCORD_WEBHOOK_URL:
            return
        logger.critical(t("app.error.discord_webhook"))
        utils.safe_exit()

    def validate_miaotixing(self) -> None:
        if not self.cfg.ARGS.MIAOTIXING or self.cfg.BOT.NOTIFICATION.MIAO_CODE:
            return
        logger.critical(t("app.error.miao_code"))
        utils.safe_exit()

    def validate_telegram(self):
        def _is_telegram_bot_valid():
            url = (
                "https://api.telegram.org/"
                f"bot{self.cfg.BOT.NOTIFICATION.TELEGRAM_BOT_TOKEN}/getMe"
            )
            return requests.get(url).status_code == 200

        if not self.cfg.ARGS.TELEGRAM:
            return

        valid = True
        if not _is_telegram_bot_valid():
            logger.critical(t("app.error.telegram_token"))
            valid = False
        if self.cfg.BOT.NOTIFICATION.TELEGRAM_CHAT_ID == -1:
            logger.critical(t("app.error.telegram_chat_id"))
            valid = False
        if not valid:
            logger.critical(t("app.error.telegram_refer"))
            utils.safe_exit()

    def validate_profile(self, profile_name: str) -> None:
        """Check if a profile configuration is valid and complete.

        :param profile_name: Name of the profile to validate.
        :type profile_name: str
        """
        if profile_name not in self.cfg.PROFILE:
            logger.critical(t("app.error.invalid_profile", name=profile_name))
            utils.safe_exit()

        mode = self.cfg.PROFILE[profile_name].MODE
        if mode.upper() not in self.cfg.PROFILE:
            logger.critical(t("app.error.invalid_mode", mode=mode))
            utils.safe_exit()

        expected_keys = set(self.cfg.PROFILE[mode.upper()])
        actual_keys = set(self.cfg.PROFILE[profile_name])

        invalid_keys = actual_keys - expected_keys
        missing_keys = expected_keys - actual_keys

        if invalid_keys or missing_keys:
            for key in invalid_keys:
                logger.warning(t("app.warning.invalid_setting", profile=profile_name, setting=key))
            for key in missing_keys:
                logger.warning(t("app.warning.missing_setting", profile=profile_name, setting=key))

    def display_profiles(self) -> None:
        """Display a table of available profiles for user selection.

        Shows a formatted table with profile IDs and names.
        """
        profiles = Table(
            title=t("app.select_profile"),
            box=box.HEAVY,
            show_header=False,
            min_width=36,
        )
        for i, profile in enumerate(self.cfg.PROFILE):
            profiles.add_row(f"{i:>2}. {profile}")
        print(profiles)

    def get_pid(self) -> None:
        """Prompt the user to enter a profile ID and validate the input.

        Continuously prompts until a valid profile ID is entered or the
        user chooses to quit.
        """
        utils.print_usage_box(t("app.prompt.enter_pid"))

        while True:
            user_input = input(">>> ")
            if user_input.isdigit() and 0 <= int(user_input) < len(self.cfg.PROFILE):
                break
            if user_input == "q":
                print(t("main.bye"))
                sys.exit()
            utils.print_error(t("app.error.invalid_pid"))

        self.args.pid = int(user_input)

    def setup_profile(self) -> None:
        """Configure the user profile based on arguments or interactive selection.

        Selects a profile based on command-line arguments or user input,
        validates the profile, and merges it with the configuration.
        """
        if self.args.pname is not None:
            profile_name = self.args.pname
        else:
            if self.args.pid is None:
                self.display_profiles()
                self.get_pid()
            profile_name = list(self.cfg.PROFILE)[self.args.pid]
        self.merge_default_to_profile(profile_name)

    def merge_default_to_profile(self, profile_name) -> None:
        self.validate_profile(profile_name)
        mode = self.cfg.PROFILE[profile_name].MODE.upper()
        user_profile = CN({"NAME": profile_name}, new_allowed=True)
        user_profile.merge_from_other_cfg(self.cfg.PROFILE[mode])
        user_profile.merge_from_other_cfg(self.cfg.PROFILE[profile_name])
        self.cfg.PROFILE = user_profile  # Overwrite default profiles

    def merge_args_to_cfg(self) -> None:
        """Must be called after the profile is correctly configured."""
        if len(self.args.opts) % 2:
            logger.error(
                t("app.error.invalid_launch_options",
                  options=" ".join(sys.argv[1:]),
                  opts=" ".join(self.args.opts))
            )
            sys.exit()

        self.cfg.merge_from_list(self.args.opts)
        # Merge profile-level launch options
        if self.cfg.PROFILE.LAUNCH_OPTIONS:
            new_launch_options = shlex.split(self.cfg.PROFILE.LAUNCH_OPTIONS)
            base_len = len(shlex.split(self.cfg.BOT.LAUNCH_OPTIONS)) + 2
            sys.argv = sys.argv[:base_len] + new_launch_options + sys.argv[base_len:]
            self.args = self.parser.parse_args()
        # We need to convert items in args to uppercase to make them consistent with
        # those in CN(), so it must be done manually instead of using CN(dict).
        self.cfg.ARGS = config.dict_to_cfg(vars(self.args))

    def validate_game_window(self) -> None:
        """Set up and validate the game window.

        Creates a Window object, checks if the window size is supported,
        and disables incompatible features if needed.
        """
        if self.window.is_title_bar_exist():
            logger.info(t("app.window_mode_detected"))
        if self.window.is_size_supported():
            logger.info(t("app.supported_window_size"))
            return

        window_resolution = self.window.get_resolution_str()
        if window_resolution == "0x0":
            logger.critical(t("app.error.fullscreen_not_supported"))
            utils.safe_exit()

        if self.cfg.PROFILE.MODE in ("telescopic", "bolognese"):
            logger.critical(
                t("app.error.mode_unsupported_size",
                  mode=self.cfg.PROFILE.MODE,
                  size=self.window.get_resolution_str())
            )
            utils.safe_exit()

        logger.warning(
            t("app.warning.unsupported_window_size",
              size=self.window.get_resolution_str())
        )
        logger.error(t("app.error.features_disabled"))

        self.cfg.ARGS.FRICTION_BRAKE = False
        self.cfg.BOT.SNAG_DETECTION = False
        self.cfg.BOT.SPOOLING_DETECTION = False

    def validate_favorite_icon(self):
        if (
            self.cfg.ARGS.COFFEE
            or self.cfg.ARGS.REFILL
            or self.cfg.ARGS.LURE
            or self.cfg.ARGS.DRY_MIX
            or self.cfg.ARGS.GROUNDBAIT
            or self.cfg.ARGS.PVA
        ):
            logger.info(t("app.info.favorites_reminder"))

    def validate_screenshot_notification(self):
        if self.cfg.ARGS.SCREENSHOT and self.cfg.ARGS.MIAOTIXING:
            logger.warning(t("app.warning.miaotixing_no_image"))

    def validate_spool_detection(self):
        if self.cfg.ARGS.RAINBOW is None:
            logger.warning(t("app.warning.default_retrieval"))

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Monitor user's keystrokes and convert a key press to a CTRL_C_EVENT.

        :param key: The key that was released.
        :type key: keyboard.KeyCode

        Exits the application when the configured quit key is pressed.
        """
        # Trigger CTRL_C_EVENT, which will be caught in start() to simulate pressing
        # CTRL-C to terminate the script.
        if utils.key_matches(key, self.cfg.KEY.QUIT):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            return False
        if utils.key_matches(key, self.cfg.KEY.PAUSE):
            logger.info(t("app.pausing_bot"))
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            self.paused = True
            logger.info(t("app.bot_paused"))  # Don't remove this! It messes with signal?
            return False

    def _pause_wait(self, key: keyboard.KeyCode) -> None:
        if utils.key_matches(key, self.cfg.KEY.PAUSE):
            self.paused = False
            return False

    def reload_cfg(self) -> None:
        profile_name = self.cfg.PROFILE.NAME
        self.cfg = load_cfg()
        self.merge_default_to_profile(profile_name)
        self.merge_args_to_cfg()
        self.validate_cfg()
        self.cfg.freeze()
        self.display_info()

    def start(self) -> None:
        """Start the fishing automation process.

        Sets up all required components, activates the game window,
        registers key listeners, and begins the fishing automation.
        Handles termination and displays result.
        """
        while True:
            general_listener = keyboard.Listener(on_release=self._on_release)
            general_listener.start()
            self.window.activate_game_window()
            try:
                self.player.start_fishing()
            except KeyboardInterrupt:
                general_listener.stop()
                if not self.paused:
                    break

                utils.print_usage_box(
                    t("app.press_to_reload", pause_key=self.cfg.KEY.PAUSE)
                )
                utils.print_hint_box(
                    t("app.hint.launch_options_ignored")
                )
                with self.player.hold_keys(mouse=False, shift=False, reset=True):
                    pause_listener = keyboard.Listener(on_release=self._pause_wait)
                    pause_listener.start()

                while pause_listener.is_alive():
                    sleep(add_jitter(THREAD_CHECK_DELAY))

                logger.info(t("app.restarting_bot"))
                self.reload_cfg()
                self.player = Player(
                    self.cfg,
                    self.player.timer,
                    self.player.detection,
                    self.player.result,
                )
                self.paused = False

        self.player.handle_termination(t("player.terminated_by_user"), shutdown=False, send=False)


class CraftApp(App):
    """Main application class for automating crafting.

    This class manages the configuration, detection, and execution of the crafting
    process. It tracks the number of successful and failed crafts, as well as the
    total number of materials used.
    """

    def __init__(self, cfg, args, parser):
        super().__init__(cfg, args, parser)
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(self.args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(self.args.opts)
        self.cfg.freeze()

        settings = Table(
            title=t("app.settings"), show_header=False, box=box.HEAVY, min_width=36
        )
        settings.add_row(t("app.launch_options_final"), " ".join(sys.argv[1:]))
        print(settings)

        self.result = CraftResult()
        self.window = Window()
        self.detection = Detection(self.cfg, self.window)

    def craft_item(self, accept_key: str) -> None:
        """Craft an item.

        :param craft_delay: Delay in seconds before accepting the crafted item.
        :type craft_delay: float
        :param accept_delay: Delay in seconds after accepting the crafted item.
        :type accept_delay: float
        :param accept_key: Key to press after accepting the crafted item.
        :type accept_key: str
        """
        logger.info(t("app.craft.crafting_item"))
        pag.click()
        sleep(add_jitter(CRAFT_DELAY))
        self.result.material += 1
        while True:
            if self.detection.is_operation_success():
                logger.info(t("app.craft.success"))
                self.result.success += 1
                pag.press(accept_key)
                break

            if self.detection.is_operation_failed():
                logger.warning(t("app.craft.failed"))
                self.result.fail += 1
                pag.press("space")
                break
            sleep(add_jitter(LOOP_DELAY))
        sleep(add_jitter(ANIMATION_DELAY))
        discard_yes_position = self.detection.get_discard_yes_position()
        if discard_yes_position:
            pag.click(discard_yes_position)
        sleep(add_jitter(LOOP_DELAY))

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
        :type key: keyboard.KeyCode
        """
        if utils.key_matches(key, self.cfg.KEY.QUIT):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            return False

    def start(self) -> None:
        """Main loop for crafting items.

        Executes the primary loop for crafting items until materials are exhausted or
        the crafting limit is reached. Supports fast crafting mode and discarding items.
        """
        listener = keyboard.Listener(on_release=self._on_release)
        listener.start()

        try:
            utils.print_usage_box(t("app.press_to_quit", quit_key=self.cfg.KEY.QUIT))
            logger.warning(t("app.craft.warning_ban"))
            logger.warning(t("app.craft.warning_macros"))
            random.seed(datetime.now().timestamp())
            accept_key = "backspace" if self.cfg.ARGS.DISCARD else "space"
            self.window.activate_game_window()
            make_button_position = self.detection.get_make_button_position()
            if make_button_position is None:
                logger.critical(t("app.craft.make_not_found"))
                self.window.activate_script_window()
                sys.exit()
            pag.moveTo(make_button_position)
            while True:
                if (
                    not self.cfg.ARGS.IGNORE
                    and not self.detection.is_material_complete()
                ):
                    logger.critical(t("app.craft.out_of_materials"))
                    break
                if self.result.material == self.cfg.ARGS.CRAFT_LIMIT:
                    logger.info(t("app.craft.limit_reached"))
                    break
                self.craft_item(accept_key)
                pag.moveTo(make_button_position)
        except KeyboardInterrupt:
            pass
        self.display_result()


class MoveApp(App):
    """Main controller for movement automation in Russian Fishing 4.

    Manages configuration, keyboard event listeners, and W/Shift key simulation.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments.
        w_key_pressed (bool): Tracks current state of W key simulation.
    """

    def __init__(self, cfg, args, parser):
        """Initialize configuration, CLI arguments, and game window.

        1. Format keybinds in cfg node.
        2. Create w key flag.
        """
        super().__init__(cfg, args, parser)
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(self.args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(self.args.opts)
        self.cfg.freeze()

        utils.print_usage_box(
            t("app.move.press_to_pause_quit",
              pause_key=self.cfg.KEY.MOVE_PAUSE, quit_key=self.cfg.KEY.MOVE_QUIT)
        )

        self.result = Result()
        self.window = Window()
        self.w_key_pressed = True

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
        :type key: keyboard.KeyCode
        """
        if utils.key_matches(key, self.cfg.KEY.MOVE_QUIT):
            return False
        if utils.key_matches(key, self.cfg.KEY.MOVE_PAUSE):
            if self.w_key_pressed:
                self.w_key_pressed = False
                return True
            pag.keyDown("w")
            self.w_key_pressed = True

    def start(self) -> None:
        """Wrapper method that handle window activation and result display."""
        listener = keyboard.Listener(on_release=self._on_release)
        listener.start()
        self.window.activate_game_window()

        if self.cfg.ARGS.SHIFT:
            pag.keyDown("shift")
        pag.keyDown("w")
        while listener.is_alive():
            sleep(add_jitter(THREAD_CHECK_DELAY))


class HarvestApp(App):
    """Main application class for automating bait harvesting and hunger/comfort refill.

    This class manages the configuration, detection, and execution of the harvesting
    and refill processes. It also handles power-saving mode and check delays.

    Attributes:
        timer (Timer): Timer instance for managing cooldowns.
    """

    def __init__(self, cfg, args, parser):
        """Initialize the application.

        Loads configuration, parses command-line arguments, and sets up the game window,
        detection, and timer instances.
        """
        super().__init__(cfg, args, parser)
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(self.args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(self.args.opts)
        self.cfg.freeze()

        settings = Table(
            title=t("app.settings"), show_header=False, box=box.HEAVY, min_width=36
        )
        settings.add_row(t("app.launch_options_final"), " ".join(sys.argv[1:]))
        settings.add_row(t("app.harvest.power_saving"), str(self.cfg.HARVEST.POWER_SAVING))
        settings.add_row(t("app.harvest.check_delay"), str(self.cfg.HARVEST.CHECK_DELAY))
        settings.add_row(t("app.harvest.energy_threshold"), str(self.cfg.STAT.ENERGY_THRESHOLD))
        settings.add_row(t("app.harvest.hunger_threshold"), str(self.cfg.STAT.HUNGER_THRESHOLD))
        settings.add_row(t("app.harvest.comfort_threshold"), str(self.cfg.STAT.COMFORT_THRESHOLD))
        print(settings)
        utils.print_usage_box(t("app.press_to_quit", quit_key=self.cfg.KEY.QUIT))

        self.result = HarvestResult()
        self.timer = Timer(self.cfg)
        self.window = Window()
        self.detection = Detection(self.cfg, self.window)

    def harvest_baits(self) -> None:
        """Harvest baits using shovel/spoon.

        The digging tool should be pulled out before calling this method. Waits for
        harvest success and presses the spacebar to complete the process.
        """
        logger.info(t("app.harvest.harvesting"))
        pag.click()
        while not self.detection.is_harvest_success():
            sleep(add_jitter(LOOP_DELAY))
        pag.press("space")
        logger.info(t("app.harvest.success"))
        sleep(add_jitter(ANIMATION_DELAY))

    def refill_player_stats(self) -> None:
        """Refill player stats using tea and carrot."""
        if not self.cfg.ARGS.REFILL:
            return

        logger.info(t("app.harvest.refilling"))
        # Comfort is affected by weather, add a check to avoid over drink
        if self.detection.is_comfort_low() and self.timer.is_tea_drinkable():
            self._use_item("tea")
            self.result.tea += 1

        if self.detection.is_hunger_low():
            self._use_item("carrot")
            self.result.carrot += 1

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
        :type key: keyboard.KeyCode
        """
        # Trigger CTRL_C_EVENT, which will be caught in start() to simulate pressing
        # CTRL-C to terminate the script.
        if utils.key_matches(key, self.cfg.KEY.QUIT):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            return False

    def _use_item(self, item: str) -> None:
        """Access an item by name using quick selection shortcut or menu.

        :param item: The name of the item to access.
        :type item: str
        """
        logger.info(t("app.harvest.using_item", item=item))
        key = str(self.cfg.KEY[item.upper()])
        if key != "-1":  # Use shortcut
            pag.press(key)
        else:  # Open food menu
            with pag.hold("t"):
                sleep(add_jitter(ANIMATION_DELAY))
                food_position = self.detection.get_food_position(item)
                pag.moveTo(food_position)
                pag.click()
        sleep(add_jitter(ANIMATION_DELAY))

    def start(self) -> None:
        """Wrapper method that handle window activation and result display."""
        listener = keyboard.Listener(on_release=self._on_release)
        listener.start()

        self.window.activate_game_window()
        try:
            pag.press(str(self.cfg.KEY.DIGGING_TOOL))
            sleep(3)
            while True:
                self.refill_player_stats()
                if self.detection.is_energy_high():
                    self.harvest_baits()
                    self.result.bait += 1
                else:
                    logger.info(t("app.harvest.energy_low"))

                if self.cfg.HARVEST.POWER_SAVING:
                    pag.press("esc")
                    sleep(self.cfg.HARVEST.CHECK_DELAY)
                    pag.press("esc")
                    sleep(ANIMATION_DELAY)
                else:
                    sleep(self.cfg.HARVEST.CHECK_DELAY)
        except KeyboardInterrupt:
            pass
        self.display_result()


@dataclass
class Part:
    name: str
    prompt: str
    color: str
    base: float = 0.0
    load_capacity: Optional[float] = None
    wear: Optional[float] = None
    real_load_capacity: Optional[float] = None
    pre_real_load_capacity: Optional[float] = None

    def calculate_real_load_capacity(self) -> None:
        self.real_load_capacity = (
            self.load_capacity * (1 - self.base) * (1 - self.wear / 100)
            + self.load_capacity * self.base
        )


class CalculateCommand(Enum):
    RESTART = "r"
    PREVIOUS = "p"
    PREVIOUS_REMAINING = "P"
    SKIP = "s"
    SKIP_REMAINING = "S"
    QUIT = "q"


class CalculateApp:
    def __init__(self, cfg, args, parser):
        _ = cfg, args, parser
        self.result = None
        self.parts = [
            Part(name=t("app.calculate.rod"), prompt=t("app.calculate.load_capacity"), color="orange1", base=0.3),
            Part(name=t("app.calculate.reel_mechanism"), prompt=t("app.calculate.mech"), color="plum1", base=0.3),
            Part(name=t("app.calculate.reel_friction_brake"), prompt=t("app.calculate.drag"), color="gold1"),
            Part(name=t("app.calculate.fishing_line"), prompt=t("app.calculate.load_capacity"), color="salmon1"),
            Part(name=t("app.calculate.leader"), prompt=t("app.calculate.load_capacity"), color="pale_green1"),
            Part(name=t("app.calculate.hook"), prompt=t("app.calculate.load_capacity"), color="sky_blue1"),
        ]
        self.friction_brake = next(
            part for part in self.parts if part.name == t("app.calculate.reel_friction_brake")
        )

    def calculate_tackle_stats(self):
        previous = False
        for part in self.parts:
            try:
                if previous:
                    if part.pre_real_load_capacity is not None:
                        raise exceptions.PreviousError
                    else:
                        utils.print_error(t("app.calculate.error.value_not_found", name=part.name))
                part.load_capacity = self.get_validated_input(part, part.prompt)
                part.wear = self.get_validated_input(part, t("app.calculate.wear"))
            except exceptions.SkipError:
                if part.real_load_capacity is not None:
                    part.real_load_capacity = None
                continue
            except exceptions.PreviousError:
                part.real_load_capacity = part.pre_real_load_capacity
            except exceptions.PreviousRemainingError:
                part.real_load_capacity = part.pre_real_load_capacity
                previous = True
            else:
                part.calculate_real_load_capacity()
            self.result.add_row(part.name, f"{part.real_load_capacity:.2f} kg")

    def get_validated_input(self, part: Part, prompt: str) -> float:
        while True:
            user_input = Prompt.ask(
                f"[{part.color}][{part.name}][/{part.color}] {prompt}"
            )
            match user_input.strip():
                case CalculateCommand.RESTART.value:
                    raise exceptions.RestartError
                case CalculateCommand.PREVIOUS.value:
                    if part.pre_real_load_capacity is None:
                        utils.print_error(t("app.calculate.error.value_not_found", name=part.name))
                        continue
                    raise exceptions.PreviousError
                case CalculateCommand.PREVIOUS_REMAINING.value:
                    if part.pre_real_load_capacity is None:
                        utils.print_error(t("app.calculate.error.value_not_found", name=part.name))
                        continue
                    raise exceptions.PreviousRemainingError
                case CalculateCommand.SKIP.value:
                    raise exceptions.SkipError
                case CalculateCommand.SKIP_REMAINING.value:
                    raise exceptions.SkipRemainingError
                case CalculateCommand.QUIT.value:
                    raise exceptions.QuitError

            try:
                number = float(user_input)
                if prompt == t("app.calculate.wear"):
                    if not (0 <= number <= 100):
                        utils.print_error(t("app.calculate.error.wear_range"))
                        continue
                elif number < 0:
                    utils.print_error(t("app.calculate.error.non_negative"))
                    continue
                return number
            except ValueError:
                utils.print_error(t("app.calculate.error.invalid_input"))

    def reset_stats(self) -> None:
        for part in self.parts:
            part.pre_real_load_capacity = part.real_load_capacity
            part.real_load_capacity = None
        self.result = Table(
            t("app.calculate.results"),
            title=t("app.calculate.tackle_stats"),
            show_header=False,
            box=box.HEAVY,
            min_width=36,
        )

    def update_result(self) -> None:
        valid_parts = [p for p in self.parts if p.real_load_capacity is not None]
        if not valid_parts:
            return
        weakest_part = min(valid_parts, key=lambda x: x.real_load_capacity)
        self.result.add_row(t("app.calculate.weakest_part"), weakest_part.name)

        if self.friction_brake.real_load_capacity is None:
            return
        # k / 30 * drag < weakest -> k < weakest * 30 / drag
        try:
            recommend_friction_brake = min(
                MAX_FRICTION_BRAKE - 1,
                (
                    weakest_part.real_load_capacity
                    * MAX_FRICTION_BRAKE
                    / self.friction_brake.real_load_capacity
                ),
            )
            self.result.add_row(
                t("app.calculate.recommend_fb"),
                f"{int(recommend_friction_brake):2d}",
            )
        except ZeroDivisionError:
            pass  # Fail silently

    def start(self):
        """Main function to run the friction brake calculation.

        Prompts the user for input, calculates the result, and displays them in a table.
        """
        utils.print_usage_box(t("app.calculate.commands"))
        utils.print_hint_box(t("app.calculate.hint"))

        while True:
            self.reset_stats()
            try:
                self.calculate_tackle_stats()
            except exceptions.SkipRemainingError:
                pass
            except exceptions.RestartError:
                continue
            except exceptions.QuitError:
                print(t("main.bye"))
                break
            if self.result.rows:
                self.update_result()
                print(self.result)


class FrictionBrakeApp(App):
    """Main application class for automating friction brake adjustments.

    This class manages the configuration, detection, and execution of the friction
    brake automation process. It also handles key bindings for exiting and resetting.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments.
        friction_brake (FrictionBrake): Friction brake controller instance.
    """

    def __init__(self, cfg, args, parser):
        """Initialize the application.

        1. Check the game window state.
        2. Format keybinds in cfg node.
        3. Display cfg node.
        4. Initialize a friction brake instance.
        """
        super().__init__(cfg, args, parser)
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(self.args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(self.args.opts)
        self.cfg.freeze()

        settings = Table(
            title=t("app.settings"), show_header=False, box=box.HEAVY, min_width=36
        )
        settings.add_row(t("app.launch_options_final"), " ".join(sys.argv[1:]))
        settings.add_row(t("app.fb.initial"), str(self.cfg.FRICTION_BRAKE.INITIAL))
        settings.add_row(t("app.fb.max"), str(self.cfg.FRICTION_BRAKE.MAX))
        settings.add_row(t("app.fb.start_delay"), str(self.cfg.FRICTION_BRAKE.START_DELAY))
        settings.add_row(t("app.fb.increase_delay"), str(self.cfg.FRICTION_BRAKE.INCREASE_DELAY))
        settings.add_row(t("app.fb.sensitivity"), self.cfg.FRICTION_BRAKE.SENSITIVITY)
        print(settings)

        utils.print_usage_box(
            t("app.fb.press_to_reset_quit",
              reset_key=self.cfg.KEY.FRICTION_BRAKE_RESET,
              quit_key=self.cfg.KEY.FRICTION_BRAKE_QUIT)
        )

        self.window = Window()
        if not self.is_game_window_valid():
            utils.safe_exit()

        self.detection = Detection(self.cfg, self.window)
        self.friction_brake = FrictionBrake(self.cfg, Lock(), self.detection)

    def is_game_window_valid(self) -> bool:
        """Check if the game window mode and size are valid.

        :return: True if valid, False otherwise
        :rtype: bool
        """
        if self.window.is_title_bar_exist():
            logger.info(t("app.fb.window_mode_detected"))
        if self.window.is_size_supported():
            logger.info(t("app.fb.supported_window_size"))
            return True
        logger.critical(t("app.fb.error.window_mode"))
        logger.critical(
            t("app.fb.error.unsupported_size", size=self.window.get_resolution_str())
        )
        return False

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle exit and quit events.

        :param key: The key that was released.
        :type key: keyboard.KeyCode
        """
        if utils.key_matches(key, self.cfg.KEY.FRICTION_BRAKE_QUIT):
            self.friction_brake.monitor_process.terminate()
            return False
        if utils.key_matches(key, self.cfg.KEY.FRICTION_BRAKE_RESET):
            self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

    def start(self):
        """Wrapper method that handle window activation and result display."""
        listener = keyboard.Listener(on_release=self._on_release)
        listener.start()
        self.window.activate_game_window()
        self.friction_brake.monitor_process.start()
        self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

        while listener.is_alive():
            sleep(THREAD_CHECK_DELAY)

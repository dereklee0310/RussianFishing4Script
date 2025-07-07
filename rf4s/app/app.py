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
import requests
from abc import ABC, abstractmethod
from datetime import datetime
from multiprocessing import Lock
from pathlib import Path
from socket import gaierror
from time import sleep

import pyautogui as pag
from pynput import keyboard
from rich import box, print
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s import config, utils
from rf4s.component.friction_brake import FrictionBrake
from rf4s.controller.detection import Detection
from rf4s.controller.player import Player
from rf4s.controller.timer import Timer, add_jitter
from rf4s.controller.window import Window
from rf4s.result import BotResult, CraftResult, HarvestResult, Result
from rf4s.app.core import logger

# When running as an executable, use sys.executable to find the config.yaml.
# This file is not included during compilation and could not be resolved automatically
# by Nuitka.
if utils.is_compiled():
    ROOT = Path(sys.executable).parent
else:
    ROOT = Path(__file__).resolve().parents[2]

ANIMATION_DELAY = 0.5
CRAFT_DELAY = 4.0
LOOP_DELAY = 0.5
BIAS = 1e-6


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

        table = Table(title="Running Result", box=box.HEAVY, show_header=False)
        for name, value in self.result.as_dict().items():
            table.add_row(name, str(value))
        print(table)


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
        self.validate_smtp_connection()
        self.validate_discord_webhook()
        self.validate_telegram_bot()
        self.validate_game_window()
        self.validate_electro_mode()

        self.cfg.freeze()  # cfg is done now

        table = Table(title="Settings", show_header=False, box=box.HEAVY, min_width=36)
        table.add_row("Launch options", " ".join(sys.argv[1:]))
        for k, v in self.cfg.PROFILE.items():
            if k != "DESCRIPTION":
                table.add_row(k, str(v))
        print(table)
        if self.cfg.PROFILE.DESCRIPTION:
            print(Panel.fit(f"[not bold]You're now using:[/not bold] {self.cfg.PROFILE.DESCRIPTION}", style="bold"))
        print(f"Press {self.cfg.KEY.QUIT} to quit.")

        self.result = BotResult()
        self.window = Window()
        self.player = Player(
            self.cfg, Timer(self.cfg), Detection(cfg, self.window), self.result
        )

    def validate_smtp_connection(self) -> bool:
        """Verify SMTP server connection for email notifications.

        Tests the connection to the configured SMTP server using stored
        credentials if email notifications are enabled.

        :return: Whether the SMTP configuration is valid or not needed.
        :rtype: bool
        """
        if not self.cfg.ARGS.EMAIL or not self.cfg.BOT.SMTP_VERIFICATION:
            return
        logger.info("Verifying SMTP connection")

        try:
            with smtplib.SMTP_SSL(self.cfg.BOT.NOTIFICATION.SMTP_SERVER, 465) as server:
                server.login(
                    self.cfg.BOT.NOTIFICATION.EMAIL, self.cfg.BOT.NOTIFICATION.PASSWORD
                )
        except smtplib.SMTPAuthenticationError:
            logger.critical(
                "Invalid email address or app password\n"
                "Check BOT.NOTIFICATION.EMAIL\n"
                "Check BOT.NOTIFICATION.PASSWORD\n"
                "For Gmail users, please refer to: "
                "https://support.google.com/accounts/answer/185833\n"
            )
            utils.safe_exit()
        except (TimeoutError, gaierror):
            logger.critical("Invalid BOT.NOTIFICATION.SMTP_SERVER or connection timed out")
            utils.safe_exit()

    def validate_discord_webhook(self) -> bool:
        if not self.cfg.ARGS.DISCORD or self.cfg.BOT.NOTIFICATION.DISCORD_WEBHOOK_URL:
            return
        logger.critical(
            "BOT.NOTIFICATION.DISCORD_WEBHOOK_URL is not set\n"
            "To make a webhook, please refer to "
            "https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks"
        )
        utils.safe_exit()

    def validate_telegram_bot(self):
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
            logger.critical("Invalid BOT.NOTIFICATION.TELEGRAM_BOT_TOKEN")
            valid = False
        if self.cfg.BOT.NOTIFICATION.TELEGRAM_CHAT_ID == -1:
            logger.critical("BOT.NOTIFICATION.TELEGRAM_CHAT_ID is not set")
            valid = False
        if not valid:
            logger.critical(
                "Please refer to: "
                "https://gist.github.com/nafiesl/4ad622f344cd1dc3bb1ecbe468ff9f8a",
            )
            utils.safe_exit()

    def validate_profile(self, profile_name: str) -> bool:
        """Check if a profile configuration is valid and complete.

        :param profile_name: Name of the profile to validate.
        :type profile_name: str
        :return: Whether the profile is valid.
        :rtype: bool
        """
        if profile_name not in self.cfg.PROFILE:
            logger.critical("Invalid profile name: '%s'", profile_name)
            utils.safe_exit()

        mode = self.cfg.PROFILE[profile_name].MODE
        if mode.upper() not in self.cfg.PROFILE:
            logger.critical("Invalid mode: '%s'", mode)
            utils.safe_exit()

        expected_keys = set(self.cfg.PROFILE[mode.upper()])
        actual_keys = set(self.cfg.PROFILE[profile_name])

        invalid_keys = actual_keys - expected_keys
        missing_keys = expected_keys - actual_keys

        if invalid_keys or missing_keys:
            for key in invalid_keys:
                logger.warning("Invalid setting: 'PROFILE.%s.%s'", profile_name, key)
            for key in missing_keys:
                logger.warning("Missing setting: 'PROFILE.%s.%s'", profile_name, key)

    def display_profiles(self) -> None:
        """Display a table of available profiles for user selection.

        Shows a formatted table with profile IDs and names.
        """
        table = Table(
            title="Select a profile to start ⚙️",
            box=box.HEAVY,
            show_header=False,
            min_width=36,
        )
        for i, profile in enumerate(self.cfg.PROFILE):
            table.add_row(f"{i:>2}. {profile}")
        print(table)

    def get_pid(self) -> None:
        """Prompt the user to enter a profile ID and validate the input.

        Continuously prompts until a valid profile ID is entered or the
        user chooses to quit.
        """
        print("Enter profile id to use, h to see help message, q to quit:")

        while True:
            user_input = input(">>> ")
            if user_input.isdigit() and 0 <= int(user_input) < len(self.cfg.PROFILE):
                break
            if user_input == "q":
                print("Bye.")
                sys.exit()
            if user_input == "h":
                self.parser.print_help()
                continue
            utils.print_error("Invalid profile id, please try again.")

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

        self.validate_profile(profile_name)

        # Merge args.opts here because we can only overwrite cfg.PROFILE
        self.cfg.merge_from_list(self.args.opts)

        mode = self.cfg.PROFILE[profile_name].MODE.upper()
        user_profile = CN({"NAME": profile_name}, new_allowed=True)
        user_profile.merge_from_other_cfg(self.cfg.PROFILE[mode])
        user_profile.merge_from_other_cfg(self.cfg.PROFILE[profile_name])
        self.cfg.PROFILE = user_profile  # Overwrite default profiles

    def merge_args_to_cfg(self) -> None:
        """Must be called after the profile is correctly configured."""
        # Merge profile-level launch options
        if self.cfg.PROFILE.LAUNCH_OPTIONS:
            sys.argv += shlex.split(self.cfg.PROFILE.LAUNCH_OPTIONS)
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
            logger.info("Window mode detected. Don't move the game window")
        if self.window.is_size_supported():
            logger.info("Supported window size. Don't change the game window size")
            return

        if self.cfg.PROFILE.MODE in ("telescopic", "bolognese"):
            logger.critical(
                "Fishing mode '%s' doesn't support window size '%s'",
                self.cfg.PROFILE.MODE,
                self.window.get_resolution_str(),
            )
            utils.safe_exit()

        logger.warning('Window mode must be "Borderless windowed" or "Window mode"')
        logger.warning(
            "Unsupported window size '%s'. Use '2560x1440', '1920x1080' or '1600x900'",
            self.window.get_resolution_str(),
        )
        logger.error(
            "Snag detection will be disabled\n"
            "Spooling detection will be disabled\n"
            "Auto friction brake will be disabled\n"
        )

        self.cfg.ARGS.FRICTION_BRAKE = False
        self.cfg.BOT.SNAG_DETECTION = False
        self.cfg.BOT.SPOOLING_DETECTION = False

    def validate_electro_mode(self):
        """Display helpful information about the current configuration.

        Checks configuration compatibility and prints warnings for
        potential issues.
        """
        if not self.cfg.ARGS.ELECTRO:
            return

        if self.cfg.PROFILE.MODE in ("pirk", "elevator"):
            logger.info("Electric mode detected. Make sure you're using Electro Raptor")
        else:
            logger.error(
                "Electric mode is not compatible with mode '%s'\n"
                "Electric mode will be disabled",
                self.cfg.PROFILE.MODE,
            )
            self.cfg.ARGS.ELECTRO = False

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Monitor user's keystrokes and convert a key press to a CTRL_C_EVENT.

        :param key: The key that was released.
        :type key: keyboard.KeyCode

        Exits the application when the configured quit key is pressed.
        """
        # Trigger CTRL_C_EVENT, which will be caught in start() to simulate pressing
        # CTRL-C to terminate the script.
        if key == keyboard.KeyCode.from_char(self.cfg.KEY.QUIT):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            sys.exit()

    def start(self) -> None:
        """Start the fishing automation process.

        Sets up all required components, activates the game window,
        registers key listeners, and begins the fishing automation.
        Handles termination and displays result.
        """
        if self.cfg.KEY.QUIT != "'CTRL-C'":
            listener = keyboard.Listener(on_release=self._on_release)
            listener.start()
        self.window.activate_game_window()
        try:
            self.player.start_fishing()
        except KeyboardInterrupt:
            pass

        self.display_result()
        if self.cfg.ARGS.DATA:
            self.player.timer.save_data()

    def display_result(self):
        # TODO: BUILT THIS FROM RESULT
        print(
            self.player.build_result_table(
                self.player.build_result_dict("Terminated by user")
            )
        )


class CraftApp(App):
    """Main application class for automating crafting.

    This class manages the configuration, detection, and execution of the crafting
    process. It tracks the number of successful and failed crafts, as well as the
    total number of materials used.
    """

    def __init__(self, cfg, args, parser):
        super().__init__(cfg, args, parser)
        sys.argv += shlex.split(self.cfg.CRAFT.LAUNCH_OPTIONS)
        self.args = parser.parse_args()
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(args.opts)
        self.cfg.freeze()

        table = Table(title="Settings", show_header=False, box=box.HEAVY, min_width=36)
        table.add_row("Launch options", " ".join(sys.argv[1:]))
        print(table)

        self.result = CraftResult()
        self.window = Window()
        self.detection = Detection(self.cfg, self.window)

    def move_cursor_to_make_button(self) -> None:
        """Move the cursor to the make button position.

        This method uses the Detection class to find the position of the make button
        and moves the cursor to that position.
        """
        make_button_position = self.detection.get_make_button_position()
        if make_button_position is None:
            logger.critical(
                "Make button not found, please set the interface scale to "
                "1x or move your mouse around"
            )
            self.window.activate_script_window()
            utils.safe_exit()
        pag.moveTo(make_button_position)

    def craft_item(self, accept_key: str) -> None:
        """Craft an item.

        :param craft_delay: Delay in seconds before accepting the crafted item.
        :type craft_delay: float
        :param accept_delay: Delay in seconds after accepting the crafted item.
        :type accept_delay: float
        :param accept_key: Key to press after accepting the crafted item.
        :type accept_key: str
        """
        logger.info("Crafting item")
        pag.click()
        sleep(add_jitter(CRAFT_DELAY))
        self.result.material += 1
        while True:
            if self.detection.is_operation_success():
                logger.info("Crafting successed")
                self.result.succes += 1
                break

            if self.detection.is_operation_failed():
                logger.warning("Crafting failed")
                self.result.fail += 1
                break
            sleep(add_jitter(LOOP_DELAY))
        pag.press(accept_key)
        sleep(add_jitter(LOOP_DELAY))

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
        :type key: keyboard.KeyCode
        """
        if key == keyboard.KeyCode.from_char(self.cfg.KEY.QUIT):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            sys.exit()

    def start(self) -> None:
        """Main loop for crafting items.

        Executes the primary loop for crafting items until materials are exhausted or
        the crafting limit is reached. Supports fast crafting mode and discarding items.
        """
        if self.cfg.KEY.QUIT != "'CTRL-C'":
            listener = keyboard.Listener(on_release=self._on_release)
            listener.start()

        try:
            print(f"Press {self.cfg.KEY.QUIT} to quit.")
            logger.warning("This might get you banned, use at your own risk")
            logger.warning("Use Razor or Logitech macros instead")
            random.seed(datetime.now().timestamp())
            accept_key = "backspace" if self.cfg.ARGS.DISCARD else "space"
            self.window.activate_game_window()
            self.move_cursor_to_make_button()
            while True:
                if not self.detection.is_material_complete():
                    logger.critical("Running out of materials")
                    break
                if self.result.succes == self.cfg.ARGS.CRAFT_LIMIT:
                    logger.info("Crafting limit reached")
                    break
                self.craft_item(accept_key)
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

        sys.argv += shlex.split(self.cfg.MOVE.LAUNCH_OPTIONS)
        self.args = parser.parse_args()
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(args.opts)
        self.cfg.freeze()

        print(
            f"Press {self.cfg.KEY.MOVE_PAUSE} to pause, "
            f"{self.cfg.KEY.MOVE_QUIT} to quit.",
        )

        self.result = Result()
        self.window = Window()
        self.w_key_pressed = True

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
        :type key: keyboard.KeyCode
        """
        if key == keyboard.KeyCode.from_char(self.cfg.KEY.MOVE_QUIT):
            sys.exit()
        elif key == keyboard.KeyCode.from_char(self.cfg.KEY.MOVE_PAUSE):
            if self.w_key_pressed:
                self.w_key_pressed = False
                return
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
        listener.join()  # Blocking listener loop


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

        sys.argv += shlex.split(self.cfg.HARVEST.LAUNCH_OPTIONS)
        self.args = parser.parse_args()
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(args.opts)
        self.cfg.freeze()

        table = Table(title="Settings", show_header=False, box=box.HEAVY, min_width=36)
        table.add_row("Launch options", " ".join(sys.argv[1:]))
        table.add_row("Power saving", str(self.cfg.HARVEST.POWER_SAVING))
        table.add_row("Check delay", str(self.cfg.HARVEST.CHECK_DELAY))
        table.add_row("Energy threshold", str(self.cfg.STAT.ENERGY_THRESHOLD))
        table.add_row("Hunger threshold", str(self.cfg.STAT.HUNGER_THRESHOLD))
        table.add_row("Comfort threshold", str(self.cfg.STAT.COMFORT_THRESHOLD))
        print(table)
        print(f"Press {self.cfg.KEY.QUIT} to quit.")

        self.result = HarvestResult()
        self.timer = Timer(self.cfg)
        self.window = Window()
        self.detection = Detection(self.cfg, self.window)

    def harvest_baits(self) -> None:
        """Harvest baits using shovel/spoon.

        The digging tool should be pulled out before calling this method. Waits for
        harvest success and presses the spacebar to complete the process.
        """
        logger.info("Harvesting baits")
        pag.click()
        while not self.detection.is_harvest_success():
            sleep(add_jitter(LOOP_DELAY))
        pag.press("space")
        logger.info("Baits harvested succussfully")
        sleep(ANIMATION_DELAY)

    def refill_player_stats(self) -> None:
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

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
        :type key: keyboard.KeyCode
        """
        # Trigger CTRL_C_EVENT, which will be caught in start() to simulate pressing
        # CTRL-C to terminate the script.
        if key == keyboard.KeyCode.from_char(self.cfg.KEY.QUIT):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            sys.exit()

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
        sleep(add_jitter(ANIMATION_DELAY))

    def start(self) -> None:
        """Wrapper method that handle window activation and result display."""
        if self.cfg.KEY.QUIT != "'CTRL-C'":
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
                    logger.info("Energy is not high enough")

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


class CalculateApp:
    def get_tackle_stats(self):
        """Get actual stats of reel and leader based on their wears.

        Prompts the user for input and calculates the true max drag and load capacity
        after accounting for wear.

        :return: A tuple containing the true max drag and true load capacity.
        :rtype: tuple[float, float]
        """
        prompts = (
            "Reel's max drag (kg)",
            "Reel's friction brake wear (%)",
            "Leader's load capacity (kg)",
            "Leader's wear (%)",
        )

        while True:
            restart = False
            stats = []
            for prompt in prompts:
                validated_input = self.get_validated_input(prompt)
                if validated_input is None:
                    restart = True
                    break
                stats.append(validated_input)

            if restart:
                continue

            max_drag, friction_brake_wear, leader_load_capacity, leader_wear = stats
            true_max_drag = max_drag * (100 - friction_brake_wear) / 100
            true_load_capacity = leader_load_capacity * (100 - leader_wear) / 100
            return true_max_drag, true_load_capacity

    def get_validated_input(self, prompt: str) -> float | None:
        """Get validated input from the user.

        Prompts the user for input and validates it. Supports quitting and restarting.

        :param prompt: The prompt message to display to the user.
        :type prompt: str
        :return: The validated input as a float, or None if the user chooses to restart.
        :rtype: float or None
        """
        while True:
            user_input = Prompt.ask(prompt)
            if user_input == "q":
                print("Bye.")
                sys.exit()
            if user_input == "r":
                return None

            try:
                return float(user_input)
            except ValueError:
                utils.print_error("Invalid input. Please enter a number.")

    def start(self):
        """Main function to run the friction brake calculation.

        Prompts the user for input, calculates the result, and displays them in a table.
        """
        print("Please enter your tackle's stats, type q to quit, r to restart:")
        while True:
            max_drag, load_capacity = self.get_tackle_stats()
            max_friction_brake = int(
                min(load_capacity * 30 / (max_drag + BIAS) - 1, 29)
            )
            max_tension = max_drag * max_friction_brake / 30

            table = Table(
                "Result",
                title="Your tackle's real stats 🎣",
                box=box.HEAVY,
                show_header=False,
                min_width=36,
            )
            table.add_row("Reel's true max drag", f"{max_drag:.2f} kg")
            table.add_row("Leader's true load capacity", f"{load_capacity:.2f} kg")
            table.add_row("Friction brake tension", f"{max_tension:.2f} kg")
            table.add_row("Maximum friction brake to use", f"{max_friction_brake}")
            print(table)


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
        sys.argv += shlex.split(self.cfg.FRICTION_BRAKE.LAUNCH_OPTIONS)
        self.args = parser.parse_args()
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        self.cfg.merge_from_list(args.opts)
        self.cfg.freeze()

        table = Table(title="Settings", show_header=False, box=box.HEAVY, min_width=36)
        table.add_row("Launch options", " ".join(sys.argv[1:]))
        table.add_row("Initial friction brake", str(self.cfg.FRICTION_BRAKE.INITIAL))
        table.add_row("Start delay", str(self.cfg.FRICTION_BRAKE.START_DELAY))
        table.add_row("Increase delay", str(self.cfg.FRICTION_BRAKE.INCREASE_DELAY))
        table.add_row("Sensitivity", self.cfg.FRICTION_BRAKE.SENSITIVITY)
        print(table)

        print(
            f"Press {self.cfg.KEY.FRICTION_BRAKE_RESET} to reset friction brake, "
            f"{self.cfg.KEY.FRICTION_BRAKE_QUIT} to quit."
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
            logger.info("Window mode detected. don't move the game window")
        if self.window.is_size_supported():
            logger.info("Supported window size. Don't change the game window size")
            return True
        logger.critical('Window mode must be "Borderless windowed" or "Window mode"')
        logger.critical(
            "Unsupported window size '%s', use '2560x1440', '1920x1080' or '1600x900'",
            self.window.get_resolution_str(),
        )
        return False

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle exit and quit events.

        :param key: The key that was released.
        :type key: keyboard.KeyCode
        """
        if key == keyboard.KeyCode.from_char(self.cfg.KEY.FRICTION_BRAKE_QUIT):
            self.friction_brake.monitor_process.terminate()
            sys.exit()
        if key == keyboard.KeyCode.from_char(self.cfg.KEY.FRICTION_BRAKE_RESET):
            self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

    def start(self):
        """Wrapper method that handle window activation and result display."""
        listener = keyboard.Listener(on_release=self._on_release)
        listener.start()
        self.window.activate_game_window()
        self.friction_brake.monitor_process.start()
        listener.join()

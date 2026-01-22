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
import time
import threading
from typing import Optional
import math
import numpy as np
from noise import pnoise1
import pyautogui as pag
import pydirectinput as pdi
import requests
from pynput import keyboard
from rich import box, print
from rich.prompt import Prompt
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s import config, exceptions, utils
from rf4s.app.core import logger
from rf4s.component.friction_brake import FrictionBrake
from rf4s.config import load_cfg
from rf4s.controller.detection import Detection
from rf4s.controller.player import Player
from rf4s.controller.timer import Timer, add_jitter
from rf4s.controller.window import Window
import win32gui
from rf4s.result import BotResult, CraftResult, HarvestResult, Result

BIAS = 1e-6
ANIMATION_DELAY = 0.5
THREAD_CHECK_DELAY = 0.5
LOOP_DELAY = 1
CRAFT_DELAY = 4.0
MAX_FRICTION_BRAKE = 30


def timer_sleep(duration: float, interval: float = 0.05) -> None:
    """Sleep by looping in small intervals.

    This splits a longer blocking sleep into many short sleeps so the program
    yields more frequently and other threads or user actions (e.g., moving the
    mouse) remain responsive while waiting.

    Args:
        duration: Total time to wait in seconds.
        interval: Small-sleep interval in seconds. Lower -> more responsive.
    """
    end = time.perf_counter() + float(duration)
    while time.perf_counter() < end:
        time.sleep(interval)


class HumanMouse:
    """Human-like mouse movement using numpy and Perlin noise.

    This implementation assumes `numpy` and `noise.pnoise1` are available.
    It generates a cubic Bezier trajectory with easing and adds Perlin noise
    for small jitter.
    """
    def __init__(self):
        self.noise_seed = random.randint(0, 100)

    def _ease_out_quart(self, x: float) -> float:
        return 1 - pow(1 - x, 4)

    def _get_bezier_point(self, t: float, start: np.ndarray, control1: np.ndarray, control2: np.ndarray, end: np.ndarray) -> np.ndarray:
        return (
            (1 - t) ** 3 * start
            + 3 * (1 - t) ** 2 * t * control1
            + 3 * (1 - t) * t ** 2 * control2
            + t ** 3 * end
        )

    def move_in_radius(
        self,
        radius: float = 100.0,
        min_duration: float = 0.5,
        max_duration: float = 1.5,
        pivot: Optional[tuple] = None,
        rotate: bool = False,
    ) -> None:
        start_pos = np.array(pag.position(), dtype=float)

        # If rotate is requested and a pivot is provided, generate a circular
        # If rotate is requested and a pivot is provided, produce a few short
        # symmetric micro-movements around the pivot so the camera stays
        # roughly pointed at one spot but occasionally shifts like a human hand.
        if rotate and pivot is not None:
            pivot_x, pivot_y = float(pivot[0]), float(pivot[1])
            # number of small micro-movements per wiggle cycle
            micro_moves = random.choice([1, 1, 2])
            # keep each micro move short and tight
            max_rad = max(1.0, radius * 0.35)
            for _ in range(micro_moves):
                # small random offset around pivot
                ang = random.uniform(0, 2 * math.pi)
                dist = random.uniform(max_rad * 0.25, max_rad)
                offset = np.array([math.cos(ang) * dist, math.sin(ang) * dist])

                # durations for out and return movements
                dur_out = random.uniform(min_duration * 0.5, min(max_duration, min_duration * 1.2))
                dur_back = dur_out * random.uniform(0.9, 1.2)

                # control points for smooth bezier from pivot -> pivot+offset
                start_pt = np.array([pivot_x, pivot_y])
                end_pt = start_pt + offset
                normal_vec = np.array([-offset[1], offset[0]])
                curvature = random.uniform(-0.15, 0.15)
                control1 = start_pt + (end_pt - start_pt) * 0.3 + normal_vec * curvature
                control2 = start_pt + (end_pt - start_pt) * 0.7 + normal_vec * curvature

                # perform outward movement
                steps_out = max(1, int(dur_out * 80))
                noise_offset_x = random.uniform(0, 100)
                noise_offset_y = random.uniform(0, 100)
                prev = np.array(pag.position(), dtype=float)
                t0 = time.time()
                for i in range(steps_out + 1):
                    tt = i / steps_out
                    te = self._ease_out_quart(tt)
                    base = self._get_bezier_point(te, start_pt, control1, control2, end_pt)
                    noise_scale = 4 * (1 - te)
                    jx = pnoise1(tt * 18 + noise_offset_x) * noise_scale
                    jy = pnoise1(tt * 18 + noise_offset_y) * noise_scale
                    fx = base[0] + jx
                    fy = base[1] + jy
                    dx = int(round(fx - prev[0]))
                    dy = int(round(fy - prev[1]))
                    pdi.moveRel(dx, dy, relative=True)
                    prev[0] += (fx - prev[0])
                    prev[1] += (fy - prev[1])
                    elapsed = time.time() - t0
                    target = tt * dur_out
                    if target > elapsed:
                        timer_sleep(target - elapsed)

                # perform return movement (end_pt -> start_pt)
                steps_back = max(1, int(dur_back * 80))
                noise_offset_x = random.uniform(0, 100)
                noise_offset_y = random.uniform(0, 100)
                t1 = time.time()
                for i in range(steps_back + 1):
                    tt = i / steps_back
                    te = self._ease_out_quart(tt)
                    base = self._get_bezier_point(te, end_pt, control2, control1, start_pt)
                    noise_scale = 4 * (1 - te)
                    jx = pnoise1(tt * 18 + noise_offset_x) * noise_scale
                    jy = pnoise1(tt * 18 + noise_offset_y) * noise_scale
                    fx = base[0] + jx
                    fy = base[1] + jy
                    dx = int(round(fx - prev[0]))
                    dy = int(round(fy - prev[1]))
                    pdi.moveRel(dx, dy, relative=True)
                    prev[0] += (fx - prev[0])
                    prev[1] += (fy - prev[1])
                    elapsed = time.time() - t1
                    target = tt * dur_back
                    if target > elapsed:
                        timer_sleep(target - elapsed)

            # finished micro-moves; return without executing the non-rotate path
            return
        else:
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(radius * 0.3, radius)
            offset = np.array([math.cos(angle) * dist, math.sin(angle) * dist])
            target_pos = start_pos + offset

            dist_vec = target_pos - start_pos
            normal_vec = np.array([-dist_vec[1], dist_vec[0]])

            curvature = random.uniform(-0.3, 0.3)

            control1 = start_pos + dist_vec * 0.2 + normal_vec * curvature
            control2 = start_pos + dist_vec * 0.8 + normal_vec * curvature
            use_circle = False

        duration = random.uniform(min_duration, max_duration)
        # Use slightly higher internal step rate for smoother small motions
        steps = max(1, int(duration * 80))

        noise_offset_x = random.uniform(0, 100)
        noise_offset_y = random.uniform(0, 100)
        # Track previous position so we send relative deltas to moveRel().
        prev_pos = start_pos.copy()
        loop_start = time.time()
        for step in range(steps + 1):
            t = step / steps
            t_eased = self._ease_out_quart(t)
            # compute bezier point toward the target position
            current_base = self._get_bezier_point(
                t_eased, start_pos, control1, control2, target_pos
            )

            # Reduce jitter amplitude for more subtle, human-like movement.
            noise_scale = 6 * (1 - t_eased)
            # Slightly higher frequency gives smaller micro-movements
            jitter_x = pnoise1(t * 18 + noise_offset_x) * noise_scale
            jitter_y = pnoise1(t * 18 + noise_offset_y) * noise_scale

            final_x = current_base[0] + jitter_x
            final_y = current_base[1] + jitter_y

            # Compute relative delta from the last sent position and move relatively.
            delta_x = final_x - prev_pos[0]
            delta_y = final_y - prev_pos[1]

            # Use integer deltas for the move call; pyautogui/pydirectinput accept ints.
            try:
                dx = int(round(delta_x))
                dy = int(round(delta_y))
            except Exception:
                dx = int(delta_x)
                dy = int(delta_y)

            pdi.moveRel(dx, dy, relative=True)

            # Update previous position to the new final position
            prev_pos[0] += delta_x
            prev_pos[1] += delta_y

            elapsed = time.time() - loop_start
            target_time = t * duration
            if target_time > elapsed:
                timer_sleep(target_time - elapsed)


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
        # Background thread management
        self._bg_threads = []
        self._stop_event = threading.Event()

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

        result = Table(title="Running Result", box=box.HEAVY, show_header=False)
        for name, value in self.result.as_dict().items():
            result.add_row(name, str(value))
        print(result)

    def start_background_task(self, name: str, target, *args, daemon: bool = True) -> threading.Thread:
        """Start and track a background thread task.

        The thread will be recorded in self._bg_threads and can be stopped by
        setting self._stop_event (useful when shutting down).
        """
        t = threading.Thread(target=target, args=args, name=name, daemon=daemon)
        self._bg_threads.append(t)
        t.start()
        return t

    def stop_background_tasks(self, timeout: Optional[float] = None) -> None:
        """Signal background tasks to stop and join them.

        Background tasks should check self._stop_event.is_set() periodically and exit.
        """
        # Signal all background threads to stop and wait for them to finish.
        self._stop_event.set()
        for t in self._bg_threads:
            try:
                t.join(timeout)
            except Exception:
                # ignore join errors
                pass
        # Clear tracked threads and reset stop event so tasks can be restarted later.
        self._bg_threads = []
        try:
            # allow reuse: clear the stop flag for next run
            self._stop_event.clear()
        except Exception:
            # If clearing fails, create a new Event to avoid leaving it set
            self._stop_event = threading.Event()


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
            title="Settings", show_header=False, box=box.HEAVY, min_width=36
        )
        settings.add_row("LAUNCH OPTIONS (FINAL)", " ".join(sys.argv[1:]))
        for k, v in self.cfg.PROFILE.items():
            if k != "DESCRIPTION":
                settings.add_row(k, str(v))
        print(settings)
        if self.cfg.PROFILE.DESCRIPTION:
            utils.print_description_box(self.cfg.PROFILE.DESCRIPTION)
        utils.print_usage_box(
            f"Press {self.cfg.KEY.PAUSE} to pause, {self.cfg.KEY.QUIT} to quit."
        )

    def validate_smtp(self) -> None:
        """Verify SMTP server connection for email notifications.

        Tests the connection to the configured SMTP server using stored
        credentials if email notifications are enabled.
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
            logger.critical(
                "Invalid BOT.NOTIFICATION.SMTP_SERVER or connection timed out"
            )
            utils.safe_exit()

    def validate_discord(self) -> None:
        if not self.cfg.ARGS.DISCORD or self.cfg.BOT.NOTIFICATION.DISCORD_WEBHOOK_URL:
            return
        logger.critical(
            "BOT.NOTIFICATION.DISCORD_WEBHOOK_URL is not set\n"
            "To make a webhook, please refer to "
            "https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks"
        )
        utils.safe_exit()

    def validate_miaotixing(self) -> None:
        if not self.cfg.ARGS.MIAOTIXING or self.cfg.BOT.NOTIFICATION.MIAO_CODE:
            return
        logger.critical("BOT.NOTIFICATION.MIAO_CODE is not set.")
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

    def validate_profile(self, profile_name: str) -> None:
        """Check if a profile configuration is valid and complete.

        :param profile_name: Name of the profile to validate.
        :type profile_name: str
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
        profiles = Table(
            title="Select a profile to start ⚙️",
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
        utils.print_usage_box("Enter profile id to use, q to quit.")

        while True:
            user_input = input(">>> ")
            if user_input.isdigit() and 0 <= int(user_input) < len(self.cfg.PROFILE):
                break
            if user_input == "q":
                print("Bye.")
                sys.exit()
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
        self.merge_default_to_profile(profile_name)

    def merge_default_to_profile(self, profile_name) -> None:
        self.validate_profile(profile_name)
        mode = self.cfg.PROFILE[profile_name].MODE.upper()
        
        user_profile = CN({"NAME": profile_name}, new_allowed=True)
        user_tolerance = CN({"NAME": "TOLERANCE." + profile_name}, new_allowed=True)

        user_profile.merge_from_other_cfg(self.cfg.PROFILE[mode])
        user_profile.merge_from_other_cfg(self.cfg.PROFILE[profile_name])

        # Merge tolerance profiles if they exist. Config may not include
        # tolerances for every profile/mode, so guard against missing keys.
        if hasattr(self.cfg, "TOLERANCE"):
            tol_root = getattr(self.cfg.TOLERANCE, "PROFILE", None)
            if isinstance(tol_root, CN):
                if mode in tol_root:
                    user_tolerance.merge_from_other_cfg(tol_root[mode])
                if profile_name in tol_root:
                    user_tolerance.merge_from_other_cfg(tol_root[profile_name])

        self.cfg.PROFILE = user_profile  # Overwrite default profiles
        self.cfg.TOLERANCE.PROFILE = user_tolerance  # Overwrite default tolerance profiles

    def merge_args_to_cfg(self) -> None:
        """Must be called after the profile is correctly configured."""
        if len(self.args.opts) % 2:
            logger.error("Invalid launch options: '%s'\n"
                "These arguments are used for config override: '%s'\n",
                " ".join(sys.argv[1:]), " ".join(self.args.opts)
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
            logger.info("Window mode detected. Don't move the game window")
        if self.window.is_size_supported():
            logger.info("Supported window size. Don't change the game window size")
            return

        window_resolution = self.window.get_resolution_str()
        if window_resolution == "0x0":
            logger.critical("'Fullscreen mode' is not supported")
            utils.safe_exit()

        if self.cfg.PROFILE.MODE in ("telescopic", "bolognese"):
            logger.critical(
                "Fishing mode '%s' doesn't support window size '%s'",
                self.cfg.PROFILE.MODE,
                self.window.get_resolution_str(),
            )
            utils.safe_exit()

        logger.warning(
            "Unsupported window size '%s'\n"
            "Supported window size: '2560x1440', '1920x1080' or '1600x900'\n"
            "Will search the image on the screen instead of the game window",
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

    def validate_favorite_icon(self):
        if (
            self.cfg.ARGS.COFFEE
            or self.cfg.ARGS.REFILL
            or self.cfg.ARGS.LURE
            or self.cfg.ARGS.DRY_MIX
            or self.cfg.ARGS.GROUNDBAIT
            or self.cfg.ARGS.PVA
        ):
            logger.info(
                "Some features require you to add the item to your favorites, "
                "make sure you have done so"
            )

    def validate_screenshot_notification(self):
        if self.cfg.ARGS.SCREENSHOT and self.cfg.ARGS.MIAOTIXING:
            logger.warning(
                "Miaotixing doesn't support image message, no screenshot will be sent"
            )

    def validate_spool_detection(self):
        if self.cfg.ARGS.RAINBOW is None:
            logger.warning(
                "Default retrieval detection mode detected, fully spool your reel"
            )

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Monitor user's keystrokes and convert a key press to a CTRL_C_EVENT.

        :param key: The key that was released.
        :type key: keyboard.KeyCode

        Exits the application when the configured quit key is pressed.
        """
        # Trigger CTRL_C_EVENT, which will be caught in start() to simulate pressing
        # CTRL-C to terminate the script.
        key = str(key).lower()
        if key == str(keyboard.KeyCode.from_char(self.cfg.KEY.QUIT)):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            return False
        if key == str(keyboard.KeyCode.from_char(self.cfg.KEY.PAUSE)):
            logger.info("Pausing the bot")
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            self.paused = True
            logger.info("Bot paused")  # Don't remove this! It messes with signal?
            return False

    def _pause_wait(self, key: keyboard.KeyCode) -> None:
        key = str(key).lower()
        if key == str(keyboard.KeyCode.from_char(self.cfg.KEY.PAUSE)):
            self.paused = False
            return False

    def _mouse_wiggle(self) -> None:
        """Background task: perform human-like small movements periodically.

        Uses the HumanMouse helper. The task checks self._stop_event to exit.
        """
        mover = HumanMouse()
        # Read settings from config BOT.MOUSE_WIGGLE (fallbacks provided)
        cfg_mw = getattr(self.cfg.BOT, "MOUSE_WIGGLE", None)
        if cfg_mw is not None:
            try:
                radius = float(getattr(cfg_mw, "RADIUS", 80))
            except Exception:
                radius = 80
            try:
                min_dur = float(getattr(cfg_mw, "MIN_DURATION", 0.3))
                max_dur = float(getattr(cfg_mw, "MAX_DURATION", 1.0))
            except Exception:
                min_dur, max_dur = 0.3, 1.0
            try:
                interval = float(getattr(cfg_mw, "INTERVAL", 5.0))
            except Exception:
                interval = 5.0
        else:
            radius = 80
            min_dur, max_dur = 0.3, 1.0
            interval = 5.0

        while not self._stop_event.is_set():
            # Do not wiggle while the bot is paused
            if getattr(self, "paused", False):
                logger.debug("mouse_wiggle: skipped (paused)")
                timer_sleep(THREAD_CHECK_DELAY)
                continue

            # Ensure the game window is the foreground window. If not, skip wiggle
            try:
                game_hwnd = win32gui.FindWindow(None, self.window.game_title)
                fg = win32gui.GetForegroundWindow()
                if game_hwnd == 0 or fg != game_hwnd:
                    # game window not found or not focused — wait and retry
                    logger.debug("mouse_wiggle: skipped (game not foreground or not found)")
                    timer_sleep(interval)
                    continue
            except Exception:
                # If any window API fails, skip movement this cycle
                logger.debug("mouse_wiggle: win32 check failed, skipping this cycle")
                timer_sleep(interval)
                continue

            try:
                logger.debug("mouse_wiggle: performing move radius=%s min=%s max=%s", radius, min_dur, max_dur)
                # Compute pivot as center of the game window so motion becomes
                # a rotation-like movement around that center.
                try:
                    base_x, base_y, w, h = self.window.get_box()
                    pivot = (base_x + w / 2, base_y + h / 2)
                except Exception:
                    pivot = None
                mover.move_in_radius(
                    radius=radius, min_duration=min_dur, max_duration=max_dur, pivot=pivot, rotate=True
                )
            except Exception:
                # Ignore movement errors
                pass
            # allow a short pause between human-like moves
            timer_sleep(interval)

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
            # Optional background mouse wiggle: enable by setting ARGS.MOUSE_WIGGLE to True
            try:
                # CLI flag overrides config; fall back to BOT.MOUSE_WIGGLE.ENABLED
                mw_enabled = getattr(self.cfg.ARGS, "MOUSE_WIGGLE", None)
                if mw_enabled is None:
                    cfg_mw = getattr(self.cfg.BOT, "MOUSE_WIGGLE", None)
                    mw_enabled = bool(getattr(cfg_mw, "ENABLED", False)) if cfg_mw is not None else False
                else:
                    mw_enabled = bool(mw_enabled)
            except Exception:
                mw_enabled = False
            if mw_enabled:
                # start a background thread that slightly moves the mouse periodically
                self.start_background_task("mouse_wiggle", self._mouse_wiggle)
            try:
                self.player.start_fishing()
            except KeyboardInterrupt:
                general_listener.stop()
                # If paused, stop background tasks to avoid duplicate threads and unwanted movement
                if self.paused:
                    try:
                        self.stop_background_tasks()
                    except Exception:
                        logger.debug("Failed to stop background tasks during pause")
                if not self.paused:
                    break

                utils.print_usage_box(
                    f"Press {self.cfg.KEY.PAUSE} to reload config and restart."
                )
                utils.print_hint_box(
                    "Any modifications made to LAUNCH_OPTIONS will be ignored."
                )
                with self.player.hold_keys(mouse=False, shift=False, reset=True):
                    pause_listener = keyboard.Listener(on_release=self._pause_wait)
                    pause_listener.start()

                while pause_listener.is_alive():
                    timer_sleep(add_jitter(THREAD_CHECK_DELAY))

                logger.info("Restarting bot without resetting records")
                self.reload_cfg()
                self.player = Player(
                    self.cfg,
                    self.player.timer,
                    self.player.detection,
                    self.player.result,
                )
                self.paused = False

        # stop any background threads we started
        self.stop_background_tasks()
        self.player.handle_termination("Terminated by user", shutdown=False, send=False)


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
            title="Settings", show_header=False, box=box.HEAVY, min_width=36
        )
        settings.add_row("LAUNCH OPTIONS (FINAL)", " ".join(sys.argv[1:]))
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
        logger.info("Crafting item")
        pag.click()
        timer_sleep(add_jitter(CRAFT_DELAY))
        self.result.material += 1
        while True:
            if self.detection.is_operation_success():
                logger.info("Crafting successed")
                self.result.success += 1
                pag.press(accept_key)
                break

            if self.detection.is_operation_failed():
                logger.warning("Crafting failed")
                self.result.fail += 1
                pag.press("space")
                break
            timer_sleep(add_jitter(LOOP_DELAY))
        timer_sleep(ANIMATION_DELAY)
        discard_yes_position = self.detection.get_discard_yes_position()
        if discard_yes_position:
            pag.click(discard_yes_position)
        timer_sleep(add_jitter(LOOP_DELAY))

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Handle keyboard release events for script control.

        :param key: Key released by the user.
        :type key: keyboard.KeyCode
        """
        if str(key).lower() == str(keyboard.KeyCode.from_char(self.cfg.KEY.QUIT)):
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
            utils.print_usage_box(f"Press {self.cfg.KEY.QUIT} to quit.")
            logger.warning("This might get you banned, use at your own risk")
            logger.warning("Use Razor or Logitech macros instead")
            random.seed(datetime.now().timestamp())
            accept_key = "backspace" if self.cfg.ARGS.DISCARD else "space"
            self.window.activate_game_window()
            make_button_position = self.detection.get_make_button_position()
            if make_button_position is None:
                logger.critical(
                    "Make button not found, please set the interface scale to "
                    "1x or move your mouse around"
                )
                self.window.activate_script_window()
                sys.exit()
            pag.moveTo(make_button_position)
            while True:
                if (
                    not self.cfg.ARGS.IGNORE
                    and not self.detection.is_material_complete()
                ):
                    logger.critical("Running out of materials")
                    break
                if self.result.material == self.cfg.ARGS.CRAFT_LIMIT:
                    logger.info("Crafting limit reached")
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
        key = str(key).lower()
        if key == str(keyboard.KeyCode.from_char(self.cfg.KEY.MOVE_QUIT)):
            return False
        if key == str(keyboard.KeyCode.from_char(self.cfg.KEY.MOVE_PAUSE)):
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
            timer_sleep(THREAD_CHECK_DELAY)


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
            title="Settings", show_header=False, box=box.HEAVY, min_width=36
        )
        settings.add_row("LAUNCH OPTIONS (FINAL)", " ".join(sys.argv[1:]))
        settings.add_row("Power saving", str(self.cfg.HARVEST.POWER_SAVING))
        settings.add_row("Check delay", str(self.cfg.HARVEST.CHECK_DELAY))
        settings.add_row("Energy threshold", str(self.cfg.STAT.ENERGY_THRESHOLD))
        settings.add_row("Hunger threshold", str(self.cfg.STAT.HUNGER_THRESHOLD))
        settings.add_row("Comfort threshold", str(self.cfg.STAT.COMFORT_THRESHOLD))
        print(settings)
        utils.print_usage_box(f"Press {self.cfg.KEY.QUIT} to quit.")

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
            timer_sleep(add_jitter(LOOP_DELAY))
        pag.press("space")
        logger.info("Baits harvested succussfully")
        timer_sleep(ANIMATION_DELAY)

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
        if str(key).lower() == str(keyboard.KeyCode.from_char(self.cfg.KEY.QUIT)):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            return False

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
                timer_sleep(ANIMATION_DELAY)
                food_position = self.detection.get_food_position(item)
                pag.moveTo(food_position)
                pag.click()

    def start(self) -> None:
        """Wrapper method that handle window activation and result display."""
        listener = keyboard.Listener(on_release=self._on_release)
        listener.start()

        self.window.activate_game_window()
        try:
            pag.press(str(self.cfg.KEY.DIGGING_TOOL))
            timer_sleep(add_jitter(3))
            while True:
                self.refill_player_stats()
                if self.detection.is_energy_high():
                    self.harvest_baits()
                    self.result.bait += 1
                else:
                    logger.info("Energy is not high enough")

                if self.cfg.HARVEST.POWER_SAVING:
                    pag.press("esc")
                    timer_sleep(add_jitter(self.cfg.HARVEST.CHECK_DELAY, self.cfg, "HARVEST.CHECK_DELAY"))
                    pag.press("esc")
                    timer_sleep(ANIMATION_DELAY)
                else:
                    timer_sleep(add_jitter(self.cfg.HARVEST.CHECK_DELAY, self.cfg, "HARVEST.CHECK_DELAY"))
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
            Part(name="Rod", prompt="Load capacity (kg)", color="orange1", base=0.3),
            Part(name="Reel mechanism", prompt="Mech (kg)", color="plum1", base=0.3),
            Part(name="Reel friction brake", prompt="Drag (kg)", color="gold1"),
            Part(name="Fishing line", prompt="Load capacity (kg)", color="salmon1"),
            Part(name="Leader", prompt="Load capacity (kg)", color="pale_green1"),
            Part(name="Hook", prompt="Load capacity (kg)", color="sky_blue1"),
        ]
        self.friction_brake = next(
            part for part in self.parts if part.name == "Reel friction brake"
        )

    def calculate_tackle_stats(self):
        previous = False
        for part in self.parts:
            try:
                if previous:
                    if part.pre_real_load_capacity is not None:
                        raise exceptions.PreviousError
                    else:
                        utils.print_error(f"{part.name}'s value not found.")
                part.load_capacity = self.get_validated_input(part, part.prompt)
                part.wear = self.get_validated_input(part, "Wear (%)")
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
                        utils.print_error(f"{part.name}'s value not found.")
                        continue
                    raise exceptions.PreviousError
                case CalculateCommand.PREVIOUS_REMAINING.value:
                    if part.pre_real_load_capacity is None:
                        utils.print_error(f"{part.name}'s value not found.")
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
                if prompt.startswith("Wear"):
                    if not (0 <= number <= 100):
                        utils.print_error("Wear must be between 0 and 100.")
                        continue
                elif number < 0:
                    utils.print_error("Value must be non-negative.")
                    continue
                return number
            except ValueError:
                utils.print_error("Invalid input. Please try again.")

    def reset_stats(self) -> None:
        for part in self.parts:
            part.pre_real_load_capacity = part.real_load_capacity
            part.real_load_capacity = None
        self.result = Table(
            "Results",
            title="Tackle's Stats",
            show_header=False,
            box=box.HEAVY,
            min_width=36,
        )

    def update_result(self) -> None:
        valid_parts = [p for p in self.parts if p.real_load_capacity is not None]
        if not valid_parts:
            return
        weakest_part = min(valid_parts, key=lambda x: x.real_load_capacity)
        self.result.add_row("Weakest part", weakest_part.name)

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
                "Recommend friction brake",
                f"{int(recommend_friction_brake):2d}",
            )
        except ZeroDivisionError:
            pass  # Fail silently

    def start(self):
        """Main function to run the friction brake calculation.

        Prompts the user for input, calculates the result, and displays them in a table.
        """
        utils.print_usage_box(
            "Commands:\n"
            "r: Restart\n"
            "s: Skip a part\n"
            "S: Skip the remaining parts\n"
            "p: Use previous value for a part\n"
            "P: Use previous value for the remaing parts\n"
            "q: Quit"
        )
        utils.print_hint_box("Press V and click the gear icon to view the parts.")

        while True:
            self.reset_stats()
            try:
                self.calculate_tackle_stats()
            except exceptions.SkipRemainingError:
                pass
            except exceptions.RestartError:
                continue
            except exceptions.QuitError:
                print("Bye.")
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
            title="Settings", show_header=False, box=box.HEAVY, min_width=36
        )
        settings.add_row("LAUNCH OPTIONS (FINAL)", " ".join(sys.argv[1:]))
        settings.add_row("Initial friction brake", str(self.cfg.FRICTION_BRAKE.INITIAL))
        settings.add_row("Max friction brake", str(self.cfg.FRICTION_BRAKE.MAX))
        settings.add_row("Start delay", str(self.cfg.FRICTION_BRAKE.START_DELAY))
        settings.add_row("Increase delay", str(self.cfg.FRICTION_BRAKE.INCREASE_DELAY))
        settings.add_row("Sensitivity", self.cfg.FRICTION_BRAKE.SENSITIVITY)
        print(settings)

        utils.print_usage_box(
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
        key = str(key).lower()
        if key == str(keyboard.KeyCode.from_char(self.cfg.KEY.FRICTION_BRAKE_QUIT)):
            self.friction_brake.monitor_process.terminate()
            return False
        if key == str(keyboard.KeyCode.from_char(self.cfg.KEY.FRICTION_BRAKE_RESET)):
            self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

    def start(self):
        """Wrapper method that handle window activation and result display."""
        listener = keyboard.Listener(on_release=self._on_release)
        listener.start()
        self.window.activate_game_window()
        self.friction_brake.monitor_process.start()
        self.friction_brake.reset(self.cfg.FRICTION_BRAKE.INITIAL)

        while listener.is_alive():
            timer_sleep(THREAD_CHECK_DELAY)

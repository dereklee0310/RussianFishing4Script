"""
Main CLI.

Usage: app.py
"""

# pylint: disable=no-member
# setting node's attributes will be merged on the fly

import logging
import os
import shlex
import signal
import smtplib
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from socket import gaierror

from pynput import keyboard
from rich.logging import RichHandler
from rich import print, box
from rich.panel import Panel
from rich.table import Table, Column
from rich.console import Console
from rich.prompt import Prompt
from rich.text import Text

sys.path.append(".") # python -m module -> python file

from yacs.config import CfgNode as CN

from rf4s.config import config
from rf4s.controller.window import Window
from rf4s.player import Player

# Ignore %(name)s because it's verbose
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("rich")
# Reference: https://rich.readthedocs.io/en/latest/logging.html

ARGUMENTS = (
    ("c", "coffee", "drink coffee if the stamina is low"),
    ("A", "alcohol", "regularly drink alcohol before keeping the fish"),
    ("r", "refill", "refill hunger and comfort by consuming tea and carrot"),
    ("H", "harvest", "harvest baits before casting, support mode: bottom, spin, and float"),
    ("g", "gear_ratio", "switch the gear ratio after the retrieval timed out"),
    ("f", "friction_brake", "change friction brake automatically"),
    ("l", "lift", "lift the tackle constantly while pulling a fish"),
    ("C", "skip_cast", "skip casting for the first fish, support mode: spin, marine"),
    ("o", "spod_rod", "recast spod rod regularly"),
    ("L", "lure", "change current lure with a random one regularly"),
    ("x", "mouse", "move mouse randomly before casting the rod"),
    ("X", "pause", "pause the script after keeping a fish regularly"),
    ("b", "bite", "take a screenshot after casting in screenshots/ (for fish spot)"),
    ("S", "screenshot", "take a screenshot of every fish you caught in screenshots/"),
    ("e", "email", "send email noticication afterward"),
    ("P", "plot", "save fishing data in /logs"),
    ("M", "miaotixing", "send miaotixing notification afterward"),
    ("s", "shutdown", "shutdown computer afterward"),
)

LOGO = """
██████╗ ███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝██║  ██║██╔════╝
██████╔╝█████╗  ███████║███████╗
██╔══██╗██╔══╝  ╚════██║╚════██║
██║  ██║██║          ██║███████║
╚═╝  ╚═╝╚═╝          ╚═╝╚══════╝"""
LINK = "https://github.com/dereklee0310/RussianFishing4Script"
# https://patorjk.com/software/taag/#p=testall&f=3D-ASCII&t=RF4S%0A, ANSI Shadow

ROOT = Path(__file__).resolve().parents[1]

class NoColonPrompt(Prompt):
        prompt_suffix = " "

class App:
    """Main application class."""

    def __init__(self):
        """Merge args into setting node."""
        print(Panel.fit(LOGO, box=box.HEAVY))
        print(LINK)
        self.cfg = config.setup_cfg()
        self.cfg.merge_from_file(ROOT / "config.yaml")

        # Parser will use the last occurence if the arguments are duplicated,
        # so put argv at the end to overwrite launch options.
        args_list = shlex.split(self.cfg.SCRIPT.LAUNCH_OPTIONS) + sys.argv[1:]
        args = self._setup_parser().parse_args(args_list)
        if not self._is_args_valid(args):
            sys.exit(1)
        args_cfg = CN({"ARGS": config.dict_to_cfg(vars(args))})
        self.cfg.merge_from_other_cfg(args_cfg)
        if not self._is_smtp_valid() or not self._is_images_valid():
            sys.exit(1)

        self.console = Console()

    def _setup_parser(self) -> ArgumentParser:
        """Configure argparser."""
        parser = ArgumentParser(description="Start AFK script for Russian Fishing 4")

        for argument in ARGUMENTS:
            flag1 = f"-{argument[0]}"
            flag2 = f"--{argument[1]}"
            help = argument[2]
            parser.add_argument(flag1, flag2, action="store_true", help=help)

        # ----------------------------- release strategy ----------------------------- #
        release_strategy = parser.add_mutually_exclusive_group()
        release_strategy.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="keep all captured fishes, used by default",
        )
        release_strategy.add_argument(
            "-m", "--marked", action="store_true", help="keep only the marked fishes"
        )

        # ----------------------- retrieval detection strategy ----------------------- #
        retrieval_detecton_strategy = parser.add_mutually_exclusive_group()
        retrieval_detecton_strategy.add_argument(
            "-d",
            "--default-spool",
            action="store_true",
            help="use default spool icon for retrieval detection, used by default",
        )
        retrieval_detecton_strategy.add_argument(
            "-R",
            "--rainbow-line",
            action="store_true",
            help="use rainbow line meter for retrieval detection",
        )

        # -------------------------- arguments with metavar -------------------------- #
        profile_selection_strategy = parser.add_mutually_exclusive_group()
        profile_selection_strategy.add_argument(
            "-p",
            "--pid",
            metavar="PID",
            type=int,
            help="id of the profile you want to use",
        )
        profile_selection_strategy.add_argument(
            "-N",
            "--pname",
            metavar="PROFILE_NAME",
            type=str,
            help="name of the profile you want to use",
        )

        parser.add_argument(
            "-n",
            "--fishes_in_keepnet",
            metavar="FISH_COUNT",
            type=int,
            default=0,
            help="number of fishes in your keepnet, 0 if not specified",
        )
        parser.add_argument(
            "-t",
            "--boat_ticket",
            metavar="DURATION",
            type=int,
            choices=[1, 2, 3, 5],
            help=(
                "enable boat ticket auto renewal, duration could be 1, 2, 3 or 5"
            ),
        )

        return parser

    def _is_args_valid(self, args: Namespace) -> bool:
        if not 0 <= args.fishes_in_keepnet < self.cfg.KEEPNET.CAPACITY:
            logger.critical(
                "Invalid number of fishes in keepnet: '%s'",
                args.fishes_in_keepnet
            )
            return False

        if args.pid is not None and not self._is_pid_valid(str(args.pid)):
            logger.critical("Invalid profile id: '%s'", args.pid)
            return False

        if args.pname is not None and args.pname not in self.cfg.PROFILE:
            logger.critical("Invalid profile name: '%s'", args.pname)
            return False

        # boat_ticket_duration already checked by choices[...]
        return True

    def _is_pid_valid(self, pid: str) -> bool:
        """Validate the profile id."""
        return pid.isdigit() and 0 <= int(pid) < len(self.cfg.PROFILE)

    def _is_smtp_valid(self) -> None:
        """Validate email configuration in .env."""
        if not self.cfg.ARGS.EMAIL or not self.cfg.SCRIPT.SMTP_VERIFICATION:
            return True

        logger.info("Verifying SMTP connection...")

        email = self.cfg.NOTIFICATION.EMAIL
        password = self.cfg.NOTIFICATION.PASSWORD
        smtp_server_name = self.cfg.NOTIFICATION.SMTP_SERVER

        if self.cfg.NOTIFICATION.SMTP_SERVER == "smtp.example.com":
            logger.critical("SMTP_SERVER is not specified")
            return False

        try:
            with smtplib.SMTP_SSL(smtp_server_name, 465) as smtp_server:
                smtp_server.login(email, password)
        except smtplib.SMTPAuthenticationError:
            logger.critical("Email address or app password not accepted")
            print(
                (
                    "Please check your email address and password.\n"
                    "If Gmail is used, please refer to "
                    "https://support.google.com/accounts/answer/185833 \n"
                    "to get more information about app password authentication."
                )
            )
            return False
        except (TimeoutError, gaierror):
            logger.critical("Invalid SMTP Server or connection timed out")
            return False
        return True

    def _is_images_valid(self) -> None:
        """Verify the file integrity of static/{language}.

        Compare files in static/en and static/{language}
        and print missing files in static/{language}.
        """
        if not self.cfg.SCRIPT.IMAGE_VERIFICATION:
            return True

        logger.info("Verifying image files...")
        if self.cfg.SCRIPT.LANGUAGE == "en":
            return True

        image_dir = ROOT / "static" / self.cfg.SCRIPT.LANGUAGE
        try:
            current_images = [f.name for f in image_dir.iterdir() if f.is_file()]
        except FileNotFoundError:
            logger.critical("Invalid language: '%s'", self.cfg.SCRIPT.LANGUAGE)
            return False
        template_dir = ROOT / "static" / "en"
        target_images = [f.name for f in template_dir.iterdir() if f.is_file()]
        missing_images = set(target_images) - set(current_images)
        if len(missing_images) > 0:
            logger.critical("Integrity check failed")
            from rich.style import Style
            table = Table(
                # "Filename",
                Column("Filename", style=Style(color="red")),
                title="Missing Images",
                box=box.DOUBLE,
                show_header=False
            )
            for filename in missing_images:
                table.add_row(f"static/{self.cfg.SCRIPT.LANGUAGE}/{filename}")
            print(table)
            return False

    def _is_profile_valid(self, profile_name):
        if profile_name not in self.cfg.PROFILE:
            logger.critical("Invalid profile name: '%s'", profile_name)
            return False

        mode = self.cfg.PROFILE[profile_name].MODE
        if mode.upper() not in ("SPIN", "BOTTOM", "PIRK", "ELEVATOR", "FLOAT"):
            logger.critical("Invalid mode: '%s'", mode)
            return False

        for key in self.cfg.PROFILE[profile_name]:
            if key not in self.cfg.PROFILE[mode.upper()]:
                logger.critical("Invalid setting: '%s'", key)
                return False
        return True

    def _display_available_profiles(self) -> None:
        """List available user profiles from setting node."""
        table = Table(
            "Profile",
            title="Select a profile to start :rocket:",
            show_header=False,
            min_width=36,
        )
        for i, profile in enumerate(self.cfg.PROFILE):
            table.add_row(f"{i:>2}. {profile}")
        print(table)

    def _get_pid(self) -> None:
        """Get and validate user profile id from user input."""
        print("Enter profile id to use, q to exit:")

        while True:
            pid = NoColonPrompt.ask(prompt=">>>")
            if self._is_pid_valid(pid):
                break
            if pid == "q":
                sys.exit()
            self._print_error("Invalid profile id, please try again.")

        self.cfg.ARGS.PID = int(pid)

    def _print_error(self, msg):
        text = Text(msg)
        text.stylize("red")
        self.console.print(text)

    def _setup_user_profile(self):
        if self.cfg.ARGS.PNAME is not None:
            profile_name = self.cfg.ARGS.PNAME
        else:
            if self.cfg.ARGS.PID is None:
                self._display_available_profiles()
                self._get_pid()
            profile_name = list(self.cfg.PROFILE)[self.cfg.ARGS.PID]

        if not self._is_profile_valid(profile_name):
            sys.exit(1)

        self.cfg.SELECTED = CN({"NAME": profile_name})
        self.cfg.SELECTED.set_new_allowed(True)
        self.cfg.SELECTED.merge_from_other_cfg(self.cfg.PROFILE[profile_name])
        self.cfg.freeze()

    def setup_window(self):
        self.window = Window()
        if not self.window.is_size_valid():
            self.cfg.SCRIPT.SNAG_DETECTION = False
            self.cfg.ARGS.FRICTION_BRAKE = False

            if self.cfg.SELECTED.MODE == "float":
                width, height = self.window.get_box()[2:]
                logger.critical(
                    "Float fishing mode doesn't support window size '%s'",
                    f"{width}x{height}"
                )
                sys.exit(1)

    def _setup_player(self):
        self.player = Player(self.cfg, self.window)

    def _on_release(self, key: keyboard.KeyCode) -> None:
        """Callback for button release.

        :param key: key code used by OS
        :type key: keyboard.KeyCode
        """
        if key == keyboard.KeyCode.from_char(self.cfg.KEY.QUIT):
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            sys.exit()

    def start(self):
        self._setup_user_profile()
        self.setup_window()
        self._setup_player()
        self.cfg.freeze()
        self.window.activate_game_window()

        if self.cfg.KEY.QUIT != "CTRL-C":
            listener = keyboard.Listener(on_release=self._on_release)
            listener.start()

        try:
            self.player.start_fishing()
        except KeyboardInterrupt:
            pass

        # self.player.friction_brake_monitor_process.join()
        print(self.player.gen_result("Terminated by user"))
        if self.cfg.ARGS.PLOT:
            self.player.plot_and_save()



if __name__ == "__main__":
    app = App()
    app.start()

    # CTRL_C_EVENT: https://stackoverflow.com/questions/58455684/

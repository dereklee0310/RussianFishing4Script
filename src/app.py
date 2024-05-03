"""
Main CLI.

Usage: app.py
"""

import threading
import os
import smtplib
import logging
import sys
import shlex
from pathlib import Path
from argparse import ArgumentParser
from configparser import ConfigParser
from socket import gaierror

from prettytable import PrettyTable
from dotenv import load_dotenv

from windowcontroller import WindowController
from player import Player
from script import ask_for_confirmation
from monitor import parent_dir

# logging.BASIC_FORMAT: %(levelname)s:%(name)s:%(message)s
# timestamp: %(asctime)s, datefmt='%Y-%m-%d %H:%M:%S',
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class App:
    def __init__(self):
        """Initalize config parser and a list of user profiles."""
        self.config_path = Path(__file__).resolve().parents[1] / "config.ini"
        self.config = ConfigParser()
        self.config.read(self.config_path)

        # filter user profiles
        self.profile_names = ["edit configuration file"]
        for section in self.config.sections():
            if self.config.has_option(section, "fishing_strategy"):
                self.profile_names.append(section)

    def get_args(self) -> None:
        """Configure argparser and parse the args."""
        parser = ArgumentParser(description="Start the script for Russian Fishing 4")
        # boolean flags
        parser.add_argument(
            "-c",
            "--coffee",
            action="store_true",
            help="Drink coffee if retrieval takes longer than 2 minutes",
        )
        parser.add_argument(
            "-A",
            "--alcohol",
            action="store_true",
            help="Drink alcohol before keeping the fish regularly",
        )
        parser.add_argument(
            "-r",
            "--refill",
            action="store_true",
            help="Refill hunger and comfort by consuming tea and carrot",
        )
        parser.add_argument(
            "-H",
            "--harvest",
            action="store_true",
            help="Harvest baits when bottom fishing",
        )
        parser.add_argument(
            "-e",
            "--email",
            action="store_true",
            help=(
                (
                    "Send email to yourself after the program is terminated "
                    "without user interruption (Ctrl-C)"
                )
            ),
        )
        parser.add_argument(
            "-P",
            "--plot",
            action="store_true",
            help=(
                "Save a chart of catch per real/game hour in log/ "
                "after the program is terminated"
            ),
        )
        parser.add_argument(
            "-s",
            "--shutdown",
            action="store_true",
            help=(
                "Shutdown computer after the program is terminated "
                "without user interruption (Ctrl-C)"
            ),
        )
        parser.add_argument(
            "-l",
            "--lift",
            action="store_true",
            help=(
                "Lift the tackle constantly while retrieving " "after a fish is hooked"
            ),
        )
        parser.add_argument(
            "-g",
            "--gear-ratio-switching",
            action="store_true",
            help="When the retrieval timed out, switch the gear ratio",
        )
        parser.add_argument(
            "-D",
            "--DEBUG",
            action="store_true",
            help="This is only for testing and should not be used",
        )

        # release strategy
        release_group = parser.add_mutually_exclusive_group()
        release_group.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Keep all captured fishes, used by default",
        )
        release_group.add_argument(
            "-m", "--marked", action="store_true", help="Keep only the marked fishes"
        )

        # retrieval detection
        spool_icon_group = parser.add_mutually_exclusive_group()
        spool_icon_group.add_argument(
            "-d",
            "--default-spool-icon",
            action="store_true",
            help=("Use default spool icon for retrieval detection, " "used by default"),
        )
        spool_icon_group.add_argument(
            "-R",
            "--rainbow-line",
            action="store_true",
            help="Use rainbow line icon for retrieval detection",
        )

        # options with arguments
        parser.add_argument(
            "-n",
            "--fishes_in_keepnet",
            metavar="FISH_COUNT",
            type=int,
            default=0,
            help="Number of fishes in your keepnet, 0 if not specified",
        )
        parser.add_argument(
            "-p",
            "--pid",
            metavar="PID",
            type=int,
            help="The id of profile you want to use",
        )
        parser.add_argument(
            "-t",
            "--boat-ticket-duration",
            metavar="DURATION",
            type=int,
            choices=[1, 2, 3, 5],
            help=(
                "Enable boat ticket auto renewal, "
                "use 1, 2, 3, or 5 to speicfy the ticket duration"
            ),
        )

        argv = self.config["game"].get("default_arguments", fallback="")
        self.args = parser.parse_args(shlex.split(argv) + sys.argv[1:])

    def validate_args(self) -> None:
        """Validate args that comes with an argument."""

        if not self.is_fish_count_valid(self.args.fishes_in_keepnet):
            logger.error("Invalid number of fishes in keepnet")
            sys.exit()

        # pid has no fallback value, check if it's None
        if self.args.pid and not self.is_pid_valid(str(self.args.pid)):
            logger.error("Invalid profile id")
            sys.exit()
        self.pid = self.args.pid

        # boat_ticket_duration was already checked by choices[...]

    def validate_email(self) -> None:
        """Validate email configuration in .env."""
        load_dotenv()
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        smtp_server_name = os.getenv("SMTP_SERVER")

        if not smtp_server_name:
            logger.error("SMTP_SERVER is not specified")
            sys.exit()

        try:
            with smtplib.SMTP_SSL(smtp_server_name, 465) as smtp_server:
                smtp_server.login(email, password)
        except smtplib.SMTPAuthenticationError:
            logger.error("Email address or password not accepted")
            print(
                (
                    "Please configure your email address and password in .env\n"
                    "If Gmail is used, please refer to "
                    "https://support.google.com/accounts/answer/185833 \n"
                    "to get more information about app password authentication"
                )
            )
            sys.exit()
        except (TimeoutError, gaierror) as SMTPServerError:
            logger.error("Invalid SMTP Server or connection timed out")
            sys.exit()

    def is_fish_count_valid(self, fish_count: int) -> bool:
        """Validate the current # of fishes in keepnet.

        :param fish_count: # of fishes
        :type fish_count: int
        :return: True if valid, False otherwise
        :rtype: bool
        """
        keepnet_limit = self.config["game"].getint("keepnet_limit")
        return fish_count >= 0 and fish_count < keepnet_limit

    def is_pid_valid(self, pid: str) -> bool:
        """Validate the profile id.

        :param pid: user profile id
        :type pid: str
        :return: True if valid, False otherwise
        :rtype: bool
        """
        if not pid.isdigit():
            return False
        pid = int(pid)
        return pid >= 0 and pid < len(self.profile_names)

    def show_available_profiles(self) -> None:
        """List available user profiles."""
        table = PrettyTable(header=False, align="l")
        table.title = "Welcome! Please select a profile id to use it"
        for i, profile in enumerate(self.profile_names):
            table.add_row([f"{i:>2}. {profile}"])
        print(table)

    def ask_for_pid(self) -> None:
        """Get and validate user profile id from user input."""
        pid = input("Enter profile id or press q to exit: ")
        while not self.is_pid_valid(pid):
            if pid.strip() == "q":
                sys.exit()
            print("Invalid profile id, please try again.")
            pid = input("Profile id: ")
        self.pid = int(pid)

    def gen_player_from_settings(self) -> None:
        """Generate a player object from args and configuration file."""
        if self.pid == 0:
            logger.info("Opening configuration file")
            os.startfile(self.config_path)
            print("Save it before restarting the script to apply changes")
            sys.exit()

        self.profile_name = self.profile_names[self.pid]
        self.player = Player(self.args, self.config, self.profile_name)

    def show_user_settings(self) -> None:
        """Display user settings."""
        table = PrettyTable(header=False, align="l")
        table.title = "User Settings"
        table.add_row(["Profile name", self.profile_name])

        arg_names = self._get_args_names()
        self._build_table(arg_names, table)
        config_names = self._get_config_names()
        self._build_table(config_names, table)
        print(table)

    def _get_args_names(self) -> list:
        """Get names of command line options

        :return: list of option names
        :rtype: list
        """
        return [
            "Fishing strategy",
            "Unmarked release",
            "Coffee drinking",
            "Alcohol drinking",
            "Hunger and comfort refill",
            "Baits harvesting",
            "Email sending",
            "Plotting",
            "Shutdown",
            "Rainbow line",
            "Lift",
            "Gear ratio switching",
            "Fishes in keepnet",
            "Cast power level",
            "Boat ticket duration",
        ]

    def _get_config_names(self) -> list:
        """Get names of configurations w.r.t fishing strategy.

        :return: list of configuration names
        :rtype: list
        """
        # strategy-specific settings
        config_names = []
        match self.player.fishing_strategy:
            case "spin":
                pass
            case "spin_with_pause":
                config_names.extend(
                    [
                        "Retrieval duration",
                        "Retrieval delay",
                        "Base iteration",
                        "Acceleration",
                    ]
                )
            case "bottom":
                config_names.extend(["Check delay"])
            case "marine":
                config_names.extend(
                    [
                        "Sink timeout",
                        "Pirk duration",
                        "Pirk delay",
                        "Pirk timeout",
                        "Tighten duration",
                        "Fish hooked check delay",
                    ]
                )
            case "wakey_rig":
                pass
        return config_names
        # default case is already handled in player.py

    def _build_table(self, names: list, table: PrettyTable) -> None:
        """Construct a prettytable from list of setting names.

        :param names: list of settings names
        :type names: list
        :param table: table to be extended
        :type table: PrettyTable
        """
        for name in names:
            real_name = name.lower().replace(" ", "_")
            try:
                attribute = getattr(self.player, real_name)
                table.add_row([name, attribute])
            except AttributeError:
                # convert True/False to enabled/disabled
                attribute = getattr(self.player, real_name + "_enabled")
                table.add_row([name, "enabled" if attribute else "disabled"])

    def run_experimental_func(self) -> None:
        """For debugging."""
        # for debugging
        # from monitor import *
        # from pyautogui import *
        # from time import sleep
        WindowController().activate_game_window()
        self.player.replace_broken_lures()

    def verify_file_integrity(self) -> None:
        """Compare files in static/en and static/{language}
        and print missing files in static/{language}."""
        logger.info("Verifying file integrity...")

        if parent_dir == "../static/en/":
            logger.info("Integrity check passed")
            return

        complete_filenames = os.listdir("../static/en/")  # use en version as reference
        try:
            current_filenames = os.listdir(parent_dir)
        except FileNotFoundError:
            logger.error(f"Directory {parent_dir} not found")
            print("Please check your language setting in ../config.ini")
            sys.exit()

        missing_filenames = set(complete_filenames) - set(current_filenames)
        if len(missing_filenames) != 0:
            logger.error(f"Integrity check failed")
            guide_link = "https://github.com/dereklee0310/RussianFishing4Script/blob/main/integrity_guide.md"
            print(f"Please refer to {guide_link}")
            table = PrettyTable(header=False, align="l")
            table.title = "Missing images"
            for filename in missing_filenames:
                table.add_row([filename])
            print(table)
            sys.exit()

        logger.info("Integrity check passed")


if __name__ == "__main__":
    app = App()
    app.get_args()
    app.verify_file_integrity()

    app.validate_args()
    if app.args.email:
        app.validate_email()

    if app.args.pid is None:
        app.show_available_profiles()
        app.ask_for_pid()
    app.gen_player_from_settings()
    app.show_user_settings()

    if app.args.DEBUG:
        app.run_experimental_func()
        exit()

    ask_for_confirmation("Do you want to continue with the settings above")
    WindowController().activate_game_window()
    app.player.start_fishing()

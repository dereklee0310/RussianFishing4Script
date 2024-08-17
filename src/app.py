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

import pyautogui as pag
from dotenv import load_dotenv
from prettytable import PrettyTable
from pynput import keyboard

import script
from player import Player
from setting import COMMON_CONFIGS, SPECIAL_CONFIGS, Setting

# logging.BASIC_FORMAT: %(levelname)s:%(name)s:%(message)s
# timestamp: %(asctime)s, datefmt='%Y-%m-%d %H:%M:%S',
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------- flag name, help message ------------------------- #
HELP = [
    ("c", "Drink coffee if retrieval takes longer than 2 minutes"),
    ("A", "Drink alcohol before keeping the fish regularly"),
    ("r", "Refill hunger and comfort by consuming tea and carrot"),
    ("H", "Harvest baits when bottom fishing"),
    ("g", "Switch the gear ratio automatically"),
    ("P", "Save a chart of catch logs in log/ after it's terminated"),
    ("s", "Shutdown computer after terminated without user interruption"),
    ("l", "After fish is hooked, lift the tackle constantly while retrieving"),
    ("e", "Send email to yourself after terminated without user interruption"),
    ("M", "Send miaotixing notification after terminated without user interruption"),
    ("S", "Take screenshots of every fish you catch and save them in screenshots/"),
    ("C", "Except for bottom and float fishing, skip rod casting for the first fish"),
]

# ------------------ flag name, attribute name, description ------------------ #
COMMON_ARGS = (
    ("coffee", "coffee_drinking_enabled", "Coffee drinking"),
    ("alcohol", "alcohol_drinking_enabled", "Alcohol drinking"),
    ("refill", "player_stat_refill_enabled", "Player stat refill"),
    ("harvest", "baits_harvesting_enabled", "Baits harvesting"),
    ("gear_ratio", "gr_switching_enabled", "Gear ratio switching"),
    ("plot", "plotting_enabled", "Plotting"),
    ("shutdown", "shutdown_enabled", "Shutdown"),
    ("lift", "lifting_enabled", "Lifting"),
    ("email", "email_sending_enabled", "Email sending"),
    ("miaotixing", "miaotixing_sending_enabled", "miaotixing sending"),
    ("screenshot", "screenshot_enabled", "Screenshot"),
    ("cast", "cast_skipping_enabled", "Cast skipping"),
)

SPECIAL_ARGS = (
    ("marked", "unmarked_release_enabled", "Unmarked release"),
    ("rainbow_line", "rainbow_line_enabled", "Rainbow line"),
    ("fishes_in_keepnet", "fishes_in_keepnet", "Fishes in keepnet"),
    ("boat_ticket_duration", "boat_ticket_duration", "Boat ticket duratioin"),
)

# https://patorjk.com/software/taag/#p=testall&f=3D-ASCII&t=RF4S%0A, ANSI Shadow
ASCII_LOGO = """
██████╗ ███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝██║  ██║██╔════╝
██████╔╝█████╗  ███████║███████╗
██╔══██╗██╔══╝  ╚════██║╚════██║
██║  ██║██║          ██║███████║
╚═╝  ╚═╝╚═╝          ╚═╝╚══════╝"""


class App:
    """Main application class."""

    def __init__(self):
        """Merge args into setting node."""
        self.pid = None
        self.player = None

        self._build_args()
        self._verify_args()

        if self.args.email is not None and self.setting.SMTP_validation_enabled:
            self._validate_smtp_connection()
        if self.setting.image_verification_enabled:
            self._verify_image_file_integrity()

        # pname -> pid
        if self.args.pname is not None:
            try:
                self.pid = self.setting.profile_names.index(self.args.pname)
            except ValueError:
                logger.error("Invalid profile name")
                sys.exit()

        # all checks passed, merge settings
        args_attributes = COMMON_ARGS + SPECIAL_ARGS
        self.setting.merge_args(self.args, args_attributes)

        # update number of fishes to catch
        fishes_to_catch = self.setting.keepnet_limit - self.setting.fishes_in_keepnet
        self.setting.fishes_to_catch = fishes_to_catch
        print(ASCII_LOGO)
        print("https://github.com/dereklee0310/RussianFishing4Script")

    def setup_parser(self) -> ArgumentParser:
        """Configure argparser and parse the args."""
        parser = ArgumentParser(description="Start the script for Russian Fishing 4")

        # use first column of .common_arg_table as the second flag name
        for arg_help, common_arg in zip(HELP, COMMON_ARGS):
            flag1 = f"-{arg_help[0]}"
            flag2 = f"--{common_arg[0]}"
            help_msg = arg_help[1]
            parser.add_argument(flag1, flag2, action="store_true", help=help_msg)

        # ----------------------------- release strategy ----------------------------- #
        release_strategy = parser.add_mutually_exclusive_group()
        release_strategy.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Keep all captured fishes, used by default",
        )
        release_strategy.add_argument(
            "-m", "--marked", action="store_true", help="Keep only the marked fishes"
        )

        # ----------------------- retrieval detection strategy ----------------------- #
        retrieval_detecton_strategy = parser.add_mutually_exclusive_group()
        retrieval_detecton_strategy.add_argument(
            "-d",
            "--default-spool",
            action="store_true",
            help="Use default spool icon for retrieval detection, used by default",
        )
        retrieval_detecton_strategy.add_argument(
            "-R",
            "--rainbow-line",
            action="store_true",
            help="Use rainbow line meter for retrieval detection",
        )

        # -------------------------- arguments with metavar -------------------------- #
        parser.add_argument(
            "-p",
            "--pid",
            metavar="PID",
            type=int,
            help="Id of the profile you want to use",
        )
        parser.add_argument(
            "-N",
            "--pname",
            metavar="PROFILE_NAME",
            type=str,
            help="Name of the profile you want to use",
        )
        parser.add_argument(
            "-n",
            "--fishes_in_keepnet",
            metavar="FISH_COUNT",
            type=int,
            default=0,
            help="Number of fishes in your keepnet, 0 if not specified",
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

        return parser

    def _build_args(self) -> None:
        """Build args from command line arguments and configuration file."""
        # parse command line arguments first for help
        parser = self.setup_parser()
        command_line_args = parser.parse_args()

        # merge with default arguments
        self.setting = Setting()
        default_args = parser.parse_args(shlex.split(self.setting.default_arguments))

        # merge with default arguments
        command_line_args = vars(command_line_args)
        default_args = vars(default_args)
        for k, v in default_args.items():
            if k not in command_line_args:
                command_line_args[k] = v
        command_line_args = Namespace(**command_line_args)
        self.args = command_line_args

    def _verify_args(self) -> None:
        """Verify args that comes with an argument."""

        # verify number of fishes in keepnet
        if not 0 <= self.args.fishes_in_keepnet < self.setting.keepnet_limit:
            logger.error("Invalid number of fishes in keepnet")
            sys.exit()

        # pid has no fallback value, check if it's None
        if self.args.pid and not self._is_pid_valid(str(self.args.pid)):
            logger.error("Invalid profile id")
            sys.exit()
        self.pid = self.args.pid

        # boat_ticket_duration already checked by choices[...]

    def _validate_smtp_connection(self) -> None:
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
        except (TimeoutError, gaierror):
            logger.error("Invalid SMTP Server or connection timed out")
            sys.exit()

    def _verify_image_file_integrity(self) -> None:
        """Verify the file integrity of static/{language}.

        Compare files in static/en and static/{language}
        and print missing files in static/{language}.
        """
        logger.info("Verifying file integrity...")

        image_dir = self.setting.image_dir
        if image_dir == "../static/en/":
            logger.info("Integrity check passed")
            return

        complete_filenames = os.listdir("../static/en/")  # use en version as reference
        try:
            current_filenames = os.listdir(image_dir)
        except FileNotFoundError:
            logger.error("Directory %s not found", image_dir)
            print("Please check your language setting in ../config.ini")
            sys.exit()

        missing_filenames = set(complete_filenames) - set(current_filenames)
        if len(missing_filenames) != 0:
            logger.error("Integrity check failed")
            guide_link = "https://shorturl.at/2AzUI"
            print(f"Please refer to {guide_link}")
            table = PrettyTable(header=False, align="l")
            table.title = "Missing images"
            for filename in missing_filenames:
                table.add_row([filename])
            print(table)
            sys.exit()

        logger.info("Integrity check passed")

    def _is_pid_valid(self, pid: str) -> bool:
        """Validate the profile id.

        :param pid: user profile id
        :type pid: str
        :return: True if valid, False otherwise
        :rtype: bool
        """
        if not pid.isdigit():
            return False
        pid = int(pid)
        return 0 <= pid < len(self.setting.profile_names)

    def display_available_profiles(self) -> None:
        """List available user profiles from setting node."""
        table = PrettyTable(header=False, align="l")
        table.title = "Welcome! Please select a profile id to use it"
        for i, profile in enumerate(self.setting.profile_names):
            table.add_row([f"{i:>2}. {profile}"])
        print(table)

    def ask_for_pid(self) -> None:
        """Get and validate user profile id from user input."""
        pid = input("Enter profile id or press q to exit: ")
        while not self._is_pid_valid(pid):
            if pid.strip() == "q":
                sys.exit()
            print("Invalid profile id, please try again.")
            pid = input("Profile id: ")
        self.pid = int(pid)

        if self.pid == 0:
            os.startfile(Path(__file__).resolve().parents[1] / "config.ini")
            print("Save it before restarting the script to apply changes")
            sys.exit()

    def create_player(self) -> None:
        """Generate a player object from args and configuration file."""
        # use pid to merge user profile into setting before passing it as argument
        self.setting.merge_user_configs(self.pid)
        self.player = Player(self.setting)

    def _build_args_table(self) -> None:
        """build table for command line arguments."""
        self.table = PrettyTable(header=False, align="l")
        self.table.title = "Settings"

        arg_table = COMMON_ARGS + SPECIAL_ARGS
        for _, attribute_name, column_name in arg_table:
            attribute_value = getattr(self.setting, attribute_name)
            if isinstance(attribute_value, bool):
                attribute_value = "enabled" if attribute_value else "disabled"
            self.table.add_row([column_name, attribute_value])

    def _build_user_config_table(self) -> None:
        """Append user profile to existing table."""
        self.table.add_row(["Profile name", self.setting.profile_names[self.pid]])

        for attribute_name, column_name, _ in COMMON_CONFIGS:
            attribute_value = getattr(self.setting, attribute_name)
            self.table.add_row([column_name, attribute_value])

        special_configs = SPECIAL_CONFIGS.get(self.setting.fishing_strategy)
        for attribute_name, column_name, _ in special_configs:
            attribute_value = getattr(self.setting, attribute_name)
            self.table.add_row([column_name, attribute_value])

    def display_settings(self) -> None:
        self._build_args_table()
        self._build_user_config_table()
        print(self.table)

    def on_release(self, key: keyboard.KeyCode) -> None:
        """Callback for button release.

        :param key: key code used by OS
        :type key: keyboard.KeyCode
        """
        if key == keyboard.KeyCode.from_char(self.setting.quitting_shortcut):
            logger.info("Shutting down...")
            os.kill(os.getpid(), signal.CTRL_C_EVENT)
            sys.exit()


if __name__ == "__main__":
    app = App()
    if app.pid is None:
        app.display_available_profiles()
        app.ask_for_pid()
    app.create_player()
    app.display_settings()

    window_size = app.setting.window_size
    if window_size not in ["2560x1440", "1920x1080", "1600x900"]:
        logger.warning("Invalid window size %s, must be 2560x1440, 1920x1080 or 1600x900", window_size)
        logger.warning("Snag detection will be disabled")
        app.player.setting.snag_detection_enabled = False # modify player setting
        if app.setting.fishing_strategy == "float":
            logger.error("Float fishing mode doesn't support window size %s", window_size)
            sys.exit()

    exit()

    if app.setting.confirmation_enabled:
        script.ask_for_confirmation("Do you want to continue with the settings above")
    app.setting.window_controller.activate_game_window()

    if app.setting.quitting_shortcut != "Ctrl-C":
        listener = keyboard.Listener(on_release=app.on_release)
        listener.start()

    try:
        app.player.start_fishing()
    except KeyboardInterrupt:
        pass

    pag.keyUp("shift")  # avoid Shift key stuck
    print(app.player.gen_result("Terminated by user"))
    if app.setting.plotting_enabled:
        app.player.plot_and_save()

# CTRL_C_EVENT reference: https://stackoverflow.com/questions/58455684/

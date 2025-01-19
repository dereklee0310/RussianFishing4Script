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

# ------------------------- flag name 1, help message ------------------------ #
HELP = (
    ("c", "drink coffee if retrieval takes longer than 2 minutes"),
    ("A", "regularly drink alcohol before keeping the fish"),
    ("r", "refill hunger and comfort by consuming tea and carrot"),
    ("H", "harvest baits before casting, support mode: bottom, spin, and float"),
    ("g", "switch the gear ratio after the retrieval timed out"),
    ("P", "save a chart of catch logs in logs/"),
    ("s", "shutdown computer after terminated without user interruption"),
    ("l", "lift the tackle constantly while pulling a fish"),
    ("e", "send email to yourself after terminated without user interruption"),
    ("M", "send miaotixing notification after terminated without user interruption"),
    ("S", "take screenshots of every fish you catch and save them in screenshots/"),
    ("C", "skip rod casting for the first fish, support mode: spin, marine, wakey_rig"),
    ("f", "change friction brake automatically"),
    ("o", "recast the spod rod automatically"),
    ("L", "change current lure with a random one automatically"),
    ("x", "move mouse randomly before casting the rod"),
    ("X", "pause the script after catchig a fish regularly"),
    ("b", "take a screenshot when a fish bites and save it in screenshots/"),
)

# ----------------- flag name 2, attribute name, description ----------------- #
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
    ("result_screenshot", "result_screenshot_enabled", "Result screenshot"),
    ("cast", "cast_skipping_enabled", "Cast skipping"),
    ("friction_brake", "friction_brake_changing_enabled", "Friction brake changing"),
    ("spod_rod", "spod_rod_recast_enabled", "Spod rod recast"),
    ("lure", "lure_changing_enabled", "Lure changing"),
    ("mouse", "mouse_moving_enabled", "Mouse moving"),
    ("pause", "pause_enabled", "Pause"),
    ("bite_screenshot", "bite_screenshot_enabled", "Bite screenshot"),
)

# ----------------- flag name 2, attribute name, description ----------------- #
SPECIAL_ARGS = (
    ("marked", "unmarked_release_enabled", "Unmarked release"),
    ("rainbow_line", "rainbow_line_enabled", "Rainbow line"),
    ("fishes_in_keepnet", "fishes_in_keepnet", "Fishes in keepnet"),
    ("boat_ticket_duration", "boat_ticket_duration", "Boat ticket duratioin"),
)

ASCII_LOGO = """
██████╗ ███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝██║  ██║██╔════╝
██████╔╝█████╗  ███████║███████╗
██╔══██╗██╔══╝  ╚════██║╚════██║
██║  ██║██║          ██║███████║
╚═╝  ╚═╝╚═╝          ╚═╝╚══════╝"""
# https://patorjk.com/software/taag/#p=testall&f=3D-ASCII&t=RF4S%0A, ANSI Shadow


class App:
    """Main application class."""

    def __init__(self):
        """Merge args into setting node."""
        self.setting = None  # dummy setting, parse args first for help message
        self.pid = None
        self.player = None
        self.table = None

        self._build_setting_args()
        self._verify_args()

        if self.args.email and self.setting.SMTP_validation_enabled:
            self._validate_smtp_connection()
        if self.setting.image_verification_enabled:
            self._verify_image_file_integrity()

        # all checks passed, merge args into setting node
        args_attributes = COMMON_ARGS + SPECIAL_ARGS
        self.setting.merge_args(self.args, args_attributes)
        fishes_to_catch = self.setting.keepnet_limit - self.setting.fishes_in_keepnet
        self.setting.fishes_to_catch = fishes_to_catch

    def _setup_parser(self) -> ArgumentParser:
        """Configure argparser."""
        parser = ArgumentParser(description="Start AFK script for Russian Fishing 4")

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
        profile_selection_strategy = parser.add_mutually_exclusive_group()
        profile_selection_strategy.add_argument(
            "-p",
            "--pid",
            metavar="PID",
            type=int,
            help="Id of the profile you want to use",
        )
        profile_selection_strategy.add_argument(
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
            "--boat_ticket_duration",
            metavar="DURATION",
            type=int,
            choices=[1, 2, 3, 5],
            help=(
                "Enable boat ticket auto renewal, "
                "use 1, 2, 3, or 5 to speicfy the ticket duration"
            ),
        )

        return parser

    def _build_setting_args(self) -> None:
        """Build args from command line arguments and configuration file.

        Parse the command line arguments first to display the help message before
        attempting to locate the game window when initializing Setting node, then merge
        the parsed dictionary with the default arguments in config.ini without
        overwriting them.
        """
        # parse command line arguments first for help
        parser = self._setup_parser()
        command_line_args = vars(parser.parse_args())

        # merge with default arguments
        self.setting = Setting()
        default_arguments_list = shlex.split(self.setting.default_arguments)
        default_args = vars(parser.parse_args(default_arguments_list))
        for k, v in default_args.items():
            if (v is None or not v) and command_line_args[k] is not None:
                default_args[k] = command_line_args[k]

        self.args = Namespace(**default_args)

    def _verify_args(self) -> None:
        """Verify args that comes with an argument."""

        # verify number of fishes in keepnet
        if not 0 <= self.args.fishes_in_keepnet < self.setting.keepnet_limit:
            logger.error("Invalid number of fishes in keepnet")
            sys.exit()

        # pid has no fallback value, check if it's None
        if self.args.pid is not None and not self._is_pid_valid(str(self.args.pid)):
            logger.error("Invalid profile id")
            sys.exit()
        self.pid = self.args.pid

        # pname -> pid
        if self.args.pname is not None:
            try:
                self.pid = self.setting.profile_names.index(self.args.pname)
            except ValueError:
                logger.error("Invalid profile name")
                sys.exit()

        # boat_ticket_duration already checked by choices[...]

    def _is_pid_valid(self, pid: str) -> bool:
        """Validate the profile id.

        :param pid: user profile id
        :type pid: str
        :return: True if valid, False otherwise
        :rtype: bool
        """
        return pid.isdigit() and 0 <= int(pid) < len(self.setting.profile_names)

    def _validate_smtp_connection(self) -> None:
        """Validate email configuration in .env."""
        logger.info("Validating SMTP connection")

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
        logger.info("Verifying file integrity")

        image_dir = self.setting.image_dir
        if image_dir == "../static/en/":
            return

        target_images = os.listdir("../static/en/")  # use en version as reference
        try:
            current_images = os.listdir(image_dir)
        except FileNotFoundError:
            logger.error("Directory %s not found", image_dir)
            print("Please check your language setting in config.ini")
            sys.exit()

        missing_images = set(target_images) - set(current_images)
        if len(missing_images) != 0:
            logger.error("Integrity check failed")
            print("Please refer to docs/integrity_guide.md")
            table = PrettyTable(header=False, align="l", title="Missing Images")
            for filename in missing_images:
                table.add_row([filename])
            print(table)
            sys.exit()

    def _build_args_table(self) -> None:
        """Append command line arguments to existing table."""
        arg_table = COMMON_ARGS + SPECIAL_ARGS
        for i, (_, attribute_name, column_name) in enumerate(arg_table):
            attribute_value = getattr(self.setting, attribute_name)
            if isinstance(attribute_value, bool):
                attribute_value = "enabled" if attribute_value else "disabled"
            divider = i == len(arg_table) - 1
            self.table.add_row([column_name, attribute_value], divider=divider)

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

    def display_settings(self) -> None:
        """Display args and user profile."""
        self.table = PrettyTable(header=False, align="l", title="Setings")
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

    def verify_window_size(self) -> bool:
        """Check if the window size is supported.

        :return: True if supported, False otherwise
        :rtype: bool
        """
        if self.setting.window_controller.is_title_bar_exist():
            # logger.error("Invalid display mode: window mode")
            logger.info("Window mode detected, if you want to move the game window, " +
                        "please restart the script after moving it.")
        window_size = self.setting.window_size
        if window_size in ((2560, 1440), (1920, 1080), (1600, 900)):
            return True

        logger.warning(
            "Window size %s not supported, must be 2560x1440, 1920x1080 or 1600x900",
            window_size,
        )
        logger.warning('Window mode must be "Borderless windowed" or "Window mode"')
        logger.warning("Snag detection and friction brake changing will be disabled")
        self.setting.snag_detection_enabled = False
        self.setting.friction_brake_changing_enabled = False

        if self.setting.fishing_strategy == "float":
            logger.error(
                "Float fishing mode doesn't support window size %s", window_size
            )
            sys.exit()

        return False


if __name__ == "__main__":
    app = App()

    print(ASCII_LOGO)
    print("https://github.com/dereklee0310/RussianFishing4Script")

    if app.pid is None:
        app.display_available_profiles()
        app.ask_for_pid()
    app.create_player()
    app.display_settings()

    if app.verify_window_size():
        app.setting.set_absolute_coords()

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

    # app.player.friction_brake_monitor_process.join()
    print(app.player.gen_result("Terminated by user"))
    if app.setting.plotting_enabled:
        app.player.plot_and_save()

    # CTRL_C_EVENT: https://stackoverflow.com/questions/58455684/

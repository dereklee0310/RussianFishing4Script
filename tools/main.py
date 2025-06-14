"""Main CLI for Russian Fishing 4 Script.

This module provides the command-line interface and main execution logic
for automating fishing in Russian Fishing 4. It handles configuration,
argument parsing, window management, and fishing automation.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import shlex
import smtplib
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from socket import gaierror

from pynput import keyboard
from rich import box, print
from rich.panel import Panel
from rich.style import Style
from rich.table import Column, Table
from yacs.config import CfgNode as CN

sys.path.append(".")  # python -m module -> python file
import auto_friction_brake
import calculate
import craft
import harvest
import move

from rf4s import utils
from rf4s.app.app import App
from rf4s.config import config
from rf4s.player import Player
from rf4s.utils import create_rich_logger

logger = create_rich_logger()

ARGUMENTS = (
    ("R", "rainbow", "rainbow line meter for retrieval detection"),
    ("t", "tag", "keep only tagged fishes"),
    ("c", "coffee", "drink coffee if stamina is low during a fish fight"),
    ("a", "alcohol", "drink alcohol before keeping the fish"),
    ("r", "refill", "consume tea and carrot if hunger or comfort is low"),
    ("H", "harvest", "harvest baits before casting the rod"),
    ("L", "lure", "change current lure with a random one, mode: spin"),
    ("m", "mouse", "move mouse randomly before casting the rod"),
    ("P", "pause", "pause the script before casting the rod occasionally"),
    ("RC", "random-cast", "do a redundant rod cast randomly"),
    ("SC", "skip-cast", "skip the first rod cast"),
    ("l", "lift", "lift the tackle constantly during a fish fight"),
    ("e", "electro", "enable electric mode for Electro Raptor series reel"),
    ("FB", "friction-brake", "adjust friction brake automatically"),
    ("GR", "gear-ratio", "switch the gear ratio after the retrieval timed out"),
    ("b", "bite", "save a screenshot in screenshots/ before rod cast (for bite spot)"),
    ("s", "screenshot", "save a screenshot in screenshots/ after you caught a fish"),
    ("d", "data", "save fishing data in /logs"),
    ("E", "email", "send email noticication after the script stop"),
    ("M", "miaotixing", "send miaotixing notification after the script stop"),
    ("D", "discord", "send Discord notification after the script stop"),
    ("S", "shutdown", "shutdown computer after the script stop"),
    ("SO", "signout", "sign out instead of closing the game"),
    ("SR", "spod-rod", "recast spod rod"),
    ("DM", "dry-mix", "enable dry mix refill, mode: bottom"),
    ("GB", "groundbait", "enable groundbait refill, mode: bottom"),
    ("PVA", "pva", "enable pva refill, mode: bottom"),
)

LOGO = """
██████╗ ███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝██║  ██║██╔════╝
██████╔╝█████╗  ███████║███████╗
██╔══██╗██╔══╝  ╚════██║╚════██║
██║  ██║██║          ██║███████║
╚═╝  ╚═╝╚═╝          ╚═╝╚══════╝"""
GITHUB_LINK = "GitHub: https://github.com/dereklee0310/RussianFishing4Script"
DISCORD_LINK = "Discord: https://discord.gg/BZQWQnAMbY"
# https://patorjk.com/software/taag/#p=testall&f=3D-ASCII&t=RF4S%0A, ANSI Shadow

ROOT = Path(__file__).resolve().parents[1]

FEATURES = (
    "Fishing Bot",
    "Craft Items",
    "Harvest Baits",
    "Toggle Moving Forward",
    "Automate Friction Brake",
    "Calculate Tackle's Stats",
)


class RF4SApp(App):
    """Main application class for Russian Fishing 4 automation.

    This class orchestrates the entire automation process, from parsing command-line
    arguments to configuring the environment and executing the fishing routine.

    Attributes:
        cfg (CfgNode): Configuration node merged from YAML and CLI arguments
        args (Namespace): Parsed command-line arguments
        window (Window): Game window controller instance
        player (Player): Player instance for fishing automation
    """

    def __init__(self):
        """Initialize the application.

        Loads configuration, parses command-line arguments, and sets up the environment.
        """
        super().__init__()
        self.parser = self.create_parser()
        # Parser will use the last occurence if the arguments are duplicated,
        # so put argv at the end to overwrite launch options.
        self.args = self.parser.parse_args(
            shlex.split(self.cfg.SCRIPT.LAUNCH_OPTIONS) + sys.argv[1:]
        )
        if not self.is_args_valid(self.args):
            utils.safe_exit()
        self.cfg.merge_from_other_cfg(CN({"ARGS": config.dict_to_cfg(vars(self.args))}))

    def create_parser(self) -> ArgumentParser:
        """Configure the argument parser with all supported command-line options.

        :return: Configured ArgumentParser instance with all options and flags.
        :rtype: ArgumentParser
        """
        parser = ArgumentParser(description="Start AFK script for Russian Fishing 4")
        parser.add_argument("opts", nargs="*", help="overwrite configuration")

        for argument in ARGUMENTS:
            flag1 = f"-{argument[0]}"
            flag2 = f"--{argument[1]}"
            help_message = argument[2]
            parser.add_argument(flag1, flag2, action="store_true", help=help_message)

        profile_selection_strategy = parser.add_mutually_exclusive_group()
        profile_selection_strategy.add_argument(
            "-p",
            "--pid",
            type=int,
            help="id of the profile you want to use",
            metavar="PID",
        )
        profile_selection_strategy.add_argument(
            "-N",
            "--pname",
            type=str,
            help="name of the profile you want to use",
            metavar="PROFILE_NAME",
        )
        parser.add_argument(
            "-n",
            "--fishes-in-keepnet",
            default=0,
            type=int,
            help="number of fishes in your keepnet, 0 by default",
            metavar="FISH_COUNT",
        )
        parser.add_argument(
            "-BT",
            "--boat-ticket",
            nargs="?",
            const=5,
            type=int,
            choices=[1, 2, 3, 5],
            help=("renew boat ticket, DURATION: 1, 2, 3 or 5, 5 by default"),
            metavar="DURATION",
        )
        parser.add_argument(
            "-T",
            "--trolling",
            nargs="?",
            const="forward",
            type=str,
            choices=["forward", "left", "right"],
            help=(
                "enable trolling mode, DIRECTION: 'forward', 'left', or 'right', "
                "'forward' by default"
            ),
            metavar="DIRECTION",
        )
        parser.add_argument(
            "-BL",
            "--broken-lure",
            nargs="?",
            const="replace",
            type=str,
            choices=["replace", "alarm"],
            help=(
                "replace broken lure, ACTION: 'replace' or 'alarm', "
                "'replace' by default"
            ),
            metavar="ACTION",
        )
        return parser

    def is_args_valid(self, args: Namespace) -> bool:
        """Validate provided command-line arguments.

        :param args: Parsed command-line arguments to validate.
        :type args: Namespace
        :return: Whether the arguments are valid.
        :rtype: bool
        """
        if not 0 <= args.fishes_in_keepnet < self.cfg.KEEPNET.CAPACITY:
            logger.critical(
                "Invalid number of fishes in keepnet: '%s'", args.fishes_in_keepnet
            )
            return False

        if args.pid is not None and not self.is_pid_valid(str(args.pid)):
            logger.critical("Invalid profile id: '%s'", args.pid)
            return False

        if args.pname is not None and args.pname not in self.cfg.PROFILE:
            logger.critical("Invalid profile name: '%s'", args.pname)
            return False

        # boat_ticket_duration already checked by choices[...]
        return True

    def is_pid_valid(self, pid: str) -> bool:
        """Check if the profile ID is valid.

        :param pid: Profile ID to validate.
        :type pid: str
        :return: Whether the profile ID is valid.
        :rtype: bool
        """
        return pid.isdigit() and 0 <= int(pid) < len(self.cfg.PROFILE)

    def is_smtp_valid(self) -> bool:
        """Verify SMTP server connection for email notifications.

        Tests the connection to the configured SMTP server using stored
        credentials if email notifications are enabled.

        :return: Whether the SMTP configuration is valid or not needed.
        :rtype: bool
        """
        if not self.cfg.ARGS.EMAIL or not self.cfg.SCRIPT.SMTP_VERIFICATION:
            return True

        logger.info("Verifying SMTP connection")

        email = self.cfg.NOTIFICATION.EMAIL
        password = self.cfg.NOTIFICATION.PASSWORD
        smtp_server_name = self.cfg.NOTIFICATION.SMTP_SERVER

        try:
            with smtplib.SMTP_SSL(smtp_server_name, 465) as smtp_server:
                smtp_server.login(email, password)
        except smtplib.SMTPAuthenticationError:
            logger.critical(
                "Email address or app password not accepted,\n"
                "please check your email address and password.\n"
                "For Gmail users, please refer to\n"
                "https://support.google.com/accounts/answer/185833\n"
            )
            return False
        except (TimeoutError, gaierror):
            logger.critical("Invalid SMTP Server or connection timed out")
            return False
        return True

    def is_discord_webhook_url_valid(self) -> bool:
        if not self.cfg.ARGS.DISCORD:
            return True
        if not self.cfg.NOTIFICATION.DISCORD_WEBHOOK_URL:
            logger.critical(
                "Discord Webhook url is not set, see\n"
                "https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks"
            )
            return False
        return True

    def is_images_valid(self) -> bool:
        """Verify that all required image files exist for the selected language.

        Compares files in the reference 'en' directory with those in the current
        language directory and reports any missing files.

        :return: Whether all required image files are present.
        :rtype: bool
        """
        if not self.cfg.SCRIPT.IMAGE_VERIFICATION:
            return True

        logger.info("Verifying image files")
        if self.cfg.SCRIPT.LANGUAGE == "en":
            return True
        logger.warning(
            "Language '%s' is not fully supported, consider using EN version",
            self.cfg.SCRIPT.LANGUAGE,
        )
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
            logger.critical("Some images are missing, please add them manually")
            table = Table(
                # "Filename",
                Column("Filename", style=Style(color="red")),
                title="Missing Images",
                box=box.DOUBLE,
                show_header=False,
            )
            for filename in missing_images:
                table.add_row(f"static/{self.cfg.SCRIPT.LANGUAGE}/{filename}")
            print(table)
            return False
        return True

    def is_profile_valid(self, profile_name: str) -> bool:
        """Check if a profile configuration is valid and complete.

        :param profile_name: Name of the profile to validate.
        :type profile_name: str
        :return: Whether the profile is valid.
        :rtype: bool
        """
        if profile_name not in self.cfg.PROFILE:
            logger.critical("Invalid profile name: '%s'", profile_name)
            return False

        mode = self.cfg.PROFILE[profile_name].MODE
        if mode.upper() not in self.cfg.PROFILE:
            logger.critical("Invalid mode: '%s'", mode)
            return False

        expected_keys = set(self.cfg.PROFILE[mode.upper()])
        actual_keys = set(self.cfg.PROFILE[profile_name])

        invalid_keys = actual_keys - expected_keys
        missing_keys = expected_keys - actual_keys

        if invalid_keys or missing_keys:
            for key in invalid_keys:
                logger.warning("Invalid setting: '%s'", key)
            for key in missing_keys:
                logger.warning("Missing setting: '%s'", key)
        return True

    def display_profiles(self) -> None:
        """Display a table of available profiles for user selection.

        Shows a formatted table with profile IDs and names.
        """
        table = Table(
            "Profiles",
            title="Select a profile to start ⚙️",
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
            if self.is_pid_valid(user_input):
                break
            if user_input == "q":
                print("Bye.")
                sys.exit()
            if user_input == "h":
                self.parser.print_help()
                continue
            utils.print_error("Invalid profile id, please try again.")

        self.cfg.ARGS.PID = int(user_input)

    def create_user_profile(self) -> None:
        """Configure the user profile based on arguments or interactive selection.

        Selects a profile based on command-line arguments or user input,
        validates the profile, and merges it with the configuration.
        """
        if self.cfg.ARGS.PNAME is not None:
            profile_name = self.cfg.ARGS.PNAME
        else:
            if self.cfg.ARGS.PID is None:
                self.display_profiles()
                self.get_pid()
            profile_name = list(self.cfg.PROFILE)[self.cfg.ARGS.PID]

        if not self.is_profile_valid(profile_name):
            utils.safe_exit()

        # Merge args.opts here because we can only overwrite cfg.SELECTED
        # after it's constructed using profile id or name.
        # Process list-like values if possible
        if "KEY.BOTTOM_RODS" in self.args.opts:
            value_idx = self.args.opts.index("KEY.BOTTOM_RODS") + 1
            self.args.opts[value_idx] = [
                x.strip() for x in self.args.opts[value_idx].split(",")
            ]
        self.cfg.merge_from_list(self.args.opts)

        mode = self.cfg.PROFILE[profile_name].MODE.upper()
        self.cfg.SELECTED = CN({"NAME": profile_name}, new_allowed=True)
        self.cfg.SELECTED.merge_from_other_cfg(self.cfg.PROFILE[mode])
        self.cfg.SELECTED.merge_from_other_cfg(self.cfg.PROFILE[profile_name])

        if (
            hasattr(self.cfg.SELECTED, "LAUNCH_OPTIONS")
            and self.cfg.SELECTED.LAUNCH_OPTIONS
        ):  # Overwrite
            args_list = shlex.split(self.cfg.SELECTED.LAUNCH_OPTIONS) + sys.argv[1:]
            self.args = self.parser.parse_args(args_list)
            self.cfg.ARGS = config.dict_to_cfg(vars(self.args))

        # Check here because config might got overwritten
        if (
            not self.is_smtp_valid()
            or not self.is_images_valid()
            or not self.is_discord_webhook_url_valid()
        ):
            utils.safe_exit()
        config.print_cfg(self.cfg.ARGS)
        config.print_cfg(self.cfg.SELECTED)

    def is_window_valid(self) -> None:
        """Set up and validate the game window.

        Creates a Window object, checks if the window size is supported,
        and disables incompatible features if needed.
        """
        if self.window.is_title_bar_exist():
            logger.info("Window mode detected. Please don't move the game window")
        if not self.window.is_size_supported():
            logger.warning('Window mode must be "Borderless windowed" or "Window mode"')
            logger.warning(
                "Unsupported window size '%s', "
                "use '2560x1440', '1920x1080' or '1600x900'",
                self.window.get_resolution_str(),
            )
            logger.error(
                "Snag detection will be disabled\n"
                "Spooling detection will be disabled\n"
                "Auto friction brake will be disabled\n"
            )

            self.cfg.ARGS.FRICTION_BRAKE = False
            self.cfg.SCRIPT.SNAG_DETECTION = False
            self.cfg.SCRIPT.SPOOLING_DETECTION = False

        if (
            self.cfg.SELECTED.MODE in ("telescopic", "bolognese")
            and not self.window.is_size_supported()
        ):
            logger.critical(
                "Fishing mode '%s' doesn't support window size '%s'",
                self.cfg.SELECTED.MODE,
                self.window.get_resolution_str(),
            )
            return False
        return True

    def is_electro_valid(self):
        """Display helpful information about the current configuration.

        Checks configuration compatibility and prints warnings for
        potential issues.
        """
        if not self.cfg.ARGS.ELECTRO:
            return True

        if self.cfg.SELECTED.MODE in ("pirk", "elevator"):
            logger.info(
                "Electric mode is enabled, make sure you're using Electro Raptor"
            )
        else:
            logger.error(
                "Electric mode is not compatible with mode '%s'"
                "Electric mode will be disabled",
                self.cfg.SELECTED.MODE,
            )
            self.cfg.ARGS.ELECTRO = False
        return True

    def _start(self) -> None:
        """Entry point."""
        self.player = Player(self.cfg, self.window)
        self.player.start_fishing()

    def start(self) -> None:
        """Start the fishing automation process.

        Sets up all required components, activates the game window,
        registers key listeners, and begins the fishing automation.
        Handles termination and displays result.
        """
        self.create_user_profile()
        if not self.is_window_valid() or not self.is_electro_valid():
            utils.safe_exit()
        self.cfg.freeze()

        if self.cfg.KEY.QUIT != "CTRL-C":
            listener = keyboard.Listener(on_release=self._on_release)
            listener.start()
        print(f"Press {self.cfg.KEY.QUIT} to quit.")
        self.window.activate_game_window()
        try:
            self._start()
        except KeyboardInterrupt:
            pass

        self.display_result()
        if self.cfg.ARGS.DATA:
            self.player.timer.save_data()

    def display_result(self):
        print(
            self.player.build_result_table(
                self.player.build_result_dict("Terminated by user")
            )
        )


def display_features() -> None:
    """Display a table of available features for user selection.

    Shows a formatted table with feature IDs and names.
    """
    table = Table(
        "Features",
        title="Select a feature to start 🚀",
        show_header=False,
        min_width=36,
    )

    for i, feature in enumerate(FEATURES):
        table.add_row(f"{i:>2}. {feature}")
    print(table)


def get_pid() -> None:
    """Prompt the user to enter a profile ID and validate the input.

    Continuously prompts until a valid profile ID is entered or the
    user chooses to quit.
    """
    # print("Enter profile id to use, h to see help message, q to quit:")
    print("Enter feature id to use, q to quit:")

    while True:
        user_input = input(">>> ")
        if user_input.isdigit() and 0 <= int(user_input) < len(FEATURES):
            break
        if user_input == "q":
            print("Bye.")
            sys.exit()
        utils.print_error("Invalid feature id, please try again.")

    return int(user_input)


if __name__ == "__main__":
    print(Panel.fit(LOGO, box=box.HEAVY), GITHUB_LINK, DISCORD_LINK, sep="\n")
    utils.update_argv()
    display_features()
    match get_pid():
        case 0:
            try:
                RF4SApp().start()
            except Exception as e:
                logger.critical(e, exc_info=True)
            utils.safe_exit()
        case 1:
            craft.run_app_from_main()
        case 2:
            harvest.run_app_from_main()
        case 3:
            move.run_app_from_main()
        case 4:
            auto_friction_brake.run_app_from_main()
        case 5:
            calculate.run_app_from_main()

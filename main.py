"""Main CLI for Russian Fishing 4 Script.

This module provides the command-line interface and main execution logic
for automating fishing in Russian Fishing 4. It handles configuration,
argument parsing, window management, and fishing automation.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import argparse
import shlex
import sys

from rich import box, print
from rich.panel import Panel
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s import config, utils
from rf4s.app import (
    BotApp,
    CalculateApp,
    CraftApp,
    FrictionBrakeApp,
    HarvestApp,
    MoveApp,
)

# sys.path.append(".")  # python -m module -> python file


logger = utils.create_rich_logger()

VERSION = "0.5.3"
LOGO = """
██████╗ ███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝██║  ██║██╔════╝
██████╔╝█████╗  ███████║███████╗
██╔══██╗██╔══╝  ╚════██║╚════██║
██║  ██║██║          ██║███████║
╚═╝  ╚═╝╚═╝          ╚═╝╚══════╝"""
LINKS = """
GitHub:  https://github.com/dereklee0310/RussianFishing4Script
Discord: https://discord.gg/BZQWQnAMbY
"""
# https://patorjk.com/software/taag/#p=testall&f=3D-ASCII&t=RF4S%0A, ANSI Shadow

FEATURES = (
    {"name": "Fishing Bot", "command": "bot"},
    {"name": "Craft Items", "command": "craft"},
    {"name": "Move Forward", "command": "move"},
    {"name": "Harvest Baits", "command": "harvest"},
    {"name": "Calculate Tackle's Stats", "command": "calculate"},
    {"name": "Auto Friction Brake", "command": "frictionbrake"},
)

BOT_BOOLEAN_ARGUMENTS = (
    ("R", "rainbow", "use rainbow line meter for retrieval detection"),
    ("t", "tag", "keep only tagged fishes"),
    ("c", "coffee", "drink coffee if stamina is low during fish fight"),
    ("a", "alcohol", "drink alcohol before keeping the fish"),
    ("r", "refill", "consume tea and carrot if hunger or comfort is low"),
    ("H", "harvest", "harvest baits before casting the rod"),
    ("L", "lure", "change current lure with a random favorite one, mode: spin"),
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
    ("BL", "broken-lure", "replace broken lures with favorite ones"),
    ("SR", "spod-rod", "recast spod rod"),
    ("DM", "dry-mix", "enable dry mix refill, mode: bottom"),
    ("GB", "groundbait", "enable groundbait refill, mode: bottom"),
    ("PVA", "pva", "enable pva refill, mode: bottom"),
)

EPILOG = """
Documentation: https://github.com/dereklee0310/RussianFishing4Script/blob/main/docs/en/CONFIGURATION.md
Changelog:     https://github.com/dereklee0310/RussianFishing4Script/blob/main/docs/en/CHANGELOG.md
Bug reports:   https://github.com/dereklee0310/RussianFishing4Script/issues
"""


class Formatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


def create_parser(cfg: CN) -> argparse.ArgumentParser:
    """Configure the argument parser with all supported command-line options.

    :return: Configured ArgumentParser instance with all options and flags.
    :rtype: ArgumentParser
    """
    parser = argparse.ArgumentParser(epilog=EPILOG, formatter_class=Formatter)
    parser.add_argument("-V", "--version", action="version", version=f"RF4S {VERSION}")
    feature_parsers = parser.add_subparsers(
        title="features",
        dest="feature",
    )

    bot_parser = feature_parsers.add_parser(
        "bot", help="start fishing bot", formatter_class=Formatter
    )
    bot_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-bot {VERSION}"
    )
    bot_parser.add_argument("opts", nargs="*", help="overwrite configuration")

    for argument in BOT_BOOLEAN_ARGUMENTS:
        flag1 = f"-{argument[0]}"
        flag2 = f"--{argument[1]}"
        help_message = argument[2]
        bot_parser.add_argument(flag1, flag2, action="store_true", help=help_message)

    profile_strategy = bot_parser.add_mutually_exclusive_group()

    def pid(_pid: str) -> str:
        return int(_pid)  # ValueError will be handled

    profile_strategy.add_argument(
        "-p",
        "--pid",
        type=pid,
        choices=range(len(cfg.PROFILE)),
        help="specify the id of the profile to use",
        metavar=f"{{0-{len(cfg.PROFILE) - 1}}}",
    )

    def pname(_pname: str) -> str:
        _pname = _pname.upper()
        if _pname not in cfg.PROFILE:
            raise ValueError  # ValueError will be handled
        return _pname

    profile_strategy.add_argument(
        "-N",
        "--pname",
        type=pname,
        help="specify the name of the profile to use",
        metavar="{profile name}",
    )

    def num_fish(_num_fish: str) -> str:
        return int(_num_fish)  # ValueError will be handled

    bot_parser.add_argument(
        "-n",
        "--fishes-in-keepnet",
        default=0,  # Flag is not used
        # const=0, # Flag is used but no argument given
        type=num_fish,
        choices=range(cfg.BOT.KEEPNET.CAPACITY),
        help="specify the number of fishes in your keepnet, (default: %(default)s)",
        metavar=f"{{0-{cfg.BOT.KEEPNET.CAPACITY - 1}}}",
    )
    bot_parser.add_argument(
        "-T",
        "--trolling",
        nargs="?",
        const="forward",
        default=None,
        type=str,
        choices=["forward", "left", "right"],
        help=(
            "specify the direction for trolling mode\n"
            "(default: %(default)s, no argument: %(const)s)"
        ),
    )
    bot_parser.add_argument(
        "-BT",
        "--boat-ticket",
        nargs="?",
        const=5,
        default=None,
        type=int,
        choices=[1, 2, 3, 5],
        help=(
            "specify the duration for boat ticket renewal\n"
            "(default: %(default)s, no argument: %(const)s)"
        ),
    )

    craft_parser = feature_parsers.add_parser(
        "craft",
        help="craft items",
    )
    craft_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-craft {VERSION}"
    )
    craft_parser.add_argument("opts", nargs="*", help="overwrite configuration")
    craft_parser.add_argument(
        "-d",
        "--discard",
        action="store_true",
        help="discard all the crafted items (for groundbaits)",
    )
    craft_parser.add_argument(
        "-n",
        "--craft-limit",
        type=int,
        default=-1,
        help="specify the number of items to craft, (default: %(default)s)",
        metavar="{number of items}",
    )

    move_parser = feature_parsers.add_parser("move", help="toggle moving forward")
    move_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-move {VERSION}"
    )
    move_parser.add_argument("opts", nargs="*", help="overwrite configuration")
    move_parser.add_argument(
        "-s",
        "--shift",
        action="store_true",
        help="Hold down the Shift key while moving",
    )

    harvest_parser = feature_parsers.add_parser("harvest", help="harvest baits")
    harvest_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-harvest {VERSION}"
    )
    harvest_parser.add_argument("opts", nargs="*", help="overwrite configuration")
    harvest_parser.add_argument(
        "-r",
        "--refill",
        action="store_true",
        help="refill hunger and comfort by consuming tea and carrot",
    )

    calculate_paser = feature_parsers.add_parser(
        "calculate", help="calculate tackle's stats", aliases=["cal"]
    )
    calculate_paser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-calculate {VERSION}"
    )
    calculate_paser.add_argument("opts", nargs="*", help="overwrite configuration")

    friction_brake_parser = feature_parsers.add_parser(
        "frictionbrake",
        help="automate friction brake",
        aliases=["fb"],
    )
    friction_brake_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-frictionbrake {VERSION}"
    )
    friction_brake_parser.add_argument(
        "opts", nargs="*", help="overwrite configuration"
    )

    return parser


def display_features() -> None:
    """Display a table of available features for user selection.

    Shows a formatted table with feature IDs and names.
    """
    table = Table(
        "Features",
        title="Select a feature to start 🚀",
        show_header=False,
        box=box.HEAVY,
        min_width=36,
    )

    for i, feature in enumerate(FEATURES):
        table.add_row(f"{i:>2}. {feature['name']}")
    print(table)


def get_fid(parser) -> None:
    """Prompt the user to enter a feature ID and validate the input.

    Continuously prompts until a valid feature ID is entered or the
    user chooses to quit.
    """
    print("Enter feature id to use, h to see help message, q to quit:")

    while True:
        user_input = input(">>> ")
        if user_input.isdigit() and 0 <= int(user_input) < len(FEATURES):
            break
        if user_input == "q":
            print("Bye.")
            sys.exit()
        if user_input == "h":
            parser.print_help()
            continue
        utils.print_error("Invalid input, please try again.")
    return int(user_input)


def main() -> None:
    cfg = config.load_cfg()
    parser = create_parser(cfg)
    args = parser.parse_args()  # First parse to get {command} {flags}
    # Print logo here so the help message will not show it
    print(Panel.fit(LOGO, box=box.HEAVY), LINKS, sep="\n")

    # If user run the program without specifying a command or by double-clicking,
    # prompt user to input the feature and launch options. This handle both Python
    # interpreter and Nuitka executable use cases.
    # If a command is parsed, we assume that the user has already typed the
    # launch options and don't prompt them to type it.
    if args.feature is None:
        display_features()
        # Merge selected feature and launch options
        sys.argv = [sys.argv[0]] + [FEATURES[get_fid(parser)]["command"]] + sys.argv[1:]
        sys.argv += shlex.split(input("Enter launch options (press Enter to skip): "))
        args = parser.parse_args()
    match args.feature:
        case "bot":
            sys.argv += shlex.split(cfg.BOT.LAUNCH_OPTIONS)
            args = parser.parse_args()
            try:
                BotApp(cfg, args, parser).start()
            except Exception as e:
                logger.critical(e, exc_info=True)
        case "frictionbrake" | "fb":
            sys.argv += shlex.split(cfg.FRICTION_BRAKE.LAUNCH_OPTIONS)
            args = parser.parse_args()
            try:
                FrictionBrakeApp(cfg, args, parser).start()
            except Exception as e:
                logger.critical(e, exc_info=True)
        case "harvest":
            sys.argv += shlex.split(cfg.HARVEST.LAUNCH_OPTIONS)
            args = parser.parse_args()
            try:
                HarvestApp(cfg, args, parser).start()
            except Exception as e:
                logger.critical(e, exc_info=True)
        case "move":
            sys.argv += shlex.split(cfg.MOVE.LAUNCH_OPTIONS)
            args = parser.parse_args()
            try:
                MoveApp(cfg, args, parser).start()
            except Exception as e:
                logger.critical(e, exc_info=True)
        case "calculate" | "cal":
            try:
                CalculateApp().start()
            except Exception as e:
                logger.critical(e, exc_info=True)
        case "craft":
            try:
                CraftApp(cfg, args, parser).start()
            except Exception as e:
                logger.critical(e, exc_info=True)
        case _:
            raise NotImplementedError("This feature is not implemented.")

    utils.safe_exit()


if __name__ == "__main__":
    main()

"""Entry point for Russian Fishing 4 Script.

Parse command line arguments and config and start running the bot.
"""

import argparse
import shlex
import sys
from pathlib import Path
from packaging.version import Version
import re

import rich_argparse
from rich import box, print
from rich.prompt import Prompt
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

VERSION = "0.11.0"
MINIMUM_COMPATIBLE_CONFIG_VERSION = "0.8.0"
LOGO = """
██████╗ ███████╗██╗  ██╗███████╗
██╔══██╗██╔════╝██║  ██║██╔════╝
██████╔╝█████╗  ███████║███████╗
██╔══██╗██╔══╝  ╚════██║╚════██║
██║  ██║██║          ██║███████║
╚═╝  ╚═╝╚═╝          ╚═╝╚══════╝"""

# https://patorjk.com/software/taag/#p=testall&f=3D-ASCII&t=RF4S%0A, ANSI Shadow

FEATURES = (
    {"name": "Fishing Bot", "command": "bot"},
    {"name": "Craft Items", "command": "craft"},
    {"name": "Move Forward", "command": "move"},
    {"name": "Harvest Baits", "command": "harvest"},
    {"name": "Auto Friction Brake", "command": "frictionbrake"},
    {"name": "Calculate Tackle's Stats", "command": "calculate"},
)

BOT_BOOLEAN_ARGUMENTS = (
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
    ("GR", "gear-ratio", "switch the gear ratio or mode after the retrieval timed out"),
    ("b", "bite", "save a screenshot in screenshots/ when a fish bite"),
    ("s", "screenshot", "save a screenshot in screenshots/ after you caught a fish"),
    ("d", "data", "save fishing data in /logs"),
    ("E", "email", "send email noticication after the script stop"),
    ("M", "miaotixing", "send miaotixing notification after the script stop"),
    ("D", "discord", "send Discord notification after the script stop"),
    ("TG", "telegram", "send Telegram notification after the script stop"),
    ("S", "shutdown", "shutdown computer after the script stop"),
    ("SO", "signout", "sign out instead of closing the game"),
    ("BL", "broken-lure", "replace broken lures with favorite ones"),
    ("SR", "spod-rod", "recast spod rod"),
    ("DM", "dry-mix", "enable dry mix refill, mode: bottom"),
    ("GB", "groundbait", "enable groundbait refill, mode: bottom"),
    ("PVA", "pva", "enable pva refill, mode: bottom"),
)

EPILOG = """
Docs: https://github.com/dereklee0310/RussianFishing4Script/tree/main/docs/en
"""

# When running as an executable, use sys.executable to find the config.yaml.
# This file is not included during compilation and could not be resolved automatically
# by Nuitka.
INNER_ROOT = Path(__file__).resolve().parents[0]
if utils.is_compiled():
    OUTER_ROOT = Path(sys.executable).parent
else:
    OUTER_ROOT = INNER_ROOT


class Formatter(
    rich_argparse.RawTextRichHelpFormatter, argparse.RawDescriptionHelpFormatter
):
    # argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter
    pass


(OUTER_ROOT / "screenshots").mkdir(parents=True, exist_ok=True)
(OUTER_ROOT / "logs").mkdir(parents=True, exist_ok=True)
logger = utils.setup_logging()


def setup_parser(cfg: CN) -> tuple[argparse.ArgumentParser, tuple]:
    """Configure the argument parser with all supported command-line options.

    :return: Configured ArgumentParser instance with all options and flags.
    :rtype: ArgumentParser
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("opts", nargs="*", help="overwrite configuration")

    main_parser = argparse.ArgumentParser(epilog=EPILOG, formatter_class=Formatter)
    main_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S {VERSION}"
    )

    feature_parsers = main_parser.add_subparsers(title="features", dest="feature")

    bot_parser = feature_parsers.add_parser(
        "bot",
        help="start fishing bot",
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    bot_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-bot {VERSION}"
    )

    for argument in BOT_BOOLEAN_ARGUMENTS:
        flag1 = f"-{argument[0]}"
        flag2 = f"--{argument[1]}"
        help_message = argument[2]
        bot_parser.add_argument(flag1, flag2, action="store_true", help=help_message)

    profile_strategy = bot_parser.add_mutually_exclusive_group()

    def pid(_pid: str) -> int:
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

    def num_fish(_num_fish: str) -> int:
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
            "enable trolling mode and specify the direction\n"
            "(default: %(default)s, no argument: %(const)s)"
        ),
    )
    bot_parser.add_argument(
        "-R",
        "--rainbow",
        nargs="?",
        const=5,
        default=None,
        type=int,
        choices=[0, 5],
        help=(
            "enable rainbow line mode and specify the meter to lift the rod\n"
            "(default: %(default)s, no argument: %(const)s)"
        ),
    )

    bot_parser.add_argument(
        "-BT",
        "--boat-ticket",
        nargs="?",
        const=5,
        default=0,
        type=int,
        choices=[0, 1, 2, 3, 5],
        help=(
            "enable boat ticket renewal and specify the duration\n"
            "(default: %(default)s, no argument: %(const)s)"
        ),
    )

    craft_parser = feature_parsers.add_parser(
        "craft", help="craft items", parents=[parent_parser], formatter_class=Formatter
    )
    craft_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-craft {VERSION}"
    )
    craft_parser.add_argument(
        "-d",
        "--discard",
        action="store_true",
        help="discard all the crafted items (for groundbaits)",
    )
    craft_parser.add_argument(
        "-i",
        "--ignore",
        action="store_true",
        help="ignore unselected material slots",
    )
    craft_parser.add_argument(
        "-n",
        "--craft-limit",
        type=int,
        default=-1,
        help="specify the number of items to craft, (default: %(default)s)",
        metavar="{number of items}",
    )

    move_parser = feature_parsers.add_parser(
        "move",
        help="toggle moving forward",
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    move_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-move {VERSION}"
    )
    move_parser.add_argument(
        "-s",
        "--shift",
        action="store_true",
        help="Hold down the Shift key while moving",
    )

    harvest_parser = feature_parsers.add_parser(
        "harvest",
        help="harvest baits",
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    harvest_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-harvest {VERSION}"
    )
    harvest_parser.add_argument(
        "-r",
        "--refill",
        action="store_true",
        help="refill hunger and comfort by consuming tea and carrot",
    )

    friction_brake_parser = feature_parsers.add_parser(
        "frictionbrake",
        help="automate friction brake",
        aliases=["fb"],
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    friction_brake_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-frictionbrake {VERSION}"
    )

    calculate_paser = feature_parsers.add_parser(
        "calculate",
        help="calculate tackle's stats",
        aliases=["cal"],
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    calculate_paser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-calculate {VERSION}"
    )

    return main_parser, (
        bot_parser,
        craft_parser,
        move_parser,
        harvest_parser,
        friction_brake_parser,
        calculate_paser,
    )


def display_features() -> None:
    """Display a table of available features for user selection.

    Shows a formatted table with feature IDs and names.
    """
    table = Table(
        "Features",
        title="List of Available Features",
        show_header=False,
        box=box.HEAVY,
        min_width=36,
    )

    for i, feature in enumerate(FEATURES):
        table.add_row(f"{i:>2}. {feature['name']}")
    print(table)


def get_fid(parser: argparse.ArgumentParser) -> int:
    """Prompt the user to enter a feature ID and validate the input."""
    while True:
        user_input = Prompt.ask(
            "Enter the Feature ID you want to use (q to quit, h for help)",
            show_default=False,
        )

        utils.check_quit(user_input)

        if user_input.lower() == "h":
            parser.print_help()
            continue

        if user_input.isdigit() and 0 <= int(user_input) < len(FEATURES):
            return int(user_input)
        utils.print_error(
            f"Invalid input. Please enter a number between 0 and {len(FEATURES) - 1}."
        )


def get_launch_options(parser: argparse.ArgumentParser) -> str:
    """Prompt the user for optional launch arguments."""
    while True:
        user_input = Prompt.ask(
            "Enter launch options (Enter to skip, h for help, q to quit)",
            default="",
            show_default=False,
        )

        utils.check_quit(user_input)

        if user_input.lower() == "h":
            parser.print_help()
            continue

        return user_input


def get_language() -> str:
    """Prompt the user to select their game language."""
    user_input = Prompt.ask(
        "Select game language: (1) English, (2) Russian (q to quit)",
        choices=["1", "2", "q"],
        show_choices=False,
    )
    utils.check_quit(user_input)
    return "en" if user_input == "1" else "ru"


def get_click_lock() -> str:
    """Prompt the user to confirm Windows Mouse ClickLock status."""
    user_input = Prompt.ask(
        "Is Windows Mouse ClickLock enabled? (1) Yes, (2) No (q to quit)",
        choices=["1", "2", "q"],
        show_choices=False,
    )
    utils.check_quit(user_input)
    return "true" if user_input == "1" else "false"


def get_catch_screen_style() -> str:
    """Prompt the user to select their in-game catch screen style."""
    utils.print_hint_box(
        "We recommend 'Simple' to reduce the waiting time for the trophy animation."
    )

    user_input = Prompt.ask(
        "Select in-game catch screen style: (1) Animated, (2) Simple (q to quit)",
        choices=["1", "2", "q"],
        show_choices=False,
    )
    utils.check_quit(user_input)
    return "animated" if user_input == "1" else "simple"


def setup_cfg():
    config_path = OUTER_ROOT / "config.yaml"

    if not config_path.exists():
        utils.print_header_box(
            "Welcome to the RF4S Configuration Wizard. "
            "It will ask a few questions to generate your configuration file."
        )

        language = get_language()
        click_lock = get_click_lock()
        catch_screen_style = get_catch_screen_style()

        with open(
            INNER_ROOT / "rf4s/config/config.yaml", "r", encoding="utf-8"
        ) as file:
            content = file.read()

        # Use fucking regex because I don't want to use ruamel.yaml
        content = re.sub(
            r"^(LANGUAGE:\s*).*$", rf'\1"{language}"', content, flags=re.MULTILINE
        )
        content = re.sub(
            r"^(  CLICK_LOCK:\s*).*$", rf"\1{click_lock}", content, flags=re.MULTILINE
        )
        content = re.sub(
            r"^(  CATCH_SCREEN_STYLE:\s*).*$",
            rf'\1"{catch_screen_style}"',
            content,
            flags=re.MULTILINE,
        )

        with open(config_path, "w", encoding="utf-8") as file:
            file.write(content)
        print("Configuration file generated successfully.")

    cfg = config.load_cfg()

    if Version(cfg.VERSION) < Version(MINIMUM_COMPATIBLE_CONFIG_VERSION):
        utils.print_error(
            f"Config version {cfg.VERSION} is incompatible with RF4S {VERSION}.\n"
            f"Minimum required config version: {MINIMUM_COMPATIBLE_CONFIG_VERSION}\n"
            "Please update your config.yaml manually, or delete it to run this wizard again."
        )
        sys.exit()

    return cfg


def main() -> None:
    utils.print_logo_box(LOGO)
    cfg = setup_cfg()
    parser, subparsers = setup_parser(cfg)
    args = parser.parse_args()  # First parse to get {command} {flags}

    # If user run the program without specifying a command or by double-clicking,
    # prompt user to input the feature and launch options. This handle both Python
    # interpreter and Nuitka executable use cases.
    # If a command is parsed, we assume that the user has already typed the
    # launch options and don't prompt them to type it.
    if args.feature is None:
        display_features()
        fid = get_fid(parser)
        # Merge selected feature and launch options
        sys.argv = [sys.argv[0]] + [FEATURES[fid]["command"]] + sys.argv[1:]
        sys.argv += shlex.split(get_launch_options(subparsers[fid]))
        args = parser.parse_args()

    start, end = sys.argv[:2], sys.argv[2:]
    match args.feature:
        case "bot":
            sys.argv = start + shlex.split(cfg.BOT.LAUNCH_OPTIONS) + end
            App = BotApp
        case "craft":
            sys.argv = start + shlex.split(cfg.CRAFT.LAUNCH_OPTIONS) + end
            App = CraftApp
        case "move":
            sys.argv = start + shlex.split(cfg.MOVE.LAUNCH_OPTIONS) + end
            App = MoveApp
        case "harvest":
            sys.argv = start + shlex.split(cfg.HARVEST.LAUNCH_OPTIONS) + end
            App = HarvestApp
        case "frictionbrake" | "fb":
            sys.argv = start + shlex.split(cfg.FRICTION_BRAKE.LAUNCH_OPTIONS) + end
            App = FrictionBrakeApp
        case "calculate" | "cal":
            App = CalculateApp
        case _:
            raise NotImplementedError("You should not reach here.")
    App(cfg, parser.parse_args(), parser).start()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(e, exc_info=True)
        utils.safe_exit()  # TODO

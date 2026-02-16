"""Main CLI for Russian Fishing 4 Script.

This module provides the command-line interface and main execution logic
for automating fishing in Russian Fishing 4. It handles configuration,
argument parsing, window management, and fishing automation.

.. moduleauthor:: Derek Lee <dereklee0310@gmail.com>
"""

import argparse
import io
import logging
import logging.config
import shlex
import sys
from pathlib import Path

# Force UTF-8 for stdout/stderr on Windows to support all i18n languages (zh-TW, ru, etc.)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import rich.logging  # noqa: F401
import rich_argparse
from rich import box, print
from rich.table import Table
from yacs.config import CfgNode as CN

from rf4s import config, utils
from rf4s.i18n import setup as setup_i18n, t
from rf4s.app import (
    BotApp,
    CalculateApp,
    CraftApp,
    FrictionBrakeApp,
    HarvestApp,
    MoveApp,
)

VERSION = "0.9.1"
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
    {"name_key": "feature_bot", "command": "bot"},
    {"name_key": "feature_craft", "command": "craft"},
    {"name_key": "feature_move", "command": "move"},
    {"name_key": "feature_harvest", "command": "harvest"},
    {"name_key": "feature_frictionbrake", "command": "frictionbrake"},
    {"name_key": "feature_calculate", "command": "calculate"},
)

BOT_BOOLEAN_ARGUMENTS = (
    ("t", "tag", "help_tag"),
    ("c", "coffee", "help_coffee"),
    ("a", "alcohol", "help_alcohol"),
    ("r", "refill", "help_refill"),
    ("H", "harvest", "help_harvest_arg"),
    ("L", "lure", "help_lure"),
    ("m", "mouse", "help_mouse"),
    ("P", "pause", "help_pause"),
    ("RC", "random-cast", "help_random_cast"),
    ("SC", "skip-cast", "help_skip_cast"),
    ("l", "lift", "help_lift"),
    ("e", "electro", "help_electro"),
    ("FB", "friction-brake", "help_friction_brake"),
    ("GR", "gear-ratio", "help_gear_ratio"),
    ("b", "bite", "help_bite"),
    ("s", "screenshot", "help_screenshot"),
    ("d", "data", "help_data"),
    ("E", "email", "help_email"),
    ("M", "miaotixing", "help_miaotixing"),
    ("D", "discord", "help_discord"),
    ("TG", "telegram", "help_telegram"),
    ("S", "shutdown", "help_shutdown"),
    ("SO", "signout", "help_signout"),
    ("BL", "broken-lure", "help_broken_lure"),
    ("SR", "spod-rod", "help_spod_rod"),
    ("DM", "dry-mix", "help_dry_mix"),
    ("GB", "groundbait", "help_groundbait"),
    ("PVA", "pva", "help_pva"),
    ("NA", "no-animation", "help_no_animation"),
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


def setup_logging() -> logging.Logger:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        # "filters": {}
        "formatters": {
            # RichHandler do the job for us, so we don't need to incldue time & level
            "iso-8601-simple": {
                "format": "%(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
            "iso-8601-detailed": {
                "format": "%(asctime)s [%(levelname)s] %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            },
        },
        "handlers": {
            "stdout": {
                "level": "INFO",
                "formatter": "iso-8601-simple",
                "()": "rich.logging.RichHandler",
                "rich_tracebacks": True,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "iso-8601-detailed",
                "filename": "logs/.log",
                "maxBytes": 10000,
                "backupCount": 0,
            },
        },
        "loggers": {"root": {"level": "INFO", "handlers": ["stdout", "file"]}},
    }
    logging.config.dictConfig(config=logging_config)
    return logging.getLogger(__name__)


(OUTER_ROOT / "screenshots").mkdir(parents=True, exist_ok=True)
(OUTER_ROOT / "logs").mkdir(parents=True, exist_ok=True)
logger = setup_logging()


def setup_parser(cfg: CN) -> tuple[argparse.ArgumentParser, tuple]:
    """Configure the argument parser with all supported command-line options.

    :return: Configured ArgumentParser instance with all options and flags.
    :rtype: ArgumentParser
    """
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("opts", nargs="*", help=t("help_opts"))

    main_parser = argparse.ArgumentParser(epilog=EPILOG, formatter_class=Formatter)
    main_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S {VERSION}"
    )

    feature_parsers = main_parser.add_subparsers(title=t("features"), dest="feature")

    bot_parser = feature_parsers.add_parser(
        "bot",
        help=t("help_bot"),
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    bot_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-bot {VERSION}"
    )

    for argument in BOT_BOOLEAN_ARGUMENTS:
        flag1 = f"-{argument[0]}"
        flag2 = f"--{argument[1]}"
        help_message = t(argument[2])
        bot_parser.add_argument(flag1, flag2, action="store_true", help=help_message)

    profile_strategy = bot_parser.add_mutually_exclusive_group()

    def pid(_pid: str) -> int:
        return int(_pid)  # ValueError will be handled

    profile_strategy.add_argument(
        "-p",
        "--pid",
        type=pid,
        choices=range(len(cfg.PROFILE)),
        help=t("help_pid"),
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
        help=t("help_pname"),
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
        help=t("help_fishes_in_keepnet"),
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
        help=t("help_trolling"),
    )
    bot_parser.add_argument(
        "-R",
        "--rainbow",
        nargs="?",
        const=5,
        default=None,
        type=int,
        choices=[0, 5],
        help=t("help_rainbow"),
    )

    bot_parser.add_argument(
        "-BT",
        "--boat-ticket",
        nargs="?",
        const=5,
        default=0,
        type=int,
        choices=[0, 1, 2, 3, 5],
        help=t("help_boat_ticket"),
    )

    craft_parser = feature_parsers.add_parser(
        "craft", help=t("help_craft"), parents=[parent_parser], formatter_class=Formatter
    )
    craft_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-craft {VERSION}"
    )
    craft_parser.add_argument(
        "-d",
        "--discard",
        action="store_true",
        help=t("help_discard"),
    )
    craft_parser.add_argument(
        "-i",
        "--ignore",
        action="store_true",
        help=t("help_ignore"),
    )
    craft_parser.add_argument(
        "-n",
        "--craft-limit",
        type=int,
        default=-1,
        help=t("help_craft_limit"),
        metavar="{number of items}",
    )

    move_parser = feature_parsers.add_parser(
        "move",
        help=t("help_move"),
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
        help=t("help_shift"),
    )

    harvest_parser = feature_parsers.add_parser(
        "harvest",
        help=t("help_harvest"),
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
        help=t("help_refill_harvest"),
    )

    friction_brake_parser = feature_parsers.add_parser(
        "frictionbrake",
        help=t("help_frictionbrake"),
        aliases=["fb"],
        parents=[parent_parser],
        formatter_class=Formatter,
    )
    friction_brake_parser.add_argument(
        "-V", "--version", action="version", version=f"RF4S-frictionbrake {VERSION}"
    )

    calculate_paser = feature_parsers.add_parser(
        "calculate",
        help=t("help_calculate"),
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
        t("features"),
        title=t("select_feature"),
        show_header=False,
        box=box.HEAVY,
        min_width=36,
    )

    for i, feature in enumerate(FEATURES):
        table.add_row(f"{i:>2}. {t(feature['name_key'])}")
    print(table)


def get_fid(parser: argparse.ArgumentParser) -> int:
    """Prompt the user to enter a feature ID and validate the input.

    Continuously prompts until a valid feature ID is entered or the
    user chooses to quit.
    """
    utils.print_usage_box(t("enter_fid"))

    while True:
        user_input = input(">>> ")
        if user_input.isdigit() and 0 <= int(user_input) < len(FEATURES):
            break
        if user_input == "q":
            print(t("bye"))
            sys.exit()
        if user_input == "h":
            parser.print_help()
            continue
        utils.print_error(t("invalid_input"))
    return int(user_input)


def get_launch_options(parser: argparse.ArgumentParser) -> str:
    utils.print_usage_box(t("enter_launch_options"))
    while True:
        user_input = input(">>> ")
        if user_input == "q":
            print(t("bye"))
            sys.exit()
        if user_input == "h":
            parser.print_help()
            continue
        break
    return user_input


def get_language():
    utils.print_usage_box(t("game_language_prompt"))
    while True:
        user_input = input(">>> ")
        if user_input.isdigit() and user_input in ("1", "2"):
            break
        if user_input == "q":
            print(t("bye"))
            sys.exit()
        utils.print_error(t("invalid_input"))
    return '"en"' if user_input == "1" else '"ru"'


def get_click_lock():
    utils.print_usage_box(t("click_lock_prompt"))
    while True:
        user_input = input(">>> ")
        if user_input.isdigit() and user_input in ("1", "2"):
            break
        if user_input == "q":
            print(t("bye"))
            sys.exit()
        utils.print_error(t("invalid_input"))
    return "true" if user_input == "1" else "false"


def setup_cfg():
    config_path = OUTER_ROOT / "config.yaml"
    if not config_path.exists():
        language = get_language()
        click_lock = get_click_lock()

        with open(Path(INNER_ROOT / "rf4s/config/config.yaml"), "r") as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                if line.startswith("LANGUAGE:"):
                    lines[i] = f"LANGUAGE: {language}\n"
                if line.startswith("  CLICK_LOCK"):
                    lines[i] = f"  CLICK_LOCK: {click_lock}\n"

        with open(config_path, "w") as file:  # shutil.copy
            file.writelines(lines)

    cfg = config.load_cfg()
    if cfg.VERSION < MINIMUM_COMPATIBLE_CONFIG_VERSION:
        logger.critical(
            "Incompatible config version, some settings has been removed or deprecated\n"
            "You can delete it to allow the bot to create a new one\n"
            "Alternatively, see the CHANGELOG to modify config.yaml"
        )
        utils.safe_exit()
    return cfg


def main() -> None:
    setup_i18n("en")
    cfg = setup_cfg()
    setup_i18n(cfg.LANGUAGE)
    parser, subparsers = setup_parser(cfg)
    args = parser.parse_args()  # First parse to get {command} {flags}
    utils.print_logo_box(LOGO)  # Print logo here so the help message will not show it

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

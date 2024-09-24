"""
Module for SettingHandler class, not used yet.
"""
import sys
import configparser
import logging
import pathlib
from argparse import Namespace

from prettytable import PrettyTable

from windowcontroller import WindowController

logger = logging.getLogger(__name__)

# -------------------- attribute name - column name - type ------------------- #
GENERAL_CONFIGS = (
    ("language", "Language", str),
    ("default_arguments", "Default arguments", str),
    ("confirmation_enabled", "Enable confirmation", bool),
    ("SMTP_validation_enabled", "Enable SMTP validation", bool),
    ("image_verification_enabled", "Enable image verification", bool),
    ("coffee_limit", "Coffee limit", int),
    ("keepnet_limit", "Keepnet limit", int),
    ("keep_fish_delay", "Keep fish delay", float),
    ("energy_threshold", "Energy threshold", float),
    ("retrieval_detect_confidence", "Retrieve detect confidence", float),
    ("alcohol_drinking_delay", "Alcohol drinking delay", float),
    ("alcohol_drinking_quantity", "Alcohol drinking quantity", int),
    ("lure_broken_action", "Lure broken action", str),
    ("keepnet_full_action", "Keep net full action", str),
    ("alarm_sound_file", "Alarm sound file", str),
    ("unmarked_release_whitelist", "Unmarked release whitelist", str),
    ("snag_detection_enabled", "Enable snag detection", bool),
    ("initial_friction_brake", "Initial friction brake", int),
    ("max_friction_brake", "Max friction brake", int),
    ("friction_brake_threshold", "Friction brake threshold", float),
    ("friction_brake_check_delay", "Friction brake check delay", float),
    ("friction_brake_increase_delay", "Friction brake increase delay", float),
)

# ----------------------- config name - attribute name ----------------------- #
SHORTCUTS = (
    ("tea", "tea_shortcut"),
    ("carrot", "carrot_shortcut"),
    ("coffee", "coffee_shortcut"),
    ("shovel_spoon", "shovel_spoon_shortcut"),
    ("alcohol", "alcohol_shortcut"),
    ("bottom_rods", "bottom_rods_shortcuts"),
    ("quit", "quitting_shortcut"),
    ("main_rod", "main_rod_shortcut"),
    ("spod_rod", "spod_rod_shortcut")
)

# -------------------- attribute name - column name - type ------------------- #
COMMON_CONFIGS = (
    ("fishing_strategy", "Fishing strategy", str),
    ("cast_power_level", "Cast power level", float),
    ("cast_delay", "Cast delay", float),
    ("post_acceleration_enabled", "Enable post-acceleration", str),
)

SPECIAL_CONFIGS = {
    "spin": (),
    "spin_with_pause": (
        ("retrieval_duration", "Retrieval duration", float),
        ("retrieval_delay", "Retrieval delay", float),
        ("pre_acceleration_enabled", "Enable pre-acceleration", bool),
    ),
    "bottom": (("check_delay", "Check delay", float),),
    "marine": (
        ("sink_timeout", "Sink timeout", float),
        ("pirk_duration", "Pirk duration", float),
        ("pirk_delay", "Pirk delay", float),
        ("pirk_timeout", "Pirk timeout", float),
        ("tighten_duration", "Tighten duration", float),
        ("fish_hooked_delay", "Fish hooked delay", float),
    ),
    "float": (
        ("float_confidence", "Float confidence", float),
        ("check_delay", "Check delay", float),
        ("pull_delay", "Pull delay", float),
        ("drifting_timeout", "Drifting timeout", float),
    ),
    "wakey_rig": (
        ("sink_timeout", "Sink timeout", float),
        ("pirk_duration", "Pirk duration", float),
        ("pirk_delay", "Pirk delay", float),
        ("pirk_timeout", "Pirk timeout", float),
        ("tighten_duration", "Tighten duration", float),
        ("fish_hooked_delay", "Fish hooked delay", float),
    ),
}


class Setting:
    """Universal setting node."""

    # pylint: disable=too-many-instance-attributes, disable=maybe-no-member
    # it's a cfg node,

    def __init__(self):
        """Initialize attributes and merge the configs."""
        self.window_controller = WindowController()
        self.config = configparser.ConfigParser()

        config_file = pathlib.Path(__file__).resolve().parents[1] / "config.ini"
        if not config_file.is_file():
            logger.error("config.ini doesn't exist, please run .\\setup.bat first")
            sys.exit()


        self.config.read(pathlib.Path(__file__).resolve().parents[1] / "config.ini")

        self.profile_names = ["edit configuration file"]
        for section in self.config.sections():
            if self.config.has_option(section, "fishing_strategy"):
                self.profile_names.append(section)

        # args should be handled and merged in caller module first
        self._merge_general_configs()
        self._merge_shortcuts()

        # generate path of the image directory
        parent_dir = pathlib.Path(__file__).resolve().parents[1]
        self.image_dir = parent_dir / "static" / self.language

        # # set hard coded coordinates
        self.x_base, self.y_base = self.window_controller.get_base_coords()
        self.window_size = self.window_controller.get_window_size()
        self._set_float_camera_rect()
        self._set_snag_icon_position()

    def _merge_general_configs(self) -> None:
        """Merge general configs from config.ini."""
        section = self.config["game"]

        missing_attributes = []
        for attribute_name, _, var_type in GENERAL_CONFIGS:
            section_value = section.get(attribute_name)
            if section_value is None:
                missing_attributes.append(attribute_name)
                continue

            if var_type == bool:
                attribute_value = section_value == "True"
            else:
                attribute_value = var_type(section.get(attribute_name))
            setattr(self, attribute_name, attribute_value)

        if missing_attributes:
            logger.error("Failed to merge settings in [game] in config.ini")
            print("Please refer to template.ini to add missing settings")
            table = PrettyTable(header=False, align="l", title="Missing Settings")
            for attribute_name in missing_attributes:
                table.add_row([(attribute_name)])
            print(table)
            sys.exit()

        self.unmarked_release_whitelist = [
            key.strip() for key in self.unmarked_release_whitelist.split(",")
        ]

    def _merge_shortcuts(self) -> None:
        """Merge shortcuts from config.ini."""
        section = self.config["shortcut"]

        for config, attribute_name in SHORTCUTS:
            setattr(self, attribute_name, section.get(config))

        self.bottom_rods_shortcuts = [
            key.strip() for key in self.bottom_rods_shortcuts.split(",")
        ]

    def merge_args(self, args: Namespace, args_map: tuple[tuple]) -> None:
        """Merge command line arguments from caller module.

        :param args: parsed command line arguments
        :type args: Namespace
        :param args_attributes: flag name - attribute name - column name mapping
        :type args_attributes: tuple[tuple]
        """
        for arg_name, attribute_name, _ in args_map:
            setattr(self, attribute_name, getattr(args, arg_name))

    def merge_user_configs(self, pid: int):
        """Merge the chosen user profile using pid.

        After a profile id and args is given, this method should be invoked by app.py
        to merge the profile section in config.ini into this object.

        :param pid: user profile id
        :type pid: int
        """
        section = self.config[self.profile_names[pid]]
        missing_attributes = []

        for attribute_name, _, var_type in COMMON_CONFIGS:
            section_value = section.get(attribute_name)
            if section_value is None:
                missing_attributes.append(attribute_name)
                continue

            if var_type == bool:
                attribute_value = section_value == "True"
            else:
                attribute_value = var_type(section_value)

            setattr(self, attribute_name, attribute_value)

        special_configs = SPECIAL_CONFIGS.get(self.fishing_strategy)
        for attribute_name, _, var_type in special_configs:
            section_value = section.get(attribute_name)
            if section_value is None:
                missing_attributes.append(attribute_name)
                continue

            if var_type == bool:
                attribute_value = section_value == "True"
            else:
                attribute_value = var_type(section_value)
            setattr(self, attribute_name, attribute_value)

        if missing_attributes:
            logger.error("Failed to merge settings in [%s] in config.ini:", self.profile_names[pid])
            print("Please refer to template.ini to add missing settings")
            table = PrettyTable(header=False, align="l", title="Missing Settings")
            for attribute_name in missing_attributes:
                table.add_row([attribute_name])
            print(table)
            sys.exit()


    def _set_float_camera_rect(self) -> None:
        x, y = self.x_base, self.y_base
        match self.window_size:
            case "1600x900":
                x += 720
                y += 654
            case "1920x1080":
                x += 880
                y += 834
            case "2560x1440":
                x += 1200
                y += 1194
        self.float_camera_rect = (x, y, 160, 160)  # (left, top, w, h)

    def _set_snag_icon_position(self) -> None:
        x, y = self.x_base, self.y_base
        match self.window_size:
            case "1600x900":
                x += 1132
                y += 829
            case "1920x1080":
                x += 1292
                y += 1009
            case "2560x1440":
                x += 1612
                y += 1369
        x += 15
        self.snag_icon_position = (x, y)  # x, y coordinates

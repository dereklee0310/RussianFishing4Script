"""
Module for SettingHandler class, not used yet.
"""

import configparser
import logging
import pathlib
import sys
from argparse import Namespace

from prettytable import PrettyTable

from windowcontroller import WindowController

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------- #
#                          configuration lookup table                          #
# ---------------------------------------------------------------------------- #

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
    ("retrieval_detect_confidence", "Retrieval detect confidence", float),
    ("alcohol_drinking_delay", "Alcohol drinking delay", float),
    ("alcohol_drinking_quantity", "Alcohol drinking quantity", int),
    ("lure_broken_action", "Lure broken action", str),
    ("keepnet_full_action", "Keepnet full action", str),
    ("alarm_sound_file", "Alarm sound file", str),
    ("unmarked_release_whitelist", "Unmarked release whitelist", str),
    ("snag_detection_enabled", "Enable snag detection", bool),
    ("initial_friction_brake", "Initial friction brake", int),
    ("max_friction_brake", "Max friction brake", int),
    ("friction_brake_increase_delay", "Friction brake increase delay", float),
    ("spod_rod_recast_delay", "Friction brake increase delay", float),
    ("lure_changing_delay", "Lure changing delay", int),
    ("pause_duration", "Pause duration", int),
    ("pause_delay", "Pause delay", int),
    ("coffee_drinking_quantity", "Coffee drinking quantity", int)
)

# ----------------------- config name - attribute name ----------------------- #
SHORTCUTS = (
    ("tea", "tea_shortcut"),
    ("carrot", "carrot_shortcut"),
    ("coffee", "coffee_shortcut"),
    ("shovel_spoon", "shovel_spoon_shortcut"),
    ("alcohol", "alcohol_shortcut"),
    ("bottom_rods", "bottom_rods_shortcuts"),
    ("main_rod", "main_rod_shortcut"),
    ("spod_rod", "spod_rod_shortcut"),
    ("quit", "quitting_shortcut"),
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
    "marine_pirk": (
        ("sink_timeout", "Sink timeout", float),
        ("pirk_duration", "Pirk duration", float),
        ("pirk_delay", "Pirk delay", float),
        ("pirk_timeout", "Pirk timeout", float),
        ("pirk_timeout_action", "Pirk timeout action", str),
        ("tighten_duration", "Tighten duration", float),
        ("fish_hooked_delay", "Fish hooked delay", float),
    ),
    "marine_elevator": (
        ("sink_timeout", "Sink timeout", float),
        ("elevate_timeout", "Elevate timeout", float),
        ("lock_duration", "Lock duration", float),
        ("lock_delay", "Lock delay", float),
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
        ("pirking_timeout_action", "Pirking timeout action", str),
        ("tighten_duration", "Tighten duration", float),
        ("fish_hooked_delay", "Fish hooked delay", float),
    ),
}

# ---------------------------------------------------------------------------- #
#                     friction brake coordinates and colors                    #
# ---------------------------------------------------------------------------- #

# ----------------------------- 16x9 - 1080p - 2k ---------------------------- #
# "bases": ((480, 270), (320, 180), (0, 0)),
# ------ left - red - yellow - center(left + 424) - yellow - red - right ----- #
# absolute coordinates, should subtract x_base from them according to window size
# "x": (855, 960, 1066, 1279, 1491, 1598, 1702),
# "y": (1146, 1236, 1412),

# ------------ left - red - yellow - center - yellow - red - right ----------- #
# "1600x900": {"x": (375, 480, 586, 799, 1011, 1118, 1222), "y": 876},
# "1920x1080": {"x": (535, 640, 746, 959, 1171, 1278, 1382), "y": 1056},
# "2560x1440": {"x": (855, 960, 1066, 1279, 1491, 1598, 1702), "y": 1412},

# 70%: center + 297 (1279 + 297 = 1576)
# 80%: center + 340 (1279 + 340 = 1619)
# 90%: center + 382 (1279 + 382 = 1661)
# 95%: center + 382 (1279 + 403 = 1682)
# 100%: center + 424 (1279 + 424 = 1703)


COORD_OFFSETS = {
    "1600x900": {
        "friction_brake": (
            # {
            #     0.7: (502, 799, 1096),
            #     0.8: (459, 799, 1139),
            #     0.9: (417, 799, 1181),
            #     0.95: (396, 799, 1202),
            # },
            799,
            876,
        ),
        "fish_icon": (389, 844),
        "snag_icon": (1132 + 15, 829),
        "float_camera": (720, 654),
    },
    "1920x1080": {
        "friction_brake": (
            # {
            #     0.7: (662, 959, 1256),
            #     0.8: (619, 959, 1299),
            #     0.9: (577, 959, 1341),
            #     0.95: (556, 959, 1362),
            # },
            959,
            1056,
        ),
        "fish_icon": (549, 1024),
        "snag_icon": (1292 + 15, 1009),
        "float_camera": (880, 834),
    },
    "2560x1440": {
        "friction_brake": (
            # {
            #     0.7: (982, 1279, 1576),
            #     0.8: (939, 1279, 1619),
            #     0.9: (897, 1279, 1661),
            #     0.95: (876, 1279, 1682),
            # },
            1279,
            1412,
        ),
        "fish_icon": (869, 1384),
        "snag_icon": (1612 + 15, 1369),
        "float_camera": (1200, 1194),
    },
}

CAMERA_W = CAMERA_H = 160


class Setting:
    """Universal setting node."""

    # pylint: disable=too-many-instance-attributes, disable=maybe-no-member
    # it's a cfg node,

    def __init__(self):
        """Initialize attributes and merge the configs."""
        self.window_controller = WindowController()
        self.coord_bases = self.window_controller.get_coord_bases()
        self.window_size = self.window_controller.get_window_size()
        self.coord_offsets = None
        self.float_camera_rect = None
        self.fish_icon_position = None
        self.snag_icon_position = None
        self.friction_brake_position = None

        self.config = self._build_config()
        # build available profile table
        self.profile_names = ["edit configuration file"]
        for section in self.config.sections():
            if self.config.has_option(section, "fishing_strategy"):
                self.profile_names.append(section)

        # args will be handled and merged in App()
        self._merge_general_configs()
        self._merge_shortcuts()

        parent_dir = pathlib.Path(__file__).resolve().parents[1]
        self.image_dir = parent_dir / "static" / self.language

    def _build_config(self) -> configparser.ConfigParser:
        """Build a config and read the data from config.ini.

        :return: parsed config object
        :rtype: configparser.ConfigParser
        """
        config = configparser.ConfigParser()

        config_file = pathlib.Path(__file__).resolve().parents[1] / "config.ini"
        if not config_file.is_file():
            logger.error("config.ini doesn't exist, please run .\\setup.bat first")
            sys.exit()
        config.read(config_file)
        return config

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
        missing_attributes = []

        for section_name, attribute_name in SHORTCUTS:
            section_value = section.get(section_name)
            if section_value is None:
                missing_attributes.append(section_name)
                continue

            setattr(self, attribute_name, section.get(section_name))

        self.bottom_rods_shortcuts = [
            key.strip() for key in self.bottom_rods_shortcuts.split(",")
        ]

        if missing_attributes:
            logger.error("Failed to merge settings in [shortcut] in config.ini:")
            print("Please refer to template.ini to add missing settings")
            table = PrettyTable(header=False, align="l", title="Missing Settings")
            for attribute_name in missing_attributes:
                table.add_row([attribute_name])
            print(table)
            sys.exit()

    def _calculate_position(self, offset_key: str) -> None:
        """Calculate absolute coordinates based on given key.

        :param offset_key: a key in offset dictionary
        :type offset_key: str
        """
        return (
            self.coord_bases[0] + self.coord_offsets[offset_key][0],
            self.coord_bases[1] + self.coord_offsets[offset_key][1],
        )

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
            logger.error(
                "Failed to merge settings in [%s] in config.ini:",
                self.profile_names[pid],
            )
            print("Please refer to template.ini to add missing settings")
            table = PrettyTable(header=False, align="l", title="Missing Settings")
            for attribute_name in missing_attributes:
                table.add_row([attribute_name])
            print(table)
            sys.exit()

    def set_absolute_coords(self) -> None:
        """Add offsets to the base coordinates to get absolute ones."""
        window_size_key = f"{self.window_size[0]}x{self.window_size[1]}"
        self.coord_offsets = COORD_OFFSETS[window_size_key]
        coords = self._calculate_position("float_camera")
        self.float_camera_rect = (*coords, CAMERA_W, CAMERA_H)  # (left, top, w, h)
        self.fish_icon_position = self._calculate_position("fish_icon")
        self.snag_icon_position = self._calculate_position("snag_icon")
        self.friction_brake_position = self._calculate_position("friction_brake")

"""
Module for SettingHandler class, not used yet.
"""

import sys
import pathlib
import logging
import argparse
import configparser

logger = logging.getLogger(__name__)


class Setting():
    """Universal setting node."""
    # pylint: disable=too-many-instance-attributes, attribute-defined-outside-init
    # it's a cfg node, no need to overreact

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.config = configparser.ConfigParser()
        self.config.read(pathlib.Path(__file__).resolve().parents[1] / "config.ini")

        self.profile_names = ["edit configuration file"]
        for section in self.config.sections():
            if self.config.has_option(section, "fishing_strategy"):
                self.profile_names.append(section)

        self._get_args_settings()
        self._get_general_settings()
        self._get_shortcuts()

    def _get_args_settings(self):
        """Merge command line arguments into settings."""
        args = self.args
        self.unmarked_release_enabled = args.marked
        self.coffee_drinking_enabled = args.coffee
        self.alcohol_drinking_enabled = args.alcohol
        self.hunger_and_comfort_refill_enabled = args.refill
        self.baits_harvesting_enabled = args.harvest
        self.email_sending_enabled = args.email
        self.plotting_enabled = args.plot
        self.shutdown_enabled = args.shutdown
        self.rainbow_line_enabled = args.rainbow_line
        self.lift_enabled = args.lift
        self.gear_ratio_switching_enabled = args.gear_ratio_switching
        self.fishes_in_keepnet = args.fishes_in_keepnet
        self.boat_ticket_duration = args.boat_ticket_duration

    def _get_general_settings(self):
        """Merge general configs into settings."""
        general = self.config["game"]
        self.keepnet_limit = general.getint("keepnet_limit")
        self.fishes_to_catch = self.keepnet_limit - self.fishes_in_keepnet
        self.harvest_baits_threshold = general.getfloat("harvest_baits_threshold")
        self.coffee_limit = general.getint("coffee_limit")
        self.keep_fish_delay = general.getint("keep_fish_delay")
        self.alcohol_drinking_delay = general.getint("alcohol_drinking_delay")
        self.alcohol_quantity = general.getint("alcohol_quantity")
        self.lure_broken_action = general.get("lure_broken_action")
        self.keepnet_full_action = general.get("keepnet_full_action")
        self.alarm_sound_file_path = general.get("alarm_sound_file_path")
        self.window_size = general.getint("window_size")
        self.unmarked_release_whitelist = [
            key.strip() for key in general.get("unmarked_release_whitelist").split(",")
        ]

    def _get_shortcuts(self):
        """Merge shortcuts into settings."""
        shortcuts = self.config["shortcut"]
        self.tea_shortcut = shortcuts.get("tea")
        self.carrot_shortcut = shortcuts.get("carrot")
        self.coffee = shortcuts.get("coffee")
        self.shovel_spoon = shortcuts.get("shovel_spoon")
        self.alcohol = shortcuts.get("alcohol")
        self.bottom_rods = [
            key.strip() for key in shortcuts.get["bottom_rods"].split(",")
        ]

    def get_profile_setting(self, profile_name):
        """Merge the chosen user profile into settings.

        After a profile id is entered by the user, this method should be invoked
        to merge the profile section in config.ini into this setting object.

        :param profile_name: section name of user profile
        :type profile_name: str
        """
        profile_section = self.config[profile_name]
        self.fishing_strategy = profile_section.get("fishing_strategy")
        self.cast_power_level = profile_section.getfloat("cast_power_level")
        match self.fishing_strategy:
            case "spin":
                pass
            case "spin_with_pause":
                self.retrieval_duration = profile_section.getfloat("retrieval_duration")
                self.retrieval_delay = profile_section.getfloat("retrieval_delay")
                self.base_iteration = profile_section.getint("base_iteration")
                self.acceleration_enabled = profile_section.getboolean(
                    "acceleration_enabled"
                )
            case "bottom":
                self.check_delay = profile_section.getfloat("check_delay")
            case "marine":
                self.sink_timeout = profile_section.getfloat("sink_timeout")
                self.pirk_duration = profile_section.getfloat("pirk_duration")
                self.pirk_delay = profile_section.getfloat("pirk_delay")
                self.pirk_timeout = profile_section.getfloat("pirk_timeout")
                self.tighten_duration = profile_section.getfloat("tighten_duration")
                self.fish_hooked_check_delay = profile_section.getfloat(
                    "fish_hooked_check_delay"
                )
            case "float":
                self.float_confidence = profile_section.getfloat("float_confidence")
                self.check_delay = profile_section.getfloat("check_delay")
                self.pull_delay = profile_section.getfloat("pull_delay")
                self.drifting_timeout = profile_section.getfloat("drifting_timeout")
            case "wakey_rig":
                pass
            case _:
                logger.error("Invalid fishing strategy")
                sys.exit()


if __name__ == "__main__":
    # test = Setting(None)
    pass

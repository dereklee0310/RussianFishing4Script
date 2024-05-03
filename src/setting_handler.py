"""
Module for SettingHandler class, not used yet.
"""

from pathlib import Path
from configparser import ConfigParser


class SettingHandler:
    def __init__(self):
        config = ConfigParser()
        parent_dir = Path(__file__).resolve().parents[1]
        config.read(parent_dir / "config.ini")

        self.profile_names = ["edit configuration file"]
        for section in config.sections():
            if config.has_option(section, "fishing_strategy"):
                self.profile_names.append(section)


if __name__ == "__main__":
    test = SettingHandler()

"""
Main CLI

Usage: app.py

Todo:
    Docstrings
    Implement show_save_prompt()
"""
from time import sleep
import argparse
import configparser
import threading
import os

from pyautogui import *

from player import Player
from userprofile import UserProfile
from script import start_count_down
from windowcontroller import WindowController
# from inputimeout import inputimeout, TimeoutOccurred

class App():
    def __init__(self):
        """Initalize parser and generate a list of available user profiles.
        """
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')

        # filter user profiles
        self.profile_names = ['edit configuration file']
        for section in self.config.sections():
            if self.config.has_option(section, 'fishing_strategy'):
                self.profile_names.append(section)

    def parse_args(self):
        parser = argparse.ArgumentParser(
                            prog='app.py', 
                            description='Start the script for Russian Fishing 4', 
                            epilog='')
        parser.add_argument('-a', '--all', action='store_true',
                            help="keep all captured fishes, used by default if not specified")
        parser.add_argument('-m', '--marked', action='store_true',
                            help="keep only the marked fishes")
        parser.add_argument('-c', '--coffee', action='store_true',
                            help='drink coffee if the retrieval time is greater than 2mins, \
                                the shortcut of coffee can be modified in config.ini')
        parser.add_argument('-n', '--fishes-in-keepnet', type=int, default=0,
                            help='the current number of fishes in your keepnet, 0 if not specified')
        parser.add_argument('-p', '--pid', type=int, 
                            help='the id of profile you want to use')
        # todo
        # parser.add_argument('-r', '--refill', type=int, 
        #                     help='refill power, hunger, and temperature automatically \
        #                           using shorcut in config.ini')
        self.args = parser.parse_args()

    def process_args(self) -> bool:
        args = self.args
        self.enable_release_unmarked = args.marked 
        self.enable_drink_coffee = args.coffee

        if not self.is_fish_count_valid(args.fishes_in_keepnet):
            raise ValueError('Invalid fish count')
        self.fishes_in_keepnet = args.fishes_in_keepnet

        if not args.pid:
            return False
        elif not self.is_profile_id_valid(str(args.pid)):
            raise ValueError('Invalid profile id')
        self.pid = args.pid
        return True
    
    def is_fish_count_valid(self, fish_count: int) -> bool:
        if fish_count < 0 or fish_count >= int(self.config['game']['keepnet_limit']):
            return False
        return True
    
    def is_profile_id_valid(self, pid: str) -> bool:
        """Validate the profile id.
        #todo: pid desc.
        :return: True if profile id is valid, otherwise, return False
        :rtype: bool
        """
        if pid == '0' or pid == 'q':
            return True
        elif not pid.isdigit() or int(pid) < 0 or int(pid) > len(self.profile_names) - 1:
            return False
        return True

    def show_welcome_msg(self) -> None:
        """Display the welcome message."""
        print('+-----------------------------------------------+')
        print('|       Welcome to use RF4 fishing script       |')
        print('|    Please select an user profile using pid    |')
        print('+-----------------------------------------------+')


    def show_available_profiles(self) -> None:
        """List all available profiles from 'config.ini'.
        """
        for i, profile in enumerate(self.profile_names):
            print(f'| {i}. {profile:{42 - (i) // 10}} |')
            print('+-----------------------------------------------+')
            i += 1
    
    def ask_for_profile_id(self) -> None:
        """Let user select a profile id and validate it.
        """
        pid = input("Enter profile id or press q to exit: ")
        while not self.is_profile_id_valid(pid):
            pid = input('Invalid profile id, please try again or press q to quit: ')

        if pid == 'q':
            print('The script has been terminated')
            exit()
        elif pid == '0':
            os.startfile(r'..\config.ini') #? must be backslash
            return False
        self.pid = pid
        return True
        

    def gen_profile(self) -> None:
        """Generate a UserProfile object according to args and configuration file.
        """
        self.profile_name = self.profile_names[int(self.pid)]
        self.enable_countdown = self.config['game'].getboolean('enable_count_down')
       
        profile_section = self.config[self.profile_name]
        self.profile = UserProfile(
            self.config['game'].getint('keepnet_limit'),
            self.fishes_in_keepnet,
            self.config['shortcut']['coffee'],
            profile_section['fishing_strategy'],
            self.enable_release_unmarked,
            self.enable_drink_coffee,
            profile_section['reel_type'],
            profile_section.getfloat('retrieval_duration', fallback=0.5),
            profile_section.getfloat('retrieval_delay', fallback=1.5),
            profile_section.getint('base_iteration', fallback=0),
            profile_section.getfloat('check_delay', fallback=8),
            profile_section.getint('cast_power_level', fallback=3),
            profile_section.getfloat('pirk_duration', fallback=1.75),
            profile_section.getfloat('pirk_delay', fallback=4),
            profile_section.getfloat('tighten_duration', fallback=1))

    def display_profile_info(self) -> None:
        """Display the selected profile in the console.
        """
        profile = self.profile

        # ignore static game settings in configuration file
        print('+-----------------------------------------------+')
        print(f'| Profile name: {self.profile_name:31} |')
        print('+-----------------------------------------------+')
        print(f'| Fishing strategy: {profile.fishing_strategy:27} |')
        print('+-----------------------------------------------+')
        print(f'| Enable release unmarked: {str(profile.enable_release_unmarked):20} |')
        print('+-----------------------------------------------+')
        print(f'| Enable drink coffee: {str(profile.enable_drink_coffee):24} |')
        print('+-----------------------------------------------+')
        print(f'| Reel type: {profile.reel_type:34} |')
        print('+-----------------------------------------------+')
        print(f'| Fishes in keepnet: {str(profile.fishes_in_keepnet):26} |')
        print('+-----------------------------------------------+')

        match profile.fishing_strategy:
            case 'spin':
                pass
            case 'spin_with_pause':
                print(f'| Retrieval duration: {str(profile.retrieval_duration):25} |')
                print('+-----------------------------------------------+')
                print(f'| Retrieval delay: {str(profile.retrieval_delay):28} |')
                print('+-----------------------------------------------+')
            case 'bottom':
                print(f'| Check delay: {str(profile.check_delay):32} |')
                print('+-----------------------------------------------+')
                print(f'| Cast power level: {str(profile.cast_power_level):27} |')
                print('+-----------------------------------------------+')
            case 'marine':
                print(f'| Pirk duration: {str(profile.pirk_duration):30} |')
                print('+-----------------------------------------------+')
                print(f'| Pirk delay: {str(profile.pirk_delay):33} |')
                print('+-----------------------------------------------+')
                print(f'| Tighten duration: {str(profile.tighten_duration):27} |')
                print('+-----------------------------------------------+')
            case _:
                raise ValueError('Invalid fishing strategy')

if __name__ == '__main__':
    app = App()
    app.parse_args()
    if not app.process_args():
        app.show_welcome_msg()
        app.show_available_profiles()
        while not app.ask_for_profile_id():
            pass
    app.gen_profile()
    app.display_profile_info()

    if app.enable_countdown:
        start_count_down()
    print('The script has been started') 

    controller = WindowController()
    controller.activate_game_window()
    fisherman = Player(app.profile)
    
    # test area
    # fisherman.harvest_baits()

    fisherman.start_fishing()
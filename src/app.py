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
from script import start_count_down, msg_exit
from windowcontroller import WindowController

class App():
    def __init__(self):
        """Initalize parsers and generate a list of available user profiles.
        """
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')
        # filter user profiles
        self.profile_names = ['edit configuration file']
        for section in self.config.sections():
            if self.config.has_option(section, 'fishing_strategy'):
                self.profile_names.append(section)

        self.initialize_argparser()

    def initialize_argparser(self) -> None:
        """Configure the parser and parse the command line arguments.
        """
        parser = argparse.ArgumentParser(
                            prog='app.py', 
                            description='Start the script for Russian Fishing 4', 
                            epilog='')
        # fish keeping strategy
        parser.add_argument('-a', '--all', action='store_true',
                            help="keep all captured fishes, used by default if not specified")
        parser.add_argument('-m', '--marked', action='store_true',
                            help="keep only the marked fishes")
        
        # energy, food, and comfort refill options
        parser.add_argument('-c', '--coffee', action='store_true',
                            help='drink coffee if the retrieval time is greater than 2mins, \
                                the shortcut of coffee can be modified in config.ini')
        parser.add_argument('-r', '--refill', action='store_true', 
                            help='refill food and comfort bar by consuming tea and carrot automatically')
        parser.add_argument('-H', '--harvest_baits', action='store_true',
                            help='harvest baits automatically, must be used with bottom fishing strategy')
        
        # misc
        parser.add_argument('-n', '--fishes-in-keepnet', type=int, default=0,
                            help='the current number of fishes in your keepnet, 0 if not specified')
        parser.add_argument('-p', '--pid', type=int, 
                            help='the id of profile you want to use')
        self.parser = parser

    def validate_args(self) -> bool:
        """Validate the command line arguments.

        :return: True if profile id is given, False otherwise
        :rtype: bool
        """
        args = self.parser.parse_args()
        self.enable_release_unmarked = args.marked 
        self.enable_coffee_drinking = args.coffee
        self.enable_food_comfort_refill = args.refill
        self.enable_baits_harvesting = args.harvest_baits

        if not self.is_fish_count_valid(args.fishes_in_keepnet):
            msg_exit('Invalid fish count', is_error=True)
        self.fishes_in_keepnet = args.fishes_in_keepnet

        if not args.pid:
            return False
        elif not self.is_pid_valid(str(args.pid)):
            msg_exit('Invalid profile id', is_error=True)
            exit()
        self.pid = args.pid
        return True
    
    def is_fish_count_valid(self, fish_count: int) -> bool:
        """Validate the current # of fishes in keepnet.

        :param fish_count: # of fishes
        :type fish_count: int
        :return: True if valid, False otherwise
        :rtype: bool
        """
        if fish_count < 0 or fish_count >= int(self.config['game']['keepnet_limit']):
            return False
        return True
    
    def is_pid_valid(self, pid: str) -> bool:
        """Validate the profile id.

        :param pid: user profile id
        :type pid: str
        :return: True if valid, False otherwise
        :rtype: bool
        """
        if pid == '0' or pid == 'q':
            return True
        elif not pid.isdigit() or int(pid) < 0 or int(pid) > len(self.profile_names) - 1:
            return False
        return True

    def show_welcome_msg(self) -> None:
        """Display welcome message.
        """
        print('+-----------------------------------------------+')
        print('|       Welcome to use RF4 fishing script       |')
        print('|    Please select an user profile using pid    |')
        print('+-----------------------------------------------+')


    def show_available_profiles(self) -> None:
        """List available user profiles.
        """
        for i, profile in enumerate(self.profile_names):
            print(f'| {i}. {profile:{42 - (i) // 10}} |')
            print('+-----------------------------------------------+')
            i += 1
    
    def get_pid_from_user(self) -> None:
        """Validate user profile id from user input.
        """
        pid = input("Enter profile id or press q to exit: ")
        while not self.is_pid_valid(pid):
            pid = input('Invalid profile id, please try again or press q to quit: ')

        if pid == 'q':
            msg_exit('The script has been terminated')
        elif pid == '0':
            os.startfile(r'..\config.ini') #? must be backslash
            msg_exit('Save configuration and restart the script to apply changes')
        self.pid = pid

    def gen_player(self) -> None:
        """Generate a player object according to args and configuration file.
        """
        self.profile_name = self.profile_names[int(self.pid)]
        profile_section = self.config[self.profile_name]
        profile = UserProfile(
            self.fishes_in_keepnet,
            self.enable_release_unmarked,
            self.enable_coffee_drinking,
            self.enable_food_comfort_refill,
            self.enable_baits_harvesting,
            profile_section['fishing_strategy'],
            profile_section.getfloat('retrieval_duration', fallback=0.5),
            profile_section.getfloat('retrieval_delay', fallback=1.5),
            profile_section.getint('base_iteration', fallback=0),
            profile_section.getfloat('check_delay', fallback=8),
            profile_section.getfloat('cast_power_level', fallback=3),
            profile_section.getfloat('pirk_duration', fallback=1.75),
            profile_section.getfloat('pirk_delay', fallback=4),
            profile_section.getfloat('tighten_duration', fallback=1))
        self.player = Player(profile, self.config) # todo

    def display_general_player_info(self) -> None:
        """Display general game settings shared by all profiles.
        """
        # static game settings are handled in Player class constructor
        profile = self.player.profile
        print('+-----------------------------------------------+')
        print(f'| Profile name: {self.profile_name:31} |')
        print('+-----------------------------------------------+')
        print(f'| Fishing strategy: {profile.fishing_strategy:27} |')
        print('+-----------------------------------------------+')
        print(f'| Enable release unmarked: {str(profile.enable_release_unmarked):20} |')
        print('+-----------------------------------------------+')
        print(f'| Enable coffee drinking: {str(profile.enable_coffee_drinking):21} |')
        print('+-----------------------------------------------+')
        print(f'| Enable food and comfort refill: {str(profile.enable_food_comfort_refill):13} |')
        print('+-----------------------------------------------+')
        print(f'| Enable baits harvesting: {str(profile.enable_baits_harvesting):20} |')
        print('+-----------------------------------------------+')
        print(f'| Fishes in keepnet: {str(profile.fishes_in_keepnet):26} |')
        print('+-----------------------------------------------+')

    def display_advanced_player_info(self):
        """Display strategy-specific settings.

        :raises ValueError: _description_
        """
        profile = self.player.profile
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
                msg_exit('Invalid fishing strategy', is_error=True)

if __name__ == '__main__':
    app = App()
    if not app.validate_args():
        app.show_welcome_msg()
        app.show_available_profiles()
        app.get_pid_from_user()
    app.gen_player()
    app.display_general_player_info()
    app.display_advanced_player_info()

    if app.config['game'].getboolean('enable_count_down'):
        start_count_down()
    print('The script has been started') 

    controller = WindowController()
    controller.activate_game_window()

    from monitor import is_disconnected
    if is_disconnected():
        print('hehe')
        app.player.disconnected_quit()
    exit()

    app.player.start_fishing()
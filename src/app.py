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

from pyautogui import *

from player import Player
from userprofile import UserProfile
from script import start_count_down
from windowcontroller import WindowController
# from inputimeout import inputimeout, TimeoutOccurred

class App():
    def __init__(self):
        """Initalize configParser, generate a list of available profiles.
        """
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')
        self.enable_countdown = self.config['game'].getboolean('enable_count_down')
        self.enable_drink_coffee = self.config['game'].getboolean('enable_drink_coffee')
        self.coffee_shortcut = self.config['shortcut']['coffee']

        # filter out a list of available user profiles
        self.profile_names = ['edit custom configuration']
        for section in self.config.sections():
            if self.config.has_option(section, 'fishing_strategy'):
                self.profile_names.append(section)

        self.args = None
        self.profile = None
        self.fish_count = None
        self.keep_strategy = 'all'

    def parse_args(self):
        parser = argparse.ArgumentParser(
                            prog='app.py', 
                            description='Start the script for Russian Fishing 4', 
                            epilog='')
        parser.add_argument('-a', '--all', action='store_true',
                            help="keep all captured fishes, used by default if not specified")
        parser.add_argument('-m', '--marked', action='store_true',
                            help="keep only the marked fishes")
        parser.add_argument('-n', '--fish-count', type=int, default=0,
                            help='the current number of fishes in your keepnet, 0 if not specified')
        parser.add_argument('-p', '--pid', type=int, 
                            help='the id of profile you want to use')
        # parser.add_argument('-r', '--refill', type=int, 
        #                     help='refill power, hunger, and temperature automatically \
        #                           using shorcut in config.ini')
        self.args = parser.parse_args()

    def process_args(self) -> bool:
        args = self.args

        # self.is_refill_enabled = args.refill

        if args.marked:
            self.keep_strategy = 'marked'

        if not self.is_fish_count_valid(args.fish_count):
            raise ValueError('Invalid fish count')
        self.fish_count = args.fish_count

        if not args.pid:
            return False
        elif not self.is_profile_id_valid(str(args.pid)):
            raise ValueError('Invalid profile id')
        self.profile_id = args.pid
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
        print('+---------------------------------------+')
        print('|   Welcome to use RF4 fishing script   |')
        print('|     Please select a configuration     |')
        print('+---------------------------------------+')


    def show_available_profiles(self) -> None:
        """List all available profiles from 'config.ini'.
        """
        for i, profile in enumerate(self.profile_names):
            print(f'| {i}. {profile:{34 - (i) // 10}} |')
            print('+---------------------------------------+')
            i += 1
    
    def ask_for_profile_id(self) -> None:
        """Let user select a profile id and validate it.
        """
        pid = input("Enter profile id or press q to exit: ")
        while not self.is_profile_id_valid(pid):
            pid = input('Invalid profile id, please try again or press q to quit: ')

        # todo
        if pid == 'q':
            print('The script has been terminated')
            exit()
        elif pid == '0':
            print('Follow the guides in config.ini to configure your settings and create your own profiles')
            exit()
        self.profile_id = pid
        

    def gen_profile(self) -> None:
        """Generate a UserProfile object from config.ini using the selected profile id.
        """
        profile_name = self.profile_names[int(self.profile_id)]
        section = self.config[profile_name]

        retrieval_duration_second = float(section.get('retrieval_duration_second', fallback=0))
        retrieval_delay_second = float(section.get('retrieval_delay_second', fallback=0))
        check_delay_second = float(section.get('check_delay_second', fallback=0))
        cast_power_level = int(section.get('cast_power_level', fallback=3))
        base_iteration = int(section.get('base_iteration', fallback=0))

        self.profile = UserProfile(
            profile_name,
            section['reel_type'],
            section['fishing_strategy'],
            self.keep_strategy,
            self.fish_count,
            retrieval_duration_second,
            retrieval_delay_second,
            check_delay_second,
            cast_power_level,
            base_iteration,
            self.enable_drink_coffee,
            self.coffee_shortcut)

    def display_profile_info(self) -> None:
        """Display the selected profile in the console.
        """
        profile = self.profile
        print('+---------------------------------------+')
        print(f'| Profile name: {profile.profile_name:23} |')
        print('+---------------------------------------+')
        print(f'| Fishing strategy: {profile.fishing_strategy:19} |')
        print('+---------------------------------------+')
        print(f'| Keep strategy: {profile.keep_strategy:22} |')
        print('+---------------------------------------+')
        print(f'| Reel type: {profile.reel_type:26} |')
        print('+---------------------------------------+')
        print(f'| Enable drink coffee: {str(profile.enable_drink_coffee):16} |')
        print('+---------------------------------------+')
        print(f'| Current number of fish: {str(profile.current_fish_count):13} |')
        print('+---------------------------------------+')

    #todo
    def show_save_prompt(self, strategy, release_strategy, fish_count):
        # print('Follow the guides in config.ini to configure your settings and create your own profiles')
        exit()
        if 'y' == input('Do you want to save the current setting?'):
            config = configparser.ConfigParser()
            name = input('Please enter the name of the new setting withoutt "-" or spaces: ')
            if '-' in name or ' ' in name:
                print('Failed to save the setting due to an invalid name')
                return
            config[name] = {
                'fishing_strategy': strategy,
                'release_strategy': release_strategy,
                'fish_count': fish_count
            }

if __name__ == '__main__':
    app = App()
    app.parse_args()
    if not app.process_args():
        app.show_welcome_msg()
        app.show_available_profiles()
        app.ask_for_profile_id()
    app.gen_profile()
    app.display_profile_info()

    if app.enable_countdown:
        start_count_down()
    print('The script has been started') 

    controller = WindowController()
    controller.activate_game_window()
    fisherman = Player(app.profile)
    fisherman.start_fishing()
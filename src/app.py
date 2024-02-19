"""
Main CLI

Usage: app.py
"""
from time import sleep
from argparse import ArgumentParser
from configparser import ConfigParser
import threading
import os
import smtplib

from pyautogui import *
from prettytable import PrettyTable

from player import Player
from userprofile import UserProfile
from script import start_count_down
from windowcontroller import WindowController
from dotenv import load_dotenv

class App():
    def __init__(self):
        """Initalize parsers and generate a list of available user profiles.
        """
        self.config = ConfigParser()
        self.config.read('../config.ini')

        # filter user profiles
        self.profile_names = ['edit configuration file']
        for section in self.config.sections():
            if self.config.has_option(section, 'fishing_strategy'):
                self.profile_names.append(section)

        self.initialize_argparser()

    def initialize_argparser(self) -> None:
        """Configure argparser and parse the command line arguments.
        """
        parser = ArgumentParser(
                            prog='app.py', 
                            description='Start the script for Russian Fishing 4', 
                            epilog='')
        # boolean flags
        parser.add_argument('-a', '--all', action='store_true',
                            help="keep all captured fishes, used by default if not specified")
        parser.add_argument('-m', '--marked', action='store_true',
                            help="keep only the marked fishes")
        parser.add_argument('-c', '--coffee', action='store_true',
                            help='drink coffee if the retrieval time is greater than 2mins')
        parser.add_argument('-r', '--refill', action='store_true', 
                            help='refill food and comfort bar by consuming tea and carrot automatically')
        parser.add_argument('-H', '--harvest-baits', action='store_true',
                            help='harvest baits automatically, only applicable for bottom fishing')
        parser.add_argument('-s', '--send-email', action='store_true',
                            help='send email to yourself when the program is terminated without user interrupt')
        
        # options with arguments
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
        self.enable_unmarked_release = args.marked 
        self.enable_coffee_drinking = args.coffee
        self.enable_food_comfort_refill = args.refill
        self.enable_baits_harvesting = args.harvest_baits
        self.enable_email_sending = args.send_email

        if not self.is_fish_count_valid(args.fishes_in_keepnet):
            print('Error: Invalid fish count')
            exit()
        self.fishes_in_keepnet = args.fishes_in_keepnet

        # validate email address and app password
        if self.enable_email_sending:
            load_dotenv()
            gmail = os.getenv('GMAIL')
            app_password = os.getenv('APP_PASSWORD')

            if gmail is None:
                print('Error: Failed to load environment variable "GMAIL" from .env')
            if app_password is None:
                print('Error: Failed to load environment variable "APP_PASSWORD" from .env')
            if gmail is None or app_password is None:
                exit()

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                    smtp_server.login(gmail, app_password)
            except smtplib.SMTPAuthenticationError:
                print('Error: Username and password not accepted')
                print('Please configure your username and password in .env file')
                print('Follow the guides on https://support.google.com/accounts/answer/185833', 
                    '\nto get more information about app password authentication')
                exit()
                
        if args.pid is None:
            return False
        elif not self.is_pid_valid(str(args.pid)):
            print('Error: Invalid profile id')
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
        return fish_count >= 0 and fish_count < int(self.config['game']['keepnet_limit'])
    
    def is_pid_valid(self, pid: str) -> bool:
        """Validate the profile id.

        :param pid: user profile id
        :type pid: str
        :return: True if valid, False otherwise
        :rtype: bool
        """
        return pid.isdigit() and int(pid) >= 0 and int(pid) <= len(self.profile_names) - 1 

    def show_available_profiles(self) -> None:
        """List available user profiles.
        """
        table = PrettyTable(header=False, align='l')
        table.title = 'Welcome! Please select a profile id to use it'
        for i, profile in enumerate(self.profile_names):
            table.add_row([f'{i:>2}. {profile}'])
        print(table)
    
    def get_pid_from_user(self) -> None:
        """Get and validate user profile id from user input.
        """
        pid = input("Enter profile id or press q to exit: ")
        while not self.is_pid_valid(pid):
            if pid == 'q':
                print('The script has been terminated')
                exit()
            pid = input('Invalid profile id, please try again or press q to quit: ')
        self.pid = int(pid)

    # todo: decapsulate the profile object
    def gen_player(self) -> None:
        """Generate a player object according to args and configuration file.
        """
        if self.pid == 0:
            os.startfile(r'..\config.ini') #? must be backslash
            print('Save to apply changes before restarting the script')
            exit()

        self.profile_name = self.profile_names[self.pid]
        profile_section = self.config[self.profile_name]
        profile = UserProfile(
            self.fishes_in_keepnet,
            self.enable_unmarked_release,
            self.enable_coffee_drinking,
            self.enable_food_comfort_refill,
            self.enable_baits_harvesting,
            self.enable_email_sending,
            profile_section['fishing_strategy'],
            profile_section.getfloat('cast_power_level', fallback=5),
            profile_section.getfloat('retrieval_duration', fallback=0.5),
            profile_section.getfloat('retrieval_delay', fallback=1.5),
            profile_section.getint('base_iteration', fallback=0),
            profile_section.getboolean('enable_acceleration', fallback=False),
            profile_section.getfloat('check_delay', fallback=8),
            profile_section.getfloat('pirk_duration', fallback=1.75),
            profile_section.getfloat('pirk_delay', fallback=4),
            profile_section.getfloat('tighten_duration', fallback=1))
        self.player = Player(profile, self.config)

    def show_user_settings(self) -> None:
        """Display user settings.
        """
        profile = self.player.profile
        table = PrettyTable(header=False, align='l')
        table.title = 'User Settings'

        # general settings
        table.add_rows(
            [
                ['Profile name', self.profile_name],
                ['Fishing strategy', profile.fishing_strategy],
                ['Enable unmarked release', profile.enable_unmarked_release],
                ['Enable coffee drinking', profile.enable_coffee_drinking],
                ['Enable food/comfort refill', profile.enable_food_comfort_refill],
                ['Enable baits harvesting', profile.enable_baits_harvesting],
                ['Enable email sending', profile.enable_email_sending],
                ['Fishes in keepnet', profile.fishes_in_keepnet],
                ['Cast power level', profile.cast_power_level]
            ])
        
        # strategy-specific settings
        match profile.fishing_strategy:
            case 'spin':
                pass
            case 'spin_with_pause':
                table.add_rows(
                    [
                        ['Retrieval duration', profile.retrieval_duration],
                        ['Retrieval delay', profile.retrieval_delay],
                        ['Enable acceleration', profile.enable_acceleration]
                    ])
            case 'bottom':
                table.add_row(['Check delay', profile.check_delay])
            case 'marine':
                table.add_rows(
                    [
                        ['Pirk duration', profile.pirk_duration],
                        ['Pirk delay', profile.pirk_delay],
                        ['Tighten duration', profile.tighten_duration]
                    ])
            case _:
                print('Error: Invalid fishing strategy')
                exit()
        print(table)

if __name__ == '__main__':
    app = App()
    if not app.validate_args():
        app.show_available_profiles()
        app.get_pid_from_user()
    app.gen_player()
    app.show_user_settings()

    if app.config['game'].getboolean('enable_count_down'):
        start_count_down()
    print('The script has been started')
    controller = WindowController()
    controller.activate_game_window()
    app.player.start_fishing()
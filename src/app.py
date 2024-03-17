"""
Main CLI

Usage: app.py
"""
import threading
import os
import smtplib
import logging
from argparse import ArgumentParser
from configparser import ConfigParser

from prettytable import PrettyTable
from dotenv import load_dotenv

from windowcontroller import WindowController
from player import Player
from script import ask_for_confirmation

# logging.BASIC_FORMAT: %(levelname)s:%(name)s:%(message)s
# timestamp: %(asctime)s, datefmt='%Y-%m-%d %H:%M:%S',
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

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
        parser.add_argument('-A', '--alcohol', action='store_true',
                            help='drink alcohol before keeping thee fish regularly, the frequency can be set in config.ini')
        parser.add_argument('-r', '--refill', action='store_true', 
                            help='refill food and comfort bar by consuming tea and carrot automatically')
        parser.add_argument('-H', '--harvest', action='store_true',
                            help='harvest baits automatically, only applicable for bottom fishing')
        parser.add_argument('-e', '--email', action='store_true',
                            help='send email to yourself when the program is terminated without user interruption')
        parser.add_argument('-P', '--plot', action='store_true',
                            help='plot a chart of catch per real/game hour and save it in log directory')
        
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
        self.args = self.parser.parse_args()
        if not self.is_fish_count_valid(self.args.fishes_in_keepnet):
            logger.error('Invalid number of fishes in keepnet')
            exit()
        self.fishes_in_keepnet = self.args.fishes_in_keepnet

        # validate email address and app password
        if self.args.email:
            load_dotenv()
            gmail = os.getenv('GMAIL')
            app_password = os.getenv('APP_PASSWORD')

            if gmail is None:
                logger.error('Failed to load environment variable "GMAIL" from .env')
            if app_password is None:
                logger.error('Failed to load environment variable "APP_PASSWORD" from .env')
            if gmail is None or app_password is None:
                exit()

            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
                    smtp_server.login(gmail, app_password)
            except smtplib.SMTPAuthenticationError:
                logger.error('Username and password not accepted')
                print('Please configure your username and password in .env file')
                print('Refer to the guides on https://support.google.com/accounts/answer/185833', 
                    '\nto get more information about app password authentication')
                exit()
                
        if self.args.pid is None:
            return False
        elif not self.is_pid_valid(str(self.args.pid)):
            logger.error('Invalid profile id')
            exit()
        self.pid = self.args.pid
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
        return pid.isdigit() and int(pid) >= 0 and int(pid) < len(self.profile_names) 

    def show_available_profiles(self) -> None:
        """List available user profiles.
        """
        table = PrettyTable(header=False, align='l')
        table.title = 'Welcome! Please select a profile id to use it'
        for i, profile in enumerate(self.profile_names):
            table.add_row([f'{i:>2}. {profile}'])
        print(table)
    
    def ask_for_pid(self) -> None:
        """Get and validate user profile id from user input.
        """
        pid = input("Enter profile id or press q to exit: ")
        while not self.is_pid_valid(pid):
            if pid.strip() == 'q':
                exit()
            pid = input('Invalid profile id, please try again or press q to quit: ')
        self.pid = int(pid)

    # todo: decapsulate the user profile object
    def gen_player(self) -> None:
        """Generate a player object according to args and configuration file.
        """
        if self.pid == 0:
            os.startfile(r'..\config.ini') #? must be backslash
            print('Save the file before restarting the script to apply changes')
            exit()

        self.profile_name = self.profile_names[self.pid]
        # profile_section = self.config[self.profile_name]
        self.player = Player(self.args, self.profile_name)

    def show_user_settings(self) -> None:
        """Display user settings.
        """
        player = self.player
        table = PrettyTable(header=False, align='l')
        table.title = 'User Settings'

        arg_list = [
            'Fishing strategy',
            'Enable unmarked release',
            'Enable coffee drinking',
            'Enable alcohol drinking',
            'Enable food and comfort refill',
            'Enable baits harvesting',
            'Enable email sending',
            'Enable plotting',
            'Fishes in keepnet',
            'Cast power level']
        
        for arg in arg_list:
            table.add_row([arg, getattr(player, arg.lower().replace(' ', '_'))])
        
        # strategy-specific settings
        config_list = []
        match player.fishing_strategy:
            case 'spin':
                pass
            case 'spin_with_pause':
                config_list.extend(
                    [
                        'Retrieval duration', 
                        'Retrieval delay', 
                        'Enable acceleration'
                    ])
            case 'bottom':
                config_list.extend(['Check delay'])
            case 'marine':
                config_list.extend(
                    [
                        'Pirk duration',
                        'Pirk delay',
                        'Pirk timeout',
                        'Tighten duration',
                        'Sink timeout',
                        'Check again delay',
                    ])
            case 'wakey_rig': # todo
                pass 
            case _:
                logger.error('Invalid fishing strategy')
                exit()

        for config in config_list:
            table.add_row([config, getattr(player, config.lower().replace(' ', '_'))])

        print(table)

if __name__ == '__main__':
    app = App()
    if not app.validate_args():
        app.show_available_profiles()
        app.ask_for_pid()
    app.gen_player()
    app.show_user_settings()

    ask_for_confirmation('Do you want to continue with the settings above')
    WindowController().activate_game_window()
    
    app.player.start_fishing()
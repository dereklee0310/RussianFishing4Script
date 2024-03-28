"""
Main CLI.

Usage: app.py
"""
import threading
import os
import smtplib
import logging
from pathlib import Path
from argparse import ArgumentParser
from configparser import ConfigParser
from socket import gaierror

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
        self.config_path = Path(__file__).resolve().parents[1] / 'config.ini'
        self.config = ConfigParser()
        self.config.read(self.config_path)

        # filter user profiles
        self.profile_names = ['edit configuration file']
        for section in self.config.sections():
            if self.config.has_option(section, 'fishing_strategy'):
                self.profile_names.append(section)

    def get_args(self) -> ArgumentParser:
        """Configure argparser and parse the args.

        :return: parsed command line arguments
        :rtype: ArgumentParser
        """
        parser = ArgumentParser(
                            prog='app.py', 
                            description='Start the script for Russian Fishing 4', 
                            epilog='')
        # boolean flags
        relase_group = parser.add_mutually_exclusive_group()
        relase_group.add_argument('-a', '--all', action='store_true',
                            help='keep all captured fishes, used by default')
        relase_group.add_argument('-m', '--marked', action='store_true',
                            help='keep only the marked fishes')
        parser.add_argument('-c', '--coffee', action='store_true',
                            help='drink coffee if the retrieval time is greater than 2mins')
        parser.add_argument('-A', '--alcohol', action='store_true',
                            help='drink alcohol before keeping thee fish regularly')
        parser.add_argument('-r', '--refill', action='store_true', 
                            help='refill hunger and comfort bar by consuming tea and carrot automatically')
        parser.add_argument('-H', '--harvest', action='store_true',
                            help='harvest baits automatically, only applicable for bottom fishing')
        parser.add_argument('-e', '--email', action='store_true',
                            help='send email to yourself when the program is terminated without user interruption')
        parser.add_argument('-P', '--plot', action='store_true',
                            help='plot a chart of catch per real/game hour and save it in log directory')
        parser.add_argument('-s', '--shutdown', action='store_true',
                            help='Shutdown computer after the program is terminated without user interruption')
        parser.add_argument('-l', '--lift', action='store_true',
                            help='Lift the tackle constantly while retrieving to speed up retrieval')
        parser.add_argument('-g', '--gear-ratio-switching', action='store_true',
                            help='When the retrieval timeout, switch the gear ratio automatically')
        
        spool_group = parser.add_mutually_exclusive_group()
        spool_group.add_argument('-d', '--default-spool-icon', action='store_true',
                            help='Use default spool icon to check if the retrieval is finished, used by default')
        spool_group.add_argument('-R', '--rainbow-line', action='store_true',
                            help='Use rainbow line icon to check if the retrieval is finished')
        
        
        # options with arguments
        parser.add_argument('-n', '--fishes-in-keepnet', type=int, default=0,
                            help='the current number of fishes in your keepnet, 0 if not specified')
        parser.add_argument('-p', '--pid', type=int, 
                            help='the id of profile you want to use')
        parser.add_argument('-t', '--boat-ticket-duration', type=int,
                            help='Enable boat ticket auto renewal, use 1, 2, 3, or 5 to speicfy the duration of the ticket')
        self.args = parser.parse_args()

    def validate_args(self) -> None:
        """Validate args: fishes_in_keepnet and pid.
        """
        if not self._is_fish_count_valid(self.args.fishes_in_keepnet):
            logger.error('Invalid number of fishes in keepnet')
            exit()
            
        # pid has no fallback value, check if it's None
        if self.args.pid and not self._is_pid_valid(str(self.args.pid)):
            logger.error('Invalid profile id')
            exit()
        self.pid = self.args.pid # unify pid location in case ask_for_pid() is called afterwards

        if self.args.boat_ticket_duration is not None:
            if (self.args.boat_ticket_duration != 1 and 
                self.args.boat_ticket_duration != 2 and
                self.args.boat_ticket_duration != 3 and
                self.args.boat_ticket_duration != 5):
                logger.error('Invalid ticket duration')
                exit()


    def validate_email(self) -> None:
        load_dotenv()
        email = os.getenv('EMAIL')
        password = os.getenv('PASSWORD')
        smtp_server_name = os.getenv('SMTP_SERVER')

        if email is None:
            logger.error('Failed to load environment variable "EMAIL" from .env')
        if password is None:
            logger.error('Failed to load environment variable "PASSWORD" from .env')
        if smtp_server_name is None:
            logger.error('Failed to load environment variable "SMTP_SERVER" from .env')
        if email is None or password is None or smtp_server_name is None:
            exit()

        try:
            with smtplib.SMTP_SSL(smtp_server_name, 465) as smtp_server:
                smtp_server.login(email, password)
        except smtplib.SMTPAuthenticationError:
            logger.error('Username, password or SMTP server name not accepted')
            print('Please configure your username and password in .env file')
            print('If you are using Gmail, refer to https://support.google.com/accounts/answer/185833', 
                '\nto get more information about app password authentication')
            exit()
        except gaierror:
            logger.error("Invalid SMTP Server, try 'smtp.gmail.com', 'smtp.qq.com' or other SMTP servers")
            exit()

    
    def _is_fish_count_valid(self, fish_count: int) -> bool:
        """Validate the current # of fishes in keepnet.

        :param fish_count: # of fishes
        :type fish_count: int
        :return: True if valid, False otherwise
        :rtype: bool
        """
        return fish_count >= 0 and fish_count < self.config['game'].getint('keepnet_limit')
    
    def _is_pid_valid(self, pid: str) -> bool:
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
        while not self._is_pid_valid(pid):
            if pid.strip() == 'q':
                exit()
            pid = input('Invalid profile id, please try again or press q to quit: ')
        self.pid = int(pid)

    def gen_player_from_settings(self) -> None:
        """Generate a player object according to args and configuration file.
        """
        if self.pid == 0:
            os.startfile(self.config_path)
            print('Save the file before restarting the script to apply changes')
            exit()

        self.profile_name = self.profile_names[self.pid]
        self.player = Player(self.args, self.config, self.profile_name)

    def show_user_settings(self) -> None:
        """Display user settings.
        """
        table = PrettyTable(header=False, align='l')
        table.title = 'User Settings'

        arg_names = self._get_args_names()
        self._build_table(arg_names, table)
        
        config_names = self._get_config_names()
        self._build_table(config_names, table)

        print(table)

    def _get_args_names(self) -> list:
        return [
            'Fishing strategy',
            'Unmarked release',
            'Coffee drinking',
            'Alcohol drinking',
            'Hunger and comfort refill',
            'Baits harvesting',
            'Email sending',
            'Plotting',
            'Shutdown',
            'Rainbow line',
            'Lift',
            'Gear ratio switching',
            'Fishes in keepnet',
            'Cast power level',
            'Boat ticket duration'
            ]
    
    def _get_config_names(self) -> list:
        # strategy-specific settings
        config_names = []
        match self.player.fishing_strategy:
            case 'spin':
                pass
            case 'spin_with_pause':
                config_names.extend(
                    [
                        'Retrieval duration', 
                        'Retrieval delay', 
                        'Base iteration',
                        'Acceleration'
                    ])
            case 'bottom':
                config_names.extend(['Check delay'])
            case 'marine':
                config_names.extend(
                    [
                        'Sink timeout',
                        'Pirk duration',
                        'Pirk delay',
                        'Pirk timeout',
                        'Tighten duration',
                        'Fish hooked check delay',
                    ])
            case 'wakey_rig':
                pass
        return config_names
            # default case already handled in player.py

    def _build_table(self, names: list, table: PrettyTable) -> None:
        for name in names:
            try:
                real_attribute = getattr(self.player, name.lower().replace(' ', '_'))
                table.add_row([name, real_attribute])
            except AttributeError:
                # convert True/False to enabled/disabled
                real_attribute = getattr(self.player, name.lower().replace(' ', '_') + '_enabled')
                table.add_row([name, 'enabled' if real_attribute else 'disabled'])

if __name__ == '__main__':
    app = App()
    app.get_args()
    app.validate_args()
    if app.args.email:
        app.validate_email()

    if app.args.pid is None:
        app.show_available_profiles()
        app.ask_for_pid()
    app.gen_player_from_settings()
    app.show_user_settings()
    

    ask_for_confirmation('Do you want to continue with the settings above')
    WindowController().activate_game_window()
    app.player.start_fishing()
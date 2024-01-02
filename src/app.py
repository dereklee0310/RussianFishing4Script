from fisherman import Fisherman
from pyautogui import getWindowsWithTitle
from pyautogui import *
import configparser
from time import sleep
from userprofile import UserProfile
import sys
# from inputimeout import inputimeout, TimeoutOccurred
# from exceptions import InvalidNumberOfArgumentsError

class App():
    def __init__(self):
        """Initalize configParser, generate a list of available profiles."""
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')
        self.is_countdown_enabled = self.config['misc'].getboolean('enable_count_down')

        # filter a list of available profiles
        self.profile_names = ['edit custom configuration']
        for section in self.config.sections():
            if self.config.has_option(section, 'fishing_strategy'):
                self.profile_names.append(section)

        self.profile = None
        self.profile_id = -1

    def get_profile_id_from_argv(self) -> bool:
        """Set profile id using command line arguments, if any.

        :return: True if profile id is successfully set, otherwise, return False
        :rtype: bool
        """
        n = len(sys.argv)        
        if n == 2:
            self.profile_id = sys.argv[1]
            if self.is_profile_id_valid():
                return True
            print('Invalid profile id, Please enter the profile id manually.')
        else:
            print('Invalid number of arguments, Please enter the profile id manually.')
        return False
    
    def is_profile_id_valid(self) -> bool:
        """Validate the profile id.

        :return: True if profile id is valid, otherwise, return False
        :rtype: bool
        """

        id = self.profile_id
        if id == '0' or id == 'q':
            return True
        elif not id.isdigit() or int(id) < 0 or int(id) > len(self.config.sections()):
            return False
        return True

    def show_welcome_msg(self) -> None:
        """Display the welcome message."""
        print('+---------------------------------------+')
        print('|   Welcome to use RF4 fishing script   |')
        print('|     Please select a configuration     |')
        print('+---------------------------------------+')


    def show_available_profiles(self) -> None:
        """List all available profiles from 'config.ini'."""
        for i, profile in enumerate(self.profile_names):
            print(f'| {i}. {profile:{34 - (i) // 10}} |')
            print('+---------------------------------------+')
            i += 1
    

    def ask_for_profile_id(self) -> None:
        """Let user select a profile id and validate it."""
        self.profile_id = input("Enter profile id or press q to exit: ")
        while not self.is_profile_id_valid():
            self.profile_id = input('Invalid profile id, please try again or press q to quit: ')

        # todo
        if self.profile_id == 'q':
            print('The script has been terminated.')
            exit()
        elif self.profile_id == '0':
            print('This feature has not been implemented yet.')
            exit()
        self.profile_id = self.profile_id
        

    def gen_selected_profile(self) -> None:
        """Generate a UserProfile object from config.ini using the selected profile id."""
        profile_name = self.profile_names[int(self.profile_id)]
        section = self.config[profile_name]
        self.profile = UserProfile(
            profile_name,
            section['reel_name'],
            section['fishing_strategy'],
            section['release_strategy'],
            int(section['current_fish_count']))
        

    def display_selected_profile(self) -> None:
        """Display the selected profile in the console."""

        profile = self.profile
        print('+---------------------------------------+')
        print(f'| Profile name: {profile.profile_name:23} |')
        print('+---------------------------------------+')
        print(f'| Reel name: {profile.reel_name:26} |')
        print('+---------------------------------------+')
        print(f'| Fishing strategy: {profile.fishing_strategy:19} |')
        print('+---------------------------------------+')
        print(f'| Release strategy: {profile.release_strategy:19} |')
        print('+---------------------------------------+')
        print(f'| Current number of fish: {str(profile.current_fish_count):13} |')
        print('+---------------------------------------+')
    

    def start_count_down(self) -> None:
        """
        If the 'enable_count_down' option is enabled, 
        start a count down before executing the script.
        """

        print("Hint: Edit 'enable_count_down' option in config.ini to disable the count down")
        for i in range(5, 0, -1):
            print(f'The script will start in: {i} seconds', end='\r')
            sleep(1)
        print('')

    #todo
    def show_save_prompt(self, strategy, release_strategy, fish_count):
        print('This feature has not been implemented yet.')
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


def main():
    app = App()
    if not app.get_profile_id_from_argv():
        app.show_welcome_msg()
        app.show_available_profiles()
        app.ask_for_profile_id()
    app.gen_selected_profile()
    
    app.display_selected_profile()

    if app.is_countdown_enabled:
        app.start_count_down()
    print('The script has been started.') 

    window = getWindowsWithTitle("Russian Fishing 4")[0]
    window.activate()

    fisherman = Fisherman(app.profile) # todo: bottom fishing trophy slow mode
    fisherman.start_fishing()

if __name__ == '__main__':
    main()
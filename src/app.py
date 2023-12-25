from fisherman import Fisherman
from pyautogui import getWindowsWithTitle
import configparser
from time import sleep
from userprofile import UserProfile
import sys
# from inputimeout import inputimeout, TimeoutOccurred
# from exceptions import InvalidNumberOfArgumentsError
from monitor import is_reel_state_valid

class App():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('../config.ini')
        self.is_countdown_enabled = self.config['misc'].getboolean('enable_count_down')

        # filter a list of available profiles
        self.profile_names = ['custom']
        for section in self.config.sections():
            if self.config.has_option(section, 'fishing_strategy'):
                self.profile_names.append(section)

        self.profile = None
        self.profile_id = -1

    def get_profile_id_from_argv(self) -> bool:
        """Set profile id using command line arguments, if any."""

        n = len(sys.argv)        
        if n == 2:
            if not self.is_profile_id_valid():
                print('Invalid profile id, the program has been terminated.')
                exit()
            self.profile_id = sys.argv[1]
            return True
        elif n > 2:
            print('Invalid number of arguments, the program has been terminated.')
            exit()
        return False
    
    def is_profile_id_valid(self) -> bool:
        """Validate the profile id."""

        id = self.profile_id
        if id == '0' or id == 'q':
            return True
        elif not id.isdigit() or int(id) < 0 or int(id) > len(self.config.sections()):
            return False
        return True

    def show_welcome_msg(self):
        """Display the welcome message."""

        print('+---------------------------------------+')
        print('|   Welcome to use RF4 fishing script   |')
        print('|     Please select a configuration     |')
        print('+---------------------------------------+')

    def show_available_profiles(self):
        """List all available profiles from 'config.ini'."""

        print('| 0. edit custom configuration          |')
        print('+---------------------------------------+')
        for i, profile in enumerate(self.profile_names):
            print(f'| {i + 1}. {profile:{34 - (i + 1) // 10}} |')
            print('+---------------------------------------+')
            i += 1
    

    def ask_for_profile_id(self):
        """Let user select a profile id and validate it."""

        self.profile_id = input("Enter profile id or press 'q' to exit: ")
        while not self.is_profile_id_valid():
            self.profile_id = input('Invalid profile id, please try again or press q to quit: ')

        if self.profile_id == 'q':
            print('The script has been terminated.')
            exit()
        elif self.profile_id == '0':
            print('This feature has not been implemented yet.') #todo
            exit()
        self.profile_id = self.profile_id
        

    def gen_selected_profile(self):
        """Generate a UserProfile object from config.ini using the selected profile id."""

        profile_name = self.profile_names[int(self.profile_id)]
        section = self.config[profile_name]
        self.profile = UserProfile(
            profile_name,
            section['reel_name'],
            section['fishing_strategy'],
            section['release_strategy'],
            int(section['current_fish_count']))
        

    def display_selected_profile(self):
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
    

    def start_count_down(self):
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
    app.show_welcome_msg()
    if not app.get_profile_id_from_argv():
        app.show_available_profiles()
        app.ask_for_profile_id()
    app.gen_selected_profile()
    
    app.display_selected_profile()

    if app.is_countdown_enabled:
        app.start_count_down()

    # window = getWindowsWithTitle("Russian Fishing 4")[0]
    # window.activate()
    if not is_reel_state_valid():
        print('Failed to identify the spool icon.')
        print('Please make sure your reel is at full capacity or change the game resolution and try again.')
        exit()

    fisherman = Fisherman(app.profile) #todo: trophy mode is none
    fisherman.start_fishing()
    print('The script has been started.') 

if __name__ == '__main__':
    main()